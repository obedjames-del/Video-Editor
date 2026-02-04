"""ElevenLabs voiceover generation service."""

import hashlib
from pathlib import Path
from typing import Optional

import httpx
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class VoiceoverError(Exception):
    """Custom exception for voiceover generation errors."""

    pass


async def generate_voiceover(
    text: str,
    voice_id: str,
    output_path: Path,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> tuple[Path, float]:
    """
    Generate voiceover using ElevenLabs API and return file path and duration.

    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID to use
        output_path: Path where the audio file should be saved
        model: ElevenLabs model to use (default: eleven_multilingual_v2)
        stability: Voice stability setting (0.0-1.0, default: 0.5)
        similarity_boost: Voice similarity boost (0.0-1.0, default: 0.75)

    Returns:
        Tuple of (file_path, duration_in_seconds)

    Raises:
        VoiceoverError: If voiceover generation fails
    """
    settings = get_settings()

    logger.info(f"Generating voiceover for text: '{text[:50]}...'")
    logger.debug(
        f"Voice ID: {voice_id}, Model: {model}, "
        f"Stability: {stability}, Similarity Boost: {similarity_boost}"
    )

    try:
        # Initialize ElevenLabs async client
        client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)

        # Create voice settings
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
        )

        # Generate audio using async API
        logger.debug("Calling ElevenLabs API...")
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model,
            voice_settings=voice_settings,
        )

        # Convert async generator to bytes
        audio_bytes = b""
        async for chunk in audio_generator:
            audio_bytes += chunk

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save audio to file
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Voiceover saved to: {output_path}")

        # Get audio duration
        duration = await _get_audio_duration(output_path)
        logger.info(f"Audio duration: {duration:.2f}s")

        return (output_path, duration)

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_message = str(e)

        if status_code == 401:
            logger.error("ElevenLabs authentication failed - invalid API key")
            raise VoiceoverError(
                "ElevenLabs authentication failed. Please check your API key in .env file."
            ) from e
        elif status_code == 429:
            logger.error("ElevenLabs rate limit exceeded")
            raise VoiceoverError(
                "ElevenLabs rate limit exceeded. Please wait a few minutes before trying again."
            ) from e
        elif status_code == 400:
            logger.error(f"ElevenLabs bad request: {error_message}")
            raise VoiceoverError(
                f"Invalid request to ElevenLabs API. Check voice_id and parameters: {error_message}"
            ) from e
        elif status_code == 402:
            logger.error("ElevenLabs quota exceeded")
            raise VoiceoverError(
                "ElevenLabs quota exceeded. Please upgrade your plan or wait until quota resets."
            ) from e
        else:
            logger.error(f"ElevenLabs API error {status_code}: {error_message}")
            raise VoiceoverError(
                f"ElevenLabs API error (status {status_code}): {error_message}"
            ) from e

    except Exception as e:
        logger.error(f"Unexpected error generating voiceover: {e}", exc_info=True)
        raise VoiceoverError(f"Failed to generate voiceover: {str(e)}") from e


async def generate_voiceover_cached(
    text: str,
    voice_id: str,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> tuple[Path, float]:
    """
    Generate voiceover with automatic caching based on text content.

    This function generates a hash from the text and voice parameters to create
    a unique filename. If the file already exists, it returns the cached version.

    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID to use
        model: ElevenLabs model to use (default: eleven_multilingual_v2)
        stability: Voice stability setting (0.0-1.0, default: 0.5)
        similarity_boost: Voice similarity boost (0.0-1.0, default: 0.75)

    Returns:
        Tuple of (file_path, duration_in_seconds)

    Raises:
        VoiceoverError: If voiceover generation fails
    """
    settings = get_settings()

    # Generate cache key from text and parameters
    cache_key = _generate_cache_key(
        text=text,
        voice_id=voice_id,
        model=model,
        stability=stability,
        similarity_boost=similarity_boost,
    )

    # Create output path in cache directory
    audio_cache_dir = settings.cache_dir / "audio"
    audio_cache_dir.mkdir(parents=True, exist_ok=True)
    output_path = audio_cache_dir / f"{cache_key}.mp3"

    # Check if cached version exists
    if settings.enable_cache and output_path.exists():
        logger.info(f"Using cached voiceover: {output_path}")
        duration = await _get_audio_duration(output_path)
        return (output_path, duration)

    # Generate new voiceover
    logger.info("Cache miss - generating new voiceover")
    return await generate_voiceover(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
        model=model,
        stability=stability,
        similarity_boost=similarity_boost,
    )


def _generate_cache_key(
    text: str,
    voice_id: str,
    model: str,
    stability: float,
    similarity_boost: float,
) -> str:
    """
    Generate a unique cache key from voiceover parameters.

    Args:
        text: Voiceover text
        voice_id: ElevenLabs voice ID
        model: Model name
        stability: Voice stability
        similarity_boost: Voice similarity boost

    Returns:
        16-character hexadecimal hash
    """
    # Create deterministic string from all parameters
    content = f"{text}|{voice_id}|{model}|{stability:.2f}|{similarity_boost:.2f}"

    # Generate SHA-256 hash and return first 16 characters
    hash_obj = hashlib.sha256(content.encode("utf-8"))
    return hash_obj.hexdigest()[:16]


async def _get_audio_duration(audio_path: Path) -> float:
    """
    Get duration of audio file in seconds using ffprobe.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds

    Raises:
        VoiceoverError: If duration cannot be determined
    """
    try:
        # Use ffprobe to get duration (more reliable than mutagen)
        import json
        import subprocess

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        probe_data = json.loads(result.stdout)
        duration = float(probe_data["format"]["duration"])

        return duration

    except subprocess.CalledProcessError as e:
        logger.error(f"ffprobe failed: {e.stderr}")
        raise VoiceoverError(
            f"Failed to get audio duration using ffprobe: {e.stderr}"
        ) from e
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse ffprobe output: {e}")
        raise VoiceoverError(f"Failed to parse audio duration: {str(e)}") from e
    except FileNotFoundError:
        logger.error("ffprobe not found - please install ffmpeg")
        raise VoiceoverError(
            "ffprobe not found. Please install ffmpeg to determine audio duration."
        ) from None
