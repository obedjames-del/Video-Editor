"""Scene timing processor for calculating optimal video/audio synchronization."""

import json
import subprocess
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger

logger = get_logger()


def get_audio_duration(audio_path: Path) -> float:
    """
    Get duration of audio file using ffprobe.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If ffprobe fails or returns invalid data
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        logger.debug(f"Getting duration for audio file: {audio_path}")

        # Run ffprobe to get duration
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse JSON output
        data = json.loads(result.stdout)

        if "format" not in data or "duration" not in data["format"]:
            raise RuntimeError(f"ffprobe returned unexpected format: {result.stdout}")

        duration = float(data["format"]["duration"])
        logger.debug(f"Audio duration: {duration:.2f}s")

        return duration

    except subprocess.CalledProcessError as e:
        error_msg = f"ffprobe failed for {audio_path}: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        error_msg = f"Failed to parse ffprobe output for {audio_path}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_video_duration(video_path: Path) -> float:
    """
    Get duration of video file using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds

    Raises:
        FileNotFoundError: If video file doesn't exist
        RuntimeError: If ffprobe fails or returns invalid data
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        logger.debug(f"Getting duration for video file: {video_path}")

        # Run ffprobe to get duration
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse JSON output
        data = json.loads(result.stdout)

        if "format" not in data or "duration" not in data["format"]:
            raise RuntimeError(f"ffprobe returned unexpected format: {result.stdout}")

        duration = float(data["format"]["duration"])
        logger.debug(f"Video duration: {duration:.2f}s")

        return duration

    except subprocess.CalledProcessError as e:
        error_msg = f"ffprobe failed for {video_path}: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        error_msg = f"Failed to parse ffprobe output for {video_path}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def calculate_scene_timings(
    scene_audios: list[tuple[Path, float]],  # (audio_path, duration)
    scene_videos: list[Path],
) -> list[dict[str, Any]]:
    """
    Calculate timing information for each scene.

    This function determines how to synchronize video clips with audio narration
    for each scene. It calculates whether videos need to be looped (if too short)
    or trimmed (if too long) to match the audio duration.

    Args:
        scene_audios: List of (audio_path, duration) tuples for each scene
        scene_videos: List of video file paths for each scene

    Returns:
        List of timing dicts with:
        - audio_path: Path - Path to audio file
        - audio_duration: float - Duration of audio in seconds
        - video_path: Path - Path to video file
        - video_duration: float - Duration of video in seconds
        - target_duration: float - Target duration (same as audio_duration)
        - needs_loop: bool - True if video needs to be looped
        - needs_trim: bool - True if video needs to be trimmed

    Raises:
        ValueError: If scene_audios and scene_videos lengths don't match
        FileNotFoundError: If any audio or video file doesn't exist
        RuntimeError: If ffprobe fails for any file
    """
    if len(scene_audios) != len(scene_videos):
        raise ValueError(
            f"Mismatch between audio and video counts: "
            f"{len(scene_audios)} audios vs {len(scene_videos)} videos"
        )

    if not scene_audios:
        logger.warning("No scenes to process")
        return []

    logger.info(f"Calculating timings for {len(scene_audios)} scenes")

    timings = []

    for idx, ((audio_path, audio_duration), video_path) in enumerate(
        zip(scene_audios, scene_videos), start=1
    ):
        logger.info(f"Processing scene {idx}/{len(scene_audios)}")

        try:
            # Validate audio duration or get it if not provided
            if audio_duration <= 0:
                logger.debug(f"Invalid audio duration {audio_duration}, fetching from file")
                audio_duration = get_audio_duration(audio_path)

            # Get video duration
            video_duration = get_video_duration(video_path)

            # Determine if we need to loop or trim
            # Add a small tolerance (0.1s) to avoid unnecessary operations
            tolerance = 0.1
            needs_loop = video_duration < (audio_duration - tolerance)
            needs_trim = video_duration > (audio_duration + tolerance)

            timing_info = {
                "audio_path": audio_path,
                "audio_duration": audio_duration,
                "video_path": video_path,
                "video_duration": video_duration,
                "target_duration": audio_duration,  # Video should match audio duration
                "needs_loop": needs_loop,
                "needs_trim": needs_trim,
            }

            # Log timing decision
            if needs_loop:
                logger.info(
                    f"Scene {idx}: Video ({video_duration:.2f}s) will be looped "
                    f"to match audio ({audio_duration:.2f}s)"
                )
            elif needs_trim:
                logger.info(
                    f"Scene {idx}: Video ({video_duration:.2f}s) will be trimmed "
                    f"to match audio ({audio_duration:.2f}s)"
                )
            else:
                logger.info(
                    f"Scene {idx}: Video ({video_duration:.2f}s) matches audio "
                    f"({audio_duration:.2f}s) - no adjustment needed"
                )

            timings.append(timing_info)

        except Exception as e:
            logger.error(f"Failed to process scene {idx}: {e}")
            raise

    # Log summary
    loop_count = sum(1 for t in timings if t["needs_loop"])
    trim_count = sum(1 for t in timings if t["needs_trim"])
    match_count = len(timings) - loop_count - trim_count

    logger.info(
        f"Timing calculation complete: {match_count} matched, "
        f"{loop_count} need looping, {trim_count} need trimming"
    )

    return timings
