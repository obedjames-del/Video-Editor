# Video Editor - Technical Architecture

## Project Overview

An automated video generation tool that creates finished videos from structured JSON scripts by:
- Pulling stock videos from Pexels API
- Generating AI voiceovers via ElevenLabs
- Using Gemini for intelligent video keyword extraction
- Assembling everything with FFmpeg

**Timeline:** 2-week MVP
**Focus:** Speed and simplicity
**Use Case:** Personal video production

---

## Technology Stack (2026 Modern)

### Core Runtime
- **Python 3.12+** - Latest stable with performance improvements
- **uv** - Ultra-fast package manager (replaces pip/poetry)
- **asyncio** - Concurrent API calls for speed

### Key Dependencies
```toml
click>=8.1.7              # CLI framework
httpx>=0.27.0             # Modern async HTTP client
pydantic>=2.6.0           # JSON validation & parsing
elevenlabs>=1.0.0         # AI voiceover generation
google-generativeai>=0.4.0 # Gemini 2.0 Flash
ffmpeg-python>=0.2.0      # FFmpeg Python wrapper
rich>=13.7.0              # Beautiful terminal UI
python-dotenv>=1.0.0      # Environment configuration
```

### External Tools
- **FFmpeg 7.x** - Video processing
- **Pexels API** - Free stock video (200 req/hour)
- **ElevenLabs API** - Text-to-speech
- **Gemini 2.0 Flash** - Script analysis

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│                   (click + rich UI)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Script Parser & Validator                   │
│                  (Pydantic Models)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│   Gemini Analyzer    │  │  Direct Processing   │
│ (Smart video search) │  │   (User keywords)    │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           └──────────┬──────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Parallel Processing   │
         │    (asyncio)           │
         └────────┬───────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ElevenLabs│ │  Pexels  │ │  Cache   │
│Voiceover │ │  Video   │ │  Manager │
└─────┬────┘ └────┬─────┘ └────┬─────┘
      │           │            │
      └───────────┼────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  FFmpeg Processor  │
         │  - Trim/Loop video │
         │  - Sync to audio   │
         │  - Add transitions │
         │  - Concatenate     │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │   Final Video      │
         │   (MP4 output)     │
         └────────────────────┘
```

---

## Project Structure

```
video-editor/
├── .env.example              # Template for API keys
├── .gitignore
├── pyproject.toml            # uv/pip configuration
├── README.md                 # User documentation
├── ARCHITECTURE.md           # This file
├── CLAUDE.MD                 # AI assistant context
│
├── src/
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── cli.py                # CLI commands (click)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── script.py         # Pydantic models for JSON schema
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini.py         # Gemini API integration
│   │   ├── voiceover.py      # ElevenLabs integration
│   │   ├── video_search.py   # Pexels API integration
│   │   └── cache.py          # Download caching
│   │
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── script_parser.py  # JSON validation
│   │   ├── video_assembler.py # FFmpeg operations
│   │   └── scene_timing.py   # Audio/video sync logic
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py         # Rich console logging
│       └── config.py         # Settings management
│
├── examples/
│   ├── simple_script.json    # Basic example
│   ├── travel_video.json     # Full example
│   └── tutorial_video.json   # Multi-scene example
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
    ├── test_video_search.py
    └── fixtures/
```

---

## JSON Script Schema

### Basic Structure (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class SceneConfig(BaseModel):
    text: str = Field(..., description="Voiceover text for this scene")
    video_query: Optional[str] = Field(None, description="Pexels search query")
    duration: Optional[float] = Field(None, description="Override duration (seconds)")

class ProjectConfig(BaseModel):
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    output_file: str = Field(default="output.mp4")
    resolution: str = Field(default="1920x1080")
    fps: int = Field(default=30)
    orientation: Literal["landscape", "portrait", "square"] = Field(default="landscape")
    transition_duration: float = Field(default=1.0, description="Crossfade duration")

class VideoScript(BaseModel):
    scenes: list[SceneConfig]
    config: ProjectConfig
```

