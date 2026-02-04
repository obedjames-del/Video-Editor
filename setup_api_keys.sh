#!/bin/bash
# Setup script for API keys

set -e

echo "🔑 Video-Editor API Key Setup"
echo "================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Edit .env manually or delete it first."
        exit 1
    fi
fi

# Copy template
echo "📄 Copying .env.example to .env..."
cp .env.example .env

echo ""
echo "📝 You need to add your API keys to .env"
echo ""
echo "================================"
echo "1️⃣  ElevenLabs API Key"
echo "================================"
echo ""
echo "How to get:"
echo "  1. Sign up at https://elevenlabs.io"
echo "  2. Go to Profile → API Keys"
echo "  3. Generate or copy existing key"
echo "  4. Free tier: 10,000 chars/month"
echo ""
read -p "Paste your ElevenLabs API key: " ELEVENLABS_KEY

echo ""
echo "🎤 Voice ID (optional - press Enter for default):"
echo "  Default: 21m00Tcm4TlvDq8ikWAM (Rachel)"
echo "  Or get from: https://elevenlabs.io/app/voice-library"
echo ""
read -p "Voice ID (or press Enter for default): " VOICE_ID
if [ -z "$VOICE_ID" ]; then
    VOICE_ID="21m00Tcm4TlvDq8ikWAM"
fi

echo ""
echo "================================"
echo "2️⃣  Pexels API Key"
echo "================================"
echo ""
echo "How to get:"
echo "  1. Sign up at https://www.pexels.com/api/"
echo "  2. Click 'Request Access'"
echo "  3. Receive key via email"
echo "  4. Free tier: 200 requests/hour"
echo ""
read -p "Paste your Pexels API key: " PEXELS_KEY

echo ""
echo "================================"
echo "3️⃣  Google Gemini API Key"
echo "================================"
echo ""
echo "How to get:"
echo "  1. Go to https://ai.google.dev/"
echo "  2. Click 'Get API Key'"
echo "  3. Create or use existing key"
echo "  4. Free tier: Generous limits"
echo ""
read -p "Paste your Gemini API key: " GEMINI_KEY

# Update .env file
echo ""
echo "💾 Saving to .env..."

sed -i "s/ELEVENLABS_API_KEY=.*/ELEVENLABS_API_KEY=$ELEVENLABS_KEY/" .env
sed -i "s/PEXELS_API_KEY=.*/PEXELS_API_KEY=$PEXELS_KEY/" .env
sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_KEY/" .env
sed -i "s/DEFAULT_VOICE_ID=.*/DEFAULT_VOICE_ID=$VOICE_ID/" .env

echo ""
echo "✅ API keys saved to .env!"
echo ""
echo "================================"
echo "🧪 Next Steps"
echo "================================"
echo ""
echo "1. Verify configuration:"
echo "   $ uv run video-editor config"
echo ""
echo "2. Run unit tests (fast, no API calls):"
echo "   $ pytest tests/ -m unit"
echo ""
echo "3. Run integration tests (uses real APIs):"
echo "   $ pytest tests/ -m integration -v"
echo ""
echo "4. Generate your first video:"
echo "   $ uv run video-editor generate examples/simple_script.json"
echo ""
echo "📖 For more info, see TESTING.md"
echo ""
echo "🎉 Setup complete!"
