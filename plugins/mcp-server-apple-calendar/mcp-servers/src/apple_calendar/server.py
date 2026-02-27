"""FastMCP 3.x server for Apple Calendar integration."""

import os

from fastmcp import FastMCP

from .tools import (
    create_calendar_event,
    delete_calendar_event,
    get_calendar_event,
    list_calendar_events,
    list_calendars,
    update_calendar_event,
)

mcp = FastMCP(
    name="mcp-server-apple-calendar",
    instructions=(
        "Apple Calendar MCP server for macOS. "
        "Read calendar events and calendars, create/update/delete events with confirmation. "
        "Use list_calendars to discover available calendars before creating events."
    ),
    on_duplicate="error",
)

mcp.tool(
    list_calendar_events,
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
mcp.tool(
    get_calendar_event,
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
mcp.tool(
    create_calendar_event,
    annotations={
        "readOnlyHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
mcp.tool(
    update_calendar_event,
    annotations={
        "readOnlyHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
mcp.tool(
    delete_calendar_event,
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
mcp.tool(
    list_calendars,
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)


def main():
    """Run the MCP server."""
    port_str = os.environ.get("PORT")
    if port_str:
        port = int(port_str)
        mcp.run(transport="streamable-http", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
