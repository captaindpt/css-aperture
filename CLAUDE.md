# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is Content Semantic Search - a unified tool for extracting and searching content from multiple sources including YouTube videos and EPUB books. The system implements natural language search over textual content using sentence embeddings and cosine similarity.

### Core Components

**src/core/base.py** - Abstract base classes for content extraction:
- `ContentExtractor` - Base class for all content extractors
- `ContentProcessor` - Base class for content processing

**src/core/extractor.py** - YouTube subtitle extraction with `YouTubeExtractor` class that:
- Downloads subtitles from any YouTube video using yt-dlp
- Automatically retrieves video titles for organized folder naming
- Converts VTT format to clean text
- Handles multiple languages and auto-generated subtitles
- Removes timing information and duplicates

**src/core/epub_extractor.py** - EPUB text extraction with `EPUBExtractor` class that:
- Extracts text content from EPUB files
- Automatically retrieves book titles from metadata
- Converts XHTML content to clean text
- Handles proper reading order via EPUB spine
- Removes HTML formatting and navigation elements

**src/core/extractor_factory.py** - Factory for creating appropriate extractors:
- Automatically detects content type (YouTube URL vs EPUB file)
- Creates appropriate extractor instance
- Provides unified interface for different content types

**src/core/searcher.py** - Semantic search engine with `SemanticSearcher` class that:
- Loads transcripts from various formats (markdown, text)
- Chunks content into searchable segments (~4-6 sentences)
- Generates sentence embeddings using `all-MiniLM-L6-v2` model
- Implements semantic search via cosine similarity
- Provides expandable context viewing

**src/core/processor.py** - Text processing utilities with `TextProcessor` class that:
- Handles both speaker-formatted and generic transcripts
- Chunks content intelligently based on format
- Extracts snippets for search results
- Splits large chunks for better granularity

**src/core/cache.py** - Embedding cache management with `EmbeddingCache` class that:
- Caches embeddings for performance (~3000 vectors, 384-dimensional)
- Manages per-transcript cache directories
- Validates cache integrity and handles updates

**css-aprtr** - Main CLI entry point that provides:
- `extract` - Extract content from YouTube videos or EPUB books
- `search` - Search existing transcripts or extracted text
- `auto` - Extract and search in one command

### Key Files

- `extractions/` - transcripts and analysis go here for each respective effort
- `cache/` - Local storage for embeddings per transcript
- `pyproject.toml` - Modern Python packaging configuration
- `requirements.txt` - Core dependencies: sentence-transformers, numpy, scikit-learn, yt-dlp

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**IMPORTANT FOR CLAUDE CODE**: Always ensure the virtual environment is properly activated before running css-aprtr commands. If you encounter "ModuleNotFoundError" or dependency issues:

1. First check if venv exists and is properly set up: `ls -la venv/`
2. If venv is corrupted or missing, recreate it: `rm -rf venv && python3 -m venv venv`
3. Always activate the virtual environment before running commands: `source venv/bin/activate`
4. Then install dependencies: `pip install -e .`
5. All css-aprtr commands must be prefixed with: `source venv/bin/activate && ./css-aprtr ...`

### Usage Examples
```bash
# Extract YouTube video subtitles with automatic title naming (recommended)
./css-aprtr extract "https://youtube.com/watch?v=abc123"

# Extract EPUB book text with automatic title naming
./css-aprtr extract "/path/to/book.epub"

# Extract with custom name (optional)
./css-aprtr extract "https://youtube.com/watch?v=abc123" -n my_interview
./css-aprtr extract "/path/to/book.epub" -n philosophy_book

# Search existing transcript or text
./css-aprtr search "consciousness artificial intelligence" -t transcript.md -r 10

# Extract and search in one command with automatic naming
./css-aprtr auto "https://youtube.com/watch?v=xyz789" "neural networks" -r 15
./css-aprtr auto "/path/to/book.epub" "consciousness" -r 20

# Expand specific result for full context
./css-aprtr search "substrate consciousness" -t extracted_text.txt --expand 950 --context 4
```

### Configuration
```bash
# Set environment variables for customization
export YSS_MODEL_NAME="all-MiniLM-L6-v2"
export YSS_CACHE_DIR="cache"
export YSS_DEFAULT_RESULTS="10"
```

### Development Notes

- **Model**: Uses `all-MiniLM-L6-v2` (~90MB download on first run)
- **Performance**: First run creates ~3000 embeddings, subsequent searches are instant
- **Chunking**: Paragraph-level chunks split into 4-6 sentence segments for better granularity
- **Similarity**: Results ranked by cosine similarity (0-1 scale)
- **Cache**: Embeddings stored in `cache/embeddings.pkl` and `cache/chunks.pkl`

## AI-Optimized Usage for Claude Code

**Built for AI Analysis**: This repository is specifically designed to be used with Claude Code or other AI agents to read, analyze, and explore YouTube video content through natural language queries.

