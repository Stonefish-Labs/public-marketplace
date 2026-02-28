"""
Auth Patterns for MCP Tools

PATTERN A — Lazy Authentication (the correct approach)
------------------------------------------------------
Authentication is deferred to the first tool call that needs it. The server
starts instantly and responds to the MCP initialize handshake with no delay.

WHY NOT IN LIFESPAN?
MCP clients (Cursor, Claude Desktop) expect the initialize response within ~5s.
The lifespan startup phase blocks that response. Any OAuth flow, network call, or
ctx.elicit() placed in lifespan will cause a client timeout.

  ❌ WRONG — blocks initialize:
      @asynccontextmanager
      async def lifespan(server):
          token = await ctx.elicit("Enter token:")  # not even available here
          yield {"token": token}

  ✅ CORRECT — defer to first tool call (see authenticated_action below)

For cross-restart credential persistence, pair with secretstore (see mcp-secrets
skill). For token refresh on startup, see mcp-startup-patterns Pattern B.
"""

import asyncio

from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext

# Version-safe: check result.action ("accept" | "decline" | "cancel") instead of
# importing AcceptedElicitation / DeclinedElicitation / CancelledElicitation, which
# are not reliably re-exported from fastmcp.server.elicitation across all 3.x builds.

mcp = FastMCP("AuthAndParametersDemo")

# ── PATTERN A: Lazy singleton with session-state caching ─────────────────────
# No I/O at module level. Lock prevents duplicate init on concurrent calls.
_auth_lock: asyncio.Lock | None = None

def _lock() -> asyncio.Lock:
    global _auth_lock
    if _auth_lock is None:
        _auth_lock = asyncio.Lock()
    return _auth_lock


@mcp.tool()
async def authenticated_action(ctx: Context = CurrentContext()) -> str:
    """
    Demonstrates lazy-authentication caching using ctx.get_state() and ctx.elicit().

    Pattern A: Authentication deferred to first tool call. Server starts instantly.
    Token is cached in session state so the user is only prompted once per session.
    """
    # 1. Attempt to retrieve a previously cached token for this session
    token = await ctx.get_state("auth_token")

    # 2. If the token is missing, request it interactively from the user.
    #    This is safe here — we're inside a tool call, not blocking server startup.
    if not token:
        async with _lock():
            # Double-check after acquiring — another coroutine may have set it
            token = await ctx.get_state("auth_token")
            if not token:
                result = await ctx.elicit(
                    "Enter your private API token to proceed:", response_type=str
                )

                if result.action == "accept":
                    token = result.data
                    # Cache the token securely to avoid re-prompting this session.
                    # Note: For highly sensitive out-of-band secrets, use
                    # FormWizard's URL mode or secretstore (mcp-secrets skill).
                    await ctx.set_state("auth_token", token, serializable=False)
                elif result.action == "decline":
                    return "Error: Authentication was declined. Cannot proceed."
                elif result.action == "cancel":
                    return "Operation cancelled by the user."
                else:
                    return "Unknown elicitation error."

    return f"Authenticated successfully! Using token: {token[:4]}..."

@mcp.tool()
async def export_data(data: str, export_format: str | None = None, ctx: Context = CurrentContext()) -> str:
    """
    Demonstrates runtime parameter clarification. Elicits optional parameters only if missing.
    """
    # Check if the LLM provided the optional parameter
    if export_format is None:
        # Prompt the user directly via the UI if the parameter was omitted
        result = await ctx.elicit(
            "Which output format do you prefer?",
            response_type=["json", "csv", "markdown"]
        )
        
        if result.action == "accept":
            export_format = result.data
        elif result.action == "decline":
            # Default fallback if the user declined to choose
            export_format = "json"
        elif result.action == "cancel":
            return "Operation cancelled by the user."
        else:
            return "Unknown elicitation error."
                
    return f"Exporting '{data}' in {export_format.upper()} format..."

if __name__ == "__main__":
    mcp.run()
