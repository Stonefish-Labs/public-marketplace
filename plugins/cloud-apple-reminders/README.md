# MCP Server — Apple Reminders

FastMCP 3.x server for Apple Reminders integration on macOS.

## Overview

Exposes Apple Reminders via the Model Context Protocol so any MCP-capable agent can read, create, update, and delete reminders and reminder lists. Write operations use FastMCP's elicitation feature to require explicit user confirmation before committing changes. Backed by a precompiled Swift `EventKitCLI` binary that accesses EventKit directly — no AppleScript required.

## Prerequisites

- macOS (EventKit access required)
- Python 3.12+
- `uv` package manager

Install and run the server:

```bash
cd mcp-servers
uv run mcp-server-apple-reminders
```

To run over HTTP instead of stdio, set the `PORT` environment variable:

```bash
PORT=8080 uv run mcp-server-apple-reminders
```

## Permission preflight and bootstrap

On startup, the server runs a permission preflight to check Reminders access.
If access is denied, it attempts an AppleScript bootstrap call to trigger the
macOS permission prompt:

```bash
osascript -e 'tell application "Reminders" to get the name of every list'
```

Environment controls:

- `REMINDERS_PERMISSION_PREFLIGHT=0` disables startup permission checks.
- `REMINDERS_PERMISSION_BOOTSTRAP=0` disables the automatic bootstrap prompt.

## Tools

| Tool | Description |
|------|-------------|
| `list_reminder_lists` | List all available reminder lists |
| `list_reminders` | List reminders with optional list, completion, search, and due-date filters |
| `get_reminder` | Retrieve full details for a specific reminder by ID |
| `create_reminder` | Create a new reminder (requires confirmation) |
| `update_reminder` | Update an existing reminder (requires confirmation) |
| `delete_reminder` | Permanently delete a reminder (requires confirmation, destructive) |
| `create_reminder_list` | Create a new reminder list (requires confirmation) |
| `update_reminder_list` | Rename an existing reminder list (requires confirmation) |
| `delete_reminder_list` | Permanently delete a reminder list (requires confirmation, destructive) |

Call `list_reminder_lists` first to discover available list names before creating or moving reminders.

## License

MIT
