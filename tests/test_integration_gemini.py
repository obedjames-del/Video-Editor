"""Integration tests for Gemini AI service.

These tests make real API calls to Google Gemini and require a valid API key.
They use minimal inputs to reduce API usage and costs.
"""

import pytest

from src.services.gemini import (
    generate_video_queries,
    reset_model,
)


@pytest.fixture(autouse=True)
def reset_gemini_model():
    """Reset Gemini model before each test."""
    reset_model()
    yield
    reset_model()


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_generates_queries(skip_without_api_keys):
    """Test real Gemini API call with minimal scene list."""
    # Use short scene text to minimize API usage
    scenes_text = [
        "Welcome to the product.",
        "Amazing features included.",
    ]

    # Generate queries
    queries = await generate_video_queries(scenes_text)

    # Assertions
    assert isinstance(queries, list)
    assert len(queries) == len(scenes_text)

    # Each query should be a non-empty string
    for query in queries:
        assert isinstance(query, str)
        assert len(query) > 0
        assert len(query.strip()) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_single_scene(skip_without_api_keys):
    """Test Gemini with a single scene."""
    scenes_text = ["Technology innovation"]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 1
    assert isinstance(queries[0], str)
    assert len(queries[0]) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_multiple_scenes(skip_without_api_keys):
    """Test Gemini with multiple scenes."""
    scenes_text = [
        "The city comes alive at night.",
        "People working in modern offices.",
        "Nature and wildlife in harmony.",
    ]

    queries = await generate_video_queries(scenes_text)

    # Should return exactly the same number of queries as scenes
    assert len(queries) == len(scenes_text)

    # All queries should be strings
    for i, query in enumerate(queries):
        assert isinstance(query, str)
        assert len(query) > 0
        # Queries should be reasonably short (typical search query length)
        assert len(query) < 200


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_query_quality(skip_without_api_keys):
    """Test that Gemini generates relevant queries."""
    scenes_text = [
        "A beautiful sunset over the ocean waves.",
        "An athlete running on a mountain trail.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 2

    # First query should be related to ocean/sunset
    query1_lower = queries[0].lower()
    # Should contain relevant keywords (at least one)
    relevant_keywords_1 = ["sunset", "ocean", "sea", "beach", "water", "waves", "sky"]
    assert any(keyword in query1_lower for keyword in relevant_keywords_1)

    # Second query should be related to running/athlete/mountain
    query2_lower = queries[1].lower()
    relevant_keywords_2 = ["run", "athlete", "mountain", "trail", "sport", "fitness", "outdoor"]
    assert any(keyword in query2_lower for keyword in relevant_keywords_2)


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_handles_short_text(skip_without_api_keys):
    """Test Gemini with very short scene text."""
    scenes_text = [
        "Hello",
        "Goodbye",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 2
    for query in queries:
        assert isinstance(query, str)
        assert len(query) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_handles_descriptive_text(skip_without_api_keys):
    """Test Gemini with more descriptive scene text."""
    scenes_text = [
        "Transform your workflow with cutting-edge technology and innovative solutions.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 1
    query = queries[0]

    # Should generate a focused search query (not copy the entire text)
    assert isinstance(query, str)
    assert len(query) > 0
    # Query should be shorter than input (condensed for search)
    assert len(query) < len(scenes_text[0])


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_consistency(skip_without_api_keys):
    """Test that Gemini returns consistent structure across calls."""
    scenes_text = ["Technology", "Innovation"]

    # Make two calls with same input
    queries1 = await generate_video_queries(scenes_text)
    queries2 = await generate_video_queries(scenes_text)

    # Both should return same structure
    assert len(queries1) == len(scenes_text)
    assert len(queries2) == len(scenes_text)

    # All should be strings
    for q in queries1 + queries2:
        assert isinstance(q, str)
        assert len(q) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_empty_scene_list(skip_without_api_keys):
    """Test Gemini with empty scene list."""
    scenes_text = []

    queries = await generate_video_queries(scenes_text)

    # Should return empty list for empty input
    assert isinstance(queries, list)
    assert len(queries) == 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_special_characters(skip_without_api_keys):
    """Test Gemini with special characters in scene text."""
    scenes_text = [
        "Amazing! Transform today.",
        "Question? Yes, absolutely.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 2
    for query in queries:
        assert isinstance(query, str)
        assert len(query) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_numeric_text(skip_without_api_keys):
    """Test Gemini with numeric content in scene text."""
    scenes_text = [
        "Save 50% today with our special offer.",
        "Over 1000 satisfied customers worldwide.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 2
    for query in queries:
        assert isinstance(query, str)
        assert len(query) > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_diverse_topics(skip_without_api_keys):
    """Test Gemini with diverse scene topics."""
    scenes_text = [
        "Cooking delicious food in the kitchen.",
        "Space exploration and the universe.",
        "Financial growth and investment success.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 3

    # Check that queries are topic-appropriate
    # Query 1 should relate to cooking/food
    assert any(
        keyword in queries[0].lower()
        for keyword in ["cook", "food", "kitchen", "chef", "culinary"]
    )

    # Query 2 should relate to space
    assert any(
        keyword in queries[1].lower()
        for keyword in ["space", "universe", "star", "planet", "cosmos", "galaxy", "astronaut"]
    )

    # Query 3 should relate to finance/business
    assert any(
        keyword in queries[2].lower()
        for keyword in ["finance", "business", "investment", "money", "growth", "success"]
    )


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_query_length_reasonable(skip_without_api_keys):
    """Test that generated queries have reasonable length for search."""
    scenes_text = [
        "An entrepreneur working late at night in a modern startup office, "
        "surrounded by computers and innovative technology, drinking coffee "
        "and focused on building the future.",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 1
    query = queries[0]

    # Query should be shorter than input (condensed)
    assert len(query) < len(scenes_text[0])

    # Query should be reasonable search length (typically 2-6 words)
    # Split by spaces to count words
    words = query.split()
    assert 1 <= len(words) <= 10  # Reasonable search query word count


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_gemini_maintains_order(skip_without_api_keys):
    """Test that Gemini returns queries in the same order as scenes."""
    scenes_text = [
        "First scene about nature",
        "Second scene about technology",
        "Third scene about people",
    ]

    queries = await generate_video_queries(scenes_text)

    assert len(queries) == 3

    # Query order should match scene order
    # First query should relate to nature
    assert any(
        keyword in queries[0].lower()
        for keyword in ["nature", "forest", "tree", "wildlife", "outdoor", "landscape"]
    )

    # Second query should relate to technology
    assert any(
        keyword in queries[1].lower()
        for keyword in ["technology", "tech", "computer", "digital", "innovation"]
    )

    # Third query should relate to people
    assert any(
        keyword in queries[2].lower()
        for keyword in ["people", "person", "human", "group", "crowd", "team"]
    )