### Example JSON Files

**Simple Example:**
```json
{
  "scenes": [
    {
      "text": "Welcome to our amazing product showcase.",
      "video_query": "modern technology"
    },
    {
      "text": "Our innovative solution helps you work faster.",
      "video_query": "productivity workspace"
    },
    {
      "text": "Get started today and transform your workflow.",
      "video_query": "success celebration"
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "output_file": "product_showcase.mp4",
    "resolution": "1920x1080",
    "orientation": "landscape"
  }
}
```

**Advanced Example with Gemini:**
```json
{
  "scenes": [
    {
      "text": "Discover the hidden beaches of Southeast Asia."
    },
    {
      "text": "Where crystal waters meet untouched paradise."
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "use_gemini": true,
    "output_file": "travel_promo.mp4"
  }
}
```

---

## Core Workflows

### Week 1 MVP Workflow

```
1. User creates script.json with scenes
2. CLI: video-editor generate script.json
3. System validates JSON schema
4. For each scene (parallel):
   a. Generate voiceover via ElevenLabs
   b. Search Pexels for video (use video_query)
   c. Download top result
5. Process videos:
   a. Get voiceover duration for each scene
   b. Trim/loop video to match audio duration
6. FFmpeg concatenation:
   a. Simple cuts (no transitions week 1)
   b. Merge all scenes
7. Output final MP4
```

### Week 2 Enhanced Workflow (with Gemini)

```
1. User creates minimal JSON (text only, no video_query)
2. Gemini analyzes script:
   a. Extract key visual concepts
   b. Suggest optimal video queries per scene
   c. Determine scene pacing
3. Enhanced video selection:
   a. Fetch top 5 Pexels results per query
   b. Gemini analyzes video descriptions
   c. Pick best contextual match
4. Advanced processing:
   a. Smart scene detection
   b. Crossfade transitions
   c. Progress bars with rich
5. Output with metadata
```

---

## API Integration Strategies

### Pexels API

**Endpoint:** `https://api.pexels.com/videos/search`

**Rate Limits:** 200 requests/hour (free tier)

**Implementation:**
```python
import httpx
from typing import List, Dict

async def search_videos(
    query: str,
    orientation: str = "landscape",
    size: str = "medium",
    per_page: int = 5
) -> List[Dict]:
    """Search Pexels for videos matching query."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query": query,
                "orientation": orientation,
                "size": size,
                "per_page": per_page
            }
        )
        data = response.json()
        return data.get("videos", [])

async def download_video(url: str, output_path: str):
    """Download video file from Pexels."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            with open(output_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
```

**Video Selection Logic:**
- Week 1: Always pick first result
- Week 2: Use Gemini to rank top 5 by relevance

### ElevenLabs API

**Endpoint:** `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

**Rate Limits:** Depends on tier (Starter: 30k chars/month)

**Implementation:**
```python
from elevenlabs import generate, save

def generate_voiceover(
    text: str,
    voice_id: str,
    model: str = "eleven_multilingual_v2",
    output_path: str = "output.mp3"
) -> float:
    """Generate voiceover and return duration in seconds."""
    audio = generate(
        text=text,
        voice=voice_id,
        model=model
    )
    save(audio, output_path)

    # Get audio duration
    from mutagen.mp3 import MP3
    audio_file = MP3(output_path)
    return audio_file.info.length
```

**Voice Options:**
- Default voice IDs available in ElevenLabs dashboard
- Support for emotional range in v2 model
- Streaming option for real-time generation (future)

### Gemini API

**Model:** Gemini 2.0 Flash (fastest, cheapest)

**Implementation:**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def analyze_script(script_text: str) -> List[Dict]:
    """Analyze script and suggest video queries."""
    prompt = f"""
    Analyze this video script and suggest optimal video search queries
    for each sentence or scene. Return as JSON array.

    Script: {script_text}

    Format:
    [
      {{"scene": "sentence 1", "video_query": "suggested keywords"}},
      {{"scene": "sentence 2", "video_query": "suggested keywords"}}
    ]
    """

    response = await model.generate_content_async(prompt)
    # Parse JSON from response
    import json
    return json.loads(response.text)
```

**Gemini Use Cases:**
- Week 1: Basic script → video query mapping
- Week 2: Video content analysis, smart selection
- Future: Full script generation from prompts

---

## FFmpeg Processing Pipeline

### Video Trimming/Looping

```python
import ffmpeg

def process_video_clip(
    input_path: str,
    output_path: str,
    target_duration: float,
    resolution: str = "1920x1080"
):
    """Trim or loop video to match target duration."""
    # Get input video duration
    probe = ffmpeg.probe(input_path)
    video_duration = float(probe['format']['duration'])

    if video_duration >= target_duration:
        # Trim video
        stream = ffmpeg.input(input_path, ss=0, t=target_duration)
    else:
        # Loop video to reach target duration
        loops = int(target_duration / video_duration) + 1
        stream = ffmpeg.input(input_path, stream_loop=loops)
        stream = ffmpeg.trim(stream, duration=target_duration)

    # Scale to target resolution
    stream = ffmpeg.filter(stream, 'scale', resolution)
    stream = ffmpeg.output(stream, output_path)
    ffmpeg.run(stream, overwrite_output=True)
```

### Video Concatenation

**Week 1: Simple Cuts**
```python
def concatenate_videos_simple(video_files: List[str], output: str):
    """Concatenate videos with simple cuts."""
    # Create concat file
    with open('concat_list.txt', 'w') as f:
        for video in video_files:
            f.write(f"file '{video}'\n")

    # Concatenate
    stream = ffmpeg.input('concat_list.txt', format='concat', safe=0)
    stream = ffmpeg.output(stream, output, c='copy')
    ffmpeg.run(stream, overwrite_output=True)
```

**Week 2: With Transitions**
```python
def concatenate_with_transitions(
    video_files: List[str],
    output: str,
    transition_duration: float = 1.0
):
    """Concatenate videos with crossfade transitions."""
    if len(video_files) == 1:
        # No transition needed
        return video_files[0]

    # Build complex filter for crossfades
    inputs = [ffmpeg.input(v) for v in video_files]

    # Create xfade filters between each pair
    current = inputs[0]
    for i in range(1, len(inputs)):
        current = ffmpeg.filter(
            [current, inputs[i]],
            'xfade',
            transition='fade',
            duration=transition_duration,
            offset='auto'
        )

    stream = ffmpeg.output(current, output)
    ffmpeg.run(stream, overwrite_output=True)
```

### Audio Overlay

```python
def add_voiceover_track(
    video_path: str,
    audio_path: str,
    output_path: str
):
    """Add voiceover audio to video."""
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)

    stream = ffmpeg.output(
        video,
        audio,
        output_path,
        vcodec='copy',
        acodec='aac'
    )
    ffmpeg.run(stream, overwrite_output=True)
```

---

## Caching Strategy

### Cache Structure

```
cache/
├── videos/
│   ├── pexels_<video_id>.mp4
│   └── processed_<hash>.mp4
├── audio/
│   ├── scene_<hash>.mp3
│   └── final_voiceover.mp3
└── metadata.json
```

### Implementation

```python
import hashlib
import json
from pathlib import Path

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.videos_dir = self.cache_dir / "videos"
        self.audio_dir = self.cache_dir / "audio"
        self.metadata_file = self.cache_dir / "metadata.json"

        # Create directories
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, data: str) -> str:
        """Generate cache key from content."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_cached_video(self, query: str) -> Optional[str]:
        """Check if video for query exists in cache."""
        cache_key = self.get_cache_key(query)
        video_path = self.videos_dir / f"pexels_{cache_key}.mp4"
        return str(video_path) if video_path.exists() else None

    def cache_video(self, query: str, video_path: str) -> str:
        """Save video to cache."""
        cache_key = self.get_cache_key(query)
        cached_path = self.videos_dir / f"pexels_{cache_key}.mp4"
        shutil.copy(video_path, cached_path)
        return str(cached_path)
```

