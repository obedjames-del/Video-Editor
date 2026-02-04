"""Integration tests for Pexels video search service.

These tests make real API calls to Pexels and require a valid API key.
They use minimal queries to reduce API usage.
"""

import pytest
from pathlib import Path

from src.services.video_search import (
    VideoSearchService,
    search_videos,
    download_video,
    PexelsAPIError,
)


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_search_videos(skip_without_api_keys):
    """Test real Pexels API search with minimal query."""
    service = VideoSearchService()

    # Search with simple query
    query = "ocean"
    videos = await service.search_videos(
        query=query,
        orientation="landscape",
        per_page=3,  # Keep small to minimize API usage
    )

    # Assertions
    assert isinstance(videos, list)
    assert len(videos) > 0
    assert len(videos) <= 3

    # Check video structure
    video = videos[0]
    assert "id" in video
    assert "url" in video
    assert "duration" in video
    assert "width" in video
    assert "height" in video
    assert "video_files" in video
    assert "best_video_url" in video

    # Verify video properties
    assert isinstance(video["id"], int)
    assert video["duration"] > 0
    assert video["width"] > 0
    assert video["height"] > 0
    assert isinstance(video["video_files"], list)
    assert len(video["video_files"]) > 0
    assert video["best_video_url"].startswith("http")


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_search_different_orientations(skip_without_api_keys):
    """Test Pexels search with different orientations."""
    service = VideoSearchService()

    # Test landscape orientation
    landscape_videos = await service.search_videos(
        query="nature",
        orientation="landscape",
        per_page=2,
    )

    assert len(landscape_videos) > 0
    # Landscape videos should be wider than tall
    video = landscape_videos[0]
    assert video["width"] >= video["height"]

    # Test portrait orientation
    portrait_videos = await service.search_videos(
        query="nature",
        orientation="portrait",
        per_page=2,
    )

    assert len(portrait_videos) > 0
    # Portrait videos should be taller than wide
    video = portrait_videos[0]
    assert video["height"] >= video["width"]


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_convenience_search_function(skip_without_api_keys):
    """Test the convenience search_videos function."""
    # Use the convenience function
    videos = await search_videos(
        query="sky",
        orientation="landscape",
        per_page=2,
    )

    # Should return same structure as service method
    assert isinstance(videos, list)
    assert len(videos) > 0
    assert "id" in videos[0]
    assert "best_video_url" in videos[0]


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_download_video(skip_without_api_keys, temp_dir):
    """Test downloading a video from Pexels."""
    service = VideoSearchService()

    # First, search for a video
    videos = await service.search_videos(
        query="waves",
        orientation="landscape",
        per_page=1,
    )

    assert len(videos) > 0
    video = videos[0]
    video_url = video["best_video_url"]

    # Download the video
    output_path = temp_dir / "test_video.mp4"
    downloaded_path = await service.download_video(
        video_url=video_url,
        output_path=output_path,
    )

    # Assertions
    assert downloaded_path.exists()
    assert downloaded_path == output_path
    assert downloaded_path.suffix == ".mp4"
    assert downloaded_path.stat().st_size > 0
    assert downloaded_path.stat().st_size > 10000  # Should be at least 10KB


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_download_convenience_function(skip_without_api_keys, temp_dir):
    """Test the convenience download_video function."""
    # Search for a video first
    videos = await search_videos(query="sunset", per_page=1)
    assert len(videos) > 0

    video_url = videos[0]["best_video_url"]
    output_path = temp_dir / "convenience_test.mp4"

    # Use convenience function
    downloaded_path = await download_video(
        video_url=video_url,
        output_path=output_path,
    )

    # Verify download
    assert downloaded_path.exists()
    assert downloaded_path.stat().st_size > 0


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_search_no_results(skip_without_api_keys):
    """Test search with a query that returns no results."""
    service = VideoSearchService()

    # Use a very specific/unlikely query
    videos = await service.search_videos(
        query="xyzabc123nonexistent",
        orientation="landscape",
        per_page=5,
    )

    # Should return empty list, not error
    assert isinstance(videos, list)
    # May or may not be empty depending on Pexels' search algorithm


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_search_invalid_orientation(skip_without_api_keys):
    """Test that invalid orientation raises ValueError."""
    service = VideoSearchService()

    # Should raise ValueError for invalid orientation
    with pytest.raises(ValueError) as exc_info:
        await service.search_videos(
            query="test",
            orientation="invalid",
            per_page=5,
        )

    assert "orientation" in str(exc_info.value).lower()


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_search_invalid_per_page(skip_without_api_keys):
    """Test that invalid per_page value raises ValueError."""
    service = VideoSearchService()

    # per_page too large
    with pytest.raises(ValueError) as exc_info:
        await service.search_videos(
            query="test",
            orientation="landscape",
            per_page=100,  # Max is 80
        )

    assert "per_page" in str(exc_info.value).lower()

    # per_page too small
    with pytest.raises(ValueError) as exc_info:
        await service.search_videos(
            query="test",
            orientation="landscape",
            per_page=0,
        )

    assert "per_page" in str(exc_info.value).lower()


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_video_metadata_complete(skip_without_api_keys):
    """Test that returned video metadata has all expected fields."""
    videos = await search_videos(query="beach", per_page=1)

    assert len(videos) > 0
    video = videos[0]

    # Check all expected fields are present
    expected_fields = [
        "id",
        "url",
        "duration",
        "width",
        "height",
        "image",
        "user",
        "video_files",
        "best_video_url",
        "best_video_quality",
        "best_video_width",
        "best_video_height",
    ]

    for field in expected_fields:
        assert field in video, f"Missing field: {field}"

    # Verify types
    assert isinstance(video["id"], int)
    assert isinstance(video["url"], str)
    assert isinstance(video["duration"], (int, float))
    assert isinstance(video["width"], int)
    assert isinstance(video["height"], int)
    assert isinstance(video["video_files"], list)
    assert isinstance(video["best_video_url"], str)


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_download_invalid_url(skip_without_api_keys, temp_dir):
    """Test that downloading from invalid URL raises appropriate error."""
    service = VideoSearchService()
    output_path = temp_dir / "invalid_download.mp4"

    # Should raise PexelsAPIError for invalid URL
    with pytest.raises((PexelsAPIError, Exception)):
        await service.download_video(
            video_url="https://invalid-url-that-does-not-exist.com/video.mp4",
            output_path=output_path,
        )


@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_pexels_multiple_searches(skip_without_api_keys):
    """Test multiple consecutive searches to verify API stability."""
    service = VideoSearchService()

    queries = ["mountain", "forest", "river"]

    for query in queries:
        videos = await service.search_videos(
            query=query,
            orientation="landscape",
            per_page=2,
        )

        assert isinstance(videos, list)
        assert len(videos) > 0
        assert "id" in videos[0]
        assert "best_video_url" in videos[0]
