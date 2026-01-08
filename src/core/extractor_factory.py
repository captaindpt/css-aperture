"""Factory for creating appropriate content extractors."""

import re
from pathlib import Path
from typing import Union, Optional

from .base import ContentExtractor
from .extractor import YouTubeExtractor
from .epub_extractor import EPUBExtractor
from .playlist_extractor import YouTubePlaylistExtractor
from .channel_extractor import YouTubeChannelExtractor


class ExtractorFactory:
    """Factory for creating appropriate extractors based on source type."""

    @staticmethod
    def create_extractor(
        source: str,
        output_dir: str = ".",
        use_whisper: bool = False,
        whisper_model: str = "base",
        use_api: bool = False
    ) -> ContentExtractor:
        """
        Create appropriate extractor based on source type.

        Args:
            source: Source identifier (URL for YouTube, file path for EPUB/audio/video)
            output_dir: Output directory for extractions
            use_whisper: Use Whisper for transcription instead of subtitles
            whisper_model: Whisper model size (tiny, base, small, medium, large, turbo)
            use_api: Use OpenAI API for transcription (requires OPENAI_API_KEY)

        Returns:
            Appropriate ContentExtractor instance

        Raises:
            ValueError: If source type is not supported
        """
        # Check playlist first (before single video)
        if ExtractorFactory.is_youtube_playlist_url(source):
            return YouTubePlaylistExtractor(
                output_dir,
                use_whisper=use_whisper,
                whisper_model=whisper_model,
                use_api=use_api
            )
        elif ExtractorFactory.is_youtube_channel_url(source):
            return YouTubeChannelExtractor(output_dir)
        elif ExtractorFactory.is_youtube_url(source):
            if use_whisper:
                from .whisper_extractor import WhisperYouTubeExtractor
                return WhisperYouTubeExtractor(output_dir, model=whisper_model, use_api=use_api)
            return YouTubeExtractor(output_dir)
        elif ExtractorFactory.is_epub_file(source):
            return EPUBExtractor(output_dir)
        elif ExtractorFactory.is_media_file(source):
            from .whisper_extractor import WhisperExtractor
            return WhisperExtractor(output_dir, model=whisper_model, use_api=use_api)
        else:
            raise ValueError(
                f"Unsupported source type: {source}\n"
                "Supported types:\n"
                "  - YouTube URLs\n"
                "  - YouTube channel URLs\n"
                "  - EPUB files (.epub)\n"
                "  - Audio/Video files (.mp3, .mp4, .m4a, .wav, .webm, etc.)"
            )
    
    @staticmethod
    def is_youtube_playlist_url(source: str) -> bool:
        """Check if source is a YouTube playlist URL."""
        playlist_patterns = [
            r'youtube\.com/playlist\?list=',
            r'youtube\.com/watch\?.*list=PL',
            r'youtu\.be/.*\?list=PL'
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in playlist_patterns)

    @staticmethod
    def is_youtube_url(source: str) -> bool:
        """Check if source is a YouTube video URL (not playlist)."""
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'youtube\.com/v/',
            r'm\.youtube\.com/watch\?v='
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in youtube_patterns)

    @staticmethod
    def is_youtube_channel_url(source: str) -> bool:
        """Check if source is a YouTube channel URL (handle/channel/user/c)."""
        channel_patterns = [
            r'youtube\.com/@[^/?#]+(?:/[^?#]+)?',
            r'youtube\.com/channel/[^/?#]+(?:/[^?#]+)?',
            r'youtube\.com/user/[^/?#]+(?:/[^?#]+)?',
            r'youtube\.com/c/[^/?#]+(?:/[^?#]+)?'
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in channel_patterns)
    
    @staticmethod
    def is_epub_file(source: str) -> bool:
        """Check if source is an EPUB file."""
        path = Path(source)
        return path.exists() and path.suffix.lower() == '.epub'

    @staticmethod
    def is_media_file(source: str) -> bool:
        """Check if source is an audio/video file."""
        path = Path(source)
        if not path.exists():
            return False

        media_extensions = {
            # Audio formats
            '.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg', '.wma', '.opus',
            # Video formats
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mpeg', '.mpg'
        }
        return path.suffix.lower() in media_extensions

    @staticmethod
    def get_source_type(source: str) -> str:
        """
        Determine the type of source.

        Args:
            source: Source identifier

        Returns:
            Source type string
        """
        if ExtractorFactory.is_youtube_playlist_url(source):
            return "youtube_playlist"
        elif ExtractorFactory.is_youtube_channel_url(source):
            return "youtube_channel"
        elif ExtractorFactory.is_youtube_url(source):
            return "youtube"
        elif ExtractorFactory.is_epub_file(source):
            return "epub"
        elif ExtractorFactory.is_media_file(source):
            return "media"
        else:
            return "unknown"
