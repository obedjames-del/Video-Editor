"""Integration tests for ElevenLabs voiceover service.

These tests make real API calls to ElevenLabs and require a valid API key.
They use minimal payloads to reduce API usage and costs.
"""

import pytest
from pathlib import Path

from src.services.voiceover import (
    generate_voiceover,
    generate_voiceover_cached,
    VoiceoverError,
)


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_generates_audio(skip_without_api_keys, temp_dir, mock_settings):
    """Test real ElevenLabs API call with minimal text."""
    # Use short text to minimize API usage
    text = "Hello, testing"
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)
    output_path = temp_dir / "test_voiceover.mp3"

    # Generate voiceover
    audio_path, duration = await generate_voiceover(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
    )

    # Assertions
    assert audio_path.exists()
    assert audio_path == output_path
    assert audio_path.suffix == ".mp3"
    assert duration > 0
    assert duration < 5.0  # Short text should be under 5 seconds
    assert audio_path.stat().st_size > 0
    assert audio_path.stat().st_size > 1000  # Should be at least 1KB


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_cached_voiceover(skip_without_api_keys, temp_dir, mock_settings):
    """Test cached voiceover generation (should only call API once)."""
    text = "Test caching"
    voice_id = "21m00Tcm4TlvDq8ikWAM"

    # First call - should hit API
    audio_path_1, duration_1 = await generate_voiceover_cached(
        text=text,
        voice_id=voice_id,
    )

    # Second call with same parameters - should use cache
    audio_path_2, duration_2 = await generate_voiceover_cached(
        text=text,
        voice_id=voice_id,
    )

    # Should return the same cached file
    assert audio_path_1 == audio_path_2
    assert duration_1 == duration_2
    assert audio_path_1.exists()
    assert audio_path_1.stat().st_size > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_different_voices(skip_without_api_keys, temp_dir, mock_settings):
    """Test voiceover generation with different voice IDs."""
    text = "Testing voices"

    # Test with Rachel voice
    rachel_voice = "21m00Tcm4TlvDq8ikWAM"
    output_path_1 = temp_dir / "rachel.mp3"

    audio_path_1, duration_1 = await generate_voiceover(
        text=text,
        voice_id=rachel_voice,
        output_path=output_path_1,
    )

    # Test with Antoni voice
    antoni_voice = "ErXwobaYiN019PkySvjV"
    output_path_2 = temp_dir / "antoni.mp3"

    audio_path_2, duration_2 = await generate_voiceover(
        text=text,
        voice_id=antoni_voice,
        output_path=output_path_2,
    )

    # Both should succeed
    assert audio_path_1.exists()
    assert audio_path_2.exists()
    assert duration_1 > 0
    assert duration_2 > 0

    # Different voices should produce different files
    assert audio_path_1.read_bytes() != audio_path_2.read_bytes()


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_voice_settings(skip_without_api_keys, temp_dir, mock_settings):
    """Test voiceover generation with custom voice settings."""
    text = "Custom settings"
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    output_path = temp_dir / "custom_settings.mp3"

    # Generate with custom stability and similarity boost
    audio_path, duration = await generate_voiceover(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
        stability=0.3,
        similarity_boost=0.8,
    )

    # Should succeed with custom settings
    assert audio_path.exists()
    assert duration > 0
    assert audio_path.stat().st_size > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_invalid_voice_id(skip_without_api_keys, temp_dir, mock_settings):
    """Test that invalid voice ID raises appropriate error."""
    text = "Testing error"
    invalid_voice_id = "invalid_voice_id_12345"
    output_path = temp_dir / "error_test.mp3"

    # Should raise VoiceoverError for invalid voice ID
    with pytest.raises(VoiceoverError) as exc_info:
        await generate_voiceover(
            text=text,
            voice_id=invalid_voice_id,
            output_path=output_path,
        )

    # Error message should indicate the problem
    assert "ElevenLabs" in str(exc_info.value)


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_empty_text(skip_without_api_keys, temp_dir, mock_settings):
    """Test voiceover generation with empty text."""
    text = ""
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    output_path = temp_dir / "empty_text.mp3"

    # Empty text might be rejected by API or generate minimal audio
    # Either outcome is acceptable - just verify it handles gracefully
    try:
        audio_path, duration = await generate_voiceover(
            text=text,
            voice_id=voice_id,
            output_path=output_path,
        )
        # If it succeeds, verify minimal output
        assert audio_path.exists()
        assert duration >= 0
    except VoiceoverError:
        # If it fails, that's also acceptable for empty text
        pass


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_elevenlabs_long_text(skip_without_api_keys, temp_dir, mock_settings):
    """Test voiceover generation with longer text (but still minimal for cost)."""
    # Use a sentence that's longer but still minimal
    text = "This is a slightly longer test sentence to verify the API can handle it."
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    output_path = temp_dir / "long_text.mp3"

    audio_path, duration = await generate_voiceover(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
    )

    # Should succeed with longer text
    assert audio_path.exists()
    assert duration > 0
    assert duration > 1.0  # Should be at least 1 second for this text
    assert audio_path.stat().st_size > 2000  # Larger file for more text
