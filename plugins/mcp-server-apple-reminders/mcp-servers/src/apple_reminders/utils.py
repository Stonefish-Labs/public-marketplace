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


def format_reminder_markdown(reminder: dict) -> list[str]:
    """Format a reminder as markdown list item lines."""
    checkbox = "[x]" if reminder.get("isCompleted") else "[ ]"
    lines = [f"- {checkbox} {reminder.get('title', 'Untitled')}"]
    if list_name := reminder.get("list"):
        lines.append(f"  - List: {list_name}")
    if reminder_id := reminder.get("id"):
        lines.append(f"  - ID: {reminder_id}")
    if due_date := reminder.get("dueDate"):
        lines.append(f"  - Due: {due_date}")
    if notes := reminder.get("notes"):
        lines.append(f"  - Notes: {format_multiline_notes(notes)}")
    if url := reminder.get("url"):
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
    if action == "updated" and item_type == "list":
        prefix = f"Successfully updated {item_type} to"
    else:
        prefix = f"Successfully {action} {item_type}"
    return f'{prefix} "{title}".\n- ID: {item_id}'


def format_delete_message(item_type: str, identifier: str, use_quotes: bool = True) -> str:
    """Format a success message for delete operations."""
    formatted_id = f'"{identifier}"' if use_quotes else identifier
    return f"Successfully deleted {item_type} with ID: {formatted_id}."
