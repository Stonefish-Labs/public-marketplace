"""Calendar event tools with elicitation for write operations."""

from typing import Annotated

from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult
from pydantic import Field

from .. import repository
from ..models import (
    CreateEventData,
    SafeCalendarName,
    SafeLocation,
    SafeNote,
    SafeSearch,
    SafeTitle,
    SafeTitleOptional,
    SafeUrl,
    UpdateEventData,
    validate_date,
)
from ..utils import (
    format_delete_message,
    format_event_markdown,
    format_list_markdown,
    format_success_message,
    text_response,
)


def _is_confirmed(result: object, expected_response: str) -> bool:
    if getattr(result, "action", None) != "accept":
        return False

    data = getattr(result, "data", None)
    if data == expected_response:
        return True

    if isinstance(data, dict):
        for value in data.values():
            if value == expected_response:
                return True

    return False


async def list_calendar_events(
    start_date: str | None = None,
    end_date: str | None = None,
    calendar: SafeCalendarName = None,
    search: SafeSearch = None,
) -> ToolResult:
    """List calendar events with optional filtering by date range, calendar, or search term.

    Args:
        start_date: Filter events starting after this date (YYYY-MM-DD or ISO 8601)
        end_date: Filter events ending before this date (YYYY-MM-DD or ISO 8601)
        calendar: Filter events by calendar name
        search: Search term to filter events by title, notes, or location

    Returns:
        Markdown-formatted list of matching events
    """
    events = await repository.find_events(
        start_date=start_date,
        end_date=end_date,
        calendar_name=calendar,
        search=search,
    )

    events_data = [
        {
            "id": e.id,
            "title": e.title,
            "calendar": e.calendar,
            "startDate": e.start_date,
            "endDate": e.end_date,
            "notes": e.notes,
            "location": e.location,
            "url": e.url,
            "isAllDay": e.is_all_day,
        }
        for e in events
    ]

    return text_response(
        format_list_markdown(
            "Calendar Events",
            events_data,
            format_event_markdown,
            "No calendar events found.",
        )
    )


async def get_calendar_event(
    event_id: Annotated[str, Field(description="The unique identifier of the event")],
) -> ToolResult:
    """Get details for a specific calendar event by ID.

    Args:
        event_id: The unique identifier of the event to retrieve

    Returns:
        Markdown-formatted event details
    """
    event = await repository.find_event_by_id(event_id)

    event_data = {
        "id": event.id,
        "title": event.title,
        "calendar": event.calendar,
        "startDate": event.start_date,
        "endDate": event.end_date,
        "notes": event.notes,
        "location": event.location,
        "url": event.url,
        "isAllDay": event.is_all_day,
    }

    return text_response("\n".join(format_event_markdown(event_data)))


