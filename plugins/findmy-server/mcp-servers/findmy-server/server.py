"""
Apple Find My MCP Server - Entrypoint

Thin entrypoint delegating to modular app package per design guidelines.
"""


import os
from typing import Any
from fastmcp import FastMCP

from middleware_auth import AuthenticationMiddleware
from tools_admin import register as register_admin
from tools_devices import register as register_devices
from secrets_manager import secrets_manager


_instructions = (
    """
    Provides access to Apple Find My network for device tracking.
    Use list_devices to see all available devices, then get_device_info with a discovery ID for detailed information including location.
    Data is cached for 5 minutes by default to minimize API calls and improve performance.
    Uses interactive elicitation for Apple ID authentication when first accessing the service.
    """
)

try:
    kwargs: dict[str, Any] = {
        "name": "FindMyDevices",
        "instructions": _instructions,
        "on_duplicate": "error",
    }
    mcp = FastMCP(**kwargs)
except TypeError:
    mcp = FastMCP(name="FindMyDevices", instructions=_instructions)

secrets_manager.initialize(mcp.name)

# Register tools
register_admin(mcp)
register_devices(mcp)

# Add authentication middleware first to ensure it runs before tools
mcp.add_middleware(AuthenticationMiddleware())


def main():
    """Entry point function for running the server."""
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    if mcp_port:
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
