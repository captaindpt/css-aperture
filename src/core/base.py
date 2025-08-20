"""Base classes for content extraction and processing."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


class ContentExtractor(ABC):
    """Abstract base class for content extractors."""
    
    def __init__(self, output_dir: str = "."):
        self.base_output_dir = Path(output_dir)
        self.extractions_dir = self.base_output_dir / "extractions"
        self.extractions_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def extract_content(
        self, 
        source: str, 
        output_name: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Extract content from source.
        
        Args:
            source: Source identifier (URL, file path, etc.)
            output_name: Custom output filename
            **kwargs: Additional extractor-specific parameters
        
        Returns:
            Tuple of (raw_file_path, processed_text_path)
        """
        pass
    
    @abstractmethod
    def get_content_info(self, source: str) -> Tuple[str, str]:
        """
        Get content information for naming.
        
        Args:
            source: Source identifier
            
        Returns:
            Tuple of (clean_name, identifier)
        """
        pass
    
    @abstractmethod
    def get_source_type(self) -> str:
        """Return the type of content this extractor handles."""
        pass
    
    def _create_output_directory(self, name: str) -> Path:
        """Create and return output directory for extraction."""
        output_dir = self.extractions_dir / name
        output_dir.mkdir(exist_ok=True)
        return output_dir


class ContentProcessor(ABC):
    """Abstract base class for content processors."""
    
    @abstractmethod
    def process_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process raw content into clean text.
        
        Args:
            content: Raw content string
            metadata: Additional metadata about the content
            
        Returns:
            Processed clean text
        """
        pass
    
    @abstractmethod
    def get_processor_type(self) -> str:
        """Return the type of content this processor handles."""
        pass