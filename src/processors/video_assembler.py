"""FFmpeg-based video assembler for processing and combining video clips."""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional
import ffmpeg

from src.utils.config import get_settings
from src.utils.logger import get_logger


logger = get_logger()


class VideoAssemblerError(Exception):
    """Base exception for video assembler errors."""
    pass


class FFmpegError(VideoAssemblerError):
    """Exception raised when FFmpeg operations fail."""
    pass


async def _run_ffmpeg_async(stream, overwrite: bool = True) -> None:
    """
    Run an FFmpeg command asynchronously.

    Args:
        stream: FFmpeg stream object
        overwrite: Whether to overwrite output files

    Raises:
        FFmpegError: If FFmpeg command fails
    """
    settings = get_settings()

    try:
        # Build command arguments
        if overwrite:
            stream = stream.overwrite_output()

        # Get the command as a list
        cmd = stream.compile()

        logger.debug(f"Running FFmpeg command: {' '.join(cmd)}")

        # Run the command asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
            logger.error(f"FFmpeg error: {error_msg}")
            raise FFmpegError(f"FFmpeg command failed: {error_msg}")

        logger.debug("FFmpeg command completed successfully")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg process error: {error_msg}")
        raise FFmpegError(f"FFmpeg execution failed: {error_msg}") from e
    except Exception as e:
        logger.error(f"Unexpected error running FFmpeg: {e}")
        raise FFmpegError(f"Unexpected FFmpeg error: {e}") from e


async def get_video_duration(video_path: Path) -> float:
    """
    Get the duration of a video file in seconds.

    Args:
        video_path: Path to the video file

    Returns:
        Duration in seconds

    Raises:
        FFmpegError: If unable to probe video
    """
    try:
        probe = ffmpeg.probe(str(video_path))
        duration = float(probe['format']['duration'])
        logger.debug(f"Video duration for {video_path.name}: {duration}s")
        return duration
    except Exception as e:
        logger.error(f"Failed to probe video {video_path}: {e}")
        raise FFmpegError(f"Could not get video duration: {e}") from e


async def get_video_info(video_path: Path) -> dict:
    """
    Get detailed information about a video file.

    Args:
        video_path: Path to the video file

    Returns:
        Dictionary with video information (duration, width, height, fps)

    Raises:
        FFmpegError: If unable to probe video
    """
    try:
        probe = ffmpeg.probe(str(video_path))
        video_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'video'),
            None
        )

        if not video_stream:
            raise FFmpegError(f"No video stream found in {video_path}")

        info = {
            'duration': float(probe['format']['duration']),
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'fps': eval(video_stream.get('r_frame_rate', '30/1')),
        }

        logger.debug(f"Video info for {video_path.name}: {info}")
        return info

    except Exception as e:
        logger.error(f"Failed to get video info for {video_path}: {e}")
        raise FFmpegError(f"Could not get video info: {e}") from e


