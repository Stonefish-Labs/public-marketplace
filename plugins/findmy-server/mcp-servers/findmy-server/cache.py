import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Simple in-memory cache configuration
CACHE_TIMEOUT_MINUTES = int(os.getenv("FINDMY_CACHE_TIMEOUT", "5"))
_device_cache: Dict[str, Dict] = {}


def get_cached_devices(session_id: str) -> Optional[List[Dict]]:
    """Get cached device list if within timeout."""
    cache_key = f"devices:{session_id}"
    if cache_key in _device_cache:
        cache_data = _device_cache[cache_key]
        cached_at = cache_data["cached_at"]
        cutoff_time = datetime.now() - timedelta(minutes=CACHE_TIMEOUT_MINUTES)
        if cached_at > cutoff_time:
            return cache_data["devices"]
        del _device_cache[cache_key]
    return None


def cache_devices(devices: List[Dict], session_id: str) -> None:
    """Cache device list with timestamp."""
    cache_key = f"devices:{session_id}"
    _device_cache[cache_key] = {"devices": devices, "cached_at": datetime.now()}


def clear_all_caches() -> None:
    _device_cache.clear()


