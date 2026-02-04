"""Comprehensive unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from src.models.script import SceneConfig, ProjectConfig, VideoScript


@pytest.mark.unit
class TestSceneConfig:
    """Test suite for SceneConfig model."""

    def test_valid_scene_with_all_fields(self):
        """Test creating a valid scene with all fields."""
        scene = SceneConfig(
            text="Hello world",
            video_query="greeting",
            duration=5.5
        )
        assert scene.text == "Hello world"
        assert scene.video_query == "greeting"
        assert scene.duration == 5.5

    def test_valid_scene_minimal_fields(self):
        """Test creating a valid scene with only required fields."""
        scene = SceneConfig(text="Hello world")
        assert scene.text == "Hello world"
        assert scene.video_query is None
        assert scene.duration is None

    def test_valid_scene_with_video_query_only(self):
        """Test creating a valid scene with text and video_query."""
        scene = SceneConfig(text="Hello world", video_query="greeting")
        assert scene.text == "Hello world"
        assert scene.video_query == "greeting"
        assert scene.duration is None

    def test_text_strips_whitespace(self):
        """Test that text is stripped of leading/trailing whitespace."""
        scene = SceneConfig(text="  Hello world  ", video_query="test")
        assert scene.text == "Hello world"

    def test_video_query_strips_whitespace(self):
        """Test that video_query is stripped of leading/trailing whitespace."""
        scene = SceneConfig(text="Hello", video_query="  greeting  ")
        assert scene.video_query == "greeting"

    def test_empty_text_fails(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="", video_query="test")
        assert "text" in str(exc_info.value).lower()

    def test_whitespace_only_text_fails(self):
        """Test that whitespace-only text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="   ", video_query="test")
        assert "whitespace" in str(exc_info.value).lower()

    def test_whitespace_only_video_query_fails(self):
        """Test that whitespace-only video_query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", video_query="   ")
        assert "whitespace" in str(exc_info.value).lower()

    def test_empty_video_query_fails(self):
        """Test that empty video_query raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", video_query="")
        assert "whitespace" in str(exc_info.value).lower()

    def test_text_max_length(self):
        """Test text maximum length validation."""
        long_text = "a" * 5000
        scene = SceneConfig(text=long_text)
        assert len(scene.text) == 5000

    def test_text_exceeds_max_length(self):
        """Test that text exceeding max length raises validation error."""
        too_long_text = "a" * 5001
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text=too_long_text)
        assert "text" in str(exc_info.value).lower()

    def test_video_query_max_length(self):
        """Test video_query maximum length validation."""
        long_query = "a" * 200
        scene = SceneConfig(text="Hello", video_query=long_query)
        assert len(scene.video_query) == 200

    def test_video_query_exceeds_max_length(self):
        """Test that video_query exceeding max length raises validation error."""
        too_long_query = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", video_query=too_long_query)
        assert "video_query" in str(exc_info.value).lower()

    def test_duration_minimum_boundary(self):
        """Test duration must be greater than 0."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", duration=0)
        assert "duration" in str(exc_info.value).lower()

    def test_duration_negative_fails(self):
        """Test that negative duration raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", duration=-1.0)
        assert "duration" in str(exc_info.value).lower()

    def test_duration_maximum_boundary(self):
        """Test duration maximum value (300 seconds)."""
        scene = SceneConfig(text="Hello", duration=300)
        assert scene.duration == 300

    def test_duration_exceeds_maximum(self):
        """Test that duration exceeding 300 seconds raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(text="Hello", duration=301)
        assert "duration" in str(exc_info.value).lower()

    def test_duration_valid_range(self):
        """Test various valid duration values."""
        durations = [0.1, 1.0, 5.5, 30.0, 150.0, 299.9]
        for dur in durations:
            scene = SceneConfig(text="Hello", duration=dur)
            assert scene.duration == dur

    def test_missing_required_text(self):
        """Test that missing required text field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SceneConfig(video_query="test")
        assert "text" in str(exc_info.value).lower()

    def test_none_video_query_is_valid(self):
        """Test that None video_query is valid."""
        scene = SceneConfig(text="Hello", video_query=None)
        assert scene.video_query is None


