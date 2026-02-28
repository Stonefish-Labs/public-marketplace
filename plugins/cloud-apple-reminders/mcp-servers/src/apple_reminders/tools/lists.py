"""Reminder list tools with elicitation for write operations."""

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult

from .. import repository
from ..models import validate_safe_text
from ..utils import (
    format_delete_message,
    format_list_markdown,
    format_success_message,
    text_response,
)


async def list_reminder_lists() -> ToolResult:
    """List all available reminder lists.

    Use this to discover list names before creating or moving reminders.

    Returns:
        Markdown-formatted list of available reminder lists with their IDs
    """
    lists = await repository.find_all_lists()

    list_data = [
        {"title": l.title, "id": l.id}
        for l in lists
    ]

    return text_response(
        format_list_markdown(
            "Reminder Lists",
            list_data,
            lambda l: [f"- {l['title']} (ID: {l['id']})"],
            "No reminder lists found.",
        )
    )


async def create_reminder_list(
    name: str,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Create a new reminder list. Requires confirmation before creating.

    Args:
        name: The name of the new reminder list

    Returns:
        Confirmation message with the created list ID
    """
    validated_name = validate_safe_text(name, "List name", 100)

    confirmation_message = (
        f"Create new reminder list?\n\n"
        f"**Name:** {validated_name}\n"
    )

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("List creation cancelled.")

    reminder_list = await repository.create_reminder_list(validated_name)

    return text_response(
        format_success_message("created", "list", reminder_list.title, reminder_list.id)
    )


async def update_reminder_list(
    name: str,
    new_name: str,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Rename a reminder list. Requires confirmation before updating.

    Args:
        name: The current name of the reminder list
        new_name: The new name for the reminder list

    Returns:
        Confirmation message with the updated list details
    """
    validated_name = validate_safe_text(name, "List name", 100)
    validated_new_name = validate_safe_text(new_name, "New list name", 100)

    confirmation_message = (
        f"Rename reminder list?\n\n"
        f"**Current name:** {validated_name}\n"
        f"**New name:** {validated_new_name}\n"
    )

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("List rename cancelled.")

    reminder_list = await repository.update_reminder_list(validated_name, validated_new_name)

    return text_response(
        format_success_message("updated", "list", reminder_list.title, reminder_list.id)
    )


async def delete_reminder_list(
    name: str,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Delete a reminder list. Requires confirmation before deleting.

    This action is irreversible. The list and all its reminders will be permanently removed.

    Args:
        name: The name of the reminder list to delete

    Returns:
        Confirmation message indicating the list was deleted
    """
    validated_name = validate_safe_text(name, "List name", 100)

    confirmation_message = (
        f"**Permanently delete this reminder list?**\n\n"
        f"**Name:** {validated_name}\n\n"
        f"This will also delete all reminders in this list.\n"
        f"This action cannot be undone."
    )

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("List deletion cancelled.")

    await repository.delete_reminder_list(validated_name)

    return text_response(format_delete_message("list", validated_name, use_quotes=True))
