"""
MCP Response Formatting Helpers

text_response() is the default — agents read clean text directly.
Only use structured_response() when a programmatic consumer needs machine-parseable data.
"""
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent


def text_response(text: str) -> ToolResult:
    """Return raw text as a ToolResult without JSON wrapping overhead."""
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=None,
    )


def structured_response(
    text: str, data: dict, meta: dict | None = None
) -> ToolResult:
    """Return both human-readable text and machine-readable structured data."""
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=data,
        meta=meta,
    )
