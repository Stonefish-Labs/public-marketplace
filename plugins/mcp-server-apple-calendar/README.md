# MCP Server — Apple Calendar

FastMCP 3.x server for Apple Calendar integration on macOS.

## Overview

Exposes Apple Calendar via the Model Context Protocol so any MCP-capable agent can read, create, update, and delete calendar events. Write operations use FastMCP's elicitation feature to require explicit user confirmation before committing changes. Backed by a precompiled Swift `EventKitCLI` binary that accesses EventKit directly — no AppleScript required.

## Prerequisites

- macOS (EventKit access required)
- Python 3.12+
- `uv` package manager

Install and run the server:

```bash
cd mcp-servers
uv run mcp-server-apple-calendar
```

To run over HTTP instead of stdio, set the `PORT` environment variable:

```bash
PORT=8080 uv run mcp-server-apple-calendar
```

## Tools

| Tool | Description |
|------|-------------|
| `list_calendars` | List all available calendars and their IDs |
| `list_calendar_events` | List events with optional date range, calendar, or search filters |
| `get_calendar_event` | Retrieve full details for a specific event by ID |
| `create_calendar_event` | Create a new event (requires confirmation) |
| `update_calendar_event` | Update an existing event (requires confirmation) |
| `delete_calendar_event` | Permanently delete an event (requires confirmation, destructive) |

Call `list_calendars` first to discover available calendar names before creating or moving events.

## License

MIT