async def process_video_clip(
    input_path: Path,
    output_path: Path,
    target_duration: float,
    resolution: str = "1920x1080",
) -> Path:
    """
    Trim or loop video to match target duration and resolution.

    Args:
        input_path: Path to input video
        output_path: Path for output video
        target_duration: Desired duration in seconds
        resolution: Target resolution (WxH format)

    Returns:
        Path to processed video

    Raises:
        FFmpegError: If processing fails
    """
    settings = get_settings()

    try:
        logger.info(f"Processing video clip: {input_path.name} -> {target_duration}s @ {resolution}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get current video duration
        current_duration = await get_video_duration(input_path)

        # Parse resolution
        width, height = map(int, resolution.split('x'))

        # Build FFmpeg stream
        stream = ffmpeg.input(str(input_path))

        if current_duration < target_duration:
            # Loop video to reach target duration
            loop_count = int(target_duration / current_duration) + 1
            logger.debug(f"Looping video {loop_count} times to reach {target_duration}s")

            # Create looped video
            stream = stream.filter('loop', loop=loop_count, size=32767)
            stream = stream.filter('setpts', f'N/FRAME_RATE/TB')

        # Trim to exact target duration
        stream = stream.filter('trim', duration=target_duration)
        stream = stream.filter('setpts', 'PTS-STARTPTS')

        # Scale to target resolution
        stream = stream.filter('scale', width, height)
        stream = stream.filter('setsar', '1/1')  # Set aspect ratio to 1:1 (square pixels)

        # Set output parameters
        stream = stream.output(
            str(output_path),
            vcodec='libx264',
            acodec='aac',
            video_bitrate='2M',
            audio_bitrate='128k',
            r=settings.default_fps,
            preset='medium',
            pix_fmt='yuv420p',
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        logger.info(f"Successfully processed video clip: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to process video clip {input_path}: {e}")
        raise FFmpegError(f"Video processing failed: {e}") from e


async def add_audio_to_video(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
) -> Path:
    """
    Overlay audio track on video.

    Args:
        video_path: Path to input video
        audio_path: Path to audio file
        output_path: Path for output video

    Returns:
        Path to video with audio

    Raises:
        FFmpegError: If audio overlay fails
    """
    settings = get_settings()

    try:
        logger.info(f"Adding audio to video: {video_path.name} + {audio_path.name}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get video duration to trim audio if needed
        video_duration = await get_video_duration(video_path)

        # Build FFmpeg stream
        video = ffmpeg.input(str(video_path))
        audio = ffmpeg.input(str(audio_path))

        # Trim audio to video duration
        audio = audio.filter('atrim', duration=video_duration)
        audio = audio.filter('asetpts', 'PTS-STARTPTS')

        # Combine video and audio
        stream = ffmpeg.output(
            video,
            audio,
            str(output_path),
            vcodec='copy',  # Copy video stream (no re-encoding)
            acodec='aac',
            audio_bitrate='128k',
            shortest=None,  # End when shortest input ends
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        logger.info(f"Successfully added audio to video: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to add audio to video: {e}")
        raise FFmpegError(f"Audio overlay failed: {e}") from e


async def concatenate_videos(
    video_files: list[Path],
    output_path: Path,
    transition_duration: float = 1.0,
) -> Path:
    """
    Concatenate videos with optional crossfade transitions.

    For MVP (Week 1): Simple concatenation without crossfade transitions.
    Crossfade can be added in future iterations.

    Args:
        video_files: List of video file paths to concatenate
        output_path: Path for output video
        transition_duration: Duration of crossfade transition in seconds (ignored in MVP)

    Returns:
        Path to concatenated video

    Raises:
        FFmpegError: If concatenation fails
    """
    settings = get_settings()

    try:
        if not video_files:
            raise VideoAssemblerError("No video files provided for concatenation")

        if len(video_files) == 1:
            logger.info("Only one video file, copying to output")
            # Just copy the single file
            import shutil
            shutil.copy2(video_files[0], output_path)
            return output_path

        logger.info(f"Concatenating {len(video_files)} videos")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a temporary file list for FFmpeg concat demuxer
        concat_file = settings.temp_dir / f"concat_list_{output_path.stem}.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)

        # Write file list in FFmpeg concat format
        with open(concat_file, 'w') as f:
            for video_file in video_files:
                # Use absolute paths and escape special characters
                abs_path = video_file.absolute()
                # Escape single quotes in the path
                escaped_path = str(abs_path).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

        logger.debug(f"Created concat file: {concat_file}")

        # Build FFmpeg command using concat demuxer
        # This is the most reliable method for concatenating videos
        stream = ffmpeg.input(
            str(concat_file),
            format='concat',
            safe=0  # Allow absolute paths
        )

        stream = stream.output(
            str(output_path),
            vcodec='libx264',
            acodec='aac',
            video_bitrate='2M',
            audio_bitrate='128k',
            preset='medium',
            pix_fmt='yuv420p',
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        # Clean up temporary concat file
        try:
            concat_file.unlink()
        except Exception as e:
            logger.warning(f"Could not delete temporary concat file: {e}")

        logger.info(f"Successfully concatenated videos: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to concatenate videos: {e}")
        raise FFmpegError(f"Video concatenation failed: {e}") from e


async def concatenate_videos_with_crossfade(
    video_files: list[Path],
    output_path: Path,
    transition_duration: float = 1.0,
) -> Path:
    """
    Concatenate videos with crossfade transitions.

    This is a more advanced version that can be used in future iterations.
    Currently not used in MVP to keep implementation simple.

    Args:
        video_files: List of video file paths to concatenate
        output_path: Path for output video
        transition_duration: Duration of crossfade transition in seconds

    Returns:
        Path to concatenated video

    Raises:
        FFmpegError: If concatenation fails
    """
    settings = get_settings()

    try:
        if not video_files:
            raise VideoAssemblerError("No video files provided for concatenation")

        if len(video_files) == 1:
            # Just copy the single file
            import shutil
            shutil.copy2(video_files[0], output_path)
            return output_path

        logger.info(f"Concatenating {len(video_files)} videos with crossfade transitions")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get durations for offset calculations
        durations = []
        for video_file in video_files:
            duration = await get_video_duration(video_file)
            durations.append(duration)

        # Build complex filter for crossfade
        # This is complex and requires careful offset calculations
        inputs = [ffmpeg.input(str(vf)) for vf in video_files]

        # Start with first video
        current = inputs[0]
        current_offset = 0

        for i in range(1, len(inputs)):
            # Calculate offset for next video
            current_offset += durations[i-1] - transition_duration

            # Apply crossfade filter
            current = ffmpeg.filter(
                [current, inputs[i]],
                'xfade',
                transition='fade',
                duration=transition_duration,
                offset=current_offset
            )

        # Output
        stream = ffmpeg.output(
            current,
            str(output_path),
            vcodec='libx264',
            acodec='aac',
            video_bitrate='2M',
            audio_bitrate='128k',
            preset='medium',
            pix_fmt='yuv420p',
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        logger.info(f"Successfully concatenated videos with crossfade: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to concatenate videos with crossfade: {e}")
        raise FFmpegError(f"Video concatenation with crossfade failed: {e}") from e


async def assemble_final_video(
    scene_videos: list[Path],
    scene_audios: list[Path],
    output_path: Path,
    resolution: str = "1920x1080",
    fps: int = 30,
    transition_duration: float = 1.0,
) -> Path:
    """
    Main function to assemble complete video from scenes.

    This function:
    1. Adds audio to each scene video
    2. Concatenates all scenes together
    3. Produces final output video

    Args:
        scene_videos: List of video files for each scene
        scene_audios: List of audio files for each scene
        output_path: Path for final output video
        resolution: Target resolution (WxH format)
        fps: Target frames per second
        transition_duration: Duration of transitions between scenes (in seconds)

    Returns:
        Path to final assembled video

    Raises:
        FFmpegError: If assembly fails
        VideoAssemblerError: If input validation fails
    """
    settings = get_settings()

    try:
        logger.info(f"Assembling final video from {len(scene_videos)} scenes")

        # Validate inputs
        if not scene_videos:
            raise VideoAssemblerError("No scene videos provided")

        if len(scene_videos) != len(scene_audios):
            raise VideoAssemblerError(
                f"Mismatch: {len(scene_videos)} videos but {len(scene_audios)} audio files"
            )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 1: Add audio to each scene video
        logger.info("Step 1: Adding audio to scene videos")
        videos_with_audio = []

        for i, (video_path, audio_path) in enumerate(zip(scene_videos, scene_audios)):
            temp_output = settings.temp_dir / f"scene_{i}_with_audio.mp4"

            try:
                result = await add_audio_to_video(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=temp_output,
                )
                videos_with_audio.append(result)
                logger.debug(f"Added audio to scene {i+1}/{len(scene_videos)}")

            except Exception as e:
                logger.error(f"Failed to add audio to scene {i}: {e}")
                raise

        # Step 2: Concatenate all scenes
        logger.info("Step 2: Concatenating scenes")

        if len(videos_with_audio) == 1:
            # Only one scene, just copy/move to output
            import shutil
            shutil.copy2(videos_with_audio[0], output_path)
        else:
            # Concatenate multiple scenes
            await concatenate_videos(
                video_files=videos_with_audio,
                output_path=output_path,
                transition_duration=transition_duration,
            )

        # Step 3: Clean up temporary files
        logger.info("Step 3: Cleaning up temporary files")
        for temp_file in videos_with_audio:
            try:
                temp_file.unlink()
                logger.debug(f"Deleted temporary file: {temp_file.name}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file {temp_file}: {e}")

        logger.info(f"Successfully assembled final video: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to assemble final video: {e}")
        raise FFmpegError(f"Video assembly failed: {e}") from e


async def extract_audio_from_video(
    video_path: Path,
    output_path: Path,
    audio_format: str = "mp3",
) -> Path:
    """
    Extract audio track from a video file.

    Args:
        video_path: Path to input video
        output_path: Path for output audio file
        audio_format: Output audio format (mp3, aac, wav, etc.)

    Returns:
        Path to extracted audio file

    Raises:
        FFmpegError: If extraction fails
    """
    settings = get_settings()

    try:
        logger.info(f"Extracting audio from video: {video_path.name}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build FFmpeg stream
        stream = ffmpeg.input(str(video_path))
        stream = stream.output(
            str(output_path),
            acodec='libmp3lame' if audio_format == 'mp3' else audio_format,
            audio_bitrate='192k',
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        logger.info(f"Successfully extracted audio: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to extract audio from video: {e}")
        raise FFmpegError(f"Audio extraction failed: {e}") from e


async def resize_video(
    input_path: Path,
    output_path: Path,
    resolution: str,
) -> Path:
    """
    Resize video to target resolution.

    Args:
        input_path: Path to input video
        output_path: Path for output video
        resolution: Target resolution (WxH format)

    Returns:
        Path to resized video

    Raises:
        FFmpegError: If resize fails
    """
    settings = get_settings()

    try:
        logger.info(f"Resizing video to {resolution}: {input_path.name}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Parse resolution
        width, height = map(int, resolution.split('x'))

        # Build FFmpeg stream
        stream = ffmpeg.input(str(input_path))
        stream = stream.filter('scale', width, height)
        stream = stream.filter('setsar', '1/1')

        stream = stream.output(
            str(output_path),
            vcodec='libx264',
            acodec='copy',  # Copy audio without re-encoding
            preset='medium',
            pix_fmt='yuv420p',
            loglevel=settings.ffmpeg_log_level,
        )

        # Run FFmpeg command
        await _run_ffmpeg_async(stream)

        logger.info(f"Successfully resized video: {output_path.name}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to resize video: {e}")
        raise FFmpegError(f"Video resize failed: {e}") from e
