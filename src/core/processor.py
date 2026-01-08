"""Text processing and formatting utilities."""

import re
from pathlib import Path
from typing import List, Dict, Any


class TextProcessor:
    """Handles text cleaning and formatting for transcripts."""
    
    @staticmethod
    def clean_transcript(input_file: Path, output_file: Path) -> None:
        """Remove consecutive duplicate lines from transcript."""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove consecutive duplicates
        cleaned_lines = []
        prev_line = ""
        
        for line in lines:
            line = line.strip()
            if line and line != prev_line:
                cleaned_lines.append(line)
                prev_line = line
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
    
    @staticmethod
    def chunk_transcript(content: str) -> List[Dict[str, Any]]:
        """
        Chunk transcript content for semantic search.
        
        Handles speaker-formatted, paragraph-formatted, and continuous text.
        """
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_speaker = None
        
        # Try speaker-based chunking first
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('**Transcript extracted'):
                continue
            
            # Check for speaker format (expandable pattern)
            speaker_patterns = [
                (r'^\*\*(DHH|Interviewer|Host|Guest):\*\*', r'\*\*(\w+):\*\*'),
                (r'^(DHH|Interviewer|Host|Guest):', r'^(\w+):'),
                (r'^\[(DHH|Interviewer|Host|Guest)\]', r'^\[(\w+)\]')
            ]
            
            speaker_detected = False
            for pattern, extract_pattern in speaker_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous chunk
                    if current_chunk and current_speaker:
                        chunk_text = '\n'.join(current_chunk)
                        if len(chunk_text.strip()) > 20:
                            chunks.append({
                                'content': chunk_text,
                                'speaker': current_speaker,
                                'original': f"**{current_speaker}:** {chunk_text}"
                            })
                    
                    # Extract speaker name
                    match = re.match(extract_pattern, line, re.IGNORECASE)
                    current_speaker = match.group(1) if match else "Speaker"
                    
                    # Start new chunk with cleaned content
                    cleaned_line = re.sub(extract_pattern, '', line, flags=re.IGNORECASE).strip()
                    current_chunk = [cleaned_line] if cleaned_line else []
                    speaker_detected = True
                    break
            
            if not speaker_detected and current_chunk is not None:
                current_chunk.append(line)
        
        # Add final speaker chunk
        if current_chunk and current_speaker:
            chunk_text = '\n'.join(current_chunk)
            if len(chunk_text.strip()) > 20:
                chunks.append({
                    'content': chunk_text,
                    'speaker': current_speaker,
                    'original': f"**{current_speaker}:** {chunk_text}"
                })
        
        # If no speaker format detected, try paragraph-based chunking
        if not chunks:
            paragraphs = content.split('\n\n')
            substantial_paragraphs = []
            
            for para in paragraphs:
                para = para.strip()
                if (para and 
                    not para.startswith('#') and 
                    not para.startswith('**Transcript extracted') and
                    len(para) > 20):
                    substantial_paragraphs.append(para)
            
            # Only use paragraph chunking if we have multiple reasonable-sized paragraphs
            # If we have just one massive paragraph, treat it as continuous text
            if len(substantial_paragraphs) > 1 and all(len(p) < 5000 for p in substantial_paragraphs):
                for para in substantial_paragraphs:
                    chunks.append({
                        'content': para,
                        'speaker': 'Speaker',
                        'original': para
                    })
        
        # If still no chunks (continuous text or single massive paragraph), use intelligent sentence-based chunking
        if not chunks:
            chunks = TextProcessor._chunk_continuous_text(content)
        
        return chunks
    
    @staticmethod
    def _chunk_continuous_text(content: str, target_sentences: int = 8, overlap_sentences: int = 2) -> List[Dict[str, Any]]:
        """
        Chunk continuous text intelligently using sentence boundaries and semantic breaks.
        
        Args:
            content: The continuous text content
            target_sentences: Target number of sentences per chunk
            overlap_sentences: Number of sentences to overlap between chunks for context
        
        Returns:
            List of chunk dictionaries
        """
        # Clean and prepare text
        text = content.strip()
        
        # Remove headers and metadata
        lines = text.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if (line and 
                not line.startswith('#') and 
                not line.startswith('**Transcript extracted') and
                not line.startswith('Kind:') and
                not line.startswith('Language:')):
                clean_lines.append(line)
        
        if not clean_lines:
            return []
        
        # Join lines and split into sentences
        full_text = ' '.join(clean_lines)
        
        # Enhanced sentence splitting that handles common edge cases
        sentence_endings = r'[.!?]+(?:\s+|$)'
        potential_sentences = re.split(sentence_endings, full_text)
        
        # Clean and filter sentences
        sentences = []
        for sent in potential_sentences:
            sent = sent.strip()
            # Keep sentences that are substantial (not just short fragments)
            if len(sent) > 15 and not re.match(r'^[A-Z]{2,}$', sent):  # Skip all-caps short fragments
                sentences.append(sent)
        
        if not sentences:
            return []
        
        chunks = []
        i = 0
        
        while i < len(sentences):
            # Determine chunk end
            end_idx = min(i + target_sentences, len(sentences))
            
            # Try to find natural breaks (periods, topic shifts) within the target range
            chunk_sentences = sentences[i:end_idx]
            
            # Look for topic transition indicators in the last few sentences
            if end_idx < len(sentences) and len(chunk_sentences) >= 4:
                for j in range(len(chunk_sentences) - 2, max(0, len(chunk_sentences) - 4), -1):
                    sentence = chunk_sentences[j].lower()
                    # Look for transition phrases that suggest topic changes
                    if any(phrase in sentence for phrase in [
                        'however', 'meanwhile', 'in contrast', 'on the other hand', 
                        'furthermore', 'moreover', 'additionally', 'nevertheless',
                        'consequently', 'therefore', 'as a result', 'in conclusion',
                        'now let', 'next', 'moving on', 'turning to', 'another',
                        'but', 'yet', 'still', 'indeed'
                    ]):
                        # End chunk after this transition
                        chunk_sentences = chunk_sentences[:j+1]
                        end_idx = i + j + 1
                        break
            
            # Create chunk content
            chunk_text = '. '.join(chunk_sentences)
            if not chunk_text.endswith('.'):
                chunk_text += '.'
            
            # Add overlap context for better semantic continuity
            if chunks and overlap_sentences > 0:
                # Get overlap from previous chunk
                prev_chunk_sentences = chunks[-1]['content'].split('. ')
                if len(prev_chunk_sentences) >= overlap_sentences:
                    overlap_text = '. '.join(prev_chunk_sentences[-overlap_sentences:])
                    chunk_text = overlap_text + '. ' + chunk_text
            
            if len(chunk_text.strip()) > 50:  # Minimum chunk size
                chunks.append({
                    'content': chunk_text,
                    'speaker': 'Speaker',
                    'original': chunk_text
                })
            
            # Move to next chunk (with overlap consideration)
            i = max(end_idx - overlap_sentences, i + 1)
        
        return chunks
    
    @staticmethod
    def split_large_chunks(chunks: List[Dict[str, Any]], max_sentences: int = 8) -> List[Dict[str, Any]]:
        """Split large chunks into smaller ones for better search granularity."""
        final_chunks = []
        
        for chunk in chunks:
            sentences = re.split(r'[.!?]+', chunk['content'])
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # If chunk is already appropriately sized, keep it
            if len(sentences) <= max_sentences:
                final_chunks.append({
                    'id': len(final_chunks),
                    'content': chunk['content'],
                    'original': chunk['original'],
                    'speaker': chunk['speaker'],
                    'start_index': len(final_chunks)
                })
            else:
                # Split large chunks with slight overlap for context
                overlap = 1  # Overlap 1 sentence for continuity
                for i in range(0, len(sentences), max_sentences - overlap):
                    end_idx = min(i + max_sentences, len(sentences))
                    sentence_group = sentences[i:end_idx]
                    
                    sub_chunk_content = '. '.join(sentence_group)
                    if not sub_chunk_content.endswith('.'):
                        sub_chunk_content += '.'
                    
                    if sentence_group:
                        final_chunks.append({
                            'id': len(final_chunks),
                            'content': sub_chunk_content,
                            'original': f"**{chunk['speaker']}:** {sub_chunk_content}",
                            'speaker': chunk['speaker'],
                            'start_index': len(final_chunks)
                        })
                    
                    # If this was the last group, break
                    if end_idx >= len(sentences):
                        break
        
        return final_chunks
    
    @staticmethod
    def extract_snippet(text: str, max_sentences: int = 2) -> str:
        """Extract a brief snippet from text."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        snippet = '. '.join(sentences[:max_sentences])
        if not snippet.endswith('.'):
            snippet += '.'
        
        return snippet
