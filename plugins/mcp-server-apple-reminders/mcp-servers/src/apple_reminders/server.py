"""FastMCP 3.x server for Apple Reminders integration."""

import asyncio
import os
import sys

from fastmcp import FastMCP

from . import repository
from .tools import (
    create_reminder,
    create_reminder_list,
    delete_reminder,
    delete_reminder_list,
    get_reminder,
    list_reminder_lists,
    list_reminders,
    update_reminder,
    update_reminder_list,
)

mcp = FastMCP(
    name="mcp-server-apple-reminders",
    instructions=(
        "Apple Reminders MCP server for macOS. "
        "Read reminders and lists, create/update/delete reminders and lists with confirmation. "
        "Use list_reminder_lists to discover available lists before creating reminders."
    ),
    on_duplicate="error",
)

READ_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
    "openWorldHint": True,
}

WRITE_ANNOTATIONS = {
    "readOnlyHint": False,
    "idempotentHint": False,
    "destructiveHint": False,
    "openWorldHint": True,
}

DELETE_ANNOTATIONS = {
    "readOnlyHint": False,
    "idempotentHint": False,
    "destructiveHint": True,
    "openWorldHint": True,
}

mcp.tool(list_reminders, annotations=READ_ANNOTATIONS)
mcp.tool(get_reminder, annotations=READ_ANNOTATIONS)
mcp.tool(create_reminder, annotations=WRITE_ANNOTATIONS)
mcp.tool(update_reminder, annotations=WRITE_ANNOTATIONS)
mcp.tool(delete_reminder, annotations=DELETE_ANNOTATIONS)
mcp.tool(list_reminder_lists, annotations=READ_ANNOTATIONS)
mcp.tool(create_reminder_list, annotations=WRITE_ANNOTATIONS)
mcp.tool(update_reminder_list, annotations=WRITE_ANNOTATIONS)
mcp.tool(delete_reminder_list, annotations=DELETE_ANNOTATIONS)


def main():
    """Run the MCP server."""
    run_preflight = os.environ.get("REMINDERS_PERMISSION_PREFLIGHT", "1") != "0"
    auto_bootstrap = os.environ.get("REMINDERS_PERMISSION_BOOTSTRAP", "1") != "0"

    if run_preflight:
        ok, preflight_message = asyncio.run(
            repository.preflight_permissions(auto_bootstrap=auto_bootstrap)
        )
        if preflight_message:
            stream = sys.stderr if not ok else sys.stdout
            print(preflight_message, file=stream)

    port_str = os.environ.get("PORT")
    if port_str:
        port = int(port_str)
        mcp.run(transport="streamable-http", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
