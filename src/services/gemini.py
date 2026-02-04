"""Gemini AI integration service for video query generation."""

import json
from typing import Any

import google.generativeai as genai

from src.utils.config import get_settings
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger()

# Global Gemini model instance
_model: genai.GenerativeModel | None = None


def _get_model() -> genai.GenerativeModel:
    """
    Get or initialize the Gemini model.

    Returns:
        Configured GenerativeModel instance
    """
    global _model

    if _model is None:
        settings = get_settings()

        # Configure Gemini API
        genai.configure(api_key=settings.gemini_api_key)

        # Initialize model with JSON response mode
        _model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )

        logger.info(f"Initialized Gemini model: {settings.gemini_model}")

    return _model


def _parse_gemini_response(response_text: str, expected_count: int) -> list[str]:
    """
    Parse JSON response from Gemini and extract video queries.

    Args:
        response_text: Raw JSON response from Gemini
        expected_count: Expected number of queries

    Returns:
        List of video search queries

    Raises:
        ValueError: If response format is invalid
    """
    try:
        data = json.loads(response_text)

        # Handle different possible response formats
        if isinstance(data, dict):
            # Try to extract queries from common keys
            if "queries" in data:
                queries = data["queries"]
            elif "video_queries" in data:
                queries = data["video_queries"]
            elif "search_queries" in data:
                queries = data["search_queries"]
            else:
                # If it's a dict with scene keys, extract values
                queries = list(data.values())
        elif isinstance(data, list):
            queries = data
        else:
            raise ValueError(f"Unexpected response format: {type(data)}")

        # Validate we got the right number of queries
        if len(queries) != expected_count:
            logger.warning(
                f"Expected {expected_count} queries but got {len(queries)}, "
                f"will pad or truncate"
            )

            # Pad with generic queries if too few
            while len(queries) < expected_count:
                queries.append("stock video footage")

            # Truncate if too many
            queries = queries[:expected_count]

        # Ensure all queries are strings
        queries = [str(q).strip() for q in queries]

        return queries

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}") from e
    except Exception as e:
        logger.error(f"Error parsing Gemini response: {e}")
        raise ValueError(f"Failed to parse Gemini response: {e}") from e


async def generate_video_queries(
    scenes_text: list[str],
) -> list[str]:
    """
    Analyze scene text and generate optimal Pexels video search queries.

    This function uses Google's Gemini 2.0 Flash model to analyze each scene's
    voiceover text and generate 2-4 keyword search queries that would find
    appropriate stock video footage on Pexels.

    Args:
        scenes_text: List of scene voiceover text

    Returns:
        List of video search queries (same length as input)

    Raises:
        ValueError: If API key is invalid or response format is unexpected
        RuntimeError: If Gemini API request fails
    """
    if not scenes_text:
        logger.warning("Empty scenes_text provided to generate_video_queries")
        return []

    settings = get_settings()
    scene_count = len(scenes_text)

    logger.info(f"Generating video queries for {scene_count} scenes using Gemini")

    # Build the prompt for Gemini
    prompt = _build_prompt(scenes_text)

    try:
        # Get the model instance
        model = _get_model()

        # Generate content with retry logic
        max_retries = settings.api_max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"Gemini API request attempt {attempt + 1}/{max_retries}")

                # Make the API call
                response = model.generate_content(prompt)

                # Check if response was blocked or empty
                if not response.text:
                    if hasattr(response, 'prompt_feedback'):
                        logger.error(
                            f"Gemini blocked the request: {response.prompt_feedback}"
                        )
                        raise RuntimeError(
                            f"Gemini blocked the request: {response.prompt_feedback}"
                        )
                    raise RuntimeError("Empty response from Gemini")

                # Parse the response
                queries = _parse_gemini_response(response.text, scene_count)

                logger.info(f"Successfully generated {len(queries)} video queries")
                logger.debug(f"Generated queries: {queries}")

                return queries

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Gemini API attempt {attempt + 1} failed: {e}, retrying..."
                    )
                    continue
                break

        # If we get here, all retries failed
        logger.error(f"All Gemini API attempts failed: {last_error}")
        raise RuntimeError(
            f"Failed to generate video queries after {max_retries} attempts: {last_error}"
        ) from last_error

    except Exception as e:
        logger.error(f"Error in generate_video_queries: {e}")

        # Return fallback queries based on scene text
        logger.warning("Returning fallback queries due to Gemini API error")
        return _generate_fallback_queries(scenes_text)


def _build_prompt(scenes_text: list[str]) -> str:
    """
    Build the prompt for Gemini to analyze scenes and generate queries.

    Args:
        scenes_text: List of scene voiceover text

    Returns:
        Formatted prompt string
    """
    # Format scenes for the prompt
    scenes_formatted = "\n".join(
        f"Scene {i+1}: {text}"
        for i, text in enumerate(scenes_text)
    )

    prompt = f"""You are a video search expert. Analyze each scene's voiceover text and generate optimal search queries for finding stock video footage on Pexels.

For each scene, create a concise search query with 2-4 keywords that will find the most relevant and visually appealing stock video footage.

Guidelines:
- Keep queries simple and focused on visual elements
- Use concrete, searchable terms (avoid abstract concepts)
- Consider the mood, setting, and key subjects mentioned
- Prioritize action verbs and specific nouns
- Make queries generic enough to find stock footage

Scenes to analyze:
{scenes_formatted}

Return a JSON object with a "queries" key containing an array of {len(scenes_text)} search query strings, one for each scene in order.

Example format:
{{
  "queries": [
    "city traffic time lapse",
    "person working laptop coffee shop",
    "sunset ocean waves"
  ]
}}"""

    return prompt


def _generate_fallback_queries(scenes_text: list[str]) -> list[str]:
    """
    Generate basic fallback queries when Gemini API fails.

    This extracts key nouns and verbs from the scene text as a simple
    fallback mechanism.

    Args:
        scenes_text: List of scene voiceover text

    Returns:
        List of basic search queries
    """
    queries = []

    for text in scenes_text:
        # Simple keyword extraction: take first few words
        words = text.lower().split()

        # Filter out common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }

        keywords = [w for w in words if w not in stop_words and len(w) > 2][:4]

        # Create query from keywords
        if keywords:
            query = " ".join(keywords)
        else:
            query = "stock video footage"

        queries.append(query)

    logger.debug(f"Generated fallback queries: {queries}")
    return queries


def reset_model() -> None:
    """Reset the global model instance (mainly for testing)."""
    global _model
    _model = None
