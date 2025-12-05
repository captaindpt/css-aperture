"""Main CLI interface for Content Semantic Search."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..core.extractor_factory import ExtractorFactory
from ..core.searcher import SemanticSearcher
from ..config.settings import default_config


def extract_command(args):
    """Handle extract subcommand."""
    try:
        use_whisper = getattr(args, 'whisper', False)
        whisper_model = getattr(args, 'whisper_model', 'base')
        use_api = getattr(args, 'api', False)

        extractor = ExtractorFactory.create_extractor(
            args.source,
            args.output_dir,
            use_whisper=use_whisper,
            whisper_model=whisper_model,
            use_api=use_api
        )
        source_type = extractor.get_source_type()

        print(f"🎯 Detected source type: {source_type}")
        if use_whisper:
            print(f"🎤 Using Whisper transcription (model: {whisper_model})")

        # Extract content with appropriate parameters
        if source_type == "youtube" or source_type == "youtube_whisper":
            # Default to English subtitles when language not provided
            lang = args.language or 'en'
            raw_file, text_file = extractor.extract_content(
                args.source,
                args.name,
                language=lang
            )
            print(f"✅ Extraction complete:")
            print(f"   Raw file: {raw_file}")
            print(f"   Text file: {text_file}")
        elif source_type == "epub":
            raw_file, text_file = extractor.extract_content(
                args.source,
                args.name
            )
            print(f"✅ Extraction complete:")
            print(f"   EPUB file: {raw_file}")
            print(f"   Text file: {text_file}")
        elif source_type == "audio/video":
            raw_file, text_file = extractor.extract_content(
                args.source,
                args.name,
                language=getattr(args, 'language', None)
            )
            print(f"✅ Transcription complete:")
            print(f"   Transcript file: {text_file}")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)


def search_command(args):
    """Handle search subcommand."""
    if not Path(args.transcript).exists():
        print(f"❌ Transcript file not found: {args.transcript}")
        print("Available files:")
        for file in Path(".").iterdir():
            if file.suffix in ['.md', '.txt']:
                print(f"  - {file}")
        sys.exit(1)
    
    # Create searcher
    searcher = SemanticSearcher(
        model_name=default_config.search.model_name,
        cache_dir=default_config.search.cache_dir
    )
    
    try:
        searcher.load_transcript(args.transcript)
        
        # Handle expand mode
        if args.expand is not None:
            print(f"🔍 Expanding result ID {args.expand} with {args.context} chunks of context:")
            print("=" * 70)
            expanded_context = searcher.get_expanded_context(args.expand, args.context)
            print(expanded_context)
            print("=" * 70)
            return
        
        # Handle search mode
        if not args.query:
            print("❌ Please provide a search query")
            sys.exit(1)
        
        # Perform search
        results = searcher.search(args.query, args.results)
        searcher.print_results(results)
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        sys.exit(1)


def extract_and_search_command(args):
    """Handle combined extract and search."""
    try:
        # First extract
        use_whisper = getattr(args, 'whisper', False)
        whisper_model = getattr(args, 'whisper_model', 'base')
        use_api = getattr(args, 'api', False)

        extractor = ExtractorFactory.create_extractor(
            args.source,
            args.output_dir,
            use_whisper=use_whisper,
            whisper_model=whisper_model,
            use_api=use_api
        )
        source_type = extractor.get_source_type()

        print(f"🎯 Extracting content from {source_type}...")

        if source_type in ["youtube", "youtube_whisper"]:
            # Default to English when language not provided
            lang = args.language or 'en'
            _, text_file = extractor.extract_content(
                args.source,
                args.name,
                language=lang
            )
        elif source_type == "audio/video":
            _, text_file = extractor.extract_content(
                args.source,
                args.name,
                language=getattr(args, 'language', None)
            )
        else:
            _, text_file = extractor.extract_content(
                args.source,
                args.name
            )

        # Then search
        print(f"\n🔍 Searching for: {args.query}")
        searcher = SemanticSearcher(
            model_name=default_config.search.model_name,
            cache_dir=default_config.search.cache_dir
        )

        searcher.load_transcript(text_file)
        results = searcher.search(args.query, args.results)
        searcher.print_results(results)

    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Content Semantic Search - Extract and search content from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract subtitles from YouTube video (requires internet)
  css extract https://youtube.com/watch?v=abc123

  # Transcribe YouTube video using Whisper (works offline if video is downloaded)
  css extract https://youtube.com/watch?v=abc123 -w -m base

  # Transcribe local audio/video file using Whisper (fully offline)
  css extract /path/to/video.mp4
  css extract /path/to/podcast.mp3 -l en

  # Extract text from EPUB book
  css extract /path/to/book.epub

  # Search existing transcript
  css search "artificial intelligence" -t transcript.txt -r 10

  # Extract and search in one command
  css auto https://youtube.com/watch?v=abc123 "AI consciousness"
  css auto /path/to/video.mp4 "machine learning" -w
  css auto /path/to/book.epub "consciousness"

  # Expand context around specific result
  css search "consciousness" -t transcript.txt --expand 45 --context 5

Whisper Models (faster → more accurate):
  tiny:   ~1GB RAM, fastest, lowest accuracy
  base:   ~1GB RAM, good balance (default)
  small:  ~2GB RAM, better accuracy
  medium: ~5GB RAM, high accuracy
  large:  ~10GB RAM, best accuracy
  turbo:  optimized large model, faster
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract content from YouTube, EPUB, or audio/video files')
    extract_parser.add_argument('source', help='YouTube URL, EPUB file path, or audio/video file path')
    extract_parser.add_argument('-l', '--language', help='Language code for transcription (e.g., en, es, fr)')
    extract_parser.add_argument('-n', '--name', help='Output filename (auto-generated if not provided)')
    extract_parser.add_argument('-o', '--output-dir', default='.', help='Output directory (default: current)')
    extract_parser.add_argument('-w', '--whisper', action='store_true', help='Use Whisper for transcription (for YouTube or local media)')
    extract_parser.add_argument('-m', '--whisper-model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large', 'turbo'], help='Whisper model size (default: base)')
    extract_parser.add_argument('--api', action='store_true', help='Use OpenAI API instead of local model (requires OPENAI_API_KEY)')
    extract_parser.set_defaults(func=extract_command)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search existing transcript')
    search_parser.add_argument('query', nargs='?', help='Search query')
    search_parser.add_argument('-t', '--transcript', required=True, help='Transcript file path')
    search_parser.add_argument('-r', '--results', type=int, default=10, help='Number of results (default: 10)')
    search_parser.add_argument('-e', '--expand', type=int, help='Expand specific result ID')
    search_parser.add_argument('-c', '--context', type=int, default=3, help='Context chunks for expand (default: 3)')
    search_parser.set_defaults(func=search_command)
    
    # Auto command (extract + search)
    auto_parser = subparsers.add_parser('auto', help='Extract and search in one command')
    auto_parser.add_argument('source', help='YouTube URL, EPUB file path, or audio/video file path')
    auto_parser.add_argument('query', help='Search query')
    auto_parser.add_argument('-l', '--language', help='Language code for transcription (e.g., en, es, fr)')
    auto_parser.add_argument('-n', '--name', help='Output filename (auto-generated if not provided)')
    auto_parser.add_argument('-o', '--output-dir', default='.', help='Output directory (default: current)')
    auto_parser.add_argument('-r', '--results', type=int, default=10, help='Number of results (default: 10)')
    auto_parser.add_argument('-w', '--whisper', action='store_true', help='Use Whisper for transcription')
    auto_parser.add_argument('-m', '--whisper-model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large', 'turbo'], help='Whisper model size (default: base)')
    auto_parser.add_argument('--api', action='store_true', help='Use OpenAI API instead of local model (requires OPENAI_API_KEY)')
    auto_parser.set_defaults(func=extract_and_search_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
