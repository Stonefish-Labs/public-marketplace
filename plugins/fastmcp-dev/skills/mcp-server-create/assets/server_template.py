"""
FastMCP 3.x Server Template

Copy this file as your server.py starting point.
Replace the example tool with your actual tools.

STARTUP SAFETY RULE
-------------------
MCP clients (Cursor, Claude Desktop) send `initialize` immediately on launch and
expect a response within ~5 seconds. Never block before mcp.run() can service
that handshake:

  ❌ asyncio.run(fetch_token())          — blocks at module level
  ❌ lifespan that awaits OAuth flow     — blocks initialize response
  ✅ Lazy singleton (init on first tool call) — see mcp-startup-patterns skill
  ✅ asyncio.create_task() in lifespan   — fires after yield, non-blocking

If your server needs authentication, use the mcp-startup-patterns skill BEFORE
adding auth to this template.
"""
from fastmcp import FastMCP
import os

mcp = FastMCP(
    name="MyServer",
    instructions="""
        [What this server does — one sentence.]
        [When to use it — one sentence.]
        [Constraints or requirements — one sentence.]
    """,
    on_duplicate="error",
)


@mcp.tool
def example_tool(input_text: str) -> dict:
    """Process input text and return structured results."""
    return {
        "input": input_text,
        "length": len(input_text),
        "status": "processed",
    }


def main():
    """Run the server. Uses stdio by default; set PORT env var for HTTP."""
    port = os.getenv("PORT")
    if port:
        mcp.run(
            port=int(port),
            host=os.getenv("HOST", "127.0.0.1"),
            transport="streamable-http",
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
