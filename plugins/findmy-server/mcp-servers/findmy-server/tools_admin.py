"""
Administrative tools for cache management.
"""

from fastmcp import Context, FastMCP

from apple_auth.client_provider import clear_stored_credentials as clear_saved_apple_credentials
from cache import CACHE_TIMEOUT_MINUTES, clear_all_caches
from formatter import format_cache_status
from utils import text_response


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "idempotentHint": True,
            "destructiveHint": True,
            "openWorldHint": False,
        }
    )
    async def clear_stored_credentials(ctx: Context):
        """
        Clear stored Apple ID and password from secure storage.

        This removes the stored credentials from our secrets manager,
        forcing re-authentication on next request. The cache and client state remain intact.
        Use this when you want to switch Apple accounts or reset credentials.
        """
        try:
            clear_saved_apple_credentials()
            await ctx.info("Stored Apple credentials cleared successfully")
            await ctx.info("Next request will require new authentication")
            return text_response("Apple credentials cleared. Next authentication will require new credentials.")
        except Exception as e:
            raise ValueError(f"Failed to clear credentials: {e}")

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "idempotentHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        }
    )
    async def refresh_cache(ctx: Context):
        """
        Clear the data cache and force fresh data retrieval on next request.

        This only clears cached device/location data, not authentication.
        Use this when you need the most up-to-date location information
        or if cached data seems stale. For authentication issues, use clear_stored_credentials instead.
        """
        try:
            clear_all_caches()
            await ctx.info("Data cache cleared successfully")
            return text_response(format_cache_status(CACHE_TIMEOUT_MINUTES, "cleared"))
        except Exception as e:
            raise ValueError(f"Failed to clear data cache: {e}")
