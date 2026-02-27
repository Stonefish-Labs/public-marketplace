"""
Output formatting utilities for Find My devices and information.
"""

from datetime import datetime
from typing import Dict, List


def format_device_list(devices: List[Dict], is_cached: bool = False) -> str:
    """Format device list for display."""
    cache_label = " (Cached)" if is_cached else ""
    lines = [f"== Available Devices{cache_label} ==", ""]

    for device in devices:
        name = device["name"]
        display_name = device.get("display_name", device.get("model", "Unknown"))
        discovery_id = device.get("discovery_id", "Unknown")
        device_class = device.get("device_class", "Unknown")

        lines.extend([
            f"# {name} ({display_name})",
            f"  - Name: {name}",
            f"  - Display Name: {display_name}",
            f"  - Discovery ID: {discovery_id}",
            f"  - Device Class: {device_class}",
            ""
        ])

    lines.append("Use get_device_info with the Discovery ID to get comprehensive details.")
    return "\n".join(lines)


def format_device_info(device: Dict, discovery_id: str) -> str:
    """Format detailed device information."""
    name = device["name"]
    display_name = device["display_name"]
    device_class = device["device_class"]
    raw_data = device.get("raw_data", {})

    lines = [f"== Device Information: {name} ==", ""]

    # Basic info
    lines.extend([
        f"Name: {name}",
        f"Display Name: {display_name}",
        f"Device Class: {device_class}",
        f"Discovery ID: {discovery_id}",
        f"Status: {_get_status_text(raw_data)}",
        ""
    ])

    # Battery info
    lines.extend([
        "## Battery Information",
        f"Level: {_get_battery_display(raw_data)}",
        f"Status: {raw_data.get('batteryStatus', 'Unknown')}",
        ""
    ])

    # Location info
    location_lines = _format_location_info(raw_data)
    if location_lines:
        lines.extend(["## Location Information"] + location_lines + [""])
    else:
        lines.extend(["## Location Information", "No location data available", ""])

    # Technical details
    lines.extend([
        "## Technical Details",
        f"Model: {raw_data.get('rawDeviceModel', 'N/A')}",
        f"Color Code: {raw_data.get('deviceColor', 'N/A')}",
        f"Location Capable: {raw_data.get('locationCapable', False)}",
        f"Lost Mode Capable: {raw_data.get('lostModeCapable', False)}"
    ])

    return "\n".join(lines)


def format_cache_status(timeout_minutes: int, action: str = "cleared") -> str:
    """Format cache operation status message."""
    return "\n".join([
        f"== Data Cache {action.title()} ==",
        "",
        f"Status: Success",
        f"Message: Data cache {action}. Next requests will fetch fresh data.",
        f"Authentication: Preserved",
        f"Cache Timeout: {timeout_minutes} minutes"
    ])


def format_reset_status(timeout_minutes: int) -> str:
    """Format authentication reset status message."""
    return "\n".join([
        "== Cache & Authentication Reset ==",
        "",
        "Status: Success",
        "Message: All caches cleared and authentication reset. Next request will require fresh login.",
        f"Cache Timeout: {timeout_minutes} minutes"
    ])


def _get_status_text(raw_data: Dict) -> str:
    """Get human-readable device status."""
    device_status = raw_data.get("deviceStatus", "Unknown")

    status_map = {
        "200": "Online",
        "203": "Offline",
        "201": "Partial"
    }

    return status_map.get(device_status, "Unknown")


def _get_battery_display(raw_data: Dict) -> str:
    """Get battery level display string."""
    battery_level = raw_data.get("batteryLevel")

    if battery_level is None:
        return "N/A"

    if battery_level > 0:
        return f"{int(battery_level * 100)}%"

    return "0%"


def _format_location_info(raw_data: Dict) -> List[str]:
    """Format location information lines."""
    location_data = raw_data.get("location")
    if not location_data:
        return []

    lines = []

    # Coordinates
    if location_data.get("latitude") and location_data.get("longitude"):
        lines.append(f"Coordinates: {location_data['latitude']}, {location_data['longitude']}")

    # Altitude
    if location_data.get("altitude"):
        lines.append(f"Altitude: {location_data['altitude']} meters")

    # Floor level
    if location_data.get("floorLevel"):
        lines.append(f"Floor Level: {location_data['floorLevel']}")

    # Accuracy
    if location_data.get("horizontalAccuracy"):
        lines.append(f"Accuracy: {location_data['horizontalAccuracy']} meters")

    # Position type
    if location_data.get("positionType"):
        lines.append(f"Position Type: {location_data['positionType']}")

    # Timestamp
    if location_data.get("timeStamp"):
        try:
            timestamp_dt = datetime.fromtimestamp(location_data["timeStamp"] / 1000)
            lines.append(f"Last Updated: {timestamp_dt.strftime('%B %d, %Y at %I:%M %p')}")
        except Exception:
            pass

    # Warnings
    if location_data.get("isOld"):
        lines.append("⚠️ Location data may be outdated")

    if location_data.get("isInaccurate"):
        lines.append("⚠️ Location may be inaccurate")

    return lines
