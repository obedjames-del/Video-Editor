"""Unit tests for configuration management."""

import os
import pytest
from pathlib import Path
from pydantic import ValidationError

from src.utils.config import Settings, get_settings, reset_settings


@pytest.mark.unit
def test_settings_loads_from_env(mock_settings):
    """Test that settings load from environment variables."""
    settings = get_settings()
    assert settings.elevenlabs_api_key == "test_elevenlabs_key"
    assert settings.pexels_api_key == "test_pexels_key"
    assert settings.gemini_api_key == "test_gemini_key"


@pytest.mark.unit
def test_settings_loads_directory_paths_from_env(mock_settings):
    """Test that directory paths load from environment variables."""
    settings = get_settings()
    assert "cache" in str(settings.cache_dir)
    assert "output" in str(settings.output_dir)
    assert "temp" in str(settings.temp_dir)


@pytest.mark.unit
def test_default_values_applied():
    """Test that default values are applied when not set in environment."""
    reset_settings()
    # Create settings with minimal env vars
    test_settings = Settings(
        elevenlabs_api_key="test_key_1",
        pexels_api_key="test_key_2",
        gemini_api_key="test_key_3"
    )

    # Check default values
    assert test_settings.default_voice_id == "21m00Tcm4TlvDq8ikWAM"
    assert test_settings.default_resolution == "1920x1080"
    assert test_settings.default_fps == 30
    assert test_settings.default_orientation == "landscape"
    assert test_settings.default_transition_duration == 1.0
    assert test_settings.enable_cache is True
    assert test_settings.max_parallel_downloads == 5
    assert test_settings.use_gemini_by_default is False
    assert test_settings.gemini_model == "gemini-2.0-flash"
    assert test_settings.log_level == "INFO"
    assert test_settings.ffmpeg_log_level == "error"
    assert test_settings.max_video_size_mb == 100
    assert test_settings.api_timeout == 30
    assert test_settings.api_max_retries == 3


@pytest.mark.unit
def test_settings_with_custom_values(monkeypatch, temp_dir):
    """Test that custom environment values override defaults."""
    reset_settings()

    # Set custom environment variables
    monkeypatch.setenv("ELEVENLABS_API_KEY", "custom_elevenlabs")
    monkeypatch.setenv("PEXELS_API_KEY", "custom_pexels")
    monkeypatch.setenv("GEMINI_API_KEY", "custom_gemini")
    monkeypatch.setenv("DEFAULT_FPS", "60")
    monkeypatch.setenv("DEFAULT_ORIENTATION", "portrait")
    monkeypatch.setenv("MAX_PARALLEL_DOWNLOADS", "10")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-pro")

    settings = Settings()

    assert settings.elevenlabs_api_key == "custom_elevenlabs"
    assert settings.default_fps == 60
    assert settings.default_orientation == "portrait"
    assert settings.max_parallel_downloads == 10
    assert settings.log_level == "DEBUG"
    assert settings.gemini_model == "gemini-1.5-pro"


@pytest.mark.unit
def test_ensure_directories_creates_all_dirs(mock_settings, temp_dir):
    """Test that ensure_directories creates all necessary directories."""
    settings = mock_settings

    # Verify main directories exist
    assert settings.cache_dir.exists()
    assert settings.output_dir.exists()
    assert settings.temp_dir.exists()

    # Verify cache subdirectories exist
    assert (settings.cache_dir / "videos").exists()
    assert (settings.cache_dir / "audio").exists()


@pytest.mark.unit
def test_ensure_directories_idempotent(mock_settings):
    """Test that ensure_directories can be called multiple times safely."""
    settings = mock_settings

    # Call multiple times - should not raise errors
    settings.ensure_directories()
    settings.ensure_directories()
    settings.ensure_directories()

    # Directories should still exist
    assert settings.cache_dir.exists()
    assert settings.output_dir.exists()
    assert settings.temp_dir.exists()


@pytest.mark.unit
def test_validate_api_keys_all_present(mock_settings):
    """Test API key validation when all keys are present."""
    settings = mock_settings
    missing = settings.validate_api_keys()

    assert missing == []
    assert len(missing) == 0


