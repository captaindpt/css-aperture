# Content Semantic Search (css-aperture)

A unified tool for extracting and searching content from multiple sources including YouTube videos and EPUB books using state-of-the-art sentence transformer models. Built specifically for AI-assisted content analysis with Claude Code.

## What It Does

**Extract YouTube Subtitles**: Downloads and cleans subtitles from any YouTube video using yt-dlp, supporting multiple languages and auto-generated captions.

**Transcribe Audio/Video**: Uses OpenAI Whisper (local or API) to transcribe any audio/video file - YouTube videos, Instagram, TikTok, podcasts, meetings, etc.

**Extract EPUB Text**: Extracts text content from EPUB books with automatic title detection and metadata parsing, converting XHTML to clean, searchable text.

**Semantic Search**: Performs natural language search over content using sentence embeddings and cosine similarity ranking. Find specific topics, concepts, or discussions without exact keyword matching.

**AI-Optimized Workflows**: Designed for Claude Code and AI agents to analyze video and book content through conversational queries and contextual exploration.

## Key Features

- **Automatic Title Naming**: Automatically retrieves video or book titles and creates organized folders named after the actual content
- **Fast Performance**: File-based embedding cache eliminates redundant processing - first search creates embeddings (~3-5s), subsequent searches are near-instant
- **Intelligent Chunking**: Content split into 4-6 sentence segments for optimal search granularity
- **Context Expansion**: View surrounding content for any search result with configurable context windows
- **Multi-format Support**: Works with YouTube subtitles, EPUB books, speaker-formatted transcripts, and plain text
- **CLI Interface**: Simple commands for extraction, search, and combined workflows

## Technical Architecture

- **Embedding Model**: `all-MiniLM-L6-v2` sentence transformer (384-dimensional vectors)
- **Search Engine**: Cosine similarity ranking with semantic understanding
- **Caching System**: Per-transcript embedding cache with file modification validation
- **Text Processing**: Intelligent chunking and snippet extraction for various transcript formats

## Installation

```bash
git clone https://github.com/your-org/css-aperture
cd css-aperture
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Optional: Add Whisper support for audio/video transcription
pip install openai-whisper  # Local model (free, offline)
# OR
pip install openai          # API mode (requires OPENAI_API_KEY)
# OR both for flexibility

# Recommended: Install ffmpeg for better media support
brew install ffmpeg  # macOS
```

## Automatic Content Naming

When you don't specify a custom name with the `-n` option, css-aperture automatically:

### For YouTube Videos:
1. **Retrieves the video title** from YouTube using yt-dlp
2. **Cleans the title** by removing special characters and normalizing spaces
3. **Creates a folder** named `{clean_title}_{video_id}` in the `extractions/` directory

### For EPUB Books:
1. **Extracts the book title** from EPUB metadata
2. **Cleans the title** by removing special characters and normalizing spaces  
3. **Creates a folder** named after the book title in the `extractions/` directory

Examples:
```bash
# YouTube video
./css-aprtr extract "https://youtube.com/watch?v=dQw4w9WgXcQ"
# Output: Rick_Astley_Never_Gonna_Give_You_Up_Official_Video_4K_Remaster_dQw4w9WgXcQ/

# EPUB book
./css-aprtr extract "/path/to/book.epub"
# Output: The_Art_of_War_Sun_Tzu/
```

This creates organized, meaningful folder names that make it easy to identify content later, especially when working with multiple sources.

## Basic Usage

### Extract Content
```bash
# YouTube (subtitles - fast, requires internet)
./css-aprtr extract "https://youtube.com/watch?v=VIDEO_ID"

# YouTube channel (index videos for later fetching)
./css-aprtr channel index "https://www.youtube.com/@plus1software/videos"

# Fetch one or more channel videos into the indexed channel folder
./css-aprtr channel fetch extractions/PLUS1_Software_Videos_UCxxxxxxxxxxxxxxxx 2GPNKKeXSyQ DYTo38TAg0w -l en

# YouTube (Whisper local - offline capable)
./css-aprtr extract "https://youtube.com/watch?v=VIDEO_ID" -w

# YouTube (Whisper API - fast, accurate)
./css-aprtr extract "https://youtube.com/watch?v=VIDEO_ID" -w --api

# Transcribe local video/audio (requires Whisper)
./css-aprtr extract video.mp4
./css-aprtr extract podcast.mp3 --api  # Use OpenAI API

# Extract EPUB book
./css-aprtr extract "/path/to/book.epub"

# With custom name
./css-aprtr extract video.mp4 -n my_video

# YouTube with custom language and automatic title naming
./css-aprtr extract "https://youtube.com/watch?v=VIDEO_ID" -l es
```

### Search Content
```bash
# Semantic search
./yt-aprtr search "artificial intelligence" -t transcript.txt -r 10

# Expand specific result with context
./yt-aprtr search "machine learning" -t transcript.txt --expand 42 --context 3
```

### Extract and Search Combined
```bash
# YouTube video: one command workflow with automatic title naming (recommended)
./css-aprtr auto "https://youtube.com/watch?v=VIDEO_ID" "neural networks" -r 15

# EPUB book: extract and search in one step
./css-aprtr auto "/path/to/book.epub" "philosophy" -r 20

# With custom names
./css-aprtr auto "https://youtube.com/watch?v=VIDEO_ID" "neural networks" -n interview -r 15
./css-aprtr auto "/path/to/book.epub" "strategy" -n war_book -r 25
```

## Using with Claude Code

This tool is specifically designed for AI-assisted analysis. Launch Claude Code in the repository directory:

```bash
cd css-aperture
claude
```

Claude Code can then:
- Extract content from YouTube videos and EPUB books you provide
- Search content using natural language queries
- Analyze themes, extract insights, and synthesize findings across multiple sources
- Create structured analysis reports in markdown format

**AI Instructions**: Claude Code will automatically read [`CLAUDE.md`](./CLAUDE.md) for detailed usage patterns, command examples, and analysis workflows optimized for AI agents.

## Sample Output

```
🔍 Searching for: 'startup advice'

🎯 Found 10 results:

[156] Speaker (Score: 0.847)
    The most important thing for early-stage startups is to focus on product-market fit before anything else.

[203] Speaker (Score: 0.792)
    Don't scale your team until you've validated that people actually want what you're building.

[089] Speaker (Score: 0.761)
    Talking to customers daily is not optional - it's the difference between success and failure.

💡 Use --expand [ID] to see full context around a specific result
```

Expand for full context:
```bash
./css-aprtr search "startup advice" -t transcript.txt --expand 156 --context 2
```

## Performance Characteristics

- **First Search**: Downloads sentence transformer model (~90MB), creates embeddings for content chunks
- **Subsequent Searches**: Uses cached embeddings for near-instant results
- **Memory Usage**: ~2GB RAM recommended for model loading
- **Cache Storage**: ~5MB per content file for embeddings and chunks

## Project Structure

```
css-aperture/
├── src/core/           # Core functionality (extractors, searcher, processor, cache)
├── extractions/        # Extracted content from videos and books (auto-created)
├── cache/             # Embedding cache storage (auto-created)
├── css-aprtr          # Main executable script
├── CLAUDE.md          # AI agent instructions and technical examples
├── pyproject.toml     # Python packaging configuration
└── requirements.txt   # Dependencies
```

## Dependencies

- **yt-dlp**: YouTube video/subtitle downloading
- **ebooklib**: EPUB book text extraction
- **beautifulsoup4**: HTML/XHTML content parsing
- **sentence-transformers**: Semantic embedding generation  
- **scikit-learn**: Cosine similarity calculations
- **numpy**: Numerical operations
- **torch**: PyTorch backend for transformers

## Configuration

Set environment variables to customize behavior:
```bash
export YSS_MODEL_NAME="all-MiniLM-L6-v2"  # Sentence transformer model
export YSS_CACHE_DIR="cache"              # Cache directory
export YSS_DEFAULT_RESULTS="10"           # Default number of results
```

## Development

```bash
# Run tests
pytest tests/

# Code formatting
black src/ tests/

# Type checking  
mypy src/
```

## License

MIT License - see LICENSE file for details.
