"""
MCP Server: {{SERVER_NAME}}
{{DESCRIPTION}}

FastMCP 3.x — replace the example tool with your actual tools.
Run with stdio by default; set PORT env var for HTTP transport.
"""
import os

from fastmcp import FastMCP

mcp = FastMCP(
    name="{{SERVER_NAME}}",
    instructions="""
        [What this server does — one sentence.]
        [When to use it — one sentence.]
        [Constraints or requirements — one sentence.]
    """,
    on_duplicate="error",
)


@mcp.tool
def example_tool(input_text: str) -> dict:
    """Process input text and return a structured result.

    Use this tool when you need to [describe trigger condition].
    Accepts [input description] and returns [output description].
    """
    return {
        "input": input_text,
        "length": len(input_text),
        "status": "processed",
    }


def main() -> None:
    """Run the server. Stdio by default; set PORT env var for HTTP."""
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