@pytest.mark.unit
def test_validate_api_keys_detects_missing():
    """Test detection of missing API keys."""
    reset_settings()

    # Create settings with placeholder keys
    settings = Settings(
        elevenlabs_api_key="your_elevenlabs_api_key_here",
        pexels_api_key="test_pexels_key",
        gemini_api_key="test_gemini_key"
    )

    missing = settings.validate_api_keys()

    assert "ELEVENLABS_API_KEY" in missing
    assert "PEXELS_API_KEY" not in missing
    assert "GEMINI_API_KEY" not in missing


@pytest.mark.unit
def test_validate_api_keys_detects_all_missing():
    """Test detection when all API keys are missing/placeholder."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="your_elevenlabs_api_key_here",
        pexels_api_key="your_pexels_api_key_here",
        gemini_api_key="your_gemini_api_key_here"
    )

    missing = settings.validate_api_keys()

    assert len(missing) == 3
    assert "ELEVENLABS_API_KEY" in missing
    assert "PEXELS_API_KEY" in missing
    assert "GEMINI_API_KEY" in missing


@pytest.mark.unit
def test_validate_api_keys_detects_empty_strings():
    """Test detection of empty string API keys."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="",
        pexels_api_key="valid_key",
        gemini_api_key=""
    )

    missing = settings.validate_api_keys()

    assert "ELEVENLABS_API_KEY" in missing
    assert "GEMINI_API_KEY" in missing
    assert "PEXELS_API_KEY" not in missing


@pytest.mark.unit
def test_settings_singleton_pattern(mock_settings):
    """Test that get_settings returns the same instance."""
    reset_settings()

    # Get settings multiple times
    settings1 = get_settings()
    settings2 = get_settings()
    settings3 = get_settings()

    # All should be the same instance
    assert settings1 is settings2
    assert settings2 is settings3
    assert settings1 is settings3


@pytest.mark.unit
def test_reset_settings_clears_singleton(monkeypatch):
    """Test that reset_settings clears the singleton instance."""
    reset_settings()

    # Set up environment for both calls
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test_key_1")
    monkeypatch.setenv("PEXELS_API_KEY", "test_key_2")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_3")

    settings1 = get_settings()
    original_id = id(settings1)

    # Reset and get again
    reset_settings()
    settings2 = get_settings()
    new_id = id(settings2)

    # Should be different instances
    assert original_id != new_id