### Perfect for Claude Code Workflows

This tool is designed to work seamlessly with Claude Code and other AI agents. Here are the key workflows:

### Extract Content for AI Analysis
```bash
# Extract YouTube videos with automatic title naming (recommended) - AI gets meaningful folder names
./css-aprtr extract "https://youtube.com/watch?v=abc123"

# Extract EPUB books with automatic title naming
./css-aprtr extract "/path/to/book.epub"

# Extract with custom name when needed
./css-aprtr extract "https://youtube.com/watch?v=abc123" -n my_video
./css-aprtr extract "/path/to/book.epub" -n my_book

# Extract with custom language and automatic title naming (YouTube only)
./css-aprtr extract "https://youtube.com/watch?v=abc123" -l es
```

### AI-Optimized Semantic Search
```bash
# Search content using natural language - perfect for AI queries
./css-aprtr search "artificial intelligence" -t transcript.txt -r 10

# Expand specific results with full context for deeper AI analysis
./css-aprtr search "consciousness" -t extracted_text.txt --expand 45 --context 5
```

### One-Step Extract & Analyze
```bash
# Extract and immediately search with automatic title naming (recommended)
./css-aprtr auto "https://youtube.com/watch?v=abc123" "neural networks" -r 15
./css-aprtr auto "/path/to/book.epub" "consciousness" -r 20

# With custom name when needed
./css-aprtr auto "https://youtube.com/watch?v=abc123" "neural networks" -n interview -r 15
./css-aprtr auto "/path/to/book.epub" "philosophy" -n philosophy_book -r 25
```

## Command Line Arguments

### Extract Command
- `source`: YouTube video URL or EPUB file path (required)
- `-l, --language`: Subtitle language code for YouTube (default: en)
- `-n, --name`: Custom output filename
- `-o, --output-dir`: Output directory (default: current)

### Search Command
- `query`: Search query (required for search mode)
- `-t, --transcript`: Transcript file path (required)
- `-r, --results`: Number of results (default: 10)
- `-e, --expand`: Expand specific result ID
- `-c, --context`: Context chunks for expand (default: 3)

### Auto Command (Extract + Search)
- `source`: YouTube video URL or EPUB file path (required)
- `query`: Search query (required)
- `-l, --language`: Subtitle language code for YouTube (default: en)
- `-n, --name`: Custom output filename
- `-o, --output-dir`: Output directory (default: current)
- `-r, --results`: Number of results (default: 10)

## AI Analysis Examples

### Extract Content
```bash
# YouTube videos with automatic title naming (creates: Rick_Astley_Never_Gonna_Give_You_Up_Official_Video_4K_Remaster_dQw4w9WgXcQ/)
./css-aprtr extract "https://youtube.com/watch?v=dQw4w9WgXcQ"

# EPUB books with automatic title naming (creates: The_Art_of_War_Sun_Tzu/)
./css-aprtr extract "/path/to/the_art_of_war.epub"

# French video with automatic title naming
./css-aprtr extract "https://youtube.com/watch?v=abc123" -l fr

# Custom names when needed
./css-aprtr extract "https://youtube.com/watch?v=abc123" -n french_interview
./css-aprtr extract "/path/to/book.epub" -n philosophy_book
```

### Search Content
```bash
./css-aprtr search "machine learning algorithms" -t extractions/interview/interview.en.txt -r 15
./css-aprtr search "startup advice" -t extracted_text.txt --expand 123 --context 4
./css-aprtr search "philosophy of war" -t extractions/The_Art_of_War_Sun_Tzu/The_Art_of_War_Sun_Tzu.txt -r 10
```

### One-Step Extract and Search
```bash
# With automatic title naming (recommended for organized AI analysis)
./css-aprtr auto "https://youtube.com/watch?v=abc123" "artificial intelligence" -r 20
./css-aprtr auto "/path/to/book.epub" "philosophy" -r 15

# With custom name when needed
./css-aprtr auto "https://youtube.com/watch?v=abc123" "artificial intelligence" -n ai_talk -r 20
./css-aprtr auto "/path/to/book.epub" "strategy" -n war_book -r 25
```

## AI-Optimized Workflow

1. **Extract**: Use Claude Code to extract content from YouTube videos or EPUB books
2. **Search**: Ask AI to search extracted content using natural language queries
3. **Discover**: Let AI discover relevant content through semantic understanding
4. **Analyze**: Expand interesting results for deeper AI-driven analysis
5. **Synthesize**: Use AI to synthesize insights across multiple sources (videos and books)

## Sample Output for AI Analysis

### Search Results
```
🔍 Searching for: 'Ruby on Rails'

🎯 Found 10 results:

[245] DHH (Score: 0.832)
    Ruby on Rails is a web development framework I created. It's designed to make programming web applications easier and more enjoyable.

[387] DHH (Score: 0.798)
    The philosophy behind Rails is convention over configuration. We make decisions so developers don't have to make them repeatedly.

[512] DHH (Score: 0.776)
    Rails has been used to build millions of applications including Shopify and GitHub. That's incredibly gratifying to see.

💡 Use --expand [ID] to see full context around a specific result
```

