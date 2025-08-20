"""EPUB content extraction functionality."""

import re
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import xml.etree.ElementTree as ET

from .base import ContentExtractor


class EPUBExtractor(ContentExtractor):
    """Extracts text content from EPUB files."""
    
    def get_source_type(self) -> str:
        """Return the type of content this extractor handles."""
        return "epub"
    
    def get_content_info(self, source: str) -> Tuple[str, str]:
        """
        Get EPUB information for naming.
        
        Args:
            source: EPUB file path
            
        Returns:
            Tuple of (clean_title, file_identifier)
        """
        epub_path = Path(source)
        if not epub_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {source}")
        
        try:
            # Try to extract title from EPUB metadata
            with zipfile.ZipFile(epub_path, 'r') as epub_zip:
                # Look for metadata in content.opf or similar files
                title = self._extract_title_from_epub(epub_zip)
                
                if not title:
                    # Fallback to filename
                    title = epub_path.stem
                
                # Clean title for filename
                clean_title = re.sub(r'[^\w\s-]', '', title)
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                
                # Use filename stem as identifier
                identifier = epub_path.stem
                
                return clean_title, identifier
                
        except Exception as e:
            # Fallback to filename if metadata extraction fails
            title = epub_path.stem
            clean_title = re.sub(r'[^\w\s-]', '', title)
            clean_title = re.sub(r'[-\s]+', '_', clean_title)
            return clean_title, title
    
    def extract_content(
        self, 
        source: str, 
        output_name: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Extract text content from EPUB file.
        
        Args:
            source: EPUB file path
            output_name: Custom output filename
            **kwargs: Additional parameters (currently unused)
        
        Returns:
            Tuple of (epub_file_path, text_file_path)
        """
        epub_path = Path(source)
        if not epub_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {source}")
        
        try:
            # Get content info to generate filename if not provided
            if not output_name:
                clean_title, identifier = self.get_content_info(source)
                output_name = f"{clean_title}_{identifier}"
                print(f"📚 Book title: {clean_title.replace('_', ' ')}")
                print(f"📁 Creating folder: {output_name}")
            
            # Create output directory
            output_dir = self._create_output_directory(output_name)
            
            # Copy EPUB to extraction directory for reference
            epub_copy = output_dir / f"{output_name}.epub"
            if not epub_copy.exists():
                import shutil
                shutil.copy2(epub_path, epub_copy)
            
            # Extract text content
            text_content = self._extract_text_from_epub(epub_path)
            
            # Save processed text
            text_file = output_dir / f"{output_name}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write("**Text extracted from EPUB file**\n\n")
                f.write(text_content)
            
            print(f"✅ Text extracted: {text_file}")
            return str(epub_copy), str(text_file)
            
        except Exception as e:
            raise RuntimeError(f"EPUB extraction failed: {str(e)}")
    
    def _extract_title_from_epub(self, epub_zip: zipfile.ZipFile) -> Optional[str]:
        """Extract title from EPUB metadata."""
        try:
            # Look for content.opf files
            for file_path in epub_zip.namelist():
                if file_path.endswith('.opf') or 'content.opf' in file_path:
                    with epub_zip.open(file_path) as opf_file:
                        content = opf_file.read().decode('utf-8', errors='ignore')
                        
                        # Parse XML to find title
                        try:
                            root = ET.fromstring(content)
                            # Handle namespaces
                            namespaces = {
                                'dc': 'http://purl.org/dc/elements/1.1/',
                                'opf': 'http://www.idpf.org/2007/opf'
                            }
                            
                            title_elem = root.find('.//dc:title', namespaces)
                            if title_elem is not None and title_elem.text:
                                return title_elem.text.strip()
                        except ET.ParseError:
                            # Try regex fallback
                            title_match = re.search(r'<dc:title[^>]*>([^<]+)</dc:title>', content)
                            if title_match:
                                return title_match.group(1).strip()
        except Exception:
            pass
        
        return None
    
    def _extract_text_from_epub(self, epub_path: Path) -> str:
        """Extract and clean text content from EPUB."""
        text_chunks = []
        
        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            # Get list of content files (usually XHTML)
            content_files = []
            
            # Look for spine order in content.opf
            spine_order = self._get_spine_order(epub_zip)
            if spine_order:
                content_files = spine_order
            else:
                # Fallback: get all XHTML files
                content_files = [f for f in epub_zip.namelist() 
                               if f.endswith(('.xhtml', '.html', '.htm')) and not f.startswith('META-INF/')]
                content_files.sort()  # Basic alphabetical order
            
            # Extract text from each content file
            for file_path in content_files:
                try:
                    with epub_zip.open(file_path) as content_file:
                        html_content = content_file.read().decode('utf-8', errors='ignore')
                        clean_text = self._html_to_text(html_content)
                        if clean_text.strip():
                            text_chunks.append(clean_text)
                except Exception:
                    continue  # Skip problematic files
        
        # Join all text chunks
        full_text = '\n\n'.join(text_chunks)
        
        # Final cleanup
        return self._clean_extracted_text(full_text)
    
    def _get_spine_order(self, epub_zip: zipfile.ZipFile) -> list:
        """Get the correct reading order from EPUB spine."""
        try:
            for file_path in epub_zip.namelist():
                if file_path.endswith('.opf'):
                    with epub_zip.open(file_path) as opf_file:
                        content = opf_file.read().decode('utf-8', errors='ignore')
                        
                        try:
                            root = ET.fromstring(content)
                            namespaces = {'opf': 'http://www.idpf.org/2007/opf'}
                            
                            # Build manifest (id -> href mapping)
                            manifest = {}
                            manifest_elem = root.find('.//opf:manifest', namespaces)
                            if manifest_elem is not None:
                                for item in manifest_elem.findall('opf:item', namespaces):
                                    item_id = item.get('id')
                                    href = item.get('href')
                                    if item_id and href:
                                        # Resolve relative paths
                                        base_dir = Path(file_path).parent
                                        full_href = str(base_dir / href)
                                        manifest[item_id] = full_href
                            
                            # Get spine order
                            spine_order = []
                            spine_elem = root.find('.//opf:spine', namespaces)
                            if spine_elem is not None:
                                for itemref in spine_elem.findall('opf:itemref', namespaces):
                                    idref = itemref.get('idref')
                                    if idref in manifest:
                                        spine_order.append(manifest[idref])
                            
                            return spine_order
                        except ET.ParseError:
                            pass
        except Exception:
            pass
        
        return []
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to clean text."""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # Convert common block elements to newlines
        block_elements = ['p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']
        for element in block_elements:
            html_content = re.sub(f'</{element}>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(f'<{element}[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        html_content = html.unescape(html_content)
        
        return html_content
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Split into lines and clean each one
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and very short lines
            if len(line) < 3:
                continue
            
            # Remove excessive whitespace
            line = ' '.join(line.split())
            
            # Skip lines that are mostly punctuation or numbers
            if re.match(r'^[^\w]*\d*[^\w]*$', line):
                continue
            
            clean_lines.append(line)
        
        # Remove consecutive duplicates
        unique_lines = []
        prev_line = ""
        for line in clean_lines:
            if line != prev_line:
                unique_lines.append(line)
                prev_line = line
        
        # Join with paragraph breaks
        return '\n\n'.join(unique_lines)