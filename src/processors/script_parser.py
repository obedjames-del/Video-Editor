"""Script parser for loading and validating JSON video scripts."""

import json
from pathlib import Path
from typing import Tuple

from pydantic import ValidationError

from src.models.script import VideoScript, ProjectConfig, SceneConfig
from src.utils.logger import get_logger, print_error_panel


logger = get_logger()


def load_script(script_path: Path) -> VideoScript:
    """
    Load and validate video script from JSON file.

    Args:
        script_path: Path to JSON script file

    Returns:
        Validated VideoScript instance

    Raises:
        FileNotFoundError: If script file doesn't exist
        ValueError: If JSON is invalid or doesn't match schema
    """
    logger.info(f"Loading script from: {script_path}")

    # Check if file exists
    if not script_path.exists():
        error_msg = f"Script file not found: {script_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Check if it's a file (not a directory)
    if not script_path.is_file():
        error_msg = f"Path is not a file: {script_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Read and parse JSON
        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)

        logger.debug(f"Successfully parsed JSON from {script_path}")

        # Validate using Pydantic model
        script = VideoScript(**script_data)

        logger.info(
            f"Successfully loaded script with {len(script.scenes)} scene(s), "
            f"estimated duration: {script.get_total_estimated_duration():.1f}s"
        )

        return script

    except json.JSONDecodeError as e:
        error_msg = (
            f"Invalid JSON in script file: {script_path}\n"
            f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e

    except ValidationError as e:
        # Format Pydantic validation errors into user-friendly message
        error_lines = ["Script validation failed:"]
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_lines.append(f"  • {location}: {message}")

        error_msg = "\n".join(error_lines)
        logger.error(error_msg)
        raise ValueError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error loading script from {script_path}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def validate_script_file(script_path: Path) -> Tuple[bool, str]:
    """
    Validate a script file without fully loading it.

    Args:
        script_path: Path to JSON script file

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if script is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    try:
        # Attempt to load the script
        load_script(script_path)
        return (True, "")

    except FileNotFoundError as e:
        return (False, f"File not found: {str(e)}")

    except ValueError as e:
        return (False, str(e))

    except Exception as e:
        return (False, f"Validation error: {str(e)}")


def parse_script_string(json_string: str) -> VideoScript:
    """
    Parse and validate a video script from a JSON string.

    Args:
        json_string: JSON string containing script data

    Returns:
        Validated VideoScript instance

    Raises:
        ValueError: If JSON is invalid or doesn't match schema
    """
    logger.debug("Parsing script from JSON string")

    try:
        # Parse JSON string
        script_data = json.loads(json_string)

        # Validate using Pydantic model
        script = VideoScript(**script_data)

        logger.info(
            f"Successfully parsed script with {len(script.scenes)} scene(s)"
        )

        return script

    except json.JSONDecodeError as e:
        error_msg = (
            f"Invalid JSON string\n"
            f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e

    except ValidationError as e:
        # Format Pydantic validation errors into user-friendly message
        error_lines = ["Script validation failed:"]
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_lines.append(f"  • {location}: {message}")

        error_msg = "\n".join(error_lines)
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def get_script_summary(script: VideoScript) -> dict[str, any]:
    """
    Get a summary of a video script.

    Args:
        script: VideoScript instance

    Returns:
        Dictionary containing script summary information
    """
    total_text_length = sum(len(scene.text) for scene in script.scenes)
    scenes_with_queries = sum(
        1 for scene in script.scenes if scene.video_query is not None
    )

    return {
        "total_scenes": len(script.scenes),
        "estimated_duration": script.get_total_estimated_duration(),
        "total_text_length": total_text_length,
        "scenes_with_video_queries": scenes_with_queries,
        "requires_gemini": script.requires_gemini(),
        "output_file": script.config.output_file,
        "resolution": script.config.resolution,
        "fps": script.config.fps,
        "orientation": script.config.orientation,
        "voice_id": script.config.voice_id,
    }


# Example usage for testing and documentation
if __name__ == "__main__":
    from src.utils.logger import print_success, print_error, print_info, print_table

    # Example: Create a test script file
    test_script_path = Path("test_script.json")

    test_data = {
        "scenes": [
            {
                "text": "Welcome to our video editing platform.",
                "video_query": "modern video editing software",
            },
            {
                "text": "Create amazing videos with ease.",
                "video_query": "creative workspace",
            },
        ],
        "config": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "output_file": "demo.mp4",
            "resolution": "1920x1080",
            "fps": 30,
        },
    }

    # Write test script
    with open(test_script_path, "w") as f:
        json.dump(test_data, f, indent=2)

    print_info(f"Created test script at: {test_script_path}")

    # Test validation
    is_valid, error_msg = validate_script_file(test_script_path)

    if is_valid:
        print_success("Script validation passed!")

        # Load script
        script = load_script(test_script_path)

        # Get summary
        summary = get_script_summary(script)

        # Display summary
        print_table(
            title="Script Summary",
            columns=[
                ("Property", "cyan"),
                ("Value", "green"),
            ],
            rows=[
                ["Total Scenes", str(summary["total_scenes"])],
                ["Estimated Duration", f"{summary['estimated_duration']:.1f}s"],
                ["Resolution", summary["resolution"]],
                ["FPS", str(summary["fps"])],
                ["Output File", summary["output_file"]],
                ["Requires Gemini", str(summary["requires_gemini"])],
            ],
        )
    else:
        print_error(f"Script validation failed: {error_msg}")

    # Clean up
    test_script_path.unlink()
    print_info("Cleaned up test script")
