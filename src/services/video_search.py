"""Pexels video search and download service."""

import asyncio
from pathlib import Path
from typing import Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.utils.config import get_settings
from src.utils.logger import get_logger, print_api_error


logger = get_logger()


class PexelsAPIError(Exception):
    """Custom exception for Pexels API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Pexels API Error {status_code}: {message}")


class VideoSearchService:
    """Service for searching and downloading videos from Pexels."""

    def __init__(self):
        """Initialize the video search service."""
        self.settings = get_settings()
        self.api_key = self.settings.pexels_api_key
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {"Authorization": self.api_key}
        self.timeout = self.settings.api_timeout

    async def search_videos(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
    ) -> list[dict]:
        """
        Search Pexels for videos matching the query.

        Args:
            query: Search query string
            orientation: Video orientation (landscape/portrait/square)
            per_page: Number of results to return (max 80)

        Returns:
            List of video metadata dictionaries containing:
            - id: Video ID
            - url: Pexels video page URL
            - duration: Video duration in seconds
            - width: Video width
            - height: Video height
            - video_files: List of video file URLs with different qualities

        Raises:
            PexelsAPIError: If the API request fails
            ValueError: If parameters are invalid
        """
        # Validate orientation
        valid_orientations = ["landscape", "portrait", "square"]
        if orientation not in valid_orientations:
            raise ValueError(
                f"Invalid orientation: {orientation}. "
                f"Must be one of {valid_orientations}"
            )

        # Validate per_page
        if not 1 <= per_page <= 80:
            raise ValueError("per_page must be between 1 and 80")

        logger.info(
            f"Searching Pexels for videos: query='{query}', "
            f"orientation={orientation}, per_page={per_page}"
        )

        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
            "size": "medium",  # medium quality for better balance
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params=params,
                )

                # Handle error responses
                if response.status_code != 200:
                    error_message = self._parse_error_response(response)
                    print_api_error("Pexels", response.status_code, error_message)
                    raise PexelsAPIError(response.status_code, error_message)

                data = response.json()
                videos = data.get("videos", [])

                logger.info(f"Found {len(videos)} videos for query '{query}'")

                # Parse and return video metadata
                return self._parse_video_results(videos)

        except httpx.TimeoutException as e:
            logger.error(f"Pexels API request timed out: {e}")
            raise PexelsAPIError(
                408, f"Request timed out after {self.timeout}s"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Pexels API request failed: {e}")
            raise PexelsAPIError(0, f"Request failed: {str(e)}") from e

    def _parse_error_response(self, response: httpx.Response) -> str:
        """
        Parse error response from Pexels API.

        Args:
            response: HTTP response object

        Returns:
            Error message string
        """
        try:
            error_data = response.json()
            return error_data.get("error", response.text)
        except Exception:
            return response.text or "Unknown error"

    def _parse_video_results(self, videos: list[dict]) -> list[dict]:
        """
        Parse video results from Pexels API response.

        Args:
            videos: List of video data from API

        Returns:
            List of parsed video metadata dictionaries
        """
        parsed_videos = []

        for video in videos:
            # Get the best quality video file
            video_files = video.get("video_files", [])
            if not video_files:
                logger.warning(f"Video {video.get('id')} has no video files")
                continue

            # Sort by quality (prefer HD)
            video_files_sorted = sorted(
                video_files,
                key=lambda x: (x.get("width", 0), x.get("height", 0)),
                reverse=True,
            )

            # Get HD or best available quality
            best_file = video_files_sorted[0] if video_files_sorted else None
            if not best_file:
                continue

            parsed_videos.append({
                "id": video.get("id"),
                "url": video.get("url"),
                "duration": video.get("duration", 0),
                "width": video.get("width", 0),
                "height": video.get("height", 0),
                "image": video.get("image"),  # Thumbnail image
                "user": video.get("user", {}).get("name"),
                "video_files": video_files_sorted,  # All quality options
                "best_video_url": best_file.get("link"),
                "best_video_quality": best_file.get("quality"),
                "best_video_width": best_file.get("width"),
                "best_video_height": best_file.get("height"),
            })

        return parsed_videos

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.RequestError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def download_video(
        self,
        video_url: str,
        output_path: Path,
    ) -> Path:
        """
        Download a video file from a URL using streaming.

        Args:
            video_url: URL of the video to download
            output_path: Path where the video should be saved

        Returns:
            Path to the downloaded video file

        Raises:
            PexelsAPIError: If the download fails
            ValueError: If parameters are invalid
        """
        if not video_url:
            raise ValueError("video_url cannot be empty")

        if not output_path:
            raise ValueError("output_path cannot be empty")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading video from {video_url}")
        logger.debug(f"Output path: {output_path}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout * 3) as client:
                # Stream the download for large files
                async with client.stream("GET", video_url) as response:
                    if response.status_code != 200:
                        error_msg = f"Failed to download video: HTTP {response.status_code}"
                        logger.error(error_msg)
                        raise PexelsAPIError(response.status_code, error_msg)

                    # Get content length for progress tracking
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded_size = 0

                    # Stream download to file
                    with open(output_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # Log progress for large files
                            if total_size > 0 and downloaded_size % (1024 * 1024) == 0:
                                progress = (downloaded_size / total_size) * 100
                                logger.debug(
                                    f"Download progress: {progress:.1f}% "
                                    f"({downloaded_size / (1024*1024):.1f}MB / "
                                    f"{total_size / (1024*1024):.1f}MB)"
                                )

                    file_size_mb = output_path.stat().st_size / (1024 * 1024)
                    logger.info(
                        f"Successfully downloaded video: {output_path.name} "
                        f"({file_size_mb:.2f}MB)"
                    )

                    # Check file size against max limit
                    if file_size_mb > self.settings.max_video_size_mb:
                        logger.warning(
                            f"Downloaded video ({file_size_mb:.2f}MB) exceeds "
                            f"max size limit ({self.settings.max_video_size_mb}MB)"
                        )

                    return output_path

        except httpx.TimeoutException as e:
            logger.error(f"Video download timed out: {e}")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise PexelsAPIError(
                408, f"Download timed out after {self.timeout * 3}s"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Video download failed: {e}")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise PexelsAPIError(0, f"Download failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise


# Convenience functions for direct use
async def search_videos(
    query: str,
    orientation: str = "landscape",
    per_page: int = 5,
) -> list[dict]:
    """
    Search Pexels for videos matching the query.

    This is a convenience function that creates a VideoSearchService instance
    and calls its search_videos method.

    Args:
        query: Search query string
        orientation: Video orientation (landscape/portrait/square)
        per_page: Number of results to return (max 80)

    Returns:
        List of video metadata dictionaries

    Raises:
        PexelsAPIError: If the API request fails
        ValueError: If parameters are invalid
    """
    service = VideoSearchService()
    return await service.search_videos(query, orientation, per_page)


async def download_video(
    video_url: str,
    output_path: Path,
) -> Path:
    """
    Download a video file from a URL.

    This is a convenience function that creates a VideoSearchService instance
    and calls its download_video method.

    Args:
        video_url: URL of the video to download
        output_path: Path where the video should be saved

    Returns:
        Path to the downloaded video file

    Raises:
        PexelsAPIError: If the download fails
        ValueError: If parameters are invalid
    """
    service = VideoSearchService()
    return await service.download_video(video_url, output_path)


async def search_and_download_videos(
    query: str,
    orientation: str = "landscape",
    per_page: int = 5,
    download_all: bool = False,
) -> list[dict[str, Any]]:
    """
    Search for videos and optionally download them.

    Args:
        query: Search query string
        orientation: Video orientation (landscape/portrait/square)
        per_page: Number of results to return
        download_all: If True, download all found videos

    Returns:
        List of video metadata with download paths (if downloaded)

    Raises:
        PexelsAPIError: If the API request or download fails
    """
    service = VideoSearchService()
    settings = get_settings()

    # Search for videos
    videos = await service.search_videos(query, orientation, per_page)

    if not videos:
        logger.warning(f"No videos found for query: {query}")
        return []

    # Download videos if requested
    if download_all:
        logger.info(f"Downloading {len(videos)} videos...")

        # Create cache directory
        cache_dir = settings.cache_dir / "videos"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Download videos concurrently with semaphore for rate limiting
        semaphore = asyncio.Semaphore(settings.max_parallel_downloads)

        async def download_with_limit(video: dict, index: int) -> dict:
            async with semaphore:
                try:
                    # Generate filename from video ID and index
                    video_id = video.get("id", index)
                    output_path = cache_dir / f"{query.replace(' ', '_')}_{video_id}.mp4"

                    # Download the best quality video
                    video_url = video.get("best_video_url")
                    if not video_url:
                        logger.warning(f"No video URL found for video {video_id}")
                        return video

                    downloaded_path = await service.download_video(
                        video_url, output_path
                    )

                    # Add download info to video metadata
                    video["downloaded_path"] = str(downloaded_path)
                    video["file_size_mb"] = downloaded_path.stat().st_size / (1024 * 1024)

                    return video

                except Exception as e:
                    logger.error(f"Failed to download video {video.get('id')}: {e}")
                    video["download_error"] = str(e)
                    return video

        # Download all videos concurrently
        download_tasks = [
            download_with_limit(video, idx) for idx, video in enumerate(videos)
        ]
        videos = await asyncio.gather(*download_tasks)

        successful_downloads = sum(
            1 for v in videos if "downloaded_path" in v
        )
        logger.info(
            f"Successfully downloaded {successful_downloads}/{len(videos)} videos"
        )

    return videos
