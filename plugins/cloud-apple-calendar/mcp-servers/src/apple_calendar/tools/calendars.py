"""Calendar collection tools (read-only)."""

from fastmcp.tools.tool import ToolResult

from .. import repository
from ..utils import format_list_markdown, text_response


async def list_calendars() -> ToolResult:
    """List all available calendars.

    Use this to discover calendar names before creating or updating events.

    Returns:
        Markdown-formatted list of available calendars with their IDs
    """
    calendars = await repository.find_all_calendars()

    calendar_data = [
        {"title": c.title, "id": c.id}
        for c in calendars
    ]

    return text_response(
        format_list_markdown(
            "Calendars",
            calendar_data,
            lambda c: [f"- {c['title']} (ID: {c['id']})"],
            "No calendars found.",
        )
    )
