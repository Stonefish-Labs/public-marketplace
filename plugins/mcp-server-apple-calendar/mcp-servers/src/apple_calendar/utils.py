"""Utility functions for response formatting and validation."""

from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent


def text_response(text: str) -> ToolResult:
    """Return raw text as a ToolResult without JSON wrapping overhead."""
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=None,
    )


def format_multiline_notes(notes: str) -> str:
    """Format multiline notes for markdown display by indenting continuation lines."""
    return notes.replace("\n", "\n    ")


def format_event_markdown(event: dict) -> list[str]:
    """Format a calendar event as markdown list item lines."""
    lines = [f"- {event.get('title', 'Untitled')}"]
    if calendar := event.get("calendar"):
        lines.append(f"  - Calendar: {calendar}")
    if event_id := event.get("id"):
        lines.append(f"  - ID: {event_id}")
    if start_date := event.get("startDate"):
        lines.append(f"  - Start: {start_date}")
    if end_date := event.get("endDate"):
        lines.append(f"  - End: {end_date}")
    if event.get("isAllDay"):
        lines.append("  - All Day: True")
    if location := event.get("location"):
        lines.append(f"  - Location: {location}")
    if notes := event.get("notes"):
        lines.append(f"  - Notes: {format_multiline_notes(notes)}")
    if url := event.get("url"):
        lines.append(f"  - URL: {url}")
    return lines


def format_list_markdown(
    title: str, items: list, format_item, empty_message: str
) -> str:
    """Format a list of items as markdown."""
    lines = [f"### {title} (Total: {len(items)})", ""]
    if len(items) == 0:
        lines.append(empty_message)
    else:
        for item in items:
            lines.extend(format_item(item))
    return "\n".join(lines)


def format_success_message(action: str, item_type: str, title: str, item_id: str) -> str:
    """Format a success message for create/update operations."""
    return f'Successfully {action} {item_type} "{title}".\n- ID: {item_id}'


def format_delete_message(item_type: str, identifier: str) -> str:
    """Format a success message for delete operations."""
    return f'Successfully deleted {item_type} with ID: "{identifier}".'
