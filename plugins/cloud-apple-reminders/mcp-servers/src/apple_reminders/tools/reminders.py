"""Reminder tools with elicitation for write operations."""

from typing import Annotated

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult
from pydantic import Field

from .. import repository
from ..models import (
    DueWithinOption,
    SafeListName,
    SafeNote,
    SafeSearch,
    SafeUrl,
    validate_date,
    validate_safe_text,
    validate_url,
)
from ..utils import (
    format_delete_message,
    format_list_markdown,
    format_reminder_markdown,
    format_success_message,
    text_response,
)


async def list_reminders(
    filter_list: SafeListName = None,
    show_completed: bool = False,
    search: SafeSearch = None,
    due_within: DueWithinOption | None = None,
) -> ToolResult:
    """List reminders with optional filtering by list, completion status, search term, or due date.

    Args:
        filter_list: Filter reminders by a specific list name
        show_completed: Include completed reminders in the results
        search: Search term to filter reminders by title or notes
        due_within: Filter reminders by due date range (today, tomorrow, this-week, overdue, no-date)

    Returns:
        Markdown-formatted list of matching reminders
    """
    reminders = await repository.find_reminders(
        list_name=filter_list,
        show_completed=show_completed,
        search=search,
        due_within=due_within,
    )

    reminders_data = [
        {
            "id": r.id,
            "title": r.title,
            "isCompleted": r.is_completed,
            "list": r.list,
            "notes": r.notes,
            "url": r.url,
            "dueDate": r.due_date,
        }
        for r in reminders
    ]

    return text_response(
        format_list_markdown(
            "Reminders",
            reminders_data,
            format_reminder_markdown,
            "No reminders found matching the criteria.",
        )
    )


async def get_reminder(
    reminder_id: Annotated[str, Field(description="The unique identifier of the reminder")],
) -> ToolResult:
    """Get details for a specific reminder by ID.

    Args:
        reminder_id: The unique identifier of the reminder to retrieve

    Returns:
        Markdown-formatted reminder details
    """
    reminder = await repository.find_reminder_by_id(reminder_id)

    reminder_data = {
        "id": reminder.id,
        "title": reminder.title,
        "isCompleted": reminder.is_completed,
        "list": reminder.list,
        "notes": reminder.notes,
        "url": reminder.url,
        "dueDate": reminder.due_date,
    }

    lines = ["### Reminder", "", *format_reminder_markdown(reminder_data)]
    return text_response("\n".join(lines))


async def create_reminder(
    title: str,
    due_date: str | None = None,
    note: SafeNote = None,
    url: SafeUrl = None,
    target_list: SafeListName = None,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Create a new reminder. Requires confirmation before creating.

    Args:
        title: The title of the reminder
        due_date: Due date (recommended format: 'YYYY-MM-DD HH:mm:ss')
        note: Additional notes for the reminder
        url: A URL to associate with the reminder
        target_list: The list to create the reminder in (uses default if not specified)

    Returns:
        Confirmation message with the created reminder ID
    """
    validated_title = validate_safe_text(title, "Title", 200)
    if due_date:
        validate_date(due_date, "Due date")
    validated_url = validate_url(url)

    list_display = target_list or "default list"

    confirmation_message = (
        f"Create new reminder?\n\n"
        f"**Title:** {validated_title}\n"
        f"**List:** {list_display}\n"
    )
    if due_date:
        confirmation_message += f"**Due:** {due_date}\n"
    if note:
        confirmation_message += f"**Notes:** {note[:100]}{'...' if len(note) > 100 else ''}\n"
    if validated_url:
        confirmation_message += f"**URL:** {validated_url}\n"

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("Reminder creation cancelled.")

    from ..models import CreateReminderData
    data = CreateReminderData(
        title=validated_title,
        dueDate=due_date,
        notes=note,
        url=validated_url,
        list=target_list,
    )

    reminder = await repository.create_reminder(data)

    return text_response(
        format_success_message("created", "reminder", reminder.title, reminder.id)
    )


async def update_reminder(
    reminder_id: Annotated[str, Field(description="The unique identifier of the reminder to update")],
    title: str | None = None,
    due_date: str | None = None,
    note: SafeNote = None,
    url: SafeUrl = None,
    completed: bool | None = None,
    target_list: SafeListName = None,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Update an existing reminder. Requires confirmation before updating.

    Args:
        reminder_id: The unique identifier of the reminder to update
        title: New title for the reminder
        due_date: New due date
        note: New notes for the reminder
        url: New URL for the reminder
        completed: New completion status
        target_list: Move reminder to a different list

    Returns:
        Confirmation message with the updated reminder details
    """
    existing_reminder = await repository.find_reminder_by_id(reminder_id)

    validated_title = None
    if title:
        validated_title = validate_safe_text(title, "Title", 200)
    if due_date:
        validate_date(due_date, "Due date")
    validated_url = validate_url(url)

    changes = []
    if validated_title and validated_title != existing_reminder.title:
        changes.append(f"Title: '{existing_reminder.title}' → '{validated_title}'")
    if due_date and due_date != existing_reminder.due_date:
        changes.append(f"Due: '{existing_reminder.due_date}' → '{due_date}'")
    if target_list and target_list != existing_reminder.list:
        changes.append(f"List: '{existing_reminder.list}' → '{target_list}'")
    if note is not None and note != existing_reminder.notes:
        changes.append("Notes: updated")
    if validated_url is not None and validated_url != existing_reminder.url:
        changes.append("URL: updated")
    if completed is not None and completed != existing_reminder.is_completed:
        changes.append(f"Completed: {existing_reminder.is_completed} → {completed}")

    if not changes:
        return text_response(f"No changes detected for reminder '{existing_reminder.title}'.")

    confirmation_message = (
        f"Update reminder '{existing_reminder.title}'?\n\n"
        f"**Reminder ID:** {reminder_id}\n"
        f"**Changes:**\n" + "\n".join(f"- {c}" for c in changes) + "\n"
    )

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("Reminder update cancelled.")

    from ..models import UpdateReminderData
    data = UpdateReminderData(
        id=reminder_id,
        newTitle=validated_title,
        dueDate=due_date,
        notes=note,
        url=validated_url,
        isCompleted=completed,
        list=target_list,
    )

    reminder = await repository.update_reminder(data)

    return text_response(
        format_success_message("updated", "reminder", reminder.title, reminder.id)
    )


async def delete_reminder(
    reminder_id: Annotated[str, Field(description="The unique identifier of the reminder to delete")],
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Delete a reminder. Requires confirmation before deleting.

    This action is irreversible. The reminder will be permanently removed.

    Args:
        reminder_id: The unique identifier of the reminder to delete

    Returns:
        Confirmation message indicating the reminder was deleted
    """
    existing_reminder = await repository.find_reminder_by_id(reminder_id)

    confirmation_message = (
        f"**Permanently delete this reminder?**\n\n"
        f"**Title:** {existing_reminder.title}\n"
        f"**List:** {existing_reminder.list}\n"
        f"**Reminder ID:** {reminder_id}\n"
    )
    if existing_reminder.due_date:
        confirmation_message += f"**Due:** {existing_reminder.due_date}\n"
    confirmation_message += "\nThis action cannot be undone."

    result = await ctx.elicit(confirmation_message, response_type=None)
    if result.action != "accept":
        return text_response("Reminder deletion cancelled.")

    await repository.delete_reminder(reminder_id)

    return text_response(format_delete_message("reminder", reminder_id))
