# Testing Guide

This document explains how to test the Video-Editor with both mock data (unit tests) and real API keys (integration tests).

## Quick Start

### Run Unit Tests (No API Keys Needed)
```bash
# Run all unit tests (fast, no external dependencies)
pytest tests/ -m unit

# Expected: 190 tests pass in ~1 second
```

### Run Integration Tests (Requires Real API Keys)
```bash
# Set up API keys first (see below)
cp .env.example .env
nano .env  # Add your real API keys

# Run integration tests
pytest tests/ -m integration -v

# Run all tests (unit + integration)
pytest tests/
```

---

## Setting Up API Keys

### 1. **ElevenLabs API Key**

**Get Your Key:**
1. Sign up at https://elevenlabs.io
2. Go to your profile → API Keys
3. Click "Generate new API key" or copy existing key
4. Free tier: 10,000 characters/month

**Add to `.env`:**
```bash
ELEVENLABS_API_KEY=sk_abc123...your_key_here
```

**Get Voice ID:**
1. Go to https://elevenlabs.io/app/voice-library
2. Click on any voice (e.g., "Rachel")
3. Copy the Voice ID (looks like `21m00Tcm4TlvDq8ikWAM`)
4. Add to `.env`:
```bash
DEFAULT_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

---

### 2. **Pexels API Key**

**Get Your Key:**
1. Sign up at https://www.pexels.com/api/
2. Click "Request Access"
3. Fill out the form (personal project is fine)
4. Receive API key via email
5. Free tier: 200 requests/hour

**Add to `.env`:**
```bash
PEXELS_API_KEY=your_pexels_api_key_here
```

---

### 3. **Google Gemini API Key**

**Get Your Key:**
1. Go to https://ai.google.dev/
2. Click "Get API Key" → "Get API key in Google AI Studio"
3. Create new API key or use existing one
4. Free tier: Generous limits for Gemini 2.0 Flash

**Add to `.env`:**
```bash
GEMINI_API_KEY=AIzaSy...your_key_here
```

---

## Verifying Your Setup

### Check Configuration
```bash
# Verify your API keys are loaded
uv run video-editor config

# Should show:
# ✓ All API keys configured
# Default Voice: 21m00Tcm4TlvDq8ikWAM
# Default Resolution: 1920x1080
# ...
```

### Test Individual Services

**Test ElevenLabs:**
```bash
# This will use ~50 characters from your quota
pytest tests/test_integration_voiceover.py -v
```

**Test Pexels:**
```bash
# This will use 1-2 API requests
pytest tests/test_integration_video_search.py -v
```

**Test Gemini:**
```bash
# This will use minimal tokens
pytest tests/test_integration_gemini.py -v
```

---

## Test Organization

### Test Files

| File | Tests | Type | Requires |
|------|-------|------|----------|
| `test_models.py` | 106 | Unit | Nothing |
| `test_config.py` | 23 | Unit | Nothing |
| `test_cache.py` | 61 | Unit | Nothing |
| `test_script_parser.py` | TBD | Unit | Nothing |
| `test_integration_voiceover.py` | TBD | Integration | ElevenLabs key |
| `test_integration_video_search.py` | TBD | Integration | Pexels key |
| `test_integration_gemini.py` | TBD | Integration | Gemini key |
| `test_integration_e2e.py` | TBD | Integration | All keys + FFmpeg |

### Test Markers

Use pytest markers to run specific test types:

```bash
# Only unit tests (no API keys needed)
pytest tests/ -m unit

# Only integration tests (requires API keys)
pytest tests/ -m integration

# Only tests that don't require APIs
pytest tests/ -m "not requires_api"

# Only fast tests
pytest tests/ -m "not slow"

# Skip tests that need FFmpeg
pytest tests/ -m "not requires_ffmpeg"
```

---

## API Usage & Costs

### Unit Tests (Free)
- **API Calls:** 0
- **Cost:** $0
- **Speed:** ~1 second for all 190 tests

### Integration Tests (Minimal Cost)

**ElevenLabs:**
- Characters used: ~200-500 per test run
- Free tier: 10,000 chars/month
- Cost: Free (within limits)

**Pexels:**
- Requests: ~5-10 per test run
- Free tier: 200 requests/hour
- Cost: Free

**Gemini:**
- Tokens: ~1,000-2,000 per test run
- Free tier: Very generous
- Cost: Free (or <$0.01)

**Total Integration Test Cost:** Free to <$0.01 per run

---

## Troubleshooting

### "ValidationError: Field required"
**Problem:** API keys not loaded from .env

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check contents (don't commit!)
cat .env | grep API_KEY

# Ensure no trailing spaces or quotes
# Correct:   PEXELS_API_KEY=abc123
# Incorrect: PEXELS_API_KEY="abc123"
# Incorrect: PEXELS_API_KEY=abc123
```

### "401 Unauthorized" or "403 Forbidden"
**Problem:** Invalid API key

**Solution:**
1. Verify key is correct (copy-paste from dashboard)
2. Check key is active (not expired/revoked)
3. Ensure no extra characters (spaces, newlines)

### "429 Too Many Requests"
**Problem:** Rate limit exceeded

**Solution:**
```bash
# Wait a few minutes for rate limit to reset
# Pexels: 200 requests/hour
# ElevenLabs: Based on your plan

# Or run fewer tests
pytest tests/test_integration_pexels.py::test_single_video_search -v
```

### Tests Hang or Timeout
**Problem:** Network issues or API down

**Solution:**
```bash
# Check internet connection
ping google.com

# Check API status pages
# ElevenLabs: status.elevenlabs.io
# Pexels: Check website
# Gemini: Check Google Cloud Status

# Increase timeout
pytest tests/ --timeout=60
```

---

## Best Practices

### 1. **Run Unit Tests First**
Always run unit tests before integration tests:
```bash
pytest tests/ -m unit  # Should always pass
pytest tests/ -m integration  # Then test with APIs
```

### 2. **Use Cache to Save API Calls**
The system caches API responses automatically:
```bash
# First run: Uses API calls
pytest tests/test_integration_voiceover.py

# Second run: Uses cache (free!)
pytest tests/test_integration_voiceover.py
```

### 3. **Clear Cache Between Runs** (if needed)
```bash
# Clear test cache
rm -rf cache/

# Or use the CLI
uv run video-editor cache clear
```

### 4. **Monitor API Usage**
```bash
# Check ElevenLabs dashboard for character usage
# Check Pexels API usage (if available in your account)
# Gemini usage visible in Google AI Studio
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install pytest pytest-asyncio
      - run: pip install -e .
      - run: pytest tests/ -m unit

  integration-tests:
    runs-on: ubuntu-latest
    # Only run on main branch to save API quota
    if: github.ref == 'refs/heads/main'
    env:
      ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
      PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install pytest pytest-asyncio
      - run: pip install -e .
      - run: pytest tests/ -m integration
```

---

## Coverage Reports

### Generate HTML Coverage Report
```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: All API integrations tested
- E2E test: Complete video generation pipeline

---

## Quick Reference

```bash
# Setup
cp .env.example .env && nano .env

# All tests
pytest tests/

# Unit only (fast)
pytest tests/ -m unit

# Integration only (requires keys)
pytest tests/ -m integration

# Specific file
pytest tests/test_models.py -v

# With coverage
pytest tests/ --cov=src

# Verbose output
pytest tests/ -v --tb=short

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf
```

---

**Ready to test!** Start with unit tests, then add your API keys and run integration tests.