@pytest.mark.unit
def test_settings_calls_ensure_directories_on_first_get(monkeypatch, temp_dir):
    """Test that get_settings automatically calls ensure_directories."""
    reset_settings()

    # Set up clean environment
    cache_dir = temp_dir / "auto_cache"
    output_dir = temp_dir / "auto_output"
    temp_dir_path = temp_dir / "auto_temp"

    monkeypatch.setenv("ELEVENLABS_API_KEY", "test_key_1")
    monkeypatch.setenv("PEXELS_API_KEY", "test_key_2")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_3")
    monkeypatch.setenv("CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("TEMP_DIR", str(temp_dir_path))

    # Directories shouldn't exist yet
    assert not cache_dir.exists()
    assert not output_dir.exists()
    assert not temp_dir_path.exists()

    # Get settings - should auto-create directories
    settings = get_settings()

    # Now directories should exist
    assert settings.cache_dir.exists()
    assert settings.output_dir.exists()
    assert settings.temp_dir.exists()


@pytest.mark.unit
def test_settings_allows_empty_api_keys():
    """Test that Settings allows empty API keys for testing."""
    reset_settings()

    # Settings can be created with empty API keys (for testing)
    settings = Settings()
    assert settings.elevenlabs_api_key == ""
    assert settings.pexels_api_key == ""
    assert settings.gemini_api_key == ""


@pytest.mark.unit
def test_settings_orientation_literal():
    """Test that orientation only accepts valid literal values."""
    reset_settings()

    # Valid orientations should work
    for orientation in ["landscape", "portrait", "square"]:
        settings = Settings(
            elevenlabs_api_key="test1",
            pexels_api_key="test2",
            gemini_api_key="test3",
            default_orientation=orientation
        )
        assert settings.default_orientation == orientation


@pytest.mark.unit
def test_settings_log_level_literal():
    """Test that log_level only accepts valid literal values."""
    reset_settings()

    # Valid log levels should work
    for log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        settings = Settings(
            elevenlabs_api_key="test1",
            pexels_api_key="test2",
            gemini_api_key="test3",
            log_level=log_level
        )
        assert settings.log_level == log_level


@pytest.mark.unit
def test_settings_ffmpeg_log_level_literal():
    """Test that ffmpeg_log_level only accepts valid literal values."""
    reset_settings()

    # Valid FFmpeg log levels should work
    for ffmpeg_level in ["quiet", "panic", "fatal", "error", "warning", "info", "verbose", "debug"]:
        settings = Settings(
            elevenlabs_api_key="test1",
            pexels_api_key="test2",
            gemini_api_key="test3",
            ffmpeg_log_level=ffmpeg_level
        )
        assert settings.ffmpeg_log_level == ffmpeg_level


@pytest.mark.unit
def test_settings_path_types():
    """Test that directory settings are properly converted to Path objects."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="test1",
        pexels_api_key="test2",
        gemini_api_key="test3",
        cache_dir="./test_cache",
        output_dir="./test_output",
        temp_dir="./test_temp"
    )

    assert isinstance(settings.cache_dir, Path)
    assert isinstance(settings.output_dir, Path)
    assert isinstance(settings.temp_dir, Path)


@pytest.mark.unit
def test_settings_case_insensitive_env_vars(monkeypatch):
    """Test that environment variables are case-insensitive."""
    reset_settings()

    # Set environment variables in different cases
    monkeypatch.setenv("elevenlabs_api_key", "test_lower_1")
    monkeypatch.setenv("PEXELS_API_KEY", "test_upper_2")
    monkeypatch.setenv("Gemini_Api_Key", "test_mixed_3")

    settings = Settings()

    # All should be loaded correctly
    assert settings.elevenlabs_api_key == "test_lower_1"
    assert settings.pexels_api_key == "test_upper_2"
    assert settings.gemini_api_key == "test_mixed_3"


@pytest.mark.unit
def test_settings_integer_types():
    """Test that integer settings are properly validated."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="test1",
        pexels_api_key="test2",
        gemini_api_key="test3",
        default_fps=60,
        max_parallel_downloads=10,
        max_video_size_mb=200,
        api_timeout=60,
        api_max_retries=5
    )

    assert isinstance(settings.default_fps, int)
    assert isinstance(settings.max_parallel_downloads, int)
    assert isinstance(settings.max_video_size_mb, int)
    assert isinstance(settings.api_timeout, int)
    assert isinstance(settings.api_max_retries, int)


@pytest.mark.unit
def test_settings_float_types():
    """Test that float settings are properly validated."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="test1",
        pexels_api_key="test2",
        gemini_api_key="test3",
        default_transition_duration=2.5
    )

    assert isinstance(settings.default_transition_duration, float)
    assert settings.default_transition_duration == 2.5


@pytest.mark.unit
def test_settings_boolean_types():
    """Test that boolean settings are properly validated."""
    reset_settings()

    settings = Settings(
        elevenlabs_api_key="test1",
        pexels_api_key="test2",
        gemini_api_key="test3",
        enable_cache=False,
        use_gemini_by_default=True
    )

    assert isinstance(settings.enable_cache, bool)
    assert isinstance(settings.use_gemini_by_default, bool)
    assert settings.enable_cache is False
    assert settings.use_gemini_by_default is True


@pytest.mark.unit
def test_settings_extra_fields_ignored(monkeypatch):
    """Test that extra unknown fields are ignored."""
    reset_settings()

    monkeypatch.setenv("ELEVENLABS_API_KEY", "test1")
    monkeypatch.setenv("PEXELS_API_KEY", "test2")
    monkeypatch.setenv("GEMINI_API_KEY", "test3")
    monkeypatch.setenv("UNKNOWN_FIELD", "should_be_ignored")
    monkeypatch.setenv("RANDOM_CONFIG", "also_ignored")

    # Should not raise an error
    settings = Settings()

    # Should not have extra attributes
    assert not hasattr(settings, "unknown_field")
    assert not hasattr(settings, "random_config")