### Expanded Context for Deep Analysis
```bash
# Command to expand context
./css-aprtr search "Ruby on Rails" -t transcript.txt --expand 245 --context 3
```

```
🔍 Expanding result ID 245 with 3 chunks of context:
======================================================================

**DHH:** The satisfaction of driving a race car is driving it at the edge of adhesion, as we call it, where you're essentially just a tiny movement away from spinning out. That balance of danger and skill is what's so intoxicating.

**Interviewer:** For someone who became a legendary programmer, you officially got into programming late in life. Can you tell me about your journey?

>>> MAIN RESULT <<<
**DHH:** Ruby on Rails is a web development framework I created. It's designed to make programming web applications easier and more enjoyable. The philosophy behind Rails is convention over configuration - we make decisions so developers don't have to make them repeatedly.
>>> END RESULT <<<

**DHH:** This approach has allowed millions of developers to build applications faster and with less complexity. It's been used for everything from small personal projects to massive applications like Shopify and GitHub.

**Interviewer:** What inspired you to create Rails in the first place?
======================================================================
```

## How It Works for AI Analysis

1. **Chunking**: The transcript is split into paragraph-level chunks
2. **Embedding**: Each chunk is converted to a 384-dimensional vector using sentence transformers
3. **Similarity**: Your query is embedded and compared to all chunks using cosine similarity
4. **Snippets**: Brief 2-sentence previews are extracted from matches
5. **Expansion**: Full context with surrounding paragraphs available on demand
6. **Caching**: Embeddings are cached locally for performance optimization

## AI-Optimized Search Patterns

- **Use natural language queries** - perfect for AI-driven exploration
- **Let AI discover patterns** through semantic understanding
- **Expand results to get full context** for analysis
- **Try conversational queries** that mirror how you'd ask an AI
- **Leverage similarity scores** to help AI gauge relevance (0-1 scale, higher = better)
- **Use auto command** for streamlined AI workflows
- **Synthesize insights** across multiple videos using AI analysis

## Files and Structure

- `extractions/`: Directory containing extracted content from YouTube videos and EPUB books (created on first extraction)
- `cache/`: Directory containing cached embeddings (created on first search)
- `src/core/`: Core functionality modules
- `css-aprtr`: Main executable script (use `./css-aprtr` for all commands)

## Performance Characteristics for AI

- **First Search**: Creates ~3000 embeddings for transcript chunks (~3-5 seconds)
- **Subsequent Searches**: Near-instantaneous thanks to caching (<1 second)
- **Model**: `all-MiniLM-L6-v2` sentence transformer (~90MB download on first run)
- **Embeddings**: 384-dimensional vectors stored locally
- **Similarity**: Cosine similarity ranking (0-1 scale)

## Analysis Documentation Requirement

**IMPORTANT**: When completing content analysis tasks, Claude Code should create a markdown file in the specific content's extraction directory (e.g., `extractions/video_name/analysis.md` or `extractions/book_name/analysis.md`) containing:

- **Summary of key findings and insights**
- **Relevant quotes with context and timestamps/IDs**
- **Thematic analysis and patterns discovered**
- **Answers to specific research questions**
- **Synthesis of main arguments or points made**
- **Methodology used (search queries, expansion criteria)**

### Example Analysis File Structure:
```markdown
# Content Analysis: [Video Title / Book Title]

## Overview
Brief summary of the content and analysis objectives.

## Key Findings

### Theme 1: [Theme Name]
- Finding with supporting quote and context
- Reference to result ID for traceability

### Theme 2: [Theme Name]
- Analysis with specific examples
- Similarity scores and relevance notes

## Notable Quotes
> "Significant quote here" 
> - Speaker Name (Result ID: 245, Score: 0.832)

## Methodology
- Search queries used
- Expansion criteria applied
- Analysis approach taken

## Conclusions
Synthesis of insights and key takeaways.
```

This ensures analysis is preserved, referenceable, and provides a structured record of AI-driven insights while also being communicated to the user.

## Task Management for Video Analysis

**IMPORTANT**: For simple content analysis requests (e.g., "analyze this video/book and extract main points"), do NOT use the TodoWrite tool or create task lists. These are straightforward single-purpose tasks that should be completed directly without overhead of task management. Only use todo lists for complex multi-step development tasks that require planning and tracking.

## Common Workflows

1. **Content Discovery**: Search → Browse snippets → Expand interesting results → Document findings
2. **Research**: Use semantic queries to find related concepts across the transcript
3. **Analysis**: Extract quotes and context for specific topics or themes → Create analysis.md
4. **Comparative Study**: Analyze multiple videos on similar topics → Cross-reference insights