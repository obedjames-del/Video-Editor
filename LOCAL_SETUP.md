# Local Setup Guide

Your Video-Editor app is production-ready! Follow these steps to run it on your local machine.

## Prerequisites

1. **Python 3.12+** installed
2. **FFmpeg** installed (for video processing)
3. **uv** package manager (or pip)

### Install Prerequisites

**macOS:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install FFmpeg
brew install ffmpeg

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Ubuntu/Debian:**
```bash
# Install Python 3.12
sudo apt update
sudo apt install python3.12 python3.12-venv

# Install FFmpeg
sudo apt install ffmpeg

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
# Install Python 3.12 from python.org
# Then install FFmpeg via Chocolatey
choco install ffmpeg

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/obedjames-del/Video-Editor.git
cd Video-Editor
```

### 2. Install Dependencies

Using **uv** (recommended - faster):
```bash
uv sync
```

Or using **pip**:
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Configure API Keys

Your `.env` file is already configured in the repository with your API keys:
- ✅ ElevenLabs API Key
- ✅ Pexels API Key
- ✅ Gemini API Key

If you need to update them, edit the `.env` file:
```bash
nano .env  # or use your preferred editor
```

### 4. Verify Installation

Check that everything is configured correctly:
```bash
uv run video-editor config
```

You should see:
```
✓ All API keys configured
Default Voice: 21m00Tcm4TlvDq8ikWAM
Default Resolution: 1920x1080
...
```

## Usage

### Generate Your First Video

Try the example script:
```bash
uv run video-editor generate examples/simple_script.json
```

This will:
1. Generate AI voiceovers for each scene (ElevenLabs)
2. Download matching stock videos (Pexels)
3. Process and sync audio with video
4. Create final video: `output/product_showcase.mp4`

### View Available Commands

```bash
uv run video-editor --help
```

**Available commands:**
- `generate` - Generate video from JSON script
- `config` - Show current configuration
- `cache` - Manage asset cache
- `validate` - Validate a script file
- `voices` - List available ElevenLabs voices

### Example Workflows

**Generate with custom output:**
```bash
uv run video-editor generate script.json --output my_video.mp4
```

**Generate with verbose logging:**
```bash
uv run video-editor generate script.json --verbose
```

**Generate without caching:**
```bash
uv run video-editor generate script.json --no-cache
```

**Validate script before generating:**
```bash
uv run video-editor validate script.json
```

**List available voices:**
```bash
uv run video-editor voices
```

**Clear cache:**
```bash
uv run video-editor cache clear
```

**View cache statistics:**
```bash
uv run video-editor cache stats
```

## Creating Your Own Scripts

Create a JSON file with your video script:

```json
{
  "scenes": [
    {
      "text": "Welcome to my product showcase!",
      "video_query": "modern technology workspace"
    },
    {
      "text": "Our product helps you work faster and smarter.",
      "video_query": "productive team collaboration"
    },
    {
      "text": "Get started today!",
      "video_query": "successful business growth"
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "output_file": "my_product_video.mp4",
    "resolution": "1920x1080",
    "fps": 30,
    "orientation": "landscape"
  }
}
```

Save as `my_script.json` and generate:
```bash
uv run video-editor generate my_script.json
```

### Using Gemini for Smart Video Queries

Let Gemini automatically generate optimal video search queries:

```json
{
  "scenes": [
    {
      "text": "Our AI analyzes your data in real-time.",
      "duration": 5.0
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "output_file": "output.mp4",
    "use_gemini": true
  }
}
```

## Performance Expectations

- **Generation Time**: 30-60 seconds for a 60-second video
- **First Run**: Slower (downloads assets)
- **Cached Runs**: Much faster (reuses cached assets)

## Troubleshooting

### FFmpeg Not Found
```bash
# Verify FFmpeg is installed
ffmpeg -version

# If not, install it (see Prerequisites above)
```

### API Key Errors
```bash
# Verify your keys are correct
uv run video-editor config

# Update keys in .env file if needed
nano .env
```

### Python Version Issues
```bash
# Check Python version (must be 3.12+)
python3 --version

# If too old, install Python 3.12 (see Prerequisites)
```

### Module Not Found
```bash
# Reinstall dependencies
uv sync --force

# Or with pip
pip install -e . --force-reinstall
```

## Cost Estimation

With your configured API keys:

- **ElevenLabs**: ~$5-15/month (10k chars free, then ~$5/30k chars)
- **Pexels**: Free (200 requests/hour)
- **Gemini**: Free tier (pay only if exceeding free limits)

**Average video costs:**
- 60-second video: ~$0.10-0.30 (mostly voiceover)
- With caching: Even lower on subsequent runs

## Next Steps

1. **Test with example**: `uv run video-editor generate examples/simple_script.json`
2. **Create your own script**: Use the template above
3. **Explore features**: Try different voices, resolutions, orientations
4. **Read docs**: Check `ARCHITECTURE.md` for advanced features

## Need Help?

- **Architecture**: See `ARCHITECTURE.md`
- **Testing**: See `TESTING.md`
- **Project Status**: See `PROJECT_STATUS.md`
- **Issues**: Report at https://github.com/obedjames-del/Video-Editor/issues

---

**Your Video-Editor is ready to create amazing videos! 🎬**
