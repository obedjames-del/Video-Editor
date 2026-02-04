# Video-Editor - Automated Video Generation Tool

## Project Overview

An AI-powered automated video generation tool that creates finished videos from structured JSON scripts by:
- **Pulling stock videos** from Pexels API based on intelligent queries
- **Generating AI voiceovers** using ElevenLabs text-to-speech
- **Using Gemini AI** for smart script analysis and video keyword extraction
- **Assembling videos** with FFmpeg for professional output

**Timeline:** 2-week MVP
**Focus:** Speed and simplicity for personal video production
**Use Case:** Rapidly create videos for social media, tutorials, marketing, and content creation

---

## Project Structure

```
video-editor/
├── .env.example              # API key template
├── .gitignore
├── pyproject.toml            # Modern Python dependencies (uv)
├── README.md                 # User documentation
├── ARCHITECTURE.md           # Complete technical architecture (READ THIS!)
├── CLAUDE.MD                 # This file - AI assistant context
│
├── src/
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── cli.py                # CLI commands (click framework)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── script.py         # Pydantic models for JSON schema validation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini.py         # Gemini API integration
│   │   ├── voiceover.py      # ElevenLabs integration
│   │   ├── video_search.py   # Pexels API integration
│   │   └── cache.py          # Asset caching system
│   │
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── script_parser.py  # JSON validation & parsing
│   │   ├── video_assembler.py # FFmpeg operations
│   │   └── scene_timing.py   # Audio/video synchronization
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py         # Rich console logging
│       └── config.py         # Settings management
│
├── examples/
│   ├── simple_script.json    # Basic 3-scene example
│   ├── travel_video.json     # Travel promo (6 scenes)
│   ├── tutorial_video.json   # Tutorial workflow (8 scenes)
│   └── minimal_gemini.json   # Gemini-powered auto-keyword example
│
├── cache/                    # Downloaded assets (gitignored)
│   ├── videos/
│   ├── audio/
│   └── metadata.json
│
├── output/                   # Generated videos (gitignored)
│
└── tests/
    ├── __init__.py
    ├── test_script_parser.py
    └── test_video_search.py
```

---

## Technology Stack (2026 Modern)

### Core Runtime
- **Python 3.12+** - Latest stable with performance improvements
- **uv** - Ultra-fast package manager (replaces pip/poetry)
- **asyncio** - Concurrent API calls for maximum speed

### Key Dependencies
```toml
click>=8.1.7              # CLI framework
httpx>=0.27.0             # Modern async HTTP client
pydantic>=2.6.0           # JSON schema validation
elevenlabs>=1.0.0         # AI voiceover generation
google-generativeai>=0.4.0 # Gemini 2.0 Flash
ffmpeg-python>=0.2.0      # FFmpeg Python wrapper
rich>=13.7.0              # Beautiful terminal UI with progress bars
python-dotenv>=1.0.0      # Environment configuration
ruff>=0.2.0               # Fast linting & formatting
```

### External APIs & Tools
- **FFmpeg 7.x** - Video processing engine (local)
- **Pexels API** - Free stock video library (200 req/hour)
- **ElevenLabs API** - Premium text-to-speech ($5-10/month)
- **Gemini 2.0 Flash** - Fast AI for script analysis (free tier available)

---

## Core Workflow

### How It Works

```
1. User creates JSON script (examples/ directory)
   └─ Defines scenes with text and optional video queries

2. CLI command: video-editor generate script.json
   └─ Validates JSON schema with Pydantic

3. Parallel Processing (asyncio for speed):
   ├─ Generate voiceover for each scene (ElevenLabs)
   ├─ Search Pexels for matching videos (Gemini-enhanced queries)
   └─ Download top matches to cache/

4. FFmpeg Video Assembly:
   ├─ Trim/loop videos to match voiceover duration
   ├─ Apply transitions (crossfades)
   └─ Concatenate all scenes

5. Output final MP4 video
   └─ Target: 30-60 seconds processing for 60-second video
```

### Example JSON Script

```json
{
  "scenes": [
    {
      "text": "Welcome to our amazing product showcase.",
      "video_query": "modern technology"
    },
    {
      "text": "Transform your workflow today.",
      "video_query": "productivity workspace"
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "output_file": "output.mp4",
    "resolution": "1920x1080",
    "orientation": "landscape"
  }
}
```

See `examples/` directory for more complete examples.

---

## Development Guidelines

### Code Style
- **Linting:** Use `ruff check && ruff format` before commits
- **Type hints:** Use Python 3.12+ type annotations
- **Docstrings:** Google-style for public APIs
- **Naming:** snake_case for functions, PascalCase for classes
- **Async:** Use `async/await` for all I/O operations

