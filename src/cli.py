"""CLI interface using Click framework."""

import sys
import asyncio
from functools import wraps
from pathlib import Path
import click
from rich.panel import Panel

from src.utils.logger import (
    console,
    print_success,
    print_error,
    print_info,
    print_panel,
)
from src.utils.config import get_settings
from src.processors.script_parser import load_script, validate_script_file, get_script_summary
from src.services.cache import get_cache_manager


def async_command(f):
    """Decorator to run async Click commands."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """
    Video-Editor - Automated AI-powered video generation from JSON scripts.

    Generate professional videos by combining:
    - AI voiceovers from ElevenLabs
    - Stock footage from Pexels
    - Intelligent scene analysis from Gemini
    """
    pass


@cli.command()
@click.argument("script_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=str,
    help="Output filename (overrides script config)",
)
@click.option(
    "--voice-id",
    type=str,
    help="ElevenLabs voice ID (overrides script config)",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable caching (always download fresh assets)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@async_command
async def generate(
    script_path: Path,
    output: str | None,
    voice_id: str | None,
    no_cache: bool,
    verbose: bool,
) -> None:
    """Generate a video from a JSON script."""
    try:
        # Import here to avoid circular imports
        from src.main import generate_video

        # Validate script first
        print_info(f"Loading script: {script_path}")
        is_valid, error = validate_script_file(script_path)

        if not is_valid:
            print_error(f"Script validation failed:\n{error}")
            sys.exit(1)

        # Load script
        script = load_script(script_path)

        # Show summary
        summary = get_script_summary(script)
        print_panel(
            f"[cyan]Scenes:[/cyan] {summary['total_scenes']}\n"
            f"[cyan]Estimated Duration:[/cyan] {summary['estimated_duration']:.1f}s\n"
            f"[cyan]Resolution:[/cyan] {summary['resolution']}\n"
            f"[cyan]Output:[/cyan] {summary['output_file']}",
            title="📹 Video Configuration",
        )

        # Apply overrides
        if output:
            script.config.output_file = output
        if voice_id:
            script.config.voice_id = voice_id

        # Generate video
        print_info("Starting video generation...")
        output_path = await generate_video(
            script=script,
            use_cache=not no_cache,
            verbose=verbose,
        )

        print_success(f"Video generated successfully: {output_path}")
        print_panel(
            f"[green]Your video is ready![/green]\n\n"
            f"Location: {output_path}\n"
            f"Open with your video player to watch.",
            title="✨ Success",
            style="green",
        )

    except Exception as e:
        print_error(f"Video generation failed: {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("script_path", type=click.Path(exists=True, path_type=Path))
def validate(script_path: Path) -> None:
    """Validate a script file without generating video."""
    try:
        print_info(f"Validating script: {script_path}")

        is_valid, error = validate_script_file(script_path)

        if is_valid:
            script = load_script(script_path)
            summary = get_script_summary(script)

            print_success("Script is valid!")
            print_panel(
                f"[cyan]Scenes:[/cyan] {summary['total_scenes']}\n"
                f"[cyan]Estimated Duration:[/cyan] {summary['estimated_duration']:.1f}s\n"
                f"[cyan]Requires Gemini:[/cyan] {summary['requires_gemini']}\n"
                f"[cyan]Resolution:[/cyan] {summary['resolution']}\n"
                f"[cyan]FPS:[/cyan] {summary['fps']}\n"
                f"[cyan]Output File:[/cyan] {summary['output_file']}",
                title="✓ Script Summary",
                style="green",
            )
        else:
            print_error("Script validation failed:")
            console.print(error)
            sys.exit(1)

    except Exception as e:
        print_error(f"Validation error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("script_path", type=click.Path(exists=True, path_type=Path))
def preview(script_path: Path) -> None:
    """Preview what will be generated without actually generating."""
    try:
        print_info(f"Previewing script: {script_path}")

        script = load_script(script_path)
        summary = get_script_summary(script)

        # Show configuration
        print_panel(
            f"[cyan]Resolution:[/cyan] {summary['resolution']}\n"
            f"[cyan]FPS:[/cyan] {summary['fps']}\n"
            f"[cyan]Transition:[/cyan] {summary['transition_duration']}s\n"
            f"[cyan]Output:[/cyan] {summary['output_file']}\n"
            f"[cyan]Use Gemini:[/cyan] {summary['requires_gemini']}",
            title="⚙️  Configuration",
        )

        # Show scenes
        from rich.table import Table

        table = Table(title=f"📋 Scenes ({len(script.scenes)} total)", show_header=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Text", style="white")
        table.add_column("Video Query", style="green")

        for i, scene in enumerate(script.scenes, 1):
            query = scene.video_query or "[yellow]Auto (Gemini)[/yellow]"
            text_preview = scene.text[:60] + "..." if len(scene.text) > 60 else scene.text
            table.add_row(str(i), text_preview, query)

        console.print(table)

        # Show estimated costs
        print_panel(
            f"[cyan]ElevenLabs Characters:[/cyan] ~{summary['total_chars']} chars\n"
            f"[cyan]Pexels API Calls:[/cyan] {summary['total_scenes']} requests\n"
            f"[cyan]Gemini API Calls:[/cyan] {'1' if summary['requires_gemini'] else '0'} request\n\n"
            f"[dim]Estimated API costs: <$0.10[/dim]",
            title="💰 Resource Usage",
        )

    except Exception as e:
        print_error(f"Preview error: {str(e)}")
        sys.exit(1)


@cli.group()
def cache() -> None:
    """Manage cached assets."""
    pass


@cache.command("clear")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompt",
)
def cache_clear(force: bool) -> None:
    """Clear all cached videos and audio."""
    try:
        cache_mgr = get_cache_manager()
        stats = cache_mgr.get_cache_stats()

        if stats["total_size_mb"] == 0:
            print_info("Cache is already empty")
            return

        # Show current cache stats
        print_info(f"Cache contains:")
        print_info(f"  Videos: {stats['video_count']} ({stats['video_size_mb']:.2f} MB)")
        print_info(f"  Audio: {stats['audio_count']} ({stats['audio_size_mb']:.2f} MB)")
        print_info(f"  Total: {stats['total_size_mb']:.2f} MB")

        if not force:
            if not click.confirm("\nAre you sure you want to clear the cache?"):
                print_info("Cache clear cancelled")
                return

        cache_mgr.clear_cache()
        print_success("Cache cleared successfully")

    except Exception as e:
        print_error(f"Failed to clear cache: {str(e)}")
        sys.exit(1)


@cache.command("stats")
def cache_stats() -> None:
    """Show cache statistics."""
    try:
        cache_mgr = get_cache_manager()
        stats = cache_mgr.get_cache_stats()

        print_panel(
            f"[cyan]Videos:[/cyan] {stats['video_count']} files ({stats['video_size_mb']:.2f} MB)\n"
            f"[cyan]Audio:[/cyan] {stats['audio_count']} files ({stats['audio_size_mb']:.2f} MB)\n"
            f"[cyan]Total Size:[/cyan] {stats['total_size_mb']:.2f} MB\n\n"
            f"[cyan]Video Cache Hits:[/cyan] {stats['video_hits']}\n"
            f"[cyan]Audio Cache Hits:[/cyan] {stats['audio_hits']}\n"
            f"[cyan]Video Hit Rate:[/cyan] {stats['video_hit_rate']:.1f}%\n"
            f"[cyan]Audio Hit Rate:[/cyan] {stats['audio_hit_rate']:.1f}%",
            title="📊 Cache Statistics",
        )

    except Exception as e:
        print_error(f"Failed to get cache stats: {str(e)}")
        sys.exit(1)


@cli.command()
def init() -> None:
    """Initialize the project (create .env file from template)."""
    try:
        env_file = Path(".env")
        env_example = Path(".env.example")

        if env_file.exists():
            print_error(".env file already exists")
            if not click.confirm("Overwrite existing .env file?"):
                print_info("Init cancelled")
                return

        if not env_example.exists():
            print_error(".env.example not found")
            sys.exit(1)

        # Copy template
        import shutil
        shutil.copy(env_example, env_file)

        print_success("Created .env file from template")
        print_panel(
            "[yellow]Next steps:[/yellow]\n\n"
            "1. Edit .env file with your API keys:\n"
            "   - ELEVENLABS_API_KEY\n"
            "   - PEXELS_API_KEY\n"
            "   - GEMINI_API_KEY\n\n"
            "2. Get API keys from:\n"
            "   - ElevenLabs: https://elevenlabs.io\n"
            "   - Pexels: https://www.pexels.com/api/\n"
            "   - Gemini: https://ai.google.dev\n\n"
            "3. Run: video-editor validate examples/simple_script.json",
            title="🚀 Setup Instructions",
        )

    except Exception as e:
        print_error(f"Init failed: {str(e)}")
        sys.exit(1)


@cli.command()
def config() -> None:
    """Show current configuration and validate API keys."""
    try:
        settings = get_settings()

        # Validate API keys
        missing = settings.validate_api_keys()

        if missing:
            print_error(f"Missing API keys: {', '.join(missing)}")
            print_info("Run 'video-editor init' to create .env file")
            sys.exit(1)

        print_panel(
            f"[green]✓ All API keys configured[/green]\n\n"
            f"[cyan]Default Voice:[/cyan] {settings.default_voice_id}\n"
            f"[cyan]Default Resolution:[/cyan] {settings.default_resolution}\n"
            f"[cyan]Default FPS:[/cyan] {settings.default_fps}\n"
            f"[cyan]Cache Enabled:[/cyan] {settings.enable_cache}\n"
            f"[cyan]Gemini Model:[/cyan] {settings.gemini_model}",
            title="⚙️  Configuration",
            style="green",
        )

    except Exception as e:
        print_error(f"Configuration error: {str(e)}")
        print_info("Make sure .env file exists with valid API keys")
        sys.exit(1)


if __name__ == "__main__":
    cli()
