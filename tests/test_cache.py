"""Unit tests for cache management service."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.services.cache import CacheManager, get_cache_manager, reset_cache_manager


@pytest.mark.unit
class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_get_cache_key_generates_consistent_hash(self, temp_dir):
        """Test that cache key generation is consistent for same input."""
        cache_mgr = CacheManager(temp_dir)

        key1 = cache_mgr.get_cache_key("ocean sunset")
        key2 = cache_mgr.get_cache_key("ocean sunset")

        assert key1 == key2
        assert len(key1) == 64  # SHA256 produces 64 hex characters

    def test_get_cache_key_different_for_different_inputs(self, temp_dir):
        """Test that different inputs produce different cache keys."""
        cache_mgr = CacheManager(temp_dir)

        key1 = cache_mgr.get_cache_key("ocean sunset")
        key2 = cache_mgr.get_cache_key("mountain sunrise")

        assert key1 != key2

    def test_get_cache_key_handles_special_characters(self, temp_dir):
        """Test cache key generation with special characters."""
        cache_mgr = CacheManager(temp_dir)

        key = cache_mgr.get_cache_key("café ☕ with emojis 🎉")
        assert len(key) == 64
        assert isinstance(key, str)

    def test_get_cache_key_handles_empty_string(self, temp_dir):
        """Test cache key generation with empty string."""
        cache_mgr = CacheManager(temp_dir)

        key = cache_mgr.get_cache_key("")
        assert len(key) == 64

    def test_get_cache_key_is_hexadecimal(self, temp_dir):
        """Test that cache key is valid hexadecimal."""
        cache_mgr = CacheManager(temp_dir)

        key = cache_mgr.get_cache_key("test content")
        # Should not raise ValueError
        int(key, 16)


@pytest.mark.unit
class TestVideoCaching:
    """Tests for video caching operations."""

    def test_cache_video_stores_file(self, temp_dir, sample_video_file):
        """Test caching a video file."""
        cache_mgr = CacheManager(temp_dir)

        cached_path = cache_mgr.cache_video("ocean sunset", sample_video_file)

        assert cached_path.exists()
        assert cached_path.parent == cache_mgr.video_cache_dir
        assert cached_path.suffix == sample_video_file.suffix

    def test_cache_video_creates_metadata(self, temp_dir, sample_video_file):
        """Test that caching video creates metadata entry."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)
        cache_key = cache_mgr.get_cache_key("ocean sunset")

        assert cache_key in cache_mgr.metadata["videos"]
        metadata = cache_mgr.metadata["videos"][cache_key]
        assert metadata["query"] == "ocean sunset"
        assert metadata["original_name"] == sample_video_file.name
        assert "cached_at" in metadata
        assert "last_accessed" in metadata
        assert "size_bytes" in metadata

    def test_cache_video_persists_metadata(self, temp_dir, sample_video_file):
        """Test that video metadata is persisted to disk."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)

        # Load metadata file directly
        with open(cache_mgr.metadata_file, "r") as f:
            persisted_metadata = json.load(f)

        cache_key = cache_mgr.get_cache_key("ocean sunset")
        assert cache_key in persisted_metadata["videos"]

    def test_get_cached_video_returns_existing_video(self, temp_dir, sample_video_file):
        """Test retrieving a cached video."""
        cache_mgr = CacheManager(temp_dir)

        cached_path = cache_mgr.cache_video("ocean sunset", sample_video_file)
        retrieved_path = cache_mgr.get_cached_video("ocean sunset")

        assert retrieved_path == cached_path
        assert retrieved_path.exists()

    def test_get_cached_video_returns_none_for_missing(self, temp_dir):
        """Test that getting non-existent video returns None."""
        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.get_cached_video("nonexistent video")

        assert result is None

    def test_get_cached_video_updates_last_accessed(self, temp_dir, sample_video_file):
        """Test that retrieving video updates last_accessed timestamp."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)
        cache_key = cache_mgr.get_cache_key("ocean sunset")
        original_time = cache_mgr.metadata["videos"][cache_key]["last_accessed"]

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.1)

        cache_mgr.get_cached_video("ocean sunset")
        new_time = cache_mgr.metadata["videos"][cache_key]["last_accessed"]

        assert new_time > original_time

    def test_cache_video_raises_error_for_missing_file(self, temp_dir):
        """Test that caching non-existent video raises FileNotFoundError."""
        cache_mgr = CacheManager(temp_dir)
        missing_file = temp_dir / "nonexistent.mp4"

        with pytest.raises(FileNotFoundError, match="Video file not found"):
            cache_mgr.cache_video("test query", missing_file)

    def test_is_video_cached_returns_true_for_cached(self, temp_dir, sample_video_file):
        """Test is_video_cached returns True for cached videos."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)

        assert cache_mgr.is_video_cached("ocean sunset") is True

    def test_is_video_cached_returns_false_for_missing(self, temp_dir):
        """Test is_video_cached returns False for non-cached videos."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.is_video_cached("nonexistent") is False

    def test_get_cached_video_cleans_up_missing_file(self, temp_dir, sample_video_file):
        """Test that metadata is cleaned up if cached file is missing."""
        cache_mgr = CacheManager(temp_dir)

        cached_path = cache_mgr.cache_video("ocean sunset", sample_video_file)
        cache_key = cache_mgr.get_cache_key("ocean sunset")

        # Delete the cached file
        cached_path.unlink()

        # Should detect missing file and clean up metadata
        result = cache_mgr.get_cached_video("ocean sunset")

        assert result is None
        assert cache_key not in cache_mgr.metadata["videos"]


