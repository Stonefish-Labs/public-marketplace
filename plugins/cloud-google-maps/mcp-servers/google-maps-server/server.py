"""
Google Maps MCP Server - Entrypoint

Thin entrypoint delegating to modular app package per design guidelines.
"""

import os
from fastmcp import FastMCP

from tools_maps import register as register_maps

from secrets_manager import secrets_manager

"""Create FastMCP server with clear instructions."""
mcp = FastMCP(
    name="google-maps-server",
    instructions=(
        """
        Provides access to Google Maps APIs for location services.
        Use maps_geocode to convert addresses to coordinates, maps_reverse_geocode for coordinates to addresses.
        Use maps_search_places for finding places by text query, maps_place_details for detailed place information.
        Use maps_distance_matrix for travel times/distances, maps_elevation for elevation data, maps_directions for turn-by-turn directions.
        Results are cached for 10 minutes by default to minimize API calls and improve performance.
        Requires GOOGLE_MAPS_API_KEY environment variable to be set.
        """
    ),
)


# Lightweight initialization: configures keyring namespace only.
secrets_manager.initialize(mcp.name)

# Register Tools
register_maps(mcp)


def main() -> None:
    """Run server supporting both stdio and HTTP transports."""
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    if mcp_port:
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
