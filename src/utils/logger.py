"""Logging utilities using Rich for beautiful console output."""

import logging
import sys
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.table import Table

from src.utils.config import get_settings


# Global console instance
console = Console()


def setup_logging() -> logging.Logger:
    """
    Set up logging with Rich handler.

    Returns:
        Configured logger instance
    """
    settings = get_settings()

    # Configure root logger
    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                show_time=True,
                show_path=False,
            )
        ],
    )

    logger = logging.getLogger("video-editor")
    logger.setLevel(settings.log_level)

    return logger


def get_logger() -> logging.Logger:
    """Get the application logger."""
    _ensure_logger()  # Ensure logger is initialized
    return logging.getLogger("video-editor")


def create_progress() -> Progress:
    """
    Create a Rich progress bar with nice formatting.

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_panel(content: str, title: str = "", style: str = "blue") -> None:
    """
    Print content in a panel.

    Args:
        content: Panel content
        title: Optional panel title
        style: Panel border style (color)
    """
    console.print(Panel(content, title=title, border_style=style))


def print_table(
    title: str,
    columns: list[tuple[str, str]],
    rows: list[list[str]],
) -> None:
    """
    Print a formatted table.

    Args:
        title: Table title
        columns: List of (column_name, style) tuples
        rows: List of row data
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")

    for col_name, col_style in columns:
        table.add_column(col_name, style=col_style)

    for row in rows:
        table.add_row(*row)

    console.print(table)


def print_video_summary(
    scenes: int,
    duration: float,
    resolution: str,
    output_file: str,
) -> None:
    """
    Print a summary of the video generation.

    Args:
        scenes: Number of scenes
        duration: Estimated duration in seconds
        resolution: Video resolution
        output_file: Output filename
    """
    print_table(
        title="Video Generation Summary",
        columns=[
            ("Property", "cyan"),
            ("Value", "green"),
        ],
        rows=[
            ["Scenes", str(scenes)],
            ["Est. Duration", f"{duration:.1f}s"],
            ["Resolution", resolution],
            ["Output File", output_file],
        ],
    )


def print_error_panel(error: Exception, context: str = "") -> None:
    """
    Print an error in a red panel.

    Args:
        error: Exception that occurred
        context: Optional context about where the error occurred
    """
    error_message = f"[red]{type(error).__name__}:[/red] {str(error)}"
    if context:
        error_message = f"[bold]{context}[/bold]\n\n{error_message}"

    print_panel(error_message, title="⚠️  Error", style="red")


def print_api_error(service: str, status_code: int, message: str) -> None:
    """
    Print an API error with helpful context.

    Args:
        service: API service name (e.g., "Pexels", "ElevenLabs")
        status_code: HTTP status code
        message: Error message
    """
    if status_code == 401:
        content = (
            f"[red]Authentication failed for {service}[/red]\n\n"
            f"Status Code: {status_code}\n"
            f"Message: {message}\n\n"
            f"Please check your API key in the .env file."
        )
    elif status_code == 429:
        content = (
            f"[red]Rate limit exceeded for {service}[/red]\n\n"
            f"Status Code: {status_code}\n"
            f"Message: {message}\n\n"
            f"Please wait a few minutes before trying again."
        )
    else:
        content = (
            f"[red]API error from {service}[/red]\n\n"
            f"Status Code: {status_code}\n"
            f"Message: {message}"
        )

    print_panel(content, title=f"⚠️  {service} API Error", style="red")


# Logger instance - initialized lazily
_logger: logging.Logger | None = None


def _ensure_logger() -> logging.Logger:
    """Ensure logger is initialized (lazy initialization)."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger
