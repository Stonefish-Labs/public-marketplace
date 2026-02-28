"""
JEFit MCP Server - Workout tracking and analysis

This MCP server connects to the JEFit API to retrieve workout history
and detailed workout information. Provides tools for listing workout dates
and analyzing individual workout sessions.

MCP Server Configuration Examples:

=== Local/stdio Configuration ===
{
  "mcpServers": {
    "jefitWorkouts": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jefit-mcp", "python", "server.py"]
    }
  }
}

=== Local/stdio Configuration with Environment ===
{
  "mcpServers": {
    "jefitWorkouts": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/jefit-mcp", "python", "server.py"],
      "env": {
        "JEFIT_USERNAME": "your_username",
        "JEFIT_PASSWORD": "your_password",
        "JEFIT_TIMEZONE": "-04:00"
      }
    }
  }
}

=== Remote/HTTP Configuration ===
{
  "mcpServers": {
    "jefitWorkouts": {
      "type": "http",
      "url": "http://localhost:8000/mcp/"
    }
  }
}

Environment Variables Required:
- JEFIT_USERNAME: Your JEFit username
- JEFIT_PASSWORD: Your JEFit password
- JEFIT_TIMEZONE: Your timezone offset (e.g., "-04:00" for EDT)

Place this configuration in:
- VS Code: .vscode/mcp.json (project) or user settings
- Claude Desktop: claude_desktop_config.json  
- Cursor: .cursor/mcp.json (project) or ~/.cursor/mcp.json (user)
- LM Studio: ~/.lmstudio/mcp.json
"""

import os
from threading import Lock
from typing import cast
from datetime import datetime, date
from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from history import get_workout_history
from workout_info import format_workout_markdown, get_workout_for_date, load_exercise_db

# Initialize FastMCP server
mcp = FastMCP(
    name="JEFitWorkouts",
    instructions="""
        Analyzes JEFit workout data and provides workout history.
        Use for tracking workout dates, analyzing exercise routines, and viewing detailed session information.
        All dates use YYYY-MM-DD format (ISO 8601).
    """
)

_EXERCISE_DB: dict[str, dict] | None = None
_EXERCISE_DB_LOCK = Lock()


def get_exercise_db() -> dict[str, dict]:
    """Lazily load the exercise database after MCP handshake."""
    global _EXERCISE_DB
    if _EXERCISE_DB is not None:
        return _EXERCISE_DB

    with _EXERCISE_DB_LOCK:
        if _EXERCISE_DB is None:
            _EXERCISE_DB = load_exercise_db()

    return cast(dict[str, dict], _EXERCISE_DB)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def list_workout_dates(start_date: str, end_date: str | None = None) -> list[str]:
    """
    List all workout dates within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (required)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
    
    Returns:
        List of workout dates as strings in YYYY-MM-DD format
    """
    # Default end_date to today if not provided
    if end_date is None:
        end_date = date.today().isoformat()
    
    # Validate date formats
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD format: {e}")
    
    if start > end:
        raise ValueError("start_date must be before or equal to end_date")
    
    # Get all workout dates from API
    all_dates = get_workout_history()
    
    # Filter to date range
    filtered_dates = []
    for workout_date_str in all_dates:
        workout_date = datetime.strptime(workout_date_str, "%Y-%m-%d").date()
        if start <= workout_date <= end:
            filtered_dates.append(workout_date_str)
    
    return sorted(filtered_dates)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def get_workout_info(date: str) -> ToolResult:
    """
    Get detailed workout information for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
    
    Returns:
        Markdown-formatted workout details including exercises, sets, reps, and weights
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD format: {e}")
    
    # Get workout data from API
    workout_data = get_workout_for_date(date)
    
    markdown_text = format_workout_markdown(date, workout_data, get_exercise_db())
    return ToolResult(content=[TextContent(type="text", text=markdown_text)])


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
def get_batch_workouts(dates: list[str]) -> ToolResult:
    """
    Get detailed workout information for multiple dates in a single call.
    
    Args:
        dates: List of dates in YYYY-MM-DD format
    
    Returns:
        Markdown-formatted workout details for all requested dates
    """
    if not dates:
        raise ValueError("dates list cannot be empty")
    
    # Validate all date formats first
    for date_str in dates:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD format: {e}")
    
    # Build combined markdown output
    all_workouts = []
    exercise_db = get_exercise_db()

    for date_str in sorted(dates):
        workout_data = get_workout_for_date(date_str)
        all_workouts.append(format_workout_markdown(date_str, workout_data, exercise_db))
    
    # Join all workouts with separator
    markdown_text = "\n---\n\n".join(all_workouts)
    return ToolResult(content=[TextContent(type="text", text=markdown_text)])


def main():
    """Main entry point for the MCP server"""
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    
    if mcp_port:
        # Run with HTTP transport
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        # Run with stdio transport (default)
        mcp.run()


if __name__ == "__main__":
    main()
