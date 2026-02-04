# Video-Editor 🎬

**Automated AI-Powered Video Generation Tool**

Create professional videos from simple JSON scripts in seconds. Automatically pulls stock footage from Pexels, generates AI voiceovers with ElevenLabs, and assembles everything with intelligent scene timing.

---

## ✨ Features

- 🤖 **AI-Powered**: Uses Gemini to intelligently match videos to your script
- 🎤 **Professional Voiceovers**: ElevenLabs text-to-speech with natural voices
- 🎥 **Stock Video Integration**: Access to free Pexels video library
- ⚡ **Fast Processing**: Generate 60-second videos in under 60 seconds
- 📝 **Simple JSON Scripts**: No complex editing software needed
- 🔄 **Smart Caching**: Avoid re-downloading the same assets
- 🎨 **Customizable**: Control resolution, transitions, and pacing

---

## 🚀 Quick Start

> **💻 Running Locally?** See **[LOCAL_SETUP.md](LOCAL_SETUP.md)** for complete local installation guide!

### One-Command Setup (Local Machine)

```bash
# Clone and run the quick start script
git clone https://github.com/obedjames-del/Video-Editor.git
cd Video-Editor
./quick_start.sh
```

This will:
1. ✅ Check Python 3.12+ and FFmpeg
2. ✅ Install all dependencies
3. ✅ Verify API keys
4. ✅ Get you ready to generate videos!

### Manual Setup

**Prerequisites:**
- Python 3.12 or higher
- FFmpeg 7.x
- API keys (all have free tiers):
  - [Pexels API](https://www.pexels.com/api/) - Free
  - [ElevenLabs](https://elevenlabs.io) - $5/month for Starter
  - [Google Gemini](https://ai.google.dev) - Free tier available

**Installation:**

```bash
# Clone the repository
git clone https://github.com/obedjames-del/Video-Editor.git
cd Video-Editor

# Install uv (recommended - faster)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# API keys are already configured in .env
# Verify configuration
uv run video-editor config
```

### Create Your First Video

1. **Create a script** (or use an example):

```json
{
  "scenes": [
    {
      "text": "Welcome to our product showcase.",
      "video_query": "modern technology"
    },
    {
      "text": "Transform your workflow today.",
      "video_query": "productivity workspace"
    }
  ],
  "config": {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "output_file": "my_video.mp4"
  }
}
```

2. **Generate the video**:

```bash
uv run video-editor generate script.json
```

3. **Find your video** in the `output/` directory!

---

## 📖 Usage

### Basic Commands

```bash
# Generate a video from a script
video-editor generate script.json

# Validate a script without generating
video-editor validate script.json

# Preview what will be generated
video-editor preview script.json

# Clear cache
video-editor cache clear
```

### Advanced Options

```bash
# Custom output file
video-editor generate script.json --output my_video.mp4

# Enable verbose logging
video-editor generate script.json --verbose

# Disable caching
video-editor generate script.json --no-cache

# Use specific voice
video-editor generate script.json --voice-id YOUR_VOICE_ID
```

---

## 📝 Script Format

### Basic Structure

```json
{
  "scenes": [
    {
      "text": "Voiceover text for this scene",
      "video_query": "keywords for video search"
    }
  ],
  "config": {
    "voice_id": "your_elevenlabs_voice_id",
    "output_file": "output.mp4",
    "resolution": "1920x1080",
    "orientation": "landscape"
  }
}
```

### Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `voice_id` | string | required | ElevenLabs voice ID |
| `output_file` | string | `output.mp4` | Output filename |
| `resolution` | string | `1920x1080` | Video resolution |
| `fps` | integer | `30` | Frames per second |
| `orientation` | string | `landscape` | `landscape`, `portrait`, or `square` |
| `transition_duration` | float | `1.0` | Crossfade duration in seconds |
| `use_gemini` | boolean | `false` | Auto-generate video queries with AI |

### Examples

Check the `examples/` directory for complete examples:
- `simple_script.json` - Basic 3-scene product showcase
- `travel_video.json` - 6-scene travel promo
- `tutorial_video.json` - 8-scene tutorial workflow
- `minimal_gemini.json` - AI-powered keyword generation

---

## 🎯 Use Cases

- 📱 **Social Media Content**: Quick Instagram Reels, TikToks, YouTube Shorts
- 🎓 **Educational Videos**: Tutorials, explainers, how-to guides
- 💼 **Marketing**: Product showcases, promotional videos
- 📰 **News & Updates**: Company announcements, newsletter videos
- 🎨 **Creative Projects**: Art showcases, portfolio videos
- 🚀 **Startup Pitches**: Quick demo videos, concept presentations

---

## 🛠️ Architecture

Built with modern Python tools:
- **Python 3.12+** with type hints
- **uv** for fast package management
- **Pydantic** for data validation
- **FFmpeg** for video processing
- **asyncio** for concurrent API calls
- **Rich** for beautiful CLI interface

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete technical documentation.

---

## 💰 Cost

**Monthly costs for regular personal use:**
- Pexels API: **Free** (200 requests/hour)
- ElevenLabs: **$5-10/month** (Starter/Creator plan)
- Gemini API: **<$1/month** (free tier or minimal usage)
- **Total: ~$5-15/month**

Plus local storage for caching (50-100GB recommended).

---

## 🎨 Customization

### Voice Options

Get voice IDs from your [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library):
- Use pre-made voices
- Clone your own voice
- Adjust emotional range and stability

### Video Sources

Currently uses Pexels API (free), but architecture supports:
- Multiple stock video providers
- Local video libraries
- Custom video collections

---

## 📊 Performance

**Target speeds** (1080p, 60-second video):
- Script validation: <1 second
- Voiceover generation: 5-10 seconds
- Video search & download: 10-20 seconds
- Video processing: 10-30 seconds
- **Total: 30-60 seconds** ⚡

---

## 🔧 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**"Invalid API key"**
- Check your `.env` file
- Ensure no extra spaces or quotes
- Verify keys are active in respective dashboards

**"Rate limit exceeded"**
- Wait a few minutes (Pexels: 200 req/hour)
- Enable caching to avoid repeat downloads

**"Out of memory"**
- Reduce video resolution
- Process scenes sequentially
- Clear cache: `video-editor cache clear`

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting: `ruff check && ruff format`
5. Submit a pull request

See [CLAUDE.MD](CLAUDE.MD) for development guidelines.

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Attribution

- Videos from [Pexels](https://www.pexels.com)
- Voiceovers by [ElevenLabs](https://elevenlabs.io)
- AI powered by [Google Gemini](https://ai.google.dev)

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/video-editor/issues)
- 📖 **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/video-editor/discussions)

---

**Made with ❤️ for fast video creation**