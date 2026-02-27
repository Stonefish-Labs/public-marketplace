"""
Simple in-memory caching for Google Maps API responses.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry with data and timestamp."""
    data: Any
    cached_at: datetime


# Global cache - simple dictionary implementation
_cache: Dict[str, CacheEntry] = {}
CACHE_TIMEOUT_MINUTES = 10  # Cache for 10 minutes by default


def cache_response(key: str, data: Any) -> None:
    """Cache API response data."""
    _cache[key] = CacheEntry(data=data, cached_at=datetime.now())


def get_cached_response(key: str) -> Optional[Any]:
    """Get cached response if within timeout."""
    if key in _cache:
        entry = _cache[key]
        cutoff_time = datetime.now() - timedelta(minutes=CACHE_TIMEOUT_MINUTES)

        if entry.cached_at > cutoff_time:
            return entry.data
        else:
            # Remove expired cache
            del _cache[key]

    return None


def clear_cache() -> None:
    """Clear all cached data."""
    _cache.clear()


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics."""
    return {
        "total_entries": len(_cache),
        "cache_timeout_minutes": CACHE_TIMEOUT_MINUTES
    }
