"""
MCP Response Formatting Helpers

Copy this file into your MCP server project and import the helpers:

    from utils import text_response, structured_response

text_response() is the preferred default — most MCP tool consumers are agents
that read clean text directly. Only use structured_response() or dict returns
when a concrete programmatic consumer needs machine-parseable data.
"""
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent


def text_response(text: str) -> ToolResult:
    """Return raw text as a ToolResult without JSON wrapping overhead.

    This is the preferred default for MCP tool output. Agents receive clean,
    readable text instead of token-wasting {"result": "..."} wrapping.
    Use markdown formatting (headers, tables, bold) for scannability.
    """
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=None,
    )


def structured_response(
    text: str, data: dict, meta: dict | None = None
) -> ToolResult:
    """Return both human-readable text and machine-readable structured data.

    Use this only when a programmatic consumer (automation, another program)
    needs the structured data. The text appears in content blocks for agents;
    the data appears in structuredContent for programmatic access.
    """
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=data,
        meta=meta,
    )
