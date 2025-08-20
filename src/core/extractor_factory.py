"""Factory for creating appropriate content extractors."""

import re
from pathlib import Path
from typing import Union

from .base import ContentExtractor
from .extractor import YouTubeExtractor
from .epub_extractor import EPUBExtractor


class ExtractorFactory:
    """Factory for creating appropriate extractors based on source type."""
    
    @staticmethod
    def create_extractor(source: str, output_dir: str = ".") -> ContentExtractor:
        """
        Create appropriate extractor based on source type.
        
        Args:
            source: Source identifier (URL for YouTube, file path for EPUB)
            output_dir: Output directory for extractions
            
        Returns:
            Appropriate ContentExtractor instance
            
        Raises:
            ValueError: If source type is not supported
        """
        if ExtractorFactory.is_youtube_url(source):
            return YouTubeExtractor(output_dir)
        elif ExtractorFactory.is_epub_file(source):
            return EPUBExtractor(output_dir)
        else:
            raise ValueError(f"Unsupported source type: {source}")
    
    @staticmethod
    def is_youtube_url(source: str) -> bool:
        """Check if source is a YouTube URL."""
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'youtube\.com/v/',
            r'm\.youtube\.com/watch\?v='
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in youtube_patterns)
    
    @staticmethod
    def is_epub_file(source: str) -> bool:
        """Check if source is an EPUB file."""
        path = Path(source)
        return path.exists() and path.suffix.lower() == '.epub'
    
    @staticmethod
    def get_source_type(source: str) -> str:
        """
        Determine the type of source.
        
        Args:
            source: Source identifier
            
        Returns:
            Source type string
        """
        if ExtractorFactory.is_youtube_url(source):
            return "youtube"
        elif ExtractorFactory.is_epub_file(source):
            return "epub"
        else:
            return "unknown"