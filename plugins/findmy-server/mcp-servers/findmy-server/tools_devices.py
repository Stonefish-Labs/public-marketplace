"""
Find My device tools.
"""

from typing import Dict, List

from fastmcp import Context, FastMCP

from apple_auth.client_provider import get_authenticated_client
from cache import cache_devices, get_cached_devices
from formatter import format_device_list, format_device_info
from utils import text_response


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        }
    )
    async def list_devices(ctx: Context):
        """
        List all Find My devices associated with your Apple account.

        Returns device information with discovery IDs for use with get_device_info.
        Use get_device_info with a discovery ID to get comprehensive details including location, battery, and status.
        Results are cached for improved performance.
        """
        session_id = ctx.session_id
        cached_devices = get_cached_devices(session_id)

        if cached_devices:
            await ctx.info(f"Retrieved {len(cached_devices)} devices from cache")
            return text_response(format_device_list(cached_devices, is_cached=True))

        await ctx.info("Fetching devices from Apple iCloud...")
        client = await get_authenticated_client(ctx)
        devices = client.devices

        device_list = []
        for device in devices:
            try:
                status = device.status()
                device_data = device.data

                device_info = {
                    "name": status.get("name", str(device)),
                    "display_name": status.get("deviceDisplayName", "Unknown"),
                    "discovery_id": device_data.get("deviceDiscoveryId", "Unknown"),
                    "device_class": device_data.get("deviceClass", "Unknown"),
                    "raw_data": device_data,
                }
            except Exception as exc:
                device_info = {
                    "name": str(device),
                    "display_name": "Unknown",
                    "discovery_id": "Unknown",
                    "device_class": "Unknown",
                    "raw_data": {},
                    "error": str(exc),
                }

            device_list.append(device_info)

        cache_devices(device_list, session_id)
        await ctx.info(f"Retrieved {len(device_list)} devices from iCloud")
        return text_response(format_device_list(device_list))

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        }
    )
    async def get_device_info(discovery_id: str, ctx: Context):
        """
        Get detailed information for a specific device using its discovery ID.

        Args:
            discovery_id: The device discovery ID from list_devices (e.g., "6196E031-C3CE-4664-875A-2D02B4071080")

        Returns detailed device information including battery, location, status, and technical details.
        Data is retrieved from cache when available.
        """
        discovery_id = discovery_id.strip()
        if not discovery_id:
            raise ValueError("discovery_id must be a non-empty string from list_devices.")

        session_id = ctx.session_id
        cached_devices = get_cached_devices(session_id)

        if cached_devices:
            for device in cached_devices:
                if device.get("discovery_id") == discovery_id:
                    await ctx.info(f"Found device {discovery_id} in cache")
                    return text_response(format_device_info(device, discovery_id))

        raise ValueError(f"Device with discovery ID '{discovery_id}' not found. Run list_devices first to populate the device cache.")
