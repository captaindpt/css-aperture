"""Semantic search engine for transcripts with hybrid BM25 + semantic search."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .cache import EmbeddingCache
from .processor import TextProcessor

# Common proper nouns to recognize as entities (hip-hop focused for transcript analysis)
KNOWN_ENTITIES = {
    "drake",
    "kanye",
    "kendrick",
    "rihanna",
    "asap",
    "rocky",
    "travis",
    "scott",
    "jay",
    "beyonce",
    "nicki",
    "minaj",
    "cardi",
    "megan",
    "future",
    "lil",
    "wayne",
    "eminem",
    "snoop",
    "dogg",
    "dre",
    "diddy",
    "pharrell",
    "tyler",
    "creator",
    "frank",
    "ocean",
    "weeknd",
    "post",
    "malone",
    "bad",
    "bunny",
    "juice",
    "wrld",
    # Tech/business figures
    "elon",
    "musk",
    "bezos",
    "zuckerberg",
    "gates",
    "jobs",
    "cook",
    "nadella",
    "altman",
    "openai",
    "anthropic",
    "google",
    "apple",
    "microsoft",
    "meta",
    "tesla",
    # General
    "trump",
    "biden",
    "obama",
    "putin",
    "china",
    "russia",
    "america",
    "usa",
}


class SemanticSearcher:
    """Semantic search engine with hybrid BM25 + semantic search capabilities."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "cache"):
        self.model = SentenceTransformer(model_name)
        self.cache = EmbeddingCache(cache_dir)
        self.processor = TextProcessor()

        self.transcript_name: Optional[str] = None
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None

        # BM25 index for keyword search
        self.bm25_index: Optional[BM25Okapi] = None
        self.chunk_tokens: List[List[str]] = []

    def load_transcript(self, transcript_path: str) -> None:
        """Load and process transcript for searching."""
        transcript_path = Path(transcript_path)
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        self.transcript_name = transcript_path.stem

        # Try to load from cache first
        if self.cache.is_cache_valid(self.transcript_name, transcript_path):
            print("Loading cached data...")
            cached_data = self.cache.load_cache(self.transcript_name)
            if cached_data:
                self.embeddings, self.chunks = cached_data
                print(f"✅ Using cached {len(self.chunks)} chunks and embeddings")
                # Build BM25 index (fast, not cached)
                self._build_bm25_index()
                return

        # Cache invalid/missing - process from scratch
        print("Loading transcript...")
        with open(transcript_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Process transcript into chunks
        raw_chunks = self.processor.chunk_transcript(content)
        self.chunks = self.processor.split_large_chunks(raw_chunks)

        print(f"Created {len(self.chunks)} chunks from transcript")

        # Create embeddings
        self._create_embeddings()

        # Build BM25 index for keyword search
        self._build_bm25_index()

    def _create_embeddings(self) -> None:
        """Create embeddings for loaded chunks."""
        if not self.transcript_name:
            raise ValueError("No transcript loaded")

        print("Creating embeddings for all chunks...")
        texts = [chunk["content"] for chunk in self.chunks]

        # Create embeddings in batches
        batch_size = 32
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=True)
            embeddings.extend(batch_embeddings)

        self.embeddings = np.array(embeddings)

        # Cache the results
        self.cache.save_cache(self.transcript_name, self.embeddings, self.chunks)

    def _build_bm25_index(self) -> None:
        """Build BM25 index for keyword search."""
        self.chunk_tokens = [self._tokenize(chunk["content"]) for chunk in self.chunks]
        self.bm25_index = BM25Okapi(self.chunk_tokens)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential named entities from query."""
        words = text.split()
        entities = []

        for i, word in enumerate(words):
            clean = re.sub(r"[^\w]", "", word)
            if not clean:
                continue

            # Check known entities list
            if clean.lower() in KNOWN_ENTITIES:
                entities.append(clean.lower())
            # Capitalized words (not at sentence start) are likely names
            elif clean[0].isupper() and i > 0:
                entities.append(clean.lower())

        return list(set(entities))

    def _bm25_scores(self, query: str) -> np.ndarray:
        """Get BM25 scores for query across all chunks."""
        tokens = self._tokenize(query)
        return np.array(self.bm25_index.get_scores(tokens))

    def _entity_boost_scores(self, entities: List[str]) -> np.ndarray:
        """Calculate entity boost scores for chunks containing query entities."""
        scores = np.zeros(len(self.chunks))
        for i, chunk in enumerate(self.chunks):
            content_lower = chunk["content"].lower()
            for entity in entities:
                if entity in content_lower:
                    scores[i] += 1.0
        return scores

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        """Min-max normalize scores to 0-1 range."""
        if scores.max() == scores.min():
            return np.zeros_like(scores)
        return (scores - scores.min()) / (scores.max() - scores.min())

    def search(
        self,
        query: str,
        num_results: int = 10,
        mode: str = "hybrid",
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.3,
        entity_weight: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search on the loaded transcript.

        Args:
            query: Search query
            num_results: Number of results to return
            mode: Search mode - "hybrid" (default), "semantic", or "keyword"
            semantic_weight: Weight for semantic similarity (default 0.6)
            keyword_weight: Weight for BM25 keyword matching (default 0.3)
            entity_weight: Weight for entity boost (default 0.1)

        Returns:
            List of search results with relevance scores
        """
        if self.embeddings is None or not self.chunks:
            raise ValueError("No transcript loaded. Call load_transcript() first.")

        mode_display = f" [{mode}]" if mode != "hybrid" else ""
        print(f"🔍 Searching for: '{query}'{mode_display}")

        # Create query embedding and get semantic scores
        query_embedding = self.model.encode([query])
        semantic_scores = cosine_similarity(query_embedding, self.embeddings)[0]

        if mode == "semantic":
            # Pure semantic search (original behavior)
            final_scores = semantic_scores
        elif mode == "keyword":
            # Pure BM25 keyword search
            final_scores = self._bm25_scores(query)
        else:
            # Hybrid mode: combine semantic + BM25 + entity boost
            bm25_scores = self._bm25_scores(query)

            # Extract entities and calculate boost
            entities = self._extract_entities(query)
            entity_scores = self._entity_boost_scores(entities)

            # Normalize all scores to 0-1 range
            semantic_norm = self._normalize(semantic_scores)
            bm25_norm = self._normalize(bm25_scores)
            entity_norm = self._normalize(entity_scores)

            # Combine with weights
            final_scores = (
                semantic_weight * semantic_norm
                + keyword_weight * bm25_norm
                + entity_weight * entity_norm
            )

        # Get top results
        top_indices = np.argsort(final_scores)[::-1][:num_results]

        results = []
        for idx in top_indices:
            chunk_idx = int(idx)
            score = final_scores[idx]

            chunk = self.chunks[chunk_idx]
            snippet = self.processor.extract_snippet(chunk["content"])

            result = {
                "id": chunk_idx,
                "similarity": score,
                "speaker": chunk["speaker"],
                "snippet": snippet,
                "full_content": chunk["content"],
                "original": chunk["original"],
            }
            results.append(result)

        return results

    def get_expanded_context(self, result_id: int, context_chunks: int = 3) -> str:
        """
        Get expanded context around a specific search result.

        Args:
            result_id: ID of the result to expand
            context_chunks: Number of chunks before/after to include

        Returns:
            Formatted text with expanded context
        """
        if result_id >= len(self.chunks):
            return f"Error: Result ID {result_id} not found"

        # Get context range
        start_idx = max(0, result_id - context_chunks)
        end_idx = min(len(self.chunks), result_id + context_chunks + 1)

        context_chunks_list = self.chunks[start_idx:end_idx]

        # Build context with main result highlighted
        context_text = ""
        for i, chunk in enumerate(context_chunks_list):
            if start_idx + i == result_id:
                context_text += f"\n>>> MAIN RESULT <<<\n"
                context_text += chunk["original"] + "\n"
                context_text += ">>> END RESULT <<<\n\n"
            else:
                context_text += chunk["original"] + "\n\n"

        return context_text.strip()

    def print_results(self, results: List[Dict[str, Any]]) -> None:
        """Print search results in a formatted way."""
        print(f"\n🎯 Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(
                f"[{result['id']}] {result['speaker']} (Score: {result['similarity']:.3f})"
            )
            print(f"    {result['snippet']}")
            print()

        if results:
            print("💡 Use --expand [ID] to see full context around a specific result")

    def search_playlist(
        self,
        playlist_dir: str,
        query: str,
        num_results: int = 10,
        mode: str = "hybrid",
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.3,
        entity_weight: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Search across all videos in a playlist directory.

        Args:
            playlist_dir: Path to the playlist directory
            query: Search query
            num_results: Number of results to return
            mode: Search mode - "hybrid" (default), "semantic", or "keyword"
            semantic_weight: Weight for semantic similarity (default 0.6)
            keyword_weight: Weight for BM25 keyword matching (default 0.3)
            entity_weight: Weight for entity boost (default 0.1)

        Returns:
            List of search results with video source information
        """
        playlist_path = Path(playlist_dir)

        # Find all transcript files in subdirectories
        transcript_files = []
        for subdir in playlist_path.iterdir():
            if subdir.is_dir():
                for txt_file in subdir.glob("*.txt"):
                    transcript_files.append((subdir.name, txt_file))

        if not transcript_files:
            raise ValueError(f"No transcript files found in {playlist_dir}")

        print(f"📋 Loading {len(transcript_files)} transcripts from playlist...")

        # Load and process all transcripts
        all_chunks = []
        all_embeddings = []

        for video_name, txt_file in transcript_files:
            # Load transcript
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Process into chunks
            raw_chunks = self.processor.chunk_transcript(content)
            chunks = self.processor.split_large_chunks(raw_chunks)

            # Add video source info to each chunk
            for chunk in chunks:
                chunk["video_name"] = video_name
                chunk["video_file"] = str(txt_file)

            # Create embeddings for these chunks
            texts = [chunk["content"] for chunk in chunks]
            if texts:
                embeddings = self.model.encode(texts, show_progress_bar=False)
                all_chunks.extend(chunks)
                all_embeddings.extend(embeddings)

        if not all_chunks:
            raise ValueError("No content found in playlist transcripts")

        print(f"✅ Loaded {len(all_chunks)} chunks from {len(transcript_files)} videos")

        # Build BM25 index for playlist chunks
        chunk_tokens = [self._tokenize(chunk["content"]) for chunk in all_chunks]
        playlist_bm25 = BM25Okapi(chunk_tokens)

        # Create query embedding
        mode_display = f" [{mode}]" if mode != "hybrid" else ""
        print(f"🔍 Searching for: '{query}'{mode_display}")
        query_embedding = self.model.encode([query])

        # Calculate semantic similarities
        embeddings_array = np.array(all_embeddings)
        semantic_scores = cosine_similarity(query_embedding, embeddings_array)[0]

        if mode == "semantic":
            final_scores = semantic_scores
        elif mode == "keyword":
            final_scores = np.array(playlist_bm25.get_scores(self._tokenize(query)))
        else:
            # Hybrid mode
            bm25_scores = np.array(playlist_bm25.get_scores(self._tokenize(query)))

            # Entity boost
            entities = self._extract_entities(query)
            entity_scores = np.zeros(len(all_chunks))
            for i, chunk in enumerate(all_chunks):
                content_lower = chunk["content"].lower()
                for entity in entities:
                    if entity in content_lower:
                        entity_scores[i] += 1.0

            # Normalize and combine
            semantic_norm = self._normalize(semantic_scores)
            bm25_norm = self._normalize(bm25_scores)
            entity_norm = self._normalize(entity_scores)

            final_scores = (
                semantic_weight * semantic_norm
                + keyword_weight * bm25_norm
                + entity_weight * entity_norm
            )

        # Get top results
        top_indices = np.argsort(final_scores)[::-1][:num_results]

        results = []
        for idx in top_indices:
            chunk_idx = int(idx)
            score = final_scores[idx]

            chunk = all_chunks[chunk_idx]
            snippet = self.processor.extract_snippet(chunk["content"])

            result = {
                "id": chunk_idx,
                "similarity": score,
                "speaker": chunk["speaker"],
                "snippet": snippet,
                "full_content": chunk["content"],
                "original": chunk["original"],
                "video_name": chunk["video_name"],
                "video_file": chunk["video_file"],
            }
            results.append(result)

        return results

    def print_playlist_results(self, results: List[Dict[str, Any]]) -> None:
        """Print search results from playlist search with video source."""
        print(f"\n🎯 Found {len(results)} results across playlist:\n")

        for i, result in enumerate(results, 1):
            video_display = result["video_name"].replace("_", " ")[:40]
            print(
                f"[{result['id']}] {result['speaker']} (Score: {result['similarity']:.3f})"
            )
            print(f"    📺 {video_display}")
            print(f"    {result['snippet']}")
            print()
