"""Main entry point and video generation orchestrator."""

import asyncio
import sys
from pathlib import Path
from typing import Tuple

from src.models.script import VideoScript
from src.utils.config import get_settings
from src.utils.logger import (
    get_logger,
    create_progress,
    print_success,
    print_error,
    print_info,
    console,
)
from src.services.voiceover import generate_voiceover_cached
from src.services.video_search import VideoSearchService
from src.services.gemini import generate_video_queries
from src.services.cache import get_cache_manager
from src.processors.script_parser import load_script
from src.processors.scene_timing import calculate_scene_timings, get_video_duration
from src.processors.video_assembler import (
    process_video_clip,
    add_audio_to_video,
    concatenate_videos,
)

from src.cli import cli

logger = get_logger()


async def generate_video(
    script: VideoScript,
    use_cache: bool = True,
    verbose: bool = False,
) -> Path:
    """
    Main video generation pipeline.

    Args:
        script: Validated video script
        use_cache: Whether to use cached assets
        verbose: Enable verbose logging

    Returns:
        Path to generated video file

    Raises:
        Exception: If video generation fails
    """
    settings = get_settings()
    cache_mgr = get_cache_manager() if use_cache else None

    # Validate API keys
    missing_keys = settings.validate_api_keys()
    if missing_keys:
        raise ValueError(
            f"Missing API keys: {', '.join(missing_keys)}. "
            "Please set them in your .env file."
        )

    output_path = settings.output_dir / script.config.output_file

    try:
        with create_progress() as progress:
            # Phase 1: Generate video queries (if needed)
            if script.requires_gemini():
                task = progress.add_task("Analyzing script with Gemini...", total=1)
                print_info("Using Gemini to generate video search queries")

                scenes_text = [scene.text for scene in script.scenes]
                video_queries = await generate_video_queries(scenes_text)

                # Update scenes with generated queries
                for i, query in enumerate(video_queries):
                    if script.scenes[i].video_query is None:
                        script.scenes[i].video_query = query

                progress.update(task, completed=1)
                print_success(f"Generated {len(video_queries)} video queries")

            # Phase 2: Generate voiceovers
            task = progress.add_task(
                "Generating voiceovers...",
                total=len(script.scenes),
            )

            voiceover_results: list[Tuple[Path, float]] = []

            for i, scene in enumerate(script.scenes):
                logger.info(f"Generating voiceover for scene {i+1}/{len(script.scenes)}")

                audio_path, duration = await generate_voiceover_cached(
                    text=scene.text,
                    voice_id=script.config.voice_id,
                    model=script.config.voice_model,
                    stability=script.config.voice_stability,
                    similarity_boost=script.config.voice_similarity_boost,
                )

                voiceover_results.append((audio_path, duration))
                progress.update(task, advance=1)

            print_success(f"Generated {len(voiceover_results)} voiceovers")

            # Phase 3: Search and download videos
            task = progress.add_task(
                "Searching and downloading videos...",
                total=len(script.scenes),
            )

            video_service = VideoSearchService()
            video_paths: list[Path] = []

            for i, scene in enumerate(script.scenes):
                logger.info(f"Searching videos for scene {i+1}/{len(script.scenes)}")

                # Check cache first
                if cache_mgr and use_cache:
                    cached_video = cache_mgr.get_cached_video(scene.video_query)
                    if cached_video:
                        logger.info(f"Using cached video for: {scene.video_query}")
                        video_paths.append(cached_video)
                        progress.update(task, advance=1)
                        continue

                # Search Pexels
                videos = await video_service.search_videos(
                    query=scene.video_query,
                    orientation=script.config.orientation,
                    per_page=1,
                )

                if not videos:
                    raise ValueError(
                        f"No videos found for query: {scene.video_query}. "
                        "Try a different search term."
                    )

                # Download first result
                video_url = videos[0]["best_video_url"]
                video_filename = f"scene_{i+1}_{hash(scene.video_query) % 10000}.mp4"
                video_path = settings.cache_dir / "videos" / video_filename

                await video_service.download_video(video_url, video_path)

                # Cache it
                if cache_mgr and use_cache:
                    cache_mgr.cache_video(scene.video_query, video_path)

                video_paths.append(video_path)
                progress.update(task, advance=1)

            print_success(f"Downloaded {len(video_paths)} videos")

            # Phase 4: Calculate timing and process video clips
            task = progress.add_task(
                "Processing video clips...",
                total=len(script.scenes),
            )

            print_info("Calculating scene timings")
            timings = calculate_scene_timings(voiceover_results, video_paths)

            processed_videos: list[Path] = []

            for i, timing in enumerate(timings):
                logger.info(f"Processing video clip {i+1}/{len(timings)}")

                # Process video to match audio duration
                processed_path = settings.temp_dir / f"processed_scene_{i+1}.mp4"

                await process_video_clip(
                    input_path=timing["video_path"],
                    output_path=processed_path,
                    target_duration=timing["target_duration"],
                    resolution=script.config.resolution,
                )

                # Add audio to video
                final_scene_path = settings.temp_dir / f"final_scene_{i+1}.mp4"

                await add_audio_to_video(
                    video_path=processed_path,
                    audio_path=timing["audio_path"],
                    output_path=final_scene_path,
                )

                processed_videos.append(final_scene_path)
                progress.update(task, advance=1)

            print_success(f"Processed {len(processed_videos)} video clips")

            # Phase 5: Concatenate all scenes
            task = progress.add_task("Assembling final video...", total=1)

            print_info("Concatenating all scenes")
            await concatenate_videos(
                video_files=processed_videos,
                output_path=output_path,
                transition_duration=script.config.transition_duration,
            )

            progress.update(task, completed=1)

        # Cleanup temp files
        print_info("Cleaning up temporary files")
        for temp_file in settings.temp_dir.glob("*.mp4"):
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")

        # Show cache stats if enabled
        if cache_mgr and use_cache:
            stats = cache_mgr.get_cache_stats()
            logger.info(
                f"Cache stats - Videos: {stats['video_hit_rate']:.1f}% hit rate, "
                f"Audio: {stats['audio_hit_rate']:.1f}% hit rate"
            )

        return output_path

    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}", exc_info=True)
        raise


async def main_async() -> None:
    """Async main entry point for testing."""
    # This is primarily for testing - CLI is the main interface
    if len(sys.argv) < 2:
        print_error("Usage: python -m src.main <script.json>")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    script = load_script(script_path)

    print_info(f"Generating video from: {script_path}")
    output_path = await generate_video(script)
    print_success(f"Video generated: {output_path}")


def main() -> None:
    """Main CLI entry point."""
    # Use click CLI
    cli(_anyio_backend="asyncio")


if __name__ == "__main__":
    # For direct execution: python -m src.main script.json
    asyncio.run(main_async())