**Cache Benefits:**
- Avoid re-downloading same videos
- Faster iteration during development
- Reduced API calls (stay under rate limits)
- Offline work capability

---

## CLI Interface

### Commands

```bash
# Initialize project (create .env template)
video-editor init

# Generate video from script
video-editor generate script.json

# Generate with options
video-editor generate script.json \
  --output my_video.mp4 \
  --voice-id <elevenlabs_voice_id> \
  --no-cache \
  --verbose

# Preview mode (analyze without generating)
video-editor preview script.json

# Validate script JSON
video-editor validate script.json

# Clear cache
video-editor cache clear

# List cached items
video-editor cache list

# Future: Auto-generate from prompt
video-editor auto "Create a 60-second travel video about Bali" \
  --scenes 5 \
  --voice-id <id>
```

### Rich UI Features

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Progress tracking
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("Generating voiceovers...", total=len(scenes))
    for scene in scenes:
        # Process scene
        progress.advance(task)

# Status tables
table = Table(title="Video Generation Summary")
table.add_column("Scene", style="cyan")
table.add_column("Duration", style="magenta")
table.add_column("Video Query", style="green")
console.print(table)
```

---

## Error Handling & Resilience

### API Failures

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_with_retry(url: str):
    """Retry API calls with exponential backoff."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

### Fallback Strategies

```python
class VideoGenerationError(Exception):
    """Custom exception for video generation failures."""
    pass

async def search_video_with_fallback(query: str) -> str:
    """Search for video with fallback queries."""
    queries = [
        query,                    # Original query
        query.split()[0],         # First word only
        "generic background"      # Ultimate fallback
    ]

    for q in queries:
        videos = await search_videos(q)
        if videos:
            return videos[0]

    raise VideoGenerationError(f"No videos found for query: {query}")
```

### User-Friendly Messages

```python
from rich.panel import Panel

def handle_error(error: Exception):
    """Display user-friendly error messages."""
    if isinstance(error, httpx.HTTPStatusError):
        if error.response.status_code == 429:
            console.print(Panel(
                "[red]API rate limit exceeded.[/red]\n"
                "Please wait a few minutes before retrying.",
                title="⚠️  Rate Limit"
            ))
        elif error.response.status_code == 401:
            console.print(Panel(
                "[red]Invalid API key.[/red]\n"
                "Please check your .env file and ensure keys are correct.",
                title="⚠️  Authentication Failed"
            ))
    else:
        console.print(Panel(
            f"[red]{str(error)}[/red]",
            title="⚠️  Error"
        ))
```

---

## Performance Optimizations

### Parallel Processing

```python
import asyncio
from typing import List, Tuple

async def process_scenes_parallel(scenes: List[SceneConfig]) -> List[Tuple[str, str]]:
    """Process all scenes in parallel for maximum speed."""

    async def process_scene(scene: SceneConfig, index: int):
        # Generate voiceover
        audio_task = generate_voiceover_async(scene.text, index)

        # Search and download video
        video_task = search_and_download_video(scene.video_query, index)

        # Wait for both to complete
        audio_path, video_path = await asyncio.gather(audio_task, video_task)

        return (audio_path, video_path)

    # Process all scenes concurrently
    results = await asyncio.gather(*[
        process_scene(scene, i) for i, scene in enumerate(scenes)
    ])

    return results
