#!/bin/bash
# Quick Start Script for Video-Editor
# Run this on your local machine to get started immediately

set -e

echo "🎬 Video-Editor Quick Start"
echo "============================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3.12 &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3.12+ is required but not found."
        echo "   Please install Python 3.12 or higher first."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.12"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo "❌ Python $PYTHON_VERSION found, but 3.12+ is required."
        exit 1
    fi
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3.12"
fi
echo "✅ Python $(${PYTHON_CMD} --version | cut -d' ' -f2) found"

# Check FFmpeg
echo ""
echo "2️⃣  Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Video processing will fail without it."
    echo "   Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ FFmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3) found"
fi

# Check uv or use pip
echo ""
echo "3️⃣  Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "   Using uv (fast mode)..."
    uv sync
else
    echo "   uv not found, using pip..."
    echo "   (Tip: Install uv for faster installs: curl -LsSf https://astral.sh/uv/install.sh | sh)"

    # Create venv if it doesn't exist
    if [ ! -d ".venv" ]; then
        ${PYTHON_CMD} -m venv .venv
    fi

    # Activate venv
    source .venv/bin/activate

    # Install package
    pip install -e .
fi
echo "✅ Dependencies installed"

# Check .env file
echo ""
echo "4️⃣  Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "❌ Please edit .env and add your API keys, then run this script again."
    exit 1
fi

# Verify config
echo "   Verifying API keys..."
if command -v uv &> /dev/null; then
    CONFIG_OUTPUT=$(uv run video-editor config 2>&1)
else
    CONFIG_OUTPUT=$(python -m src.cli config 2>&1)
fi

if echo "$CONFIG_OUTPUT" | grep -q "✓ All API keys configured"; then
    echo "✅ API keys configured correctly"
else
    echo "⚠️  API key configuration may have issues:"
    echo "$CONFIG_OUTPUT"
fi

# Success!
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete! Your Video-Editor is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Try generating your first video:"
echo ""
if command -v uv &> /dev/null; then
    echo "  uv run video-editor generate examples/simple_script.json"
else
    echo "  python -m src.cli generate examples/simple_script.json"
fi
echo ""
echo "Or explore available commands:"
echo ""
if command -v uv &> /dev/null; then
    echo "  uv run video-editor --help"
else
    echo "  python -m src.cli --help"
fi
echo ""
echo "📖 Read LOCAL_SETUP.md for detailed usage instructions"
echo ""
