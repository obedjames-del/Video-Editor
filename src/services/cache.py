"""Cache management service for videos and audio files."""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any
from datetime import datetime

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger()


class CacheManager:
    """Manages cached videos and audio files with metadata tracking."""

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage. If None, uses settings.
        """
        settings = get_settings()
        self.cache_dir = cache_dir or settings.cache_dir
        self.video_cache_dir = self.cache_dir / "videos"
        self.audio_cache_dir = self.cache_dir / "audio"
        self.metadata_file = self.cache_dir / "metadata.json"
        self.enable_cache = settings.enable_cache

        # Initialize cache directories
        self._ensure_cache_dirs()

        # Load or initialize metadata
        self.metadata = self._load_metadata()

        # Cache statistics
        self.stats = {
            "video_hits": 0,
            "video_misses": 0,
            "audio_hits": 0,
            "audio_misses": 0,
        }

        logger.debug(f"CacheManager initialized with cache_dir: {self.cache_dir}")

    def _ensure_cache_dirs(self) -> None:
        """Create cache directories if they don't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.video_cache_dir.mkdir(exist_ok=True)
            self.audio_cache_dir.mkdir(exist_ok=True)
            logger.debug("Cache directories verified")
        except Exception as e:
            logger.error(f"Failed to create cache directories: {e}")
            raise

    def _load_metadata(self) -> dict[str, Any]:
        """
        Load metadata from cache/metadata.json.

        Returns:
            Metadata dictionary
        """
        if not self.metadata_file.exists():
            logger.debug("No metadata file found, creating new one")
            return {"videos": {}, "audio": {}, "stats": {}}

        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                logger.debug(f"Loaded metadata with {len(metadata.get('videos', {}))} videos, {len(metadata.get('audio', {}))} audio files")
                return metadata
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {"videos": {}, "audio": {}, "stats": {}}

    def _save_metadata(self) -> None:
        """Save metadata to cache/metadata.json."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.debug("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise

    def get_cache_key(self, content: str) -> str:
        """
        Generate cache key from content hash using SHA256.

        Args:
            content: Content to hash (query, text, etc.)

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_cached_video(self, query: str) -> Path | None:
        """
        Get cached video path for query.

        Args:
            query: Search query to look up

        Returns:
            Path to cached video if exists, None otherwise
        """
        if not self.enable_cache:
            logger.debug("Cache disabled, skipping video cache lookup")
            return None

        cache_key = self.get_cache_key(query)
        video_metadata = self.metadata.get("videos", {}).get(cache_key)

        if video_metadata:
            video_path = Path(video_metadata["path"])
            if video_path.exists():
                self.stats["video_hits"] += 1
                logger.info(f"Cache HIT for video query: {query[:50]}...")

                # Update last accessed time
                self.metadata["videos"][cache_key]["last_accessed"] = datetime.now().isoformat()
                self._save_metadata()

                return video_path
            else:
                # File referenced in metadata but doesn't exist
                logger.warning(f"Cached video file missing: {video_path}")
                del self.metadata["videos"][cache_key]
                self._save_metadata()

        self.stats["video_misses"] += 1
        logger.debug(f"Cache MISS for video query: {query[:50]}...")
        return None

    def cache_video(self, query: str, video_path: Path) -> Path:
        """
        Save video to cache.

        Args:
            query: Search query to cache
            video_path: Path to video file to cache

        Returns:
            Path to cached video file

        Raises:
            FileNotFoundError: If video_path doesn't exist
            IOError: If copy operation fails
        """
        if not self.enable_cache:
            logger.debug("Cache disabled, skipping video caching")
            return video_path

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cache_key = self.get_cache_key(query)
        cached_video_path = self.video_cache_dir / f"{cache_key}{video_path.suffix}"

        try:
            # Copy video to cache
            shutil.copy2(video_path, cached_video_path)
            logger.info(f"Cached video: {cached_video_path.name}")

            # Save metadata
            self.metadata.setdefault("videos", {})
            self.metadata["videos"][cache_key] = {
                "query": query,
                "path": str(cached_video_path),
                "original_name": video_path.name,
                "size_bytes": cached_video_path.stat().st_size,
                "cached_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
            }
            self._save_metadata()

            return cached_video_path

        except Exception as e:
            logger.error(f"Failed to cache video: {e}")
            raise IOError(f"Failed to cache video: {e}") from e

    def get_cached_audio(self, text: str, voice_id: str) -> Path | None:
        """
        Get cached audio path for text and voice combination.

        Args:
            text: Text content
            voice_id: ElevenLabs voice ID

        Returns:
            Path to cached audio if exists, None otherwise
        """
        if not self.enable_cache:
            logger.debug("Cache disabled, skipping audio cache lookup")
            return None

        # Create combined cache key from text and voice_id
        cache_content = f"{text}|{voice_id}"
        cache_key = self.get_cache_key(cache_content)
        audio_metadata = self.metadata.get("audio", {}).get(cache_key)

        if audio_metadata:
            audio_path = Path(audio_metadata["path"])
            if audio_path.exists():
                self.stats["audio_hits"] += 1
                logger.info(f"Cache HIT for audio: {text[:50]}... (voice: {voice_id})")

                # Update last accessed time
                self.metadata["audio"][cache_key]["last_accessed"] = datetime.now().isoformat()
                self._save_metadata()

                return audio_path
            else:
                # File referenced in metadata but doesn't exist
                logger.warning(f"Cached audio file missing: {audio_path}")
                del self.metadata["audio"][cache_key]
                self._save_metadata()

        self.stats["audio_misses"] += 1
        logger.debug(f"Cache MISS for audio: {text[:50]}... (voice: {voice_id})")
        return None

    def cache_audio(self, text: str, voice_id: str, audio_path: Path) -> Path:
        """
        Save audio to cache.

        Args:
            text: Text content
            voice_id: ElevenLabs voice ID
            audio_path: Path to audio file to cache

        Returns:
            Path to cached audio file

        Raises:
            FileNotFoundError: If audio_path doesn't exist
            IOError: If copy operation fails
        """
        if not self.enable_cache:
            logger.debug("Cache disabled, skipping audio caching")
            return audio_path

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Create combined cache key from text and voice_id
        cache_content = f"{text}|{voice_id}"
        cache_key = self.get_cache_key(cache_content)
        cached_audio_path = self.audio_cache_dir / f"{cache_key}{audio_path.suffix}"

        try:
            # Copy audio to cache
            shutil.copy2(audio_path, cached_audio_path)
            logger.info(f"Cached audio: {cached_audio_path.name}")

            # Save metadata
            self.metadata.setdefault("audio", {})
            self.metadata["audio"][cache_key] = {
                "text": text[:100],  # Store truncated text for reference
                "text_hash": cache_key,
                "voice_id": voice_id,
                "path": str(cached_audio_path),
                "original_name": audio_path.name,
                "size_bytes": cached_audio_path.stat().st_size,
                "cached_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
            }
            self._save_metadata()

            return cached_audio_path

        except Exception as e:
            logger.error(f"Failed to cache audio: {e}")
            raise IOError(f"Failed to cache audio: {e}") from e

    def is_video_cached(self, query: str) -> bool:
        """
        Check if video exists in cache.

        Args:
            query: Search query

        Returns:
            True if cached video exists, False otherwise
        """
        return self.get_cached_video(query) is not None

    def is_audio_cached(self, text: str, voice_id: str) -> bool:
        """
        Check if audio exists in cache.

        Args:
            text: Text content
            voice_id: ElevenLabs voice ID

        Returns:
            True if cached audio exists, False otherwise
        """
        return self.get_cached_audio(text, voice_id) is not None

    def clear_cache(self) -> None:
        """
        Clear all cached files and reset metadata.

        This will delete all cached videos and audio files.
        """
        try:
            # Remove all cached videos
            if self.video_cache_dir.exists():
                for file in self.video_cache_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                logger.info(f"Cleared video cache: {self.video_cache_dir}")

            # Remove all cached audio
            if self.audio_cache_dir.exists():
                for file in self.audio_cache_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                logger.info(f"Cleared audio cache: {self.audio_cache_dir}")

            # Reset metadata
            self.metadata = {"videos": {}, "audio": {}, "stats": {}}
            self._save_metadata()

            # Reset statistics
            self.stats = {
                "video_hits": 0,
                "video_misses": 0,
                "audio_hits": 0,
                "audio_misses": 0,
            }

            logger.info("Cache cleared successfully")

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics including hit rates and storage info.

        Returns:
            Dictionary containing cache statistics
        """
        # Calculate cache sizes
        video_size = sum(
            Path(meta["path"]).stat().st_size
            for meta in self.metadata.get("videos", {}).values()
            if Path(meta["path"]).exists()
        )
        audio_size = sum(
            Path(meta["path"]).stat().st_size
            for meta in self.metadata.get("audio", {}).values()
            if Path(meta["path"]).exists()
        )

        # Calculate hit rates
        total_video_requests = self.stats["video_hits"] + self.stats["video_misses"]
        total_audio_requests = self.stats["audio_hits"] + self.stats["audio_misses"]

        video_hit_rate = (
            (self.stats["video_hits"] / total_video_requests * 100)
            if total_video_requests > 0
            else 0.0
        )
        audio_hit_rate = (
            (self.stats["audio_hits"] / total_audio_requests * 100)
            if total_audio_requests > 0
            else 0.0
        )

        return {
            "enabled": self.enable_cache,
            "cache_dir": str(self.cache_dir),
            "videos": {
                "count": len(self.metadata.get("videos", {})),
                "size_mb": round(video_size / (1024 * 1024), 2),
                "hits": self.stats["video_hits"],
                "misses": self.stats["video_misses"],
                "hit_rate": round(video_hit_rate, 2),
            },
            "audio": {
                "count": len(self.metadata.get("audio", {})),
                "size_mb": round(audio_size / (1024 * 1024), 2),
                "hits": self.stats["audio_hits"],
                "misses": self.stats["audio_misses"],
                "hit_rate": round(audio_hit_rate, 2),
            },
            "total_size_mb": round((video_size + audio_size) / (1024 * 1024), 2),
        }

    def cleanup_old_cache(self, max_age_days: int = 30) -> int:
        """
        Remove cache entries older than specified days.

        Args:
            max_age_days: Maximum age in days for cache entries

        Returns:
            Number of entries removed
        """
        from datetime import timedelta

        if not self.enable_cache:
            logger.debug("Cache disabled, skipping cleanup")
            return 0

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0

        try:
            # Clean old videos
            for cache_key, metadata in list(self.metadata.get("videos", {}).items()):
                last_accessed = datetime.fromisoformat(metadata.get("last_accessed", metadata.get("cached_at")))
                if last_accessed < cutoff_date:
                    video_path = Path(metadata["path"])
                    if video_path.exists():
                        video_path.unlink()
                    del self.metadata["videos"][cache_key]
                    removed_count += 1
                    logger.debug(f"Removed old cached video: {cache_key}")

            # Clean old audio
            for cache_key, metadata in list(self.metadata.get("audio", {}).items()):
                last_accessed = datetime.fromisoformat(metadata.get("last_accessed", metadata.get("cached_at")))
                if last_accessed < cutoff_date:
                    audio_path = Path(metadata["path"])
                    if audio_path.exists():
                        audio_path.unlink()
                    del self.metadata["audio"][cache_key]
                    removed_count += 1
                    logger.debug(f"Removed old cached audio: {cache_key}")

            if removed_count > 0:
                self._save_metadata()
                logger.info(f"Cleaned up {removed_count} old cache entries (older than {max_age_days} days)")

            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup old cache: {e}")
            raise


# Global cache manager instance
_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.

    Returns:
        CacheManager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def reset_cache_manager() -> None:
    """Reset the global cache manager instance (mainly for testing)."""
    global _cache_manager
    _cache_manager = None