@pytest.mark.unit
class TestAudioCaching:
    """Tests for audio caching operations."""

    def test_cache_audio_stores_file(self, temp_dir, sample_audio_file):
        """Test caching an audio file."""
        cache_mgr = CacheManager(temp_dir)
        voice_id = "test_voice_123"

        cached_path = cache_mgr.cache_audio("Hello world", voice_id, sample_audio_file)

        assert cached_path.exists()
        assert cached_path.parent == cache_mgr.audio_cache_dir
        assert cached_path.suffix == sample_audio_file.suffix

    def test_cache_audio_creates_metadata(self, temp_dir, sample_audio_file):
        """Test that caching audio creates metadata entry."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"
        voice_id = "test_voice_123"

        cache_mgr.cache_audio(text, voice_id, sample_audio_file)
        cache_content = f"{text}|{voice_id}"
        cache_key = cache_mgr.get_cache_key(cache_content)

        assert cache_key in cache_mgr.metadata["audio"]
        metadata = cache_mgr.metadata["audio"][cache_key]
        assert metadata["voice_id"] == voice_id
        assert metadata["text_hash"] == cache_key
        assert metadata["original_name"] == sample_audio_file.name
        assert "cached_at" in metadata
        assert "last_accessed" in metadata
        assert "size_bytes" in metadata

    def test_cache_audio_persists_metadata(self, temp_dir, sample_audio_file):
        """Test that audio metadata is persisted to disk."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_audio("Hello world", "voice_123", sample_audio_file)

        # Load metadata file directly
        with open(cache_mgr.metadata_file, "r") as f:
            persisted_metadata = json.load(f)

        assert len(persisted_metadata["audio"]) > 0

    def test_get_cached_audio_returns_existing_audio(self, temp_dir, sample_audio_file):
        """Test retrieving a cached audio file."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"
        voice_id = "test_voice_123"

        cached_path = cache_mgr.cache_audio(text, voice_id, sample_audio_file)
        retrieved_path = cache_mgr.get_cached_audio(text, voice_id)

        assert retrieved_path == cached_path
        assert retrieved_path.exists()

    def test_get_cached_audio_returns_none_for_missing(self, temp_dir):
        """Test that getting non-existent audio returns None."""
        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.get_cached_audio("nonexistent text", "voice_123")

        assert result is None

    def test_get_cached_audio_different_voices_different_cache(self, temp_dir, sample_audio_file):
        """Test that same text with different voices have different cache entries."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"

        # Create a second audio file
        audio_file2 = temp_dir / "test_audio2.mp3"
        audio_file2.write_bytes(b'\xff\xfb\x90\x00' + b'\x01' * 100)

        cache_mgr.cache_audio(text, "voice_1", sample_audio_file)
        cache_mgr.cache_audio(text, "voice_2", audio_file2)

        cached1 = cache_mgr.get_cached_audio(text, "voice_1")
        cached2 = cache_mgr.get_cached_audio(text, "voice_2")

        assert cached1 != cached2
        assert cached1.exists()
        assert cached2.exists()

    def test_cache_audio_raises_error_for_missing_file(self, temp_dir):
        """Test that caching non-existent audio raises FileNotFoundError."""
        cache_mgr = CacheManager(temp_dir)
        missing_file = temp_dir / "nonexistent.mp3"

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            cache_mgr.cache_audio("test text", "voice_123", missing_file)

    def test_is_audio_cached_returns_true_for_cached(self, temp_dir, sample_audio_file):
        """Test is_audio_cached returns True for cached audio."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"
        voice_id = "test_voice_123"

        cache_mgr.cache_audio(text, voice_id, sample_audio_file)

        assert cache_mgr.is_audio_cached(text, voice_id) is True

    def test_is_audio_cached_returns_false_for_missing(self, temp_dir):
        """Test is_audio_cached returns False for non-cached audio."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.is_audio_cached("nonexistent", "voice_123") is False

    def test_get_cached_audio_updates_last_accessed(self, temp_dir, sample_audio_file):
        """Test that retrieving audio updates last_accessed timestamp."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"
        voice_id = "test_voice_123"

        cache_mgr.cache_audio(text, voice_id, sample_audio_file)
        cache_content = f"{text}|{voice_id}"
        cache_key = cache_mgr.get_cache_key(cache_content)
        original_time = cache_mgr.metadata["audio"][cache_key]["last_accessed"]

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.1)

        cache_mgr.get_cached_audio(text, voice_id)
        new_time = cache_mgr.metadata["audio"][cache_key]["last_accessed"]

        assert new_time > original_time

    def test_get_cached_audio_cleans_up_missing_file(self, temp_dir, sample_audio_file):
        """Test that metadata is cleaned up if cached audio file is missing."""
        cache_mgr = CacheManager(temp_dir)
        text = "Hello world"
        voice_id = "test_voice_123"

        cached_path = cache_mgr.cache_audio(text, voice_id, sample_audio_file)
        cache_content = f"{text}|{voice_id}"
        cache_key = cache_mgr.get_cache_key(cache_content)

        # Delete the cached file
        cached_path.unlink()

        # Should detect missing file and clean up metadata
        result = cache_mgr.get_cached_audio(text, voice_id)

        assert result is None
        assert cache_key not in cache_mgr.metadata["audio"]

    def test_cache_audio_truncates_long_text_in_metadata(self, temp_dir, sample_audio_file):
        """Test that long text is truncated in metadata."""
        cache_mgr = CacheManager(temp_dir)
        long_text = "A" * 200  # Text longer than 100 characters
        voice_id = "test_voice_123"

        cache_mgr.cache_audio(long_text, voice_id, sample_audio_file)
        cache_content = f"{long_text}|{voice_id}"
        cache_key = cache_mgr.get_cache_key(cache_content)

        metadata = cache_mgr.metadata["audio"][cache_key]
        assert len(metadata["text"]) == 100  # Should be truncated


@pytest.mark.unit
class TestCacheStatistics:
    """Tests for cache hit/miss tracking and statistics."""

    def test_video_cache_hit_increments_counter(self, temp_dir, sample_video_file):
        """Test that video cache hits are tracked."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)

        assert cache_mgr.stats["video_hits"] == 0
        cache_mgr.get_cached_video("ocean sunset")
        assert cache_mgr.stats["video_hits"] == 1
        cache_mgr.get_cached_video("ocean sunset")
        assert cache_mgr.stats["video_hits"] == 2

    def test_video_cache_miss_increments_counter(self, temp_dir):
        """Test that video cache misses are tracked."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.stats["video_misses"] == 0
        cache_mgr.get_cached_video("nonexistent")
        assert cache_mgr.stats["video_misses"] == 1
        cache_mgr.get_cached_video("another nonexistent")
        assert cache_mgr.stats["video_misses"] == 2

    def test_audio_cache_hit_increments_counter(self, temp_dir, sample_audio_file):
        """Test that audio cache hits are tracked."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_audio("Hello world", "voice_123", sample_audio_file)

        assert cache_mgr.stats["audio_hits"] == 0
        cache_mgr.get_cached_audio("Hello world", "voice_123")
        assert cache_mgr.stats["audio_hits"] == 1
        cache_mgr.get_cached_audio("Hello world", "voice_123")
        assert cache_mgr.stats["audio_hits"] == 2

    def test_audio_cache_miss_increments_counter(self, temp_dir):
        """Test that audio cache misses are tracked."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.stats["audio_misses"] == 0
        cache_mgr.get_cached_audio("nonexistent", "voice_123")
        assert cache_mgr.stats["audio_misses"] == 1
        cache_mgr.get_cached_audio("another", "voice_456")
        assert cache_mgr.stats["audio_misses"] == 2

    def test_get_cache_stats_returns_complete_info(self, temp_dir, sample_video_file, sample_audio_file):
        """Test that get_cache_stats returns complete information."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("ocean sunset", sample_video_file)
        cache_mgr.cache_audio("Hello world", "voice_123", sample_audio_file)

        # Generate some hits and misses
        cache_mgr.get_cached_video("ocean sunset")  # hit
        cache_mgr.get_cached_video("nonexistent")  # miss
        cache_mgr.get_cached_audio("Hello world", "voice_123")  # hit
        cache_mgr.get_cached_audio("nonexistent", "voice_123")  # miss

        stats = cache_mgr.get_cache_stats()

        assert "enabled" in stats
        assert "cache_dir" in stats
        assert "videos" in stats
        assert "audio" in stats
        assert "total_size_mb" in stats

        assert stats["videos"]["count"] == 1
        assert stats["videos"]["hits"] == 1
        assert stats["videos"]["misses"] == 1
        assert stats["videos"]["hit_rate"] == 50.0

        assert stats["audio"]["count"] == 1
        assert stats["audio"]["hits"] == 1
        assert stats["audio"]["misses"] == 1
        assert stats["audio"]["hit_rate"] == 50.0

    def test_get_cache_stats_calculates_hit_rate(self, temp_dir, sample_video_file):
        """Test that hit rate is calculated correctly."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)

        # 3 hits, 1 miss = 75% hit rate
        cache_mgr.get_cached_video("video1")
        cache_mgr.get_cached_video("video1")
        cache_mgr.get_cached_video("video1")
        cache_mgr.get_cached_video("nonexistent")

        stats = cache_mgr.get_cache_stats()
        assert stats["videos"]["hit_rate"] == 75.0

    def test_get_cache_stats_handles_zero_requests(self, temp_dir):
        """Test that stats work with zero requests."""
        cache_mgr = CacheManager(temp_dir)

        stats = cache_mgr.get_cache_stats()

        assert stats["videos"]["hit_rate"] == 0.0
        assert stats["audio"]["hit_rate"] == 0.0

    def test_get_cache_stats_calculates_size(self, temp_dir, sample_video_file, sample_audio_file):
        """Test that cache size is calculated correctly."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)
        cache_mgr.cache_audio("audio1", "voice_123", sample_audio_file)

        stats = cache_mgr.get_cache_stats()

        # Size should be calculated (may be 0.0 for very small test files)
        assert stats["videos"]["size_mb"] >= 0
        assert stats["audio"]["size_mb"] >= 0
        assert stats["total_size_mb"] == stats["videos"]["size_mb"] + stats["audio"]["size_mb"]