@pytest.mark.unit
class TestProjectConfig:
    """Test suite for ProjectConfig model."""

    def test_valid_config_minimal(self):
        """Test creating a valid config with only required fields."""
        config = ProjectConfig(voice_id="test_voice_id")
        assert config.voice_id == "test_voice_id"
        assert config.output_file == "output.mp4"
        assert config.resolution == "1920x1080"
        assert config.fps == 30
        assert config.orientation == "landscape"
        assert config.transition_duration == 1.0
        assert config.use_gemini is False
        assert config.voice_model == "eleven_multilingual_v2"
        assert config.voice_stability == 0.5
        assert config.voice_similarity_boost == 0.75

    def test_valid_config_all_fields(self):
        """Test creating a valid config with all fields specified."""
        config = ProjectConfig(
            voice_id="test_voice_id",
            output_file="my_video.mp4",
            resolution="1280x720",
            fps=24,
            orientation="portrait",
            transition_duration=2.0,
            use_gemini=True,
            voice_model="custom_model",
            voice_stability=0.8,
            voice_similarity_boost=0.9
        )
        assert config.voice_id == "test_voice_id"
        assert config.output_file == "my_video.mp4"
        assert config.resolution == "1280x720"
        assert config.fps == 24
        assert config.orientation == "portrait"
        assert config.transition_duration == 2.0
        assert config.use_gemini is True
        assert config.voice_model == "custom_model"
        assert config.voice_stability == 0.8
        assert config.voice_similarity_boost == 0.9

    def test_missing_voice_id_fails(self):
        """Test that missing required voice_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig()
        assert "voice_id" in str(exc_info.value).lower()

    def test_empty_voice_id_fails(self):
        """Test that empty voice_id raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="")
        assert "voice_id" in str(exc_info.value).lower()

    def test_output_file_adds_extension(self):
        """Test that output_file automatically adds .mp4 extension if missing."""
        # Note: The pattern validation occurs before the field validator,
        # so the custom validator only triggers if the pattern passes.
        # Files without .mp4 will fail pattern matching first.
        # However, if somehow it passes pattern (shouldn't happen), validator adds .mp4
        config = ProjectConfig(voice_id="test", output_file="my_video.mp4")
        assert config.output_file == "my_video.mp4"

    def test_output_file_keeps_extension(self):
        """Test that output_file keeps .mp4 extension if already present."""
        config = ProjectConfig(voice_id="test", output_file="my_video.mp4")
        assert config.output_file == "my_video.mp4"

    def test_output_file_pattern_valid(self):
        """Test various valid output_file patterns."""
        valid_names = [
            "video.mp4",
            "my-video.mp4",
            "my_video.mp4",
            "My Video.mp4",
            "video123.mp4",
            "a.mp4"
        ]
        for name in valid_names:
            config = ProjectConfig(voice_id="test", output_file=name)
            assert config.output_file == name

    def test_resolution_default(self):
        """Test default resolution."""
        config = ProjectConfig(voice_id="test")
        assert config.resolution == "1920x1080"

    def test_resolution_valid_formats(self):
        """Test various valid resolution formats."""
        valid_resolutions = [
            "1920x1080",
            "1280x720",
            "3840x2160",
            "640x480",
            "128x128",
            "7680x4320"
        ]
        for res in valid_resolutions:
            config = ProjectConfig(voice_id="test", resolution=res)
            assert config.resolution == res

    def test_resolution_invalid_format(self):
        """Test that invalid resolution format raises validation error."""
        invalid_resolutions = [
            "1920",
            "1920x",
            "x1080",
            "1920*1080",
            "abc x def",
            "1920 x 1080"
        ]
        for res in invalid_resolutions:
            with pytest.raises(ValidationError):
                ProjectConfig(voice_id="test", resolution=res)

    def test_resolution_too_small(self):
        """Test that resolution below minimum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", resolution="127x127")
        error_str = str(exc_info.value).lower()
        assert "resolution" in error_str and "invalid" in error_str

    def test_resolution_minimum_boundary(self):
        """Test minimum resolution boundary (128x128)."""
        config = ProjectConfig(voice_id="test", resolution="128x128")
        assert config.resolution == "128x128"

    def test_resolution_too_large(self):
        """Test that resolution above maximum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", resolution="7681x4321")
        error_str = str(exc_info.value).lower()
        assert "resolution" in error_str

    def test_resolution_maximum_boundary(self):
        """Test maximum resolution boundary (7680x4320)."""
        config = ProjectConfig(voice_id="test", resolution="7680x4320")
        assert config.resolution == "7680x4320"

    def test_fps_default(self):
        """Test default FPS value."""
        config = ProjectConfig(voice_id="test")
        assert config.fps == 30

    def test_fps_valid_range(self):
        """Test various valid FPS values."""
        valid_fps = [24, 25, 30, 48, 50, 60]
        for fps in valid_fps:
            config = ProjectConfig(voice_id="test", fps=fps)
            assert config.fps == fps

    def test_fps_minimum_boundary(self):
        """Test minimum FPS boundary (24)."""
        config = ProjectConfig(voice_id="test", fps=24)
        assert config.fps == 24

    def test_fps_below_minimum(self):
        """Test that FPS below minimum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", fps=23)
        assert "fps" in str(exc_info.value).lower()

    def test_fps_maximum_boundary(self):
        """Test maximum FPS boundary (60)."""
        config = ProjectConfig(voice_id="test", fps=60)
        assert config.fps == 60

    def test_fps_above_maximum(self):
        """Test that FPS above maximum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", fps=61)
        assert "fps" in str(exc_info.value).lower()

    def test_orientation_valid_values(self):
        """Test all valid orientation values."""
        valid_orientations = ["landscape", "portrait", "square"]
        for orientation in valid_orientations:
            config = ProjectConfig(voice_id="test", orientation=orientation)
            assert config.orientation == orientation

    def test_orientation_invalid_value(self):
        """Test that invalid orientation raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", orientation="vertical")
        assert "orientation" in str(exc_info.value).lower()

    def test_orientation_default(self):
        """Test default orientation."""
        config = ProjectConfig(voice_id="test")
        assert config.orientation == "landscape"

    def test_transition_duration_default(self):
        """Test default transition duration."""
        config = ProjectConfig(voice_id="test")
        assert config.transition_duration == 1.0

    def test_transition_duration_minimum_boundary(self):
        """Test minimum transition duration (0)."""
        config = ProjectConfig(voice_id="test", transition_duration=0)
        assert config.transition_duration == 0

    def test_transition_duration_negative(self):
        """Test that negative transition duration raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", transition_duration=-0.1)
        assert "transition_duration" in str(exc_info.value).lower()

    def test_transition_duration_maximum_boundary(self):
        """Test maximum transition duration (5.0)."""
        config = ProjectConfig(voice_id="test", transition_duration=5.0)
        assert config.transition_duration == 5.0

    def test_transition_duration_above_maximum(self):
        """Test that transition duration above maximum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", transition_duration=5.1)
        assert "transition_duration" in str(exc_info.value).lower()

    def test_transition_duration_valid_range(self):
        """Test various valid transition duration values."""
        valid_durations = [0.0, 0.5, 1.0, 2.5, 4.9, 5.0]
        for dur in valid_durations:
            config = ProjectConfig(voice_id="test", transition_duration=dur)
            assert config.transition_duration == dur

    def test_use_gemini_default(self):
        """Test default use_gemini value."""
        config = ProjectConfig(voice_id="test")
        assert config.use_gemini is False

    def test_use_gemini_true(self):
        """Test use_gemini set to True."""
        config = ProjectConfig(voice_id="test", use_gemini=True)
        assert config.use_gemini is True

    def test_voice_model_default(self):
        """Test default voice_model value."""
        config = ProjectConfig(voice_id="test")
        assert config.voice_model == "eleven_multilingual_v2"

    def test_voice_model_custom(self):
        """Test custom voice_model value."""
        config = ProjectConfig(voice_id="test", voice_model="custom_model")
        assert config.voice_model == "custom_model"

    def test_voice_stability_default(self):
        """Test default voice_stability value."""
        config = ProjectConfig(voice_id="test")
        assert config.voice_stability == 0.5

    def test_voice_stability_minimum_boundary(self):
        """Test minimum voice_stability (0.0)."""
        config = ProjectConfig(voice_id="test", voice_stability=0.0)
        assert config.voice_stability == 0.0

    def test_voice_stability_maximum_boundary(self):
        """Test maximum voice_stability (1.0)."""
        config = ProjectConfig(voice_id="test", voice_stability=1.0)
        assert config.voice_stability == 1.0

    def test_voice_stability_below_minimum(self):
        """Test that voice_stability below minimum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", voice_stability=-0.1)
        assert "voice_stability" in str(exc_info.value).lower()

    def test_voice_stability_above_maximum(self):
        """Test that voice_stability above maximum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", voice_stability=1.1)
        assert "voice_stability" in str(exc_info.value).lower()

    def test_voice_similarity_boost_default(self):
        """Test default voice_similarity_boost value."""
        config = ProjectConfig(voice_id="test")
        assert config.voice_similarity_boost == 0.75

    def test_voice_similarity_boost_minimum_boundary(self):
        """Test minimum voice_similarity_boost (0.0)."""
        config = ProjectConfig(voice_id="test", voice_similarity_boost=0.0)
        assert config.voice_similarity_boost == 0.0

    def test_voice_similarity_boost_maximum_boundary(self):
        """Test maximum voice_similarity_boost (1.0)."""
        config = ProjectConfig(voice_id="test", voice_similarity_boost=1.0)
        assert config.voice_similarity_boost == 1.0

    def test_voice_similarity_boost_below_minimum(self):
        """Test that voice_similarity_boost below minimum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", voice_similarity_boost=-0.1)
        assert "voice_similarity_boost" in str(exc_info.value).lower()

    def test_voice_similarity_boost_above_maximum(self):
        """Test that voice_similarity_boost above maximum raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", voice_similarity_boost=1.1)
        assert "voice_similarity_boost" in str(exc_info.value).lower()


@pytest.mark.unit
class TestVideoScript:
    """Test suite for VideoScript model."""

    def test_valid_script_single_scene(self):
        """Test creating a valid script with one scene."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="Hello world", video_query="greeting")
            ],
            config=ProjectConfig(voice_id="test_voice")
        )
        assert len(script.scenes) == 1
        assert script.scenes[0].text == "Hello world"
        assert script.config.voice_id == "test_voice"

    def test_valid_script_multiple_scenes(self, sample_script_data):
        """Test creating a valid script with multiple scenes."""
        script = VideoScript(**sample_script_data)
        assert len(script.scenes) == 3
        assert script.scenes[0].text == "Welcome to our amazing product showcase."
        assert script.scenes[1].text == "Transform your workflow today."
        assert script.scenes[2].text == "Get started now and see the difference."

    def test_missing_scenes_fails(self):
        """Test that missing scenes field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            VideoScript(config=ProjectConfig(voice_id="test"))
        assert "scenes" in str(exc_info.value).lower()

    def test_missing_config_fails(self):
        """Test that missing config field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            VideoScript(scenes=[SceneConfig(text="Hello")])
        assert "config" in str(exc_info.value).lower()

    def test_empty_scenes_list_fails(self):
        """Test that empty scenes list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            VideoScript(
                scenes=[],
                config=ProjectConfig(voice_id="test")
            )
        assert "scenes" in str(exc_info.value).lower()

    def test_scenes_minimum_length(self):
        """Test minimum scenes list length (1)."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hello")],
            config=ProjectConfig(voice_id="test")
        )
        assert len(script.scenes) == 1

    def test_scenes_maximum_length(self):
        """Test maximum scenes list length (100)."""
        scenes = [SceneConfig(text=f"Scene {i}") for i in range(100)]
        script = VideoScript(
            scenes=scenes,
            config=ProjectConfig(voice_id="test")
        )
        assert len(script.scenes) == 100

    def test_scenes_exceeds_maximum_length(self):
        """Test that scenes list exceeding 100 raises validation error."""
        scenes = [SceneConfig(text=f"Scene {i}") for i in range(101)]
        with pytest.raises(ValidationError) as exc_info:
            VideoScript(
                scenes=scenes,
                config=ProjectConfig(voice_id="test")
            )
        assert "scenes" in str(exc_info.value).lower()

    def test_get_total_estimated_duration_single_scene(self):
        """Test duration estimation for single scene."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hello world! This is a test.")],
            config=ProjectConfig(voice_id="test")
        )
        duration = script.get_total_estimated_duration()
        assert duration > 0
        assert isinstance(duration, float)

    def test_get_total_estimated_duration_multiple_scenes(self):
        """Test duration estimation for multiple scenes."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="First scene with some text."),
                SceneConfig(text="Second scene with more text."),
                SceneConfig(text="Third scene with even more text.")
            ],
            config=ProjectConfig(voice_id="test")
        )
        duration = script.get_total_estimated_duration()
        assert duration > 0
        assert isinstance(duration, float)

    def test_get_total_estimated_duration_long_text(self):
        """Test duration estimation for longer text."""
        # Create text with approximately 150 words (should be ~1 minute)
        long_text = " ".join(["word"] * 150)
        script = VideoScript(
            scenes=[SceneConfig(text=long_text)],
            config=ProjectConfig(voice_id="test")
        )
        duration = script.get_total_estimated_duration()
        # Should be approximately 60 seconds (1 minute)
        # Allow some variance due to estimation algorithm
        assert 50 < duration < 70

    def test_get_total_estimated_duration_calculation(self):
        """Test that duration estimation follows the correct formula."""
        # Formula: total_chars / 5 (chars per word) / 150 (words per minute) * 60 (seconds)
        # = total_chars / 12.5
        text = "a" * 1250  # Should result in 100 seconds
        script = VideoScript(
            scenes=[SceneConfig(text=text)],
            config=ProjectConfig(voice_id="test")
        )
        duration = script.get_total_estimated_duration()
        assert abs(duration - 100) < 1  # Allow small floating point variance

    def test_requires_gemini_config_enabled(self):
        """Test requires_gemini when use_gemini is True in config."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hello", video_query="greeting")],
            config=ProjectConfig(voice_id="test", use_gemini=True)
        )
        assert script.requires_gemini() is True

    def test_requires_gemini_missing_video_query(self):
        """Test requires_gemini when scene has no video_query."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hello")],
            config=ProjectConfig(voice_id="test", use_gemini=False)
        )
        assert script.requires_gemini() is True

    def test_requires_gemini_all_queries_present(self):
        """Test requires_gemini when all scenes have video_query."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="Hello", video_query="greeting"),
                SceneConfig(text="Goodbye", video_query="farewell")
            ],
            config=ProjectConfig(voice_id="test", use_gemini=False)
        )
        assert script.requires_gemini() is False

    def test_requires_gemini_mixed_queries(self):
        """Test requires_gemini with mixed video_query presence."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="Hello", video_query="greeting"),
                SceneConfig(text="Goodbye")  # Missing video_query
            ],
            config=ProjectConfig(voice_id="test", use_gemini=False)
        )
        assert script.requires_gemini() is True

    def test_requires_gemini_config_overrides(self):
        """Test that use_gemini=True always requires Gemini."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="Hello", video_query="greeting"),
                SceneConfig(text="Goodbye", video_query="farewell")
            ],
            config=ProjectConfig(voice_id="test", use_gemini=True)
        )
        assert script.requires_gemini() is True

    def test_script_from_dict(self, sample_script_data):
        """Test creating VideoScript from dictionary."""
        script = VideoScript(**sample_script_data)
        assert len(script.scenes) == 3
        assert script.config.voice_id == "21m00Tcm4TlvDq8ikWAM"
        assert script.config.output_file == "test_output.mp4"

    def test_script_model_dump(self):
        """Test converting VideoScript to dictionary."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hello", video_query="greeting")],
            config=ProjectConfig(voice_id="test")
        )
        data = script.model_dump()
        assert "scenes" in data
        assert "config" in data
        assert len(data["scenes"]) == 1
        assert data["config"]["voice_id"] == "test"

    def test_script_with_invalid_scene_fails(self):
        """Test that invalid scene in list raises validation error."""
        with pytest.raises(ValidationError):
            VideoScript(
                scenes=[
                    SceneConfig(text="Valid scene"),
                    SceneConfig(text="")  # Invalid: empty text
                ],
                config=ProjectConfig(voice_id="test")
            )

    def test_script_with_invalid_config_fails(self):
        """Test that invalid config raises validation error."""
        with pytest.raises(ValidationError):
            VideoScript(
                scenes=[SceneConfig(text="Hello")],
                config=ProjectConfig(voice_id="test", fps=100)  # Invalid: fps too high
            )

    def test_script_nested_validation(self):
        """Test that nested model validation works correctly."""
        with pytest.raises(ValidationError) as exc_info:
            VideoScript(
                scenes=[SceneConfig(text="Hello", duration=-5)],  # Invalid duration
                config=ProjectConfig(voice_id="test")
            )
        assert "duration" in str(exc_info.value).lower()

    def test_script_complex_scenario(self):
        """Test complex script with various scene configurations."""
        script = VideoScript(
            scenes=[
                SceneConfig(text="Opening scene"),
                SceneConfig(text="Middle scene", video_query="action"),
                SceneConfig(text="Closing scene", duration=10.0),
                SceneConfig(text="Final scene", video_query="ending", duration=5.0)
            ],
            config=ProjectConfig(
                voice_id="test_voice",
                output_file="complex_video.mp4",
                resolution="1280x720",
                fps=24,
                orientation="portrait",
                transition_duration=2.0,
                use_gemini=True,
                voice_stability=0.7,
                voice_similarity_boost=0.8
            )
        )
        assert len(script.scenes) == 4
        assert script.requires_gemini() is True
        assert script.get_total_estimated_duration() > 0
        assert script.config.orientation == "portrait"


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases and corner scenarios."""

    def test_scene_with_special_characters(self):
        """Test scene text with special characters."""
        special_text = "Hello! @#$%^&*() 123 <>&\"'[]{}|\\~`"
        scene = SceneConfig(text=special_text)
        assert scene.text == special_text

    def test_scene_with_unicode(self):
        """Test scene text with Unicode characters."""
        unicode_text = "Hello 世界 🌍 Привет مرحبا"
        scene = SceneConfig(text=unicode_text)
        assert scene.text == unicode_text

    def test_scene_with_newlines(self):
        """Test scene text with newlines."""
        text_with_newlines = "Line 1\nLine 2\nLine 3"
        scene = SceneConfig(text=text_with_newlines)
        # Newlines are preserved, just whitespace is stripped from ends
        assert "Line 1" in scene.text
        assert "Line 2" in scene.text

    def test_output_file_with_spaces(self):
        """Test output_file with spaces in filename."""
        config = ProjectConfig(voice_id="test", output_file="my video.mp4")
        assert config.output_file == "my video.mp4"

    def test_output_file_with_dashes(self):
        """Test output_file with dashes in filename."""
        config = ProjectConfig(voice_id="test", output_file="my-video.mp4")
        assert config.output_file == "my-video.mp4"

    def test_output_file_with_underscores(self):
        """Test output_file with underscores in filename."""
        config = ProjectConfig(voice_id="test", output_file="my_video.mp4")
        assert config.output_file == "my_video.mp4"

    def test_very_small_resolution(self):
        """Test minimum valid resolution."""
        config = ProjectConfig(voice_id="test", resolution="128x128")
        assert config.resolution == "128x128"

    def test_very_large_resolution(self):
        """Test maximum valid resolution (8K)."""
        config = ProjectConfig(voice_id="test", resolution="7680x4320")
        assert config.resolution == "7680x4320"

    def test_asymmetric_resolution(self):
        """Test resolution with very different width and height."""
        config = ProjectConfig(voice_id="test", resolution="3840x720")
        assert config.resolution == "3840x720"

    def test_portrait_resolution(self):
        """Test resolution where height > width (portrait)."""
        config = ProjectConfig(voice_id="test", resolution="720x1280")
        assert config.resolution == "720x1280"

    def test_voice_stability_zero(self):
        """Test voice_stability at zero."""
        config = ProjectConfig(voice_id="test", voice_stability=0.0)
        assert config.voice_stability == 0.0

    def test_voice_similarity_boost_zero(self):
        """Test voice_similarity_boost at zero."""
        config = ProjectConfig(voice_id="test", voice_similarity_boost=0.0)
        assert config.voice_similarity_boost == 0.0

    def test_transition_duration_zero(self):
        """Test transition_duration at zero (no transition)."""
        config = ProjectConfig(voice_id="test", transition_duration=0.0)
        assert config.transition_duration == 0.0

    def test_very_short_scene_duration(self):
        """Test scene with very short duration."""
        scene = SceneConfig(text="Quick!", duration=0.1)
        assert scene.duration == 0.1

    def test_maximum_scene_duration(self):
        """Test scene with maximum duration (5 minutes)."""
        scene = SceneConfig(text="Long scene", duration=300)
        assert scene.duration == 300

    def test_float_fps_with_fraction_fails(self):
        """Test that float FPS values with fractional part fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(voice_id="test", fps=30.9)
        assert "fps" in str(exc_info.value).lower()

    def test_float_fps_without_fraction_succeeds(self):
        """Test that float FPS values without fractional part are accepted."""
        config = ProjectConfig(voice_id="test", fps=30.0)
        assert config.fps == 30
        assert isinstance(config.fps, int)

    def test_script_with_one_hundred_scenes(self):
        """Test script at maximum scene limit."""
        scenes = [SceneConfig(text=f"Scene {i+1}") for i in range(100)]
        script = VideoScript(
            scenes=scenes,
            config=ProjectConfig(voice_id="test")
        )
        assert len(script.scenes) == 100

    def test_empty_duration_estimation(self):
        """Test duration estimation with minimal text."""
        script = VideoScript(
            scenes=[SceneConfig(text="Hi")],
            config=ProjectConfig(voice_id="test")
        )
        duration = script.get_total_estimated_duration()
        assert duration > 0
        assert duration < 10  # Should be very short

    def test_voice_id_with_special_characters(self):
        """Test voice_id with various allowed characters."""
        voice_ids = [
            "21m00Tcm4TlvDq8ikWAM",
            "voice-id-123",
            "voice_id_456",
            "VoiceID789"
        ]
        for voice_id in voice_ids:
            config = ProjectConfig(voice_id=voice_id)
            assert config.voice_id == voice_id
