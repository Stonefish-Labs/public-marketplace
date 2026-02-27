"""
Reusable Google Maps API client helpers.

This module isolates HTTP/API interaction from MCP tool wrappers.
"""

from typing import Any, Dict

import httpx


class GoogleMapsApiError(Exception):
    """Raised when a Google Maps API call does not return OK status."""


async def get_json(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call a Google Maps endpoint and return parsed JSON data."""
    url = f"https://maps.googleapis.com/maps/api/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()


def require_ok_status(data: Dict[str, Any], prefix: str) -> None:
    """Raise a clean error when a Google Maps response status is not OK."""
    status = data.get("status")
    if status != "OK":
        error_msg = data.get("error_message", status or "Unknown error")
        raise GoogleMapsApiError(f"{prefix}: {error_msg}")