async def create_calendar_event(
    title: SafeTitle,
    start_date: Annotated[str, Field(description="Start date/time (YYYY-MM-DD HH:mm:ss or ISO 8601)")],
    end_date: Annotated[str, Field(description="End date/time (YYYY-MM-DD HH:mm:ss or ISO 8601)")],
    calendar: SafeCalendarName = None,
    notes: SafeNote = None,
    location: SafeLocation = None,
    url: SafeUrl = None,
    is_all_day: bool = False,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Create a new calendar event. Requires confirmation before creating.

    Args:
        title: The title of the event
        start_date: Start date and time (recommended: 'YYYY-MM-DD HH:mm:ss')
        end_date: End date and time (recommended: 'YYYY-MM-DD HH:mm:ss')
        calendar: The calendar to create the event in (uses default if not specified)
        notes: Additional notes for the event
        location: Location for the event
        url: A URL to associate with the event
        is_all_day: Whether this is an all-day event

    Returns:
        Confirmation message with the created event ID
    """
    validate_date(start_date, "Start date")
    validate_date(end_date, "End date")

    calendar_display = calendar or "default calendar"

    confirmation_message = (
        f"Create new calendar event?\n\n"
        f"**Title:** {title}\n"
        f"**Calendar:** {calendar_display}\n"
        f"**Start:** {start_date}\n"
        f"**End:** {end_date}\n"
    )
    if location:
        confirmation_message += f"**Location:** {location}\n"
    if notes:
        confirmation_message += f"**Notes:** {notes[:100]}{'...' if len(notes) > 100 else ''}\n"
    if is_all_day:
        confirmation_message += "**All Day:** Yes\n"

    result = await ctx.elicit(
        confirmation_message,
        response_type=["yes, create event", "cancel"],
    )
    if not _is_confirmed(result, "yes, create event"):
        return text_response("Event creation cancelled.")

    data = CreateEventData(
        title=title,
        startDate=start_date,
        endDate=end_date,
        calendar=calendar,
        notes=notes,
        location=location,
        url=url,
        isAllDay=is_all_day,
    )

    event = await repository.create_event(data)

    return text_response(
        format_success_message("created", "event", event.title, event.id)
    )


async def update_calendar_event(
    event_id: Annotated[str, Field(description="The unique identifier of the event to update")],
    title: SafeTitleOptional = None,
    start_date: str | None = None,
    end_date: str | None = None,
    calendar: SafeCalendarName = None,
    notes: SafeNote = None,
    location: SafeLocation = None,
    url: SafeUrl = None,
    is_all_day: bool | None = None,
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Update an existing calendar event. Requires confirmation before updating.

    Args:
        event_id: The unique identifier of the event to update
        title: New title for the event
        start_date: New start date/time
        end_date: New end date/time
        calendar: Move event to a different calendar
        notes: New notes for the event
        location: New location for the event
        url: New URL for the event
        is_all_day: Change all-day status

    Returns:
        Confirmation message with the updated event details
    """
    existing_event = await repository.find_event_by_id(event_id)

    if start_date:
        validate_date(start_date, "Start date")
    if end_date:
        validate_date(end_date, "End date")

    changes = []
    if title and title != existing_event.title:
        changes.append(f"Title: '{existing_event.title}' → '{title}'")
    if start_date and start_date != existing_event.start_date:
        changes.append(f"Start: '{existing_event.start_date}' → '{start_date}'")
    if end_date and end_date != existing_event.end_date:
        changes.append(f"End: '{existing_event.end_date}' → '{end_date}'")
    if calendar and calendar != existing_event.calendar:
        changes.append(f"Calendar: '{existing_event.calendar}' → '{calendar}'")
    if notes is not None and notes != existing_event.notes:
        changes.append("Notes: updated")
    if location is not None and location != existing_event.location:
        changes.append(f"Location: '{existing_event.location}' → '{location}'")
    if url is not None and url != existing_event.url:
        changes.append("URL: updated")
    if is_all_day is not None and is_all_day != existing_event.is_all_day:
        changes.append(f"All Day: {existing_event.is_all_day} → {is_all_day}")

    if not changes:
        return text_response(f"No changes detected for event '{existing_event.title}'.")

    confirmation_message = (
        f"Update calendar event '{existing_event.title}'?\n\n"
        f"**Event ID:** {event_id}\n"
        f"**Changes:**\n" + "\n".join(f"- {c}" for c in changes) + "\n"
    )

    result = await ctx.elicit(
        confirmation_message,
        response_type=["yes, update event", "cancel"],
    )
    if not _is_confirmed(result, "yes, update event"):
        return text_response("Event update cancelled.")

    data = UpdateEventData(
        id=event_id,
        title=title,
        startDate=start_date,
        endDate=end_date,
        calendar=calendar,
        notes=notes,
        location=location,
        url=url,
        isAllDay=is_all_day,
    )

    event = await repository.update_event(data)

    return text_response(
        format_success_message("updated", "event", event.title, event.id)
    )


async def delete_calendar_event(
    event_id: Annotated[str, Field(description="The unique identifier of the event to delete")],
    ctx: Context = CurrentContext(),
) -> ToolResult:
    """Delete a calendar event. Requires confirmation before deleting.

    This action is irreversible. The event will be permanently removed.

    Args:
        event_id: The unique identifier of the event to delete

    Returns:
        Confirmation message indicating the event was deleted
    """
    existing_event = await repository.find_event_by_id(event_id)

    confirmation_message = (
        f"**Permanently delete this calendar event?**\n\n"
        f"**Title:** {existing_event.title}\n"
        f"**Calendar:** {existing_event.calendar}\n"
        f"**Event ID:** {event_id}\n"
        f"**Start:** {existing_event.start_date}\n\n"
        f"This action cannot be undone."
    )

    result = await ctx.elicit(
        confirmation_message,
        response_type=["yes, delete permanently", "cancel"],
    )
    if not _is_confirmed(result, "yes, delete permanently"):
        return text_response("Event deletion cancelled.")

    await repository.delete_event(event_id)

    return text_response(format_delete_message("event", event_id))