```

### Streaming Downloads

```python
async def stream_download(url: str, output_path: str):
    """Stream large video files to disk (memory efficient)."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            total = int(response.headers.get("Content-Length", 0))

            with open(output_path, "wb") as f:
                with Progress() as progress:
                    task = progress.add_task("Downloading...", total=total)

                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
```

---

## Configuration Management

### Environment Variables (.env)

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

# Gemini Settings
USE_GEMINI_BY_DEFAULT=false
GEMINI_MODEL=gemini-2.0-flash
```

### Settings Class

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    elevenlabs_api_key: str
    pexels_api_key: str
    gemini_api_key: str

    # Defaults
    default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    default_orientation: str = "landscape"

    # Processing
    enable_cache: bool = True
    cache_dir: str = "./cache"
    output_dir: str = "./output"
    max_parallel_downloads: int = 5

    # Gemini
    use_gemini_by_default: bool = False
    gemini_model: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Testing Strategy

### Unit Tests

```python
import pytest
from src.models.script import VideoScript, SceneConfig

def test_script_validation():
    """Test JSON schema validation."""
    valid_script = {
        "scenes": [
            {"text": "Hello world", "video_query": "greeting"}
        ],
        "config": {
            "voice_id": "test_voice_id"
        }
    }

    script = VideoScript(**valid_script)
    assert len(script.scenes) == 1
    assert script.config.resolution == "1920x1080"  # Default

def test_invalid_script():
    """Test that invalid scripts raise errors."""
    invalid_script = {
        "scenes": [],  # Empty scenes
        "config": {}   # Missing voice_id
    }

    with pytest.raises(ValidationError):
        VideoScript(**invalid_script)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_pexels_search():
    """Test Pexels API integration."""
    from src.services.video_search import search_videos

    results = await search_videos("ocean")
    assert len(results) > 0
    assert "video_files" in results[0]

@pytest.mark.asyncio
async def test_end_to_end():
    """Test complete video generation pipeline."""
    script = load_test_script("examples/simple_script.json")
    output_path = await generate_video(script)

    assert Path(output_path).exists()
    assert Path(output_path).stat().st_size > 0
```

---

## Deployment & Distribution

### Installation (uv)

```bash
# Clone repository
git clone https://github.com/your-username/video-editor.git
cd video-editor

# Install with uv (fastest)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run
uv run video-editor generate examples/simple_script.json
```

### Package Distribution

```toml
# pyproject.toml
[project.scripts]
video-editor = "src.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```bash
# Build package
uv build

# Install globally
pip install dist/video_editor-0.1.0-py3-none-any.whl
```

---

## Security Considerations

### API Key Protection

```python
# Never commit .env files
# Add to .gitignore:
.env
*.env
.env.local

# Validate keys at startup
def validate_api_keys():
    required_keys = ["ELEVENLABS_API_KEY", "PEXELS_API_KEY"]
    missing = [k for k in required_keys if not os.getenv(k)]

    if missing:
        console.print(f"[red]Missing API keys: {', '.join(missing)}[/red]")
        console.print("Please set them in your .env file")
        sys.exit(1)
```

### Input Sanitization

```python
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filenames."""
    # Remove path traversal attempts
    filename = Path(filename).name

    # Remove special characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)

    # Limit length
    return filename[:255]
```

---

## Monitoring & Logging

### Structured Logging

```python
import logging
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("video-editor")

# Usage
logger.info("Starting video generation")
logger.warning("Pexels rate limit approaching")
logger.error("Failed to download video", exc_info=True)
```

### Metrics Collection (Future)

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GenerationMetrics:
    start_time: datetime
    end_time: datetime
    total_scenes: int
    total_duration: float
    api_calls: int
    cache_hits: int
    errors: int

    @property
    def processing_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
```

---

## Roadmap

### Week 1 MVP (Core Features)
- [x] Project structure setup
- [x] JSON schema with Pydantic
- [ ] ElevenLabs voiceover integration
- [ ] Pexels video search & download
- [ ] Basic FFmpeg concatenation
- [ ] CLI with click
- [ ] Simple error handling
- [ ] Example scripts