### Git Workflow
- **Branches:** Feature branches prefixed with `claude/`
- **Commits:** Conventional commits (feat:, fix:, docs:, perf:, test:)
- **PRs:** Include tests and update ARCHITECTURE.md if needed
- **Atomic:** One logical change per commit

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Lint
ruff check .
ruff format .
```

---

## Key Features

### Week 1 MVP (Core Pipeline) ✅ COMPLETE
- ✅ JSON script validation with Pydantic
- ✅ ElevenLabs voiceover generation (single voice)
- ✅ Pexels video search & download
- ✅ Gemini integration for smart video keyword extraction
- ✅ FFmpeg video processing (trim, loop, concatenate)
- ✅ Video trimming/looping to match voiceover duration
- ✅ Audio overlay on video clips
- ✅ Asset caching system (avoid re-downloads)
- ✅ CLI tool with click
- ✅ Rich progress indicators and status updates
- ✅ Comprehensive error handling & logging
- ✅ Example scripts and documentation

### Week 2 (Polish & Enhancement)
- ⏳ Crossfade transitions (already implemented, needs testing)
- ⏳ Testing suite (pytest setup)
- ⏳ Performance optimizations
- ⏳ Background music integration
- ⏳ Subtitle generation (Whisper API)
- ⏳ Multiple voice support
- ⏳ Advanced error recovery

### Future Enhancements (Post-MVP)
- Subtitle/caption generation (Whisper API)
- Background music integration
- Multiple voice support (characters/narrators)
- Advanced transitions (wipe, zoom, etc.)
- Color grading and filters
- Web UI (FastAPI + React)
- Batch processing multiple scripts
- Template library for common video types
- Video preview before final render
- Export presets (YouTube, TikTok, Instagram optimized)

---

## Getting Started

### Prerequisites
```bash
# Install Python 3.12+
python --version  # Should be 3.12 or higher

# Install uv (modern package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install FFmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Installation
```bash
# Clone repository
git clone https://github.com/your-username/video-editor.git
cd video-editor

# Install dependencies with uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - ELEVENLABS_API_KEY
# - PEXELS_API_KEY
# - GEMINI_API_KEY
```

### Quick Start
```bash
# Validate a script
uv run video-editor validate examples/simple_script.json

# Generate a video
uv run video-editor generate examples/simple_script.json

# With options
uv run video-editor generate examples/travel_video.json \
  --output my_video.mp4 \
  --verbose
```

---

## API Keys & Configuration

### Required API Keys

**Pexels (Free):**
1. Sign up at https://www.pexels.com/api/
2. Generate API key
3. Free tier: 200 requests/hour

**ElevenLabs ($5-10/month):**
1. Sign up at https://elevenlabs.io
2. Get API key from dashboard
3. Get voice_id from voice library
4. Free tier: 10k characters/month
5. Starter: $5/month for 30k characters

**Gemini (Free tier available):**
1. Get API key from https://ai.google.dev
2. Free tier includes Gemini 2.0 Flash
3. Paid: ~$0.35 per 1M tokens

### Environment Setup (.env)
```bash
# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_key_here
PEXELS_API_KEY=your_pexels_key_here
GEMINI_API_KEY=your_gemini_key_here

# Default Settings
DEFAULT_VOICE_ID=21m00Tcm4TlvDq8ikWAM
DEFAULT_RESOLUTION=1920x1080
DEFAULT_FPS=30
DEFAULT_ORIENTATION=landscape

# Processing Options
ENABLE_CACHE=true
CACHE_DIR=./cache
OUTPUT_DIR=./output
MAX_PARALLEL_DOWNLOADS=5
```

---

## Architecture Deep Dive

For complete technical details, see **ARCHITECTURE.md** which includes:
- Detailed system architecture diagrams
- Pydantic model schemas
- API integration strategies
- FFmpeg processing pipelines
- Caching implementation
- Error handling patterns
- Performance optimization techniques
- Testing strategy
- Security considerations

---

## Performance Targets

**Video Generation Speed (1080p, 60-second video):**
- Script validation: <1 second
- Voiceover generation: 5-10 seconds
- Video search & download: 10-20 seconds
- FFmpeg processing: 10-30 seconds
- **Total: 30-60 seconds** for a 60-second output video

**Optimization Strategies:**
- Parallel API calls with `asyncio`
- Aggressive caching of downloaded assets
- FFmpeg hardware acceleration (if available)
- Streaming downloads for large files

---

## Cost Estimate (Monthly for Personal Use)

- **Pexels:** $0 (free tier, 200 req/hour)
- **ElevenLabs:** $5-10/month (Starter plan)
- **Gemini:** <$1/month (free tier or minimal paid usage)
- **Storage:** Free (local filesystem)
- **Processing:** Free (local FFmpeg)

