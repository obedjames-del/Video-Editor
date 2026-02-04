"""Pytest fixtures and configuration."""

import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.models.script import VideoScript, SceneConfig, ProjectConfig
from src.utils.config import get_settings, reset_settings


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_script_data() -> dict:
    """Sample valid script data for testing."""
    return {
        "scenes": [
            {
                "text": "Welcome to our amazing product showcase.",
                "video_query": "modern technology"
            },
            {
                "text": "Transform your workflow today.",
                "video_query": "productivity workspace"
            },
            {
                "text": "Get started now and see the difference.",
                "video_query": "success celebration"
            }
        ],
        "config": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "output_file": "test_output.mp4",
            "resolution": "1920x1080",
            "orientation": "landscape"
        }
    }


@pytest.fixture
def sample_script(sample_script_data: dict) -> VideoScript:
    """Sample VideoScript instance for testing."""
    return VideoScript(**sample_script_data)


@pytest.fixture
def sample_script_file(temp_dir: Path, sample_script_data: dict) -> Path:
    """Create a sample script JSON file."""
    import json
    script_file = temp_dir / "test_script.json"
    with open(script_file, "w") as f:
        json.dump(sample_script_data, f, indent=2)
    return script_file


@pytest.fixture
def mock_settings(temp_dir: Path, monkeypatch):
    """Mock settings with test values."""
    # Set test environment variables
    test_env = {
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "PEXELS_API_KEY": "test_pexels_key",
        "GEMINI_API_KEY": "test_gemini_key",
        "CACHE_DIR": str(temp_dir / "cache"),
        "OUTPUT_DIR": str(temp_dir / "output"),
        "TEMP_DIR": str(temp_dir / "temp"),
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    # Reset settings to pick up new env vars
    reset_settings()
    settings = get_settings()
    settings.ensure_directories()

    yield settings

    # Cleanup
    reset_settings()


@pytest.fixture
def has_real_api_keys() -> bool:
    """Check if real API keys are available."""
    return all([
        os.getenv("ELEVENLABS_API_KEY") and os.getenv("ELEVENLABS_API_KEY") != "test_elevenlabs_key",
        os.getenv("PEXELS_API_KEY") and os.getenv("PEXELS_API_KEY") != "test_pexels_key",
        os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "test_gemini_key",
    ])


@pytest.fixture
def skip_without_api_keys(has_real_api_keys: bool):
    """Skip test if real API keys are not available."""
    if not has_real_api_keys:
        pytest.skip("Requires real API keys (set in .env)")


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client."""
    mock = AsyncMock()
    mock.generate.return_value = b"fake_audio_data"
    return mock


@pytest.fixture
def mock_pexels_response():
    """Mock Pexels API response."""
    return {
        "videos": [
            {
                "id": 12345,
                "url": "https://www.pexels.com/video/12345/",
                "duration": 10.5,
                "width": 1920,
                "height": 1080,
                "user": {"name": "Test User"},
                "video_files": [
                    {
                        "id": 1,
                        "quality": "hd",
                        "file_type": "video/mp4",
                        "width": 1920,
                        "height": 1080,
                        "link": "https://example.com/video.mp4"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "queries": [
            "modern technology innovation",
            "productive workspace office",
            "celebration success happy"
        ]
    }


@pytest.fixture
def sample_audio_file(temp_dir: Path) -> Path:
    """Create a sample audio file for testing."""
    # Create a tiny silent MP3 file (just for testing file operations)
    audio_file = temp_dir / "test_audio.mp3"
    # This is a minimal valid MP3 header
    audio_file.write_bytes(b'\xff\xfb\x90\x00' + b'\x00' * 100)
    return audio_file


@pytest.fixture
def sample_video_file(temp_dir: Path) -> Path:
    """Create a sample video file for testing."""
    # Create a minimal video file placeholder
    video_file = temp_dir / "test_video.mp4"
    # This is just a placeholder - real FFmpeg tests would need actual video
    video_file.write_bytes(b'\x00' * 1000)
    return video_file
