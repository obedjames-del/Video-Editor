"""Configuration management using Pydantic settings."""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys (Required)
    elevenlabs_api_key: str
    pexels_api_key: str
    gemini_api_key: str

    # Default Settings
    default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    default_orientation: Literal["landscape", "portrait", "square"] = "landscape"
    default_transition_duration: float = 1.0

    # Processing Options
    enable_cache: bool = True
    cache_dir: Path = Path("./cache")
    output_dir: Path = Path("./output")
    max_parallel_downloads: int = 5

    # Gemini Settings
    use_gemini_by_default: bool = False
    gemini_model: str = "gemini-2.0-flash"

    # Advanced Settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    ffmpeg_log_level: Literal[
        "quiet", "panic", "fatal", "error", "warning", "info", "verbose", "debug"
    ] = "error"
    temp_dir: Path = Path("./temp")
    max_video_size_mb: int = 100
    api_timeout: int = 30
    api_max_retries: int = 3

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "videos").mkdir(exist_ok=True)
        (self.cache_dir / "audio").mkdir(exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def validate_api_keys(self) -> list[str]:
        """
        Validate that all required API keys are set.

        Returns:
            List of missing API key names (empty if all present)
        """
        missing = []

        if not self.elevenlabs_api_key or self.elevenlabs_api_key == "your_elevenlabs_api_key_here":
            missing.append("ELEVENLABS_API_KEY")

        if not self.pexels_api_key or self.pexels_api_key == "your_pexels_api_key_here":
            missing.append("PEXELS_API_KEY")

        if not self.gemini_api_key or self.gemini_api_key == "your_gemini_api_key_here":
            missing.append("GEMINI_API_KEY")

        return missing


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        Settings instance loaded from environment variables
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (mainly for testing)."""
    global _settings
    _settings = None
