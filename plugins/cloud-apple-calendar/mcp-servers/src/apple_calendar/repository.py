"""Repository for calendar operations via Swift CLI."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import Calendar, CreateEventData, Event, EventsReadResult, UpdateEventData


class CalendarRepositoryError(Exception):
    """Base exception for calendar repository errors."""
    pass


class PermissionError(CalendarRepositoryError):
    """Raised when macOS permissions are denied."""
    pass


def _get_binary_path() -> Path:
    """Get path to the EventKitCLI binary."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent / "apple_calendar" / "bin"
    else:
        base = Path(__file__).parent / "bin"
    return base / "EventKitCLI"


async def _execute_cli(args: list[str]) -> dict[str, Any]:
    """Execute the Swift CLI and return parsed JSON result."""
    binary_path = _get_binary_path()

    if not binary_path.exists():
        raise CalendarRepositoryError(
            f"EventKitCLI binary not found at {binary_path}. "
            "Run 'python scripts/build_swift.py' to build it."
        )

    process = await asyncio.create_subprocess_exec(
        str(binary_path),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if stdout:
        try:
            result = json.loads(stdout.decode("utf-8"))
        except json.JSONDecodeError:
            raise CalendarRepositoryError("EventKitCLI returned invalid JSON")
    elif stderr:
        error_msg = stderr.decode("utf-8")
        if "permission" in error_msg.lower() or "authoriz" in error_msg.lower():
            raise PermissionError(
                f"Calendar permission denied. Grant access in:\n"
                "System Settings > Privacy & Security > Calendars"
            )
        raise CalendarRepositoryError(f"EventKitCLI error: {error_msg}")
    else:
        raise CalendarRepositoryError("EventKitCLI returned no output")

    if result.get("status") == "error":
        message = result.get("message", "Unknown error")
        if "permission" in message.lower() or "authoriz" in message.lower():
            raise PermissionError(message)
        raise CalendarRepositoryError(message)

    return result.get("result", result)


async def find_all_calendars() -> list[Calendar]:
    """Fetch all available calendars."""
    result = await _execute_cli(["--action", "read-calendars"])
    return [Calendar.model_validate(c) for c in result]


async def find_events(
    start_date: str | None = None,
    end_date: str | None = None,
    calendar_name: str | None = None,
    search: str | None = None,
) -> list[Event]:
    """Fetch events with optional filters."""
    args = ["--action", "read-events"]
    if start_date:
        args.extend(["--startDate", start_date])
    if end_date:
        args.extend(["--endDate", end_date])
    if calendar_name:
        args.extend(["--filterCalendar", calendar_name])
    if search:
        args.extend(["--search", search])

    result = await _execute_cli(args)
    events_data = result.get("events", [])
    return [Event.model_validate(e) for e in events_data]


async def find_event_by_id(event_id: str) -> Event:
    """Fetch a single event by ID."""
    events = await find_events()
    for event in events:
        if event.id == event_id:
            return event
    raise CalendarRepositoryError(f"Event with ID '{event_id}' not found.")


async def create_event(data: CreateEventData) -> Event:
    """Create a new calendar event."""
    args = [
        "--action", "create-event",
        "--title", data.title,
        "--startDate", data.start_date,
        "--endDate", data.end_date,
    ]
    if data.calendar:
        args.extend(["--targetCalendar", data.calendar])
    if data.notes:
        args.extend(["--note", data.notes])
    if data.location:
        args.extend(["--location", data.location])
    if data.url:
        args.extend(["--url", data.url])
    if data.is_all_day is not None:
        args.extend(["--isAllDay", str(data.is_all_day).lower()])

    result = await _execute_cli(args)
    return Event.model_validate(result)


async def update_event(data: UpdateEventData) -> Event:
    """Update an existing calendar event."""
    args = ["--action", "update-event", "--id", data.id]
    if data.title:
        args.extend(["--title", data.title])
    if data.calendar:
        args.extend(["--targetCalendar", data.calendar])
    if data.start_date:
        args.extend(["--startDate", data.start_date])
    if data.end_date:
        args.extend(["--endDate", data.end_date])
    if data.notes:
        args.extend(["--note", data.notes])
    if data.location:
        args.extend(["--location", data.location])
    if data.url:
        args.extend(["--url", data.url])
    if data.is_all_day is not None:
        args.extend(["--isAllDay", str(data.is_all_day).lower()])

    result = await _execute_cli(args)
    return Event.model_validate(result)


async def delete_event(event_id: str) -> None:
    """Delete a calendar event."""
    await _execute_cli(["--action", "delete-event", "--id", event_id])
