"""
Authentication middleware for iCloud tools.
"""

from fastmcp import Context
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from apple_auth.client_provider import get_authenticated_client


class AuthenticationMiddleware(Middleware):
    """Middleware that ensures iCloud authentication before executing tools that require it."""

    # Tools that require iCloud authentication
    ICLOUD_TOOLS = {
        "list_devices",
        "get_device_info",
        "refresh_cache",
    }

    # Tools that don't require authentication
    NO_AUTH_TOOLS = {
        "clear_stored_credentials",
    }

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Intercept tool calls and ensure authentication for iCloud-dependent tools."""
        tool_name = context.message.name
        fastmcp_context = context.fastmcp_context

        if tool_name in self.NO_AUTH_TOOLS:
            return await call_next(context)

        if tool_name in self.ICLOUD_TOOLS:
            if fastmcp_context is None:
                raise ToolError("FastMCP context unavailable for authentication")
            await self._ensure_authenticated(fastmcp_context)

        return await call_next(context)

    async def _ensure_authenticated(self, ctx: Context) -> None:
        """Ensure we have an authenticated iCloud client."""
        await ctx.info("🔐 Authentication required for iCloud access")

        try:
            client = await get_authenticated_client(ctx)
            if client is None:
                raise ToolError("Failed to authenticate with iCloud")
            await ctx.info("✅ iCloud authentication successful")
        except Exception as e:
            await ctx.info(f"❌ Authentication failed: {e}")
            raise ToolError(f"iCloud authentication required but failed: {e}")
