# jefit-mcp Plugin

Claude Code plugin that bundles a FastMCP server for analyzing JEFit workout data.

## Setup

1. **Install dependencies:**
   ```bash
   uv sync --directory mcp-servers/jefit-mcp
   ```

2. **Configure environment variables:**
   
   Set the following environment variables or use your secrets manager of choice.
   ```
   JEFIT_USERNAME=your_username
   JEFIT_PASSWORD=your_password
   JEFIT_TIMEZONE=-07:00
   ```
   
   Note: Use timezone offset format like `-07:00` for PDT, `-04:00` for EDT

The exercise database is cached under `mcp-servers/jefit-mcp/data/`.

## MCP Configuration

### Local/stdio Configuration (Direct MCP Use)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "jefit-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "server"],
      "cwd": "/path/to/jefit-mcp/mcp-servers/jefit-mcp"
    }
  }
}
```

### Configuration Locations

- **Cursor**: `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (user)
- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **VS Code**: `.vscode/mcp.json`

## Available Tools

### 1. `list_workout_dates`

List all workout dates within a date range.

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)

**Returns:** List of workout dates

**Example:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-19"
}
```

### 2. `get_workout_info`

Get detailed workout information for a specific date.

**Parameters:**
- `date` (required): Date in YYYY-MM-DD format

**Returns:** Markdown-formatted workout details including:
- Start time and duration
- Total weight lifted
- Exercise list with muscle groups, equipment, sets, and reps

**Example:**
```json
{
  "date": "2025-10-17"
}
```

### 3. `get_batch_workouts`

Get detailed workout information for multiple dates in a single call.

**Parameters:**
- `dates` (required): List of dates in YYYY-MM-DD format

**Returns:** Markdown-formatted workout details for all requested dates, separated by horizontal rules

**Example:**
```json
{
  "dates": ["2025-10-15", "2025-10-17", "2025-10-19"]
}
```

## Testing

Run in-memory MCP tests:

```bash
uv run --directory mcp-servers/jefit-mcp --with pytest --with pytest-asyncio pytest
```

## Project Structure

```
jefit-mcp/
├── .claude-plugin/plugin.json
├── .mcp.json
└── mcp-servers/
    └── jefit-mcp/
        ├── server.py
        ├── auth.py
        ├── history.py
        ├── workout_info.py
        ├── utils.py
        ├── pyproject.toml
        └── tests/
```

## Development

The bundled server uses FastMCP 3.x and supports both stdio and HTTP transports. By default, it runs in stdio mode. To run in HTTP mode, set `HOST` and `PORT` for the server process.
