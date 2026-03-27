#!/bin/bash
# Local Setup Script for GrammarOfGrace Video Editor
# Run this on your Mac to get started

echo "=== GrammarOfGrace Local Setup ==="

# 1. Clone the repo and switch to the branch
if [ ! -d ".git" ]; then
  echo "Cloning repository..."
  git clone https://github.com/obedjames-del/Video-Editor.git
  cd Video-Editor
fi

# 2. Switch to the development branch
git fetch origin claude/powerpoint-quiz-app-plan-hxETu
git checkout claude/powerpoint-quiz-app-plan-hxETu

# 3. Install dependencies
echo "Installing dependencies..."
npm install

# 4. Copy env template
if [ ! -f .env.local ]; then
  cp .env.example .env.local
  echo "Created .env.local — fill in your API keys"
fi

# 5. Reference files location
CHAPTER6_PATH="$HOME/Library/Mobile Documents/com~apple~CloudDocs/chapter 6"
if [ -d "$CHAPTER6_PATH" ]; then
  echo "✓ Found Chapter 6 folder at: $CHAPTER6_PATH"
  echo "Files:"
  ls -la "$CHAPTER6_PATH"
else
  echo "✗ Chapter 6 folder not found at expected iCloud path"
  echo "  Looking in Google Drive..."
  GDRIVE_PATH="$HOME/Library/CloudStorage/GoogleDrive-obedjames@gmail.com/My Drive/chapter 6"
  if [ -d "$GDRIVE_PATH" ]; then
    echo "✓ Found at: $GDRIVE_PATH"
    ls -la "$GDRIVE_PATH"
  fi
fi

echo ""
echo "=== Setup Complete ==="
echo "Next: Run 'claude' and ask it to analyze the Chapter 6 files"