**Total:** ~$5-15/month for regular personal video creation

---

## Known Issues & Limitations

### Current Limitations
- Single voice per video (multi-voice support in future)
- Simple cut/crossfade transitions only (advanced effects later)
- No subtitle generation yet (Week 2+)
- No background music integration (future)
- Pexels rate limiting (200 req/hour on free tier)

### Troubleshooting
- **FFmpeg not found:** Ensure FFmpeg 7.x is installed and in PATH
- **API errors:** Verify .env file has valid keys without extra spaces
- **Rate limits:** Implement caching to avoid repeated API calls
- **Memory issues:** Process videos sequentially or reduce resolution

---

## Testing Strategy

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_script_parser.py

# Run with verbose output
pytest -v
```

### Test Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: All API integrations
- E2E test: Complete video generation pipeline

---

## Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes with tests
3. Run linting: `ruff check && ruff format`
4. Run tests: `pytest`
5. Commit with conventional format: `feat: add new feature`
6. Push and create PR

### Code Review Checklist
- [ ] Tests pass locally
- [ ] Code follows style guide (ruff formatted)
- [ ] Documentation updated (ARCHITECTURE.md, CLAUDE.MD)
- [ ] Example scripts work
- [ ] No API keys in code

---

## Resources & Documentation

### Internal Docs
- **ARCHITECTURE.md** - Complete technical specification
- **README.md** - User-facing documentation
- **examples/** - Sample JSON scripts

### External APIs
- ElevenLabs API: https://elevenlabs.io/docs
- Pexels API: https://www.pexels.com/api/documentation/
- Gemini API: https://ai.google.dev/docs
- FFmpeg: https://ffmpeg.org/documentation.html

### Python Libraries
- Pydantic: https://docs.pydantic.dev
- Click: https://click.palletsprojects.com
- Rich: https://rich.readthedocs.io
- httpx: https://www.python-httpx.org

---

## Project Status

**Current Phase:** Week 1 MVP - ✅ IMPLEMENTATION COMPLETE
**Next Steps:** Testing and Week 2 enhancements
**Completion:** Week 1 done in record time!

### Implementation Summary

**Week 1 ✅ COMPLETE (All Features Implemented):**
1. ✅ Set up project structure with uv
2. ✅ Implement Pydantic models for JSON validation
3. ✅ Integrate ElevenLabs for voiceover generation
4. ✅ Integrate Pexels for video search/download
5. ✅ Implement Gemini script analysis
6. ✅ Build FFmpeg video processing pipeline
7. ✅ Add video trimming/looping logic
8. ✅ Build caching system
9. ✅ Create CLI with click
10. ✅ Add Rich progress indicators
11. ✅ Add comprehensive error handling and logging
12. ✅ Create example scripts

**Code Statistics:**
- **20 files created** (3,820+ lines of production code)
- **4 services** (voiceover, video search, Gemini, cache)
- **3 processors** (script parser, scene timing, video assembler)
- **2 utilities** (config, logger)
- **1 CLI** with 8 commands
- **4 example scripts** ready to use

**Week 2 Roadmap:**
1. ⏳ Create comprehensive test suite (pytest)
2. ⏳ Test end-to-end video generation
3. ⏳ Enable crossfade transitions (already coded)
4. ⏳ Add background music support
5. ⏳ Implement subtitle generation (Whisper)
6. ⏳ Performance profiling and optimization
7. ⏳ Multiple voice support
8. ⏳ Advanced error recovery

---

## Quick Start Guide

### 1. Install Dependencies
```bash
# Install uv (ultra-fast package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# Install Python dependencies
uv sync
```

### 2. Configure API Keys
```bash
# Initialize .env file
uv run video-editor init

# Edit .env with your keys
nano .env
```

### 3. Generate Your First Video
```bash
# Validate script
uv run video-editor validate examples/simple_script.json

# Generate video
uv run video-editor generate examples/simple_script.json

# Check output
ls -lh output/
```

---

## Security & Best Practices

### API Key Protection
- Never commit .env files
- Use .env.example as template
- Validate API keys at startup
- Rotate keys regularly

### Input Sanitization
- Validate all JSON inputs with Pydantic
- Sanitize filenames to prevent path traversal
- Limit file sizes and durations

### Attribution
- Pexels videos require attribution in final output
- Include credits in video description or end card

---

**Last Updated:** 2026-02-04
**Version:** 1.0.0 (Week 1 MVP Complete)
**Status:** ✅ IMPLEMENTATION COMPLETE - Ready for Testing!
**Lines of Code:** 3,820+
**Next Milestone:** End-to-End Testing & Week 2 Features