@pytest.mark.unit
class TestCacheClearing:
    """Tests for cache clearing operations."""

    def test_clear_cache_removes_all_videos(self, temp_dir, sample_video_file):
        """Test that clear_cache removes all cached videos."""
        cache_mgr = CacheManager(temp_dir)

        cached_path1 = cache_mgr.cache_video("video1", sample_video_file)
        cached_path2 = cache_mgr.cache_video("video2", sample_video_file)

        assert cached_path1.exists()
        assert cached_path2.exists()

        cache_mgr.clear_cache()

        assert not cached_path1.exists()
        assert not cached_path2.exists()

    def test_clear_cache_removes_all_audio(self, temp_dir, sample_audio_file):
        """Test that clear_cache removes all cached audio."""
        cache_mgr = CacheManager(temp_dir)

        cached_path1 = cache_mgr.cache_audio("text1", "voice_123", sample_audio_file)
        cached_path2 = cache_mgr.cache_audio("text2", "voice_456", sample_audio_file)

        assert cached_path1.exists()
        assert cached_path2.exists()

        cache_mgr.clear_cache()

        assert not cached_path1.exists()
        assert not cached_path2.exists()

    def test_clear_cache_resets_metadata(self, temp_dir, sample_video_file, sample_audio_file):
        """Test that clear_cache resets metadata."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)
        cache_mgr.cache_audio("audio1", "voice_123", sample_audio_file)

        cache_mgr.clear_cache()

        assert len(cache_mgr.metadata["videos"]) == 0
        assert len(cache_mgr.metadata["audio"]) == 0

    def test_clear_cache_resets_statistics(self, temp_dir, sample_video_file):
        """Test that clear_cache resets statistics."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)
        cache_mgr.get_cached_video("video1")  # hit
        cache_mgr.get_cached_video("nonexistent")  # miss

        cache_mgr.clear_cache()

        assert cache_mgr.stats["video_hits"] == 0
        assert cache_mgr.stats["video_misses"] == 0
        assert cache_mgr.stats["audio_hits"] == 0
        assert cache_mgr.stats["audio_misses"] == 0

    def test_clear_cache_persists_empty_metadata(self, temp_dir, sample_video_file):
        """Test that cleared cache persists empty metadata."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)
        cache_mgr.clear_cache()

        # Load metadata file directly
        with open(cache_mgr.metadata_file, "r") as f:
            persisted_metadata = json.load(f)

        assert len(persisted_metadata["videos"]) == 0
        assert len(persisted_metadata["audio"]) == 0


@pytest.mark.unit
class TestMetadataPersistence:
    """Tests for metadata loading and saving."""

    def test_metadata_loads_from_file(self, temp_dir):
        """Test that metadata is loaded from existing file."""
        # Create metadata file manually
        metadata_file = temp_dir / "metadata.json"
        test_metadata = {
            "videos": {"test_key": {"query": "test"}},
            "audio": {},
            "stats": {}
        }
        with open(metadata_file, "w") as f:
            json.dump(test_metadata, f)

        cache_mgr = CacheManager(temp_dir)

        assert "test_key" in cache_mgr.metadata["videos"]
        assert cache_mgr.metadata["videos"]["test_key"]["query"] == "test"

    def test_metadata_creates_new_if_missing(self, temp_dir):
        """Test that new metadata is created if file doesn't exist."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.metadata == {"videos": {}, "audio": {}, "stats": {}}

    def test_metadata_survives_manager_recreation(self, temp_dir, sample_video_file):
        """Test that metadata persists across manager instances."""
        cache_mgr1 = CacheManager(temp_dir)
        cache_mgr1.cache_video("ocean sunset", sample_video_file)

        # Create new manager with same cache dir
        cache_mgr2 = CacheManager(temp_dir)

        assert cache_mgr2.is_video_cached("ocean sunset")

    def test_corrupted_metadata_creates_new(self, temp_dir):
        """Test that corrupted metadata file is handled gracefully."""
        metadata_file = temp_dir / "metadata.json"
        metadata_file.write_text("invalid json{[}")

        cache_mgr = CacheManager(temp_dir)

        # Should create new empty metadata
        assert cache_mgr.metadata == {"videos": {}, "audio": {}, "stats": {}}

    def test_metadata_file_created_on_initialization(self, temp_dir, sample_video_file):
        """Test that metadata file is created when first item is cached."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("video1", sample_video_file)

        assert cache_mgr.metadata_file.exists()


@pytest.mark.unit
class TestCacheDirectories:
    """Tests for cache directory initialization."""

    def test_cache_directories_created(self, temp_dir):
        """Test that cache directories are created on initialization."""
        cache_mgr = CacheManager(temp_dir)

        assert cache_mgr.cache_dir.exists()
        assert cache_mgr.video_cache_dir.exists()
        assert cache_mgr.audio_cache_dir.exists()

    def test_cache_directories_with_nested_path(self, temp_dir):
        """Test that nested cache directories are created."""
        nested_path = temp_dir / "deeply" / "nested" / "cache"

        cache_mgr = CacheManager(nested_path)

        assert nested_path.exists()
        assert cache_mgr.video_cache_dir.exists()
        assert cache_mgr.audio_cache_dir.exists()


@pytest.mark.unit
class TestCacheDisabled:
    """Tests for behavior when cache is disabled."""

    def test_cache_video_returns_original_when_disabled(self, temp_dir, sample_video_file, monkeypatch):
        """Test that caching returns original path when cache is disabled."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        from src.utils.config import reset_settings
        reset_settings()

        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.cache_video("test", sample_video_file)

        assert result == sample_video_file
        assert len(list(cache_mgr.video_cache_dir.iterdir())) == 0

    def test_get_cached_video_returns_none_when_disabled(self, temp_dir, monkeypatch):
        """Test that cache lookup returns None when disabled."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        from src.utils.config import reset_settings
        reset_settings()

        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.get_cached_video("test")

        assert result is None

    def test_cache_audio_returns_original_when_disabled(self, temp_dir, sample_audio_file, monkeypatch):
        """Test that audio caching returns original path when cache is disabled."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        from src.utils.config import reset_settings
        reset_settings()

        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.cache_audio("test", "voice_123", sample_audio_file)

        assert result == sample_audio_file
        assert len(list(cache_mgr.audio_cache_dir.iterdir())) == 0

    def test_get_cached_audio_returns_none_when_disabled(self, temp_dir, monkeypatch):
        """Test that audio cache lookup returns None when disabled."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        from src.utils.config import reset_settings
        reset_settings()

        cache_mgr = CacheManager(temp_dir)

        result = cache_mgr.get_cached_audio("test", "voice_123")

        assert result is None


@pytest.mark.unit
class TestCleanupOldCache:
    """Tests for cleanup_old_cache functionality."""

    def test_cleanup_removes_old_videos(self, temp_dir, sample_video_file, mock_settings):
        """Test that cleanup removes videos older than specified days."""
        cache_mgr = CacheManager(temp_dir)

        # Cache a video
        cache_mgr.cache_video("old video", sample_video_file)
        cache_key = cache_mgr.get_cache_key("old video")

        # Verify cache was successful
        assert cache_key in cache_mgr.metadata["videos"]

        # Manually set the last_accessed to 40 days ago
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        cache_mgr.metadata["videos"][cache_key]["last_accessed"] = old_date
        cache_mgr._save_metadata()

        # Cleanup cache older than 30 days
        removed_count = cache_mgr.cleanup_old_cache(max_age_days=30)

        assert removed_count == 1
        assert cache_key not in cache_mgr.metadata["videos"]

    def test_cleanup_preserves_recent_videos(self, temp_dir, sample_video_file, mock_settings):
        """Test that cleanup preserves recent videos."""
        cache_mgr = CacheManager(temp_dir)

        cache_mgr.cache_video("recent video", sample_video_file)
        cache_key = cache_mgr.get_cache_key("recent video")

        # Verify cache was successful
        assert cache_key in cache_mgr.metadata["videos"]

        # Cleanup cache older than 30 days
        removed_count = cache_mgr.cleanup_old_cache(max_age_days=30)

        assert removed_count == 0
        assert cache_key in cache_mgr.metadata["videos"]

    def test_cleanup_removes_old_audio(self, temp_dir, sample_audio_file, mock_settings):
        """Test that cleanup removes audio older than specified days."""
        cache_mgr = CacheManager(temp_dir)

        # Cache an audio
        cache_mgr.cache_audio("old audio", "voice_123", sample_audio_file)
        cache_content = "old audio|voice_123"
        cache_key = cache_mgr.get_cache_key(cache_content)

        # Verify cache was successful
        assert cache_key in cache_mgr.metadata["audio"]

        # Manually set the last_accessed to 40 days ago
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        cache_mgr.metadata["audio"][cache_key]["last_accessed"] = old_date
        cache_mgr._save_metadata()

        # Cleanup cache older than 30 days
        removed_count = cache_mgr.cleanup_old_cache(max_age_days=30)

        assert removed_count == 1
        assert cache_key not in cache_mgr.metadata["audio"]

    def test_cleanup_returns_zero_when_disabled(self, temp_dir, monkeypatch):
        """Test that cleanup returns 0 when cache is disabled."""
        monkeypatch.setenv("ENABLE_CACHE", "false")
        from src.utils.config import reset_settings
        reset_settings()

        cache_mgr = CacheManager(temp_dir)

        removed_count = cache_mgr.cleanup_old_cache(max_age_days=30)

        assert removed_count == 0

    def test_cleanup_handles_mixed_ages(self, temp_dir, sample_video_file, mock_settings):
        """Test cleanup with mixed old and recent cache entries."""
        cache_mgr = CacheManager(temp_dir)

        # Create video files for caching
        video_file2 = temp_dir / "test_video2.mp4"
        video_file2.write_bytes(b'\x00' * 1000)

        # Cache two videos
        cache_mgr.cache_video("old video", sample_video_file)
        cache_mgr.cache_video("recent video", video_file2)

        # Verify both were cached
        old_key = cache_mgr.get_cache_key("old video")
        assert old_key in cache_mgr.metadata["videos"]
        assert cache_mgr.is_video_cached("recent video")

        # Make one old
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        cache_mgr.metadata["videos"][old_key]["last_accessed"] = old_date
        cache_mgr._save_metadata()

        # Cleanup
        removed_count = cache_mgr.cleanup_old_cache(max_age_days=30)

        assert removed_count == 1
        assert old_key not in cache_mgr.metadata["videos"]
        assert cache_mgr.is_video_cached("recent video")


@pytest.mark.unit
class TestGlobalCacheManager:
    """Tests for global cache manager functions."""

    def test_get_cache_manager_returns_instance(self):
        """Test that get_cache_manager returns a CacheManager instance."""
        reset_cache_manager()
        manager = get_cache_manager()

        assert isinstance(manager, CacheManager)

    def test_get_cache_manager_returns_same_instance(self):
        """Test that get_cache_manager returns the same instance."""
        reset_cache_manager()
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is manager2

    def test_reset_cache_manager_creates_new_instance(self):
        """Test that reset_cache_manager creates a new instance."""
        reset_cache_manager()
        manager1 = get_cache_manager()
        reset_cache_manager()
        manager2 = get_cache_manager()

        assert manager1 is not manager2


@pytest.mark.unit
class TestCacheManagerWithMockSettings:
    """Tests using mock_settings fixture."""

    def test_cache_manager_uses_settings_cache_dir(self, mock_settings):
        """Test that CacheManager uses cache_dir from settings."""
        cache_mgr = CacheManager()

        assert str(cache_mgr.cache_dir) == str(mock_settings.cache_dir)

    def test_cache_manager_respects_enable_cache_setting(self, mock_settings):
        """Test that CacheManager respects enable_cache setting."""
        cache_mgr = CacheManager()

        assert cache_mgr.enable_cache == mock_settings.enable_cache
