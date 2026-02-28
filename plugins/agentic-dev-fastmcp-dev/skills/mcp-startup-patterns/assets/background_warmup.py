"""
Pattern B: Background Warmup Task — Token Refresh

Use when the user has already authenticated (refresh_token is stored) and you want
to proactively refresh the access_token without blocking server startup.

asyncio.create_task() fires the refresh AFTER the lifespan yields, so the server
can respond to the MCP initialize handshake immediately. Tools wait for the task
only if they actually need a fresh token.

Key properties:
- lifespan yields instantly — zero blocking on initialize
- Token refresh runs concurrently in the background
- Tools use asyncio.wait_for + asyncio.shield to avoid cancellation
- Falls back to the stored (possibly expired) token if refresh times out
- Pairs with Pattern A: if no refresh token exists, fall back to lazy OAuth
"""

import asyncio
import os
import time
from contextlib import asynccontextmanager

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext
from secretstore import KeyringStorage

secrets = KeyringStorage("my-service-server")

TOKEN_REFRESH_ENDPOINT = "https://auth.myservice.example.com/oauth/token"
CLIENT_ID = os.getenv("MYSERVICE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("MYSERVICE_CLIENT_SECRET", "")

# Refresh when fewer than this many seconds remain on the access token
REFRESH_THRESHOLD_SECONDS = 300


# ── Helpers ───────────────────────────────────────────────────────────────────

def _token_is_expiring(creds: dict) -> bool:
    """Return True if the access token expires within the refresh threshold."""
    expiry = creds.get("expires_at", 0)
    return time.time() >= (expiry - REFRESH_THRESHOLD_SECONDS)


async def _refresh_token_if_needed() -> dict | None:
    """
    Refresh the access token if it is expiring. Returns updated credentials,
    or None if no stored credentials exist (first-time auth needed).

    This runs as a background task — network errors are caught and logged
    so they don't crash the server.
    """
    creds = secrets.get("oauth_token")
    if not creds:
        return None  # No stored token — let Pattern A handle first-time auth

    if not _token_is_expiring(creds):
        return creds  # Token still fresh, nothing to do

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                TOKEN_REFRESH_ENDPOINT,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": creds["refresh_token"],
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            new_tokens = resp.json()
            updated = {
                "access_token": new_tokens["access_token"],
                "refresh_token": new_tokens.get("refresh_token", creds["refresh_token"]),
                "expires_at": time.time() + new_tokens.get("expires_in", 3600),
            }
            secrets.save("oauth_token", updated)
            return updated
    except Exception as exc:
        # Log but don't crash — tools will use whatever is in the store
        print(f"[warn] Token refresh failed: {exc}")
        return secrets.get("oauth_token")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(server: FastMCP):
    """
    Start a background token-refresh task.

    create_task() schedules the coroutine on the running event loop but
    returns immediately — the lifespan yields right away, letting the server
    respond to the MCP initialize handshake without delay.
    """
    warmup: asyncio.Task = asyncio.create_task(_refresh_token_if_needed())
    yield {"warmup": warmup}
    # Teardown: cancel if still running (e.g., server shut down during refresh)
    if not warmup.done():
        warmup.cancel()


# ── Token accessor ────────────────────────────────────────────────────────────

async def get_access_token(ctx: Context) -> str:
    """
    Return a valid access token, waiting up to 5 s for the warmup task.

    Falls back to the stored token if the background task times out or fails.
    Tools should call this rather than accessing the secret store directly.
    """
    warmup: asyncio.Task = ctx.lifespan_context["warmup"]

    if not warmup.done():
        try:
            # asyncio.shield prevents cancellation propagating to the refresh task
            creds = await asyncio.wait_for(asyncio.shield(warmup), timeout=5.0)
        except asyncio.TimeoutError:
            # Refresh is slow — fall back to whatever is stored
            creds = secrets.get("oauth_token")
    else:
        try:
            creds = warmup.result()
        except Exception:
            creds = secrets.get("oauth_token")

    if not creds:
        raise RuntimeError(
            "No credentials found. Use the `authorize` tool to connect first."
        )
    return creds["access_token"]


# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP(
    name="MyServiceServer",
    instructions="""
        Integrates with MyService API.
        Use when the user wants to query or modify MyService resources.
        Proactively refreshes access tokens at startup using stored credentials.
    """,
    on_duplicate="error",
    lifespan=lifespan,
)


@mcp.tool
async def get_profile(ctx: Context = CurrentContext()) -> dict:
    """Fetch the authenticated user's profile from MyService."""
    token = await get_access_token(ctx)
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            "https://api.myservice.example.com/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool
async def list_items(limit: int = 20, ctx: Context = CurrentContext()) -> list[dict]:
    """List items from MyService for the authenticated user."""
    token = await get_access_token(ctx)
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            "https://api.myservice.example.com/v1/items",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": limit},
        )
        resp.raise_for_status()
        return resp.json()["items"]


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
