"""Main CLI interface for Content Semantic Search."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import default_config
from ..core.channel_extractor import YouTubeChannelExtractor
from ..core.extractor import YouTubeExtractor
from ..core.extractor_factory import ExtractorFactory
from ..core.searcher import SemanticSearcher


def extract_command(args):
    """Handle extract subcommand."""
    try:
        use_whisper = getattr(args, "whisper", False)
        whisper_model = getattr(args, "whisper_model", "base")
        use_api = getattr(args, "api", False)

        extractor = ExtractorFactory.create_extractor(
            args.source,
            args.output_dir,
            use_whisper=use_whisper,
            whisper_model=whisper_model,
            use_api=use_api,
        )
        source_type = extractor.get_source_type()

        print(f"🎯 Detected source type: {source_type}")
        if use_whisper:
            print(f"🎤 Using Whisper transcription (model: {whisper_model})")

        # Extract content with appropriate parameters
        if source_type == "youtube_playlist":
            # Playlist extraction
            lang = args.language or "en"
            info_file, combined_file = extractor.extract_content(
                args.source, args.name, language=lang
            )
            # Extraction summary is printed by the extractor
        elif source_type == "youtube_channel":
            # Channel indexing (metadata only)
            info_file, md_file = extractor.extract_content(
                args.source, args.name, max_videos=getattr(args, "max_videos", None)
            )
            print(f"✅ Channel indexing complete:")
            print(f"   JSON: {info_file}")
            print(f"   Markdown: {md_file}")
        elif source_type == "youtube" or source_type == "youtube_whisper":
            # Default to English subtitles when language not provided
            lang = args.language or "en"
            raw_file, text_file = extractor.extract_content(
                args.source, args.name, language=lang
            )
            print(f"✅ Extraction complete:")
            print(f"   Raw file: {raw_file}")
            print(f"   Text file: {text_file}")
        elif source_type == "epub":
            raw_file, text_file = extractor.extract_content(args.source, args.name)
            print(f"✅ Extraction complete:")
            print(f"   EPUB file: {raw_file}")
            print(f"   Text file: {text_file}")
        elif source_type == "audio/video":
            raw_file, text_file = extractor.extract_content(
                args.source, args.name, language=getattr(args, "language", None)
            )
            print(f"✅ Transcription complete:")
            print(f"   Transcript file: {text_file}")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)


def parse_weights(weights_str: str) -> tuple:
    """Parse weights string into tuple of floats."""
    try:
        parts = weights_str.split(",")
        if len(parts) != 3:
            raise ValueError("Weights must have 3 values")
        return tuple(float(p.strip()) for p in parts)
    except Exception:
        print(f"❌ Invalid weights format: {weights_str}")
        print("   Expected format: 0.6,0.3,0.1 (semantic,keyword,entity)")
        sys.exit(1)


def search_command(args):
    """Handle search subcommand."""
    # Check if searching a playlist directory
    playlist_dir = getattr(args, "playlist_dir", None)
    transcript = getattr(args, "transcript", None)

    # Parse search mode and weights
    mode = getattr(args, "mode", "hybrid")
    weights_str = getattr(args, "weights", "0.6,0.3,0.1")
    semantic_weight, keyword_weight, entity_weight = parse_weights(weights_str)

    # Require either -t or -p
    if not playlist_dir and not transcript:
        print(
            "❌ Please provide either -t (transcript file) or -p (playlist directory)"
        )
        sys.exit(1)

    if playlist_dir:
        playlist_path = Path(playlist_dir)
        if not playlist_path.exists():
            print(f"❌ Playlist directory not found: {playlist_dir}")
            sys.exit(1)

        # Create searcher for playlist
        searcher = SemanticSearcher(
            model_name=default_config.search.model_name,
            cache_dir=default_config.search.cache_dir,
        )

        try:
            # Handle search mode for playlist
            if not args.query:
                print("❌ Please provide a search query")
                sys.exit(1)

            # Load and search playlist with hybrid options
            results = searcher.search_playlist(
                playlist_dir,
                args.query,
                args.results,
                mode=mode,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight,
                entity_weight=entity_weight,
            )
            searcher.print_playlist_results(results)

        except Exception as e:
            print(f"❌ Playlist search failed: {e}")
            sys.exit(1)
        return

    # Regular transcript search
    if not Path(transcript).exists():
        print(f"❌ Transcript file not found: {transcript}")
        print("Available files:")
        for file in Path(".").iterdir():
            if file.suffix in [".md", ".txt"]:
                print(f"  - {file}")
        sys.exit(1)

    # Create searcher
    searcher = SemanticSearcher(
        model_name=default_config.search.model_name,
        cache_dir=default_config.search.cache_dir,
    )

    try:
        searcher.load_transcript(transcript)

        # Handle expand mode
        if args.expand is not None:
            print(
                f"🔍 Expanding result ID {args.expand} with {args.context} chunks of context:"
            )
            print("=" * 70)
            expanded_context = searcher.get_expanded_context(args.expand, args.context)
            print(expanded_context)
            print("=" * 70)
            return

        # Handle search mode
        if not args.query:
            print("❌ Please provide a search query")
            sys.exit(1)

        # Perform search with hybrid options
        results = searcher.search(
            args.query,
            args.results,
            mode=mode,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            entity_weight=entity_weight,
        )
        searcher.print_results(results)

    except Exception as e:
        print(f"❌ Search failed: {e}")
        sys.exit(1)


def extract_and_search_command(args):
    """Handle combined extract and search."""
    try:
        # First extract
        use_whisper = getattr(args, "whisper", False)
        whisper_model = getattr(args, "whisper_model", "base")
        use_api = getattr(args, "api", False)

        extractor = ExtractorFactory.create_extractor(
            args.source,
            args.output_dir,
            use_whisper=use_whisper,
            whisper_model=whisper_model,
            use_api=use_api,
        )
        source_type = extractor.get_source_type()

        print(f"🎯 Extracting content from {source_type}...")

        searcher = SemanticSearcher(
            model_name=default_config.search.model_name,
            cache_dir=default_config.search.cache_dir,
        )

        if source_type == "youtube_playlist":
            # Playlist: extract and search combined file
            lang = args.language or "en"
            _, combined_file = extractor.extract_content(
                args.source, args.name, language=lang
            )
            # Search the combined transcript
            print(f"\n🔍 Searching playlist for: {args.query}")
            searcher.load_transcript(combined_file)
            results = searcher.search(args.query, args.results)
            searcher.print_results(results)
        elif source_type == "youtube_channel":
            raise RuntimeError(
                "Auto mode does not support YouTube channel indexing yet.\n"
                "Use:\n"
                "  css channel index <channel_url>\n"
                "  css channel fetch <channel_dir> <video_id>\n"
                "Then search extracted transcripts normally."
            )
        elif source_type in ["youtube", "youtube_whisper"]:
            # Default to English when language not provided
            lang = args.language or "en"
            _, text_file = extractor.extract_content(
                args.source, args.name, language=lang
            )
            # Then search
            print(f"\n🔍 Searching for: {args.query}")
            searcher.load_transcript(text_file)
            results = searcher.search(args.query, args.results)
            searcher.print_results(results)
        elif source_type == "audio/video":
            _, text_file = extractor.extract_content(
                args.source, args.name, language=getattr(args, "language", None)
            )
            print(f"\n🔍 Searching for: {args.query}")
            searcher.load_transcript(text_file)
            results = searcher.search(args.query, args.results)
            searcher.print_results(results)
        else:
            _, text_file = extractor.extract_content(args.source, args.name)
            print(f"\n🔍 Searching for: {args.query}")
            searcher.load_transcript(text_file)
            results = searcher.search(args.query, args.results)
            searcher.print_results(results)

    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)


def channel_index_command(args):
    """Handle channel index subcommand."""
    try:
        extractor = YouTubeChannelExtractor(args.output_dir)
        info_file, md_file = extractor.extract_content(
            args.source, args.name, max_videos=args.max_videos
        )
        print(f"✅ Channel indexing complete:")
        print(f"   JSON: {info_file}")
        print(f"   Markdown: {md_file}")
    except Exception as e:
        print(f"❌ Channel indexing failed: {e}")
        sys.exit(1)


def channel_fetch_command(args):
    """Handle channel fetch subcommand (extract specific videos into channel directory)."""
    channel_dir = Path(args.channel_dir)
    if not channel_dir.exists():
        print(f"❌ Channel directory not found: {args.channel_dir}")
        sys.exit(1)

    use_whisper = getattr(args, "whisper", False)
    whisper_model = getattr(args, "whisper_model", "base")
    use_api = getattr(args, "api", False)
    lang = args.language

    if use_whisper:
        from ..core.whisper_extractor import WhisperYouTubeExtractor

        video_extractor = WhisperYouTubeExtractor(
            str(channel_dir.parent), model=whisper_model, use_api=use_api
        )
        video_extractor.extractions_dir = channel_dir
    else:
        video_extractor = YouTubeExtractor(str(channel_dir.parent))
        video_extractor.extractions_dir = channel_dir

    extracted_ids = []
    for item in args.videos:
        video_url = item
        if not (item.startswith("http://") or item.startswith("https://")):
            video_url = f"https://www.youtube.com/watch?v={item}"

        try:
            print(f"\n📥 Fetching: {video_url}")
            video_extractor.extract_content(
                video_url, output_name=None, language=lang or "en"
            )
            # Best-effort ID extraction
            m = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", video_url)
            extracted_ids.append(m.group(1) if m else item)
        except Exception as e:
            print(f"    ❌ Failed: {e}")

    # Best-effort: update channel_info.json with extracted flags
    info_path = channel_dir / "channel_info.json"
    if extracted_ids and info_path.exists():
        try:
            info = json.loads(info_path.read_text(encoding="utf-8"))
            extracted_set = set(extracted_ids)
            for video in info.get("videos", []):
                if video.get("video_id") in extracted_set:
                    video["extracted"] = True
            info_path.write_text(
                json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass

    if extracted_ids:
        print(f"\n✅ Fetched {len(extracted_ids)} video(s) into: {channel_dir}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Content Semantic Search - Extract and search content from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract subtitles from YouTube video (requires internet)
  css extract https://youtube.com/watch?v=abc123

  # Extract entire YouTube playlist
  css extract "https://youtube.com/playlist?list=PLxxxxxx"

  # Transcribe YouTube video using Whisper (works offline if video is downloaded)
  css extract https://youtube.com/watch?v=abc123 -w -m base

  # Transcribe local audio/video file using Whisper (fully offline)
  css extract /path/to/video.mp4
  css extract /path/to/podcast.mp3 -l en

  # Extract text from EPUB book
  css extract /path/to/book.epub

  # Search existing transcript
  css search "artificial intelligence" -t transcript.txt -r 10

  # Search across entire playlist
  css search "topic" -p extractions/Playlist_Name_PLxxxxxx/

  # Extract and search in one command
  css auto https://youtube.com/watch?v=abc123 "AI consciousness"
  css auto "https://youtube.com/playlist?list=PLxxxxxx" "machine learning"
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
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract", help="Extract content from YouTube, EPUB, or audio/video files"
    )
    extract_parser.add_argument(
        "source", help="YouTube URL, EPUB file path, or audio/video file path"
    )
    extract_parser.add_argument(
        "-l", "--language", help="Language code for transcription (e.g., en, es, fr)"
    )
    extract_parser.add_argument(
        "-n", "--name", help="Output filename (auto-generated if not provided)"
    )
    extract_parser.add_argument(
        "-o", "--output-dir", default=".", help="Output directory (default: current)"
    )
    extract_parser.add_argument(
        "--max-videos",
        type=int,
        help="For channel indexing: limit number of videos to index",
    )
    extract_parser.add_argument(
        "-w",
        "--whisper",
        action="store_true",
        help="Use Whisper for transcription (for YouTube or local media)",
    )
    extract_parser.add_argument(
        "-m",
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model size (default: base)",
    )
    extract_parser.add_argument(
        "--api",
        action="store_true",
        help="Use OpenAI API instead of local model (requires OPENAI_API_KEY)",
    )
    extract_parser.set_defaults(func=extract_command)

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search existing transcript or playlist"
    )
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("-t", "--transcript", help="Transcript file path")
    search_parser.add_argument(
        "-p",
        "--playlist-dir",
        help="Playlist directory to search (searches all videos)",
    )
    search_parser.add_argument(
        "-r", "--results", type=int, default=10, help="Number of results (default: 10)"
    )
    search_parser.add_argument(
        "-e", "--expand", type=int, help="Expand specific result ID"
    )
    search_parser.add_argument(
        "-c",
        "--context",
        type=int,
        default=3,
        help="Context chunks for expand (default: 3)",
    )
    search_parser.add_argument(
        "-m",
        "--mode",
        choices=["hybrid", "semantic", "keyword"],
        default="hybrid",
        help="Search mode: hybrid (default), semantic, or keyword",
    )
    search_parser.add_argument(
        "-w",
        "--weights",
        default="0.6,0.3,0.1",
        help="Weights for semantic,keyword,entity (hybrid mode only, default: 0.6,0.3,0.1)",
    )
    search_parser.set_defaults(func=search_command)

    # Auto command (extract + search)
    auto_parser = subparsers.add_parser(
        "auto", help="Extract and search in one command"
    )
    auto_parser.add_argument(
        "source", help="YouTube URL, EPUB file path, or audio/video file path"
    )
    auto_parser.add_argument("query", help="Search query")
    auto_parser.add_argument(
        "-l", "--language", help="Language code for transcription (e.g., en, es, fr)"
    )
    auto_parser.add_argument(
        "-n", "--name", help="Output filename (auto-generated if not provided)"
    )
    auto_parser.add_argument(
        "-o", "--output-dir", default=".", help="Output directory (default: current)"
    )
    auto_parser.add_argument(
        "-r", "--results", type=int, default=10, help="Number of results (default: 10)"
    )
    auto_parser.add_argument(
        "-w", "--whisper", action="store_true", help="Use Whisper for transcription"
    )
    auto_parser.add_argument(
        "-m",
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model size (default: base)",
    )
    auto_parser.add_argument(
        "--api",
        action="store_true",
        help="Use OpenAI API instead of local model (requires OPENAI_API_KEY)",
    )
    auto_parser.set_defaults(func=extract_and_search_command)

    # Channel command (index/fetch)
    channel_parser = subparsers.add_parser(
        "channel", help="Index and fetch videos from a YouTube channel"
    )
    channel_subparsers = channel_parser.add_subparsers(
        dest="channel_command", help="Channel commands"
    )

    channel_index_parser = channel_subparsers.add_parser(
        "index", help="Index all videos from a channel"
    )
    channel_index_parser.add_argument(
        "source", help="YouTube channel URL (e.g., https://youtube.com/@handle/videos)"
    )
    channel_index_parser.add_argument(
        "-n", "--name", help="Output folder name (auto-generated if not provided)"
    )
    channel_index_parser.add_argument(
        "-o", "--output-dir", default=".", help="Output directory (default: current)"
    )
    channel_index_parser.add_argument(
        "--max-videos", type=int, help="Limit number of videos to index"
    )
    channel_index_parser.set_defaults(func=channel_index_command)

    channel_fetch_parser = channel_subparsers.add_parser(
        "fetch", help="Fetch transcripts for specific channel videos"
    )
    channel_fetch_parser.add_argument(
        "channel_dir", help="Channel extraction directory (created by channel index)"
    )
    channel_fetch_parser.add_argument(
        "videos", nargs="+", help="One or more YouTube video IDs or URLs"
    )
    channel_fetch_parser.add_argument(
        "-l", "--language", help="Subtitle/transcription language code (default: en)"
    )
    channel_fetch_parser.add_argument(
        "-w", "--whisper", action="store_true", help="Use Whisper for transcription"
    )
    channel_fetch_parser.add_argument(
        "-m",
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model size (default: base)",
    )
    channel_fetch_parser.add_argument(
        "--api",
        action="store_true",
        help="Use OpenAI API instead of local model (requires OPENAI_API_KEY)",
    )
    channel_fetch_parser.set_defaults(func=channel_fetch_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "channel" and not getattr(args, "channel_command", None):
        channel_parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
