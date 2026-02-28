"""
Pattern A: Lazy Singleton — OAuth / First-Time Authentication

Use when the user has not yet authenticated (no stored token). The server starts
instantly. Authentication is deferred to the first tool call that needs it, where
ctx.elicit() is available to guide the user through the flow.

Key properties:
- Module level holds only None references — zero I/O at import time
- asyncio.Lock prevents duplicate init when concurrent tool calls race
- Double-checked locking avoids the lock on every subsequent call
- secretstore caches credentials so the OAuth prompt only fires once across restarts
"""

import asyncio
import os
from contextlib import asynccontextmanager

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext

# Version-safe: check result.action ("accept" | "decline" | "cancel") instead of
# importing AcceptedElicitation / DeclinedElicitation / CancelledElicitation, which
# are not reliably re-exported from fastmcp.server.elicitation across all 3.x builds.

from secretstore import KeyringStorage

secrets = KeyringStorage("my-service-server")

# ── Module-level state ────────────────────────────────────────────────────────
# These are intentionally None at module load — no I/O happens here.
_http_client: httpx.AsyncClient | None = None
_init_lock: asyncio.Lock | None = None


def _lock() -> asyncio.Lock:
    """Return (creating once) the init lock. Safe to call before the event loop exists."""
    global _init_lock
    if _init_lock is None:
        _init_lock = asyncio.Lock()
    return _init_lock


# ── Lazy initializer ─────────────────────────────────────────────────────────

async def get_http_client(ctx: Context) -> httpx.AsyncClient:
    """
    Return the authenticated HTTP client, initializing it on first call.

    This is the ONLY place credentials are fetched or elicited. All tools
    call this helper instead of accessing the credential store directly.
    """
    global _http_client

    # Fast path — already initialized (no lock needed after first init)
    if _http_client is not None:
        return _http_client

    async with _lock():
        # Double-check: another coroutine may have initialized while we waited
        if _http_client is not None:
            return _http_client

        # ── Step 1: Try stored credentials ───────────────────────────────────
        creds = secrets.get("oauth_token")

        # ── Step 2: If missing, drive OAuth via elicitation ──────────────────
        if not creds:
            result = await ctx.elicit(
                "MyService requires authorization. Open browser to connect?",
                response_type=None,  # Pure confirmation modal
            )
            if result.action == "accept":
                creds = await _run_oauth_flow()
                secrets.save("oauth_token", creds)
            else:  # "decline" or "cancel"
                raise ToolError(
                    "MyService authorization is required to use this tool."
                )

        # ── Step 3: Build authenticated client ───────────────────────────────
        _http_client = httpx.AsyncClient(
            base_url="https://api.myservice.example.com",
            headers={"Authorization": f"Bearer {creds['access_token']}"},
            timeout=30.0,
        )

    return _http_client


async def _run_oauth_flow() -> dict:
    """
    Placeholder: implement the actual OAuth exchange here.
    Returns a dict with at least {"access_token": "...", "refresh_token": "..."}.

    In a real server this might:
    - Start a local HTTP redirect handler
    - Open the browser to the authorization URL
    - Wait for the callback with the auth code
    - Exchange the code for tokens
    """
    raise NotImplementedError("Implement your OAuth exchange here")


# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="MyServiceServer",
    instructions="""
        Integrates with MyService API.
        Use when the user wants to query or modify MyService resources.
        Requires one-time OAuth authorization on first use.
    """,
    on_duplicate="error",
)


@mcp.tool
async def get_profile(ctx: Context = CurrentContext()) -> dict:
    """Fetch the authenticated user's profile from MyService."""
    client = await get_http_client(ctx)  # ← auth happens here if needed
    response = await client.get("/v1/me")
    response.raise_for_status()
    return response.json()


@mcp.tool
async def list_items(limit: int = 20, ctx: Context = CurrentContext()) -> list[dict]:
    """List items from MyService for the authenticated user."""
    client = await get_http_client(ctx)
    response = await client.get("/v1/items", params={"limit": limit})
    response.raise_for_status()
    return response.json()["items"]


@mcp.tool
async def disconnect(ctx: Context = CurrentContext()) -> str:
    """Remove stored credentials and reset the connection."""
    global _http_client
    result = await ctx.elicit(
        "Disconnect from MyService and remove stored credentials?",
        response_type=None,
    )
    if result.action == "accept":
        if _http_client:
            await _http_client.aclose()
            _http_client = None
        secrets.delete("oauth_token")
        return "Disconnected. Next tool call will prompt for re-authorization."
    else:
        return "Disconnect cancelled."


def main() -> None:
    port = os.getenv("PORT")
    if port:
        mcp.run(
            transport="streamable-http",
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(port),
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
