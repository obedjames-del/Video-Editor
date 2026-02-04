"""Pydantic models for JSON script validation."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class SceneConfig(BaseModel):
    """Configuration for a single scene in the video."""

    text: str = Field(
        ...,
        description="Voiceover text for this scene",
        min_length=1,
        max_length=5000,
    )
    video_query: Optional[str] = Field(
        None,
        description="Pexels search query for video. If not provided and use_gemini is enabled, "
        "Gemini will generate this automatically.",
        max_length=200,
    )
    duration: Optional[float] = Field(
        None,
        description="Override duration in seconds. If not set, matches voiceover length.",
        gt=0,
        le=300,  # Max 5 minutes per scene
    )

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Validate text is not just whitespace."""
        if not v.strip():
            raise ValueError("Scene text cannot be empty or whitespace")
        return v.strip()

    @field_validator("video_query")
    @classmethod
    def video_query_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate video_query is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("video_query cannot be empty or whitespace if provided")
        return v.strip() if v else None


class ProjectConfig(BaseModel):
    """Global configuration for the video project."""

    voice_id: str = Field(
        ...,
        description="ElevenLabs voice ID. Get from https://elevenlabs.io/app/voice-library",
        min_length=1,
    )
    output_file: str = Field(
        default="output.mp4",
        description="Output filename for the generated video",
        pattern=r"^[\w\-. ]+\.mp4$",
    )
    resolution: str = Field(
        default="1920x1080",
        description="Video resolution in WIDTHxHEIGHT format",
        pattern=r"^\d+x\d+$",
    )
    fps: int = Field(
        default=30,
        description="Frames per second",
        ge=24,
        le=60,
    )
    orientation: Literal["landscape", "portrait", "square"] = Field(
        default="landscape",
        description="Video orientation for Pexels search",
    )
    transition_duration: float = Field(
        default=1.0,
        description="Crossfade transition duration in seconds",
        ge=0,
        le=5.0,
    )
    use_gemini: bool = Field(
        default=False,
        description="Use Gemini to automatically generate video queries from scene text",
    )
    voice_model: str = Field(
        default="eleven_multilingual_v2",
        description="ElevenLabs voice model to use",
    )
    voice_stability: float = Field(
        default=0.5,
        description="ElevenLabs voice stability (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    voice_similarity_boost: float = Field(
        default=0.75,
        description="ElevenLabs voice similarity boost (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        """Validate resolution format and reasonable values."""
        try:
            width, height = v.split("x")
            w, h = int(width), int(height)
            if w < 128 or h < 128:
                raise ValueError("Resolution must be at least 128x128")
            if w > 7680 or h > 4320:  # 8K max
                raise ValueError("Resolution cannot exceed 7680x4320 (8K)")
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid resolution format: {v}") from e

    @field_validator("output_file")
    @classmethod
    def validate_output_file(cls, v: str) -> str:
        """Ensure output file has .mp4 extension."""
        if not v.endswith(".mp4"):
            return f"{v}.mp4"
        return v


class VideoScript(BaseModel):
    """Complete video script with scenes and configuration."""

    scenes: list[SceneConfig] = Field(
        ...,
        description="List of scenes in the video",
        min_length=1,
        max_length=100,  # Max 100 scenes per video
    )
    config: ProjectConfig = Field(
        ...,
        description="Global project configuration",
    )

    @field_validator("scenes")
    @classmethod
    def validate_scenes(cls, v: list[SceneConfig]) -> list[SceneConfig]:
        """Validate scenes list is not empty."""
        if not v:
            raise ValueError("Video must have at least one scene")
        return v

    def get_total_estimated_duration(self) -> float:
        """
        Estimate total video duration based on scene text length.
        Rough estimate: ~150 words per minute for voiceover.
        """
        total_chars = sum(len(scene.text) for scene in self.scenes)
        # Rough estimate: 5 chars per word, 150 words per minute
        estimated_words = total_chars / 5
        estimated_minutes = estimated_words / 150
        return estimated_minutes * 60  # Convert to seconds

    def requires_gemini(self) -> bool:
        """Check if any scenes require Gemini for video query generation."""
        return self.config.use_gemini or any(
            scene.video_query is None for scene in self.scenes
        )


# Example usage for documentation
if __name__ == "__main__":
    # Example valid script
    example_script = {
        "scenes": [
            {
                "text": "Welcome to our amazing product showcase.",
                "video_query": "modern technology",
            },
            {
                "text": "Transform your workflow today.",
                "video_query": "productivity workspace",
            },
        ],
        "config": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "output_file": "my_video.mp4",
        },
    }

    # Validate and parse
    script = VideoScript(**example_script)
    print(f"✅ Valid script with {len(script.scenes)} scenes")
    print(f"📊 Estimated duration: {script.get_total_estimated_duration():.1f} seconds")
    print(f"🤖 Requires Gemini: {script.requires_gemini()}")