### Week 2 (Polish & Intelligence)
- [ ] Gemini script analysis
- [ ] Video trimming/looping to match audio
- [ ] Crossfade transitions
- [ ] Caching system
- [ ] Rich progress indicators
- [ ] Better error messages
- [ ] Testing suite
- [ ] Documentation

### Future Enhancements
- [ ] Subtitle generation (Whisper API)
- [ ] Background music integration
- [ ] Multiple voice support (characters/narrators)
- [ ] Advanced transitions (wipe, zoom, etc.)
- [ ] Color grading/filters
- [ ] Web UI (FastAPI + React)
- [ ] Batch processing
- [ ] Template library
- [ ] Video preview before final render
- [ ] Export presets (YouTube, TikTok, Instagram)
- [ ] Plugin system for custom processors

---

## Cost Analysis

### API Costs (Monthly Estimates for Personal Use)

**Pexels:**
- Free tier: 200 requests/hour
- Cost: $0/month
- Limitations: Rate limited, attribution required

**ElevenLabs:**
- Free: 10,000 characters/month
- Starter: $5/month for 30,000 characters
- Creator: $22/month for 100,000 characters
- Estimated: ~$5-10/month for personal use

**Gemini:**
- Gemini 2.0 Flash: Free tier available
- Paid: ~$0.35 per 1M tokens
- Estimated: <$1/month for personal use

**Total Estimated Cost:** $5-15/month for regular personal use

### Infrastructure Costs

**Storage:**
- Video cache: ~1-2 GB per 10 videos
- Recommendation: 50 GB local storage = Free

**Processing:**
- Local CPU/GPU (FFmpeg): Free
- Cloud option (future): $0.05-0.10 per minute of video

---

## Performance Benchmarks (Target)

### Video Generation Speed

**Target Times (1080p, 60-second video):**
- Script validation: <1 second
- Voiceover generation: 5-10 seconds
- Video search & download: 10-20 seconds
- FFmpeg processing: 10-30 seconds
- **Total: 30-60 seconds** for a 60-second output video

**Optimization Tips:**
- Use parallel processing (asyncio)
- Cache aggressively
- Download videos in parallel
- Use FFmpeg hardware acceleration if available

---

## Troubleshooting Guide

### Common Issues

**1. FFmpeg not found**
```bash
# Install FFmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**2. API Key errors**
```
Check .env file exists and contains valid keys
Ensure no extra spaces or quotes in .env values
Verify keys are active in respective dashboards
```

**3. Video quality issues**
```
Check resolution setting in JSON
Verify Pexels video quality (use "large" size)
Ensure FFmpeg encoding settings are correct
```

**4. Out of memory errors**
```
Process videos sequentially instead of parallel
Reduce video resolution
Clear cache regularly
Use streaming downloads
```

---

## Contributing Guidelines

### Code Style

```bash
# Use ruff for linting and formatting
uv add --dev ruff
uv run ruff check .
uv run ruff format .
```

### Commit Messages

```
feat: Add Gemini video selection
fix: Handle Pexels rate limiting
docs: Update API integration guide
test: Add unit tests for script parser
perf: Optimize parallel video downloads
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes with tests
3. Run linting: `ruff check && ruff format`
4. Run tests: `pytest`
5. Submit PR with clear description

---

## License & Attribution

### Pexels Attribution
All videos from Pexels require attribution in final videos or project documentation.

**Example:**
```
Videos provided by Pexels (https://www.pexels.com)
Voiceover generated by ElevenLabs
```

---

## Support & Resources

### Documentation Links
- ElevenLabs API: https://elevenlabs.io/docs
- Pexels API: https://www.pexels.com/api/documentation/
- Gemini API: https://ai.google.dev/docs
- FFmpeg Documentation: https://ffmpeg.org/documentation.html

### Community
- GitHub Issues: Bug reports and feature requests
- Discussions: Architecture and design questions

---

**Last Updated:** 2026-02-04
**Version:** 1.0 (MVP Architecture)
**Status:** Ready for Implementation
