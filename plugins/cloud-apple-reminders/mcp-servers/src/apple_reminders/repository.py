"""Repository for reminder operations via Swift CLI."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .models import (
    CreateReminderData,
    Reminder,
    ReminderList,
    UpdateReminderData,
)


class ReminderRepositoryError(Exception):
    """Base exception for reminder repository errors."""
    pass


class PermissionError(ReminderRepositoryError):
    """Raised when macOS permissions are denied."""
    pass


def _permission_help_text() -> str:
    """Return actionable guidance when Reminders permission is denied."""
    return (
        "Reminders permission denied. Grant access in:\n"
        "System Settings > Privacy & Security > Reminders\n"
        "If the prompt does not appear, run:\n"
        "osascript -e 'tell application \"Reminders\" to get the name of every list'"
    )


def _bootstrap_reminders_prompt() -> tuple[bool, str | None]:
    """Trigger the Reminders permission prompt using AppleScript."""
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "Reminders" to get the name of every list',
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)

    if result.returncode == 0:
        return True, None

    error_output = (result.stderr or result.stdout or "osascript failed").strip()
    return False, error_output


def _get_binary_path() -> Path:
    """Get path to the EventKitCLI binary."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent / "apple_reminders" / "bin"
    else:
        base = Path(__file__).parent / "bin"
    return base / "EventKitCLI"


async def _execute_cli(args: list[str]) -> dict[str, Any]:
    """Execute the Swift CLI and return parsed JSON result."""
    binary_path = _get_binary_path()

    if not binary_path.exists():
        raise ReminderRepositoryError(
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
            raise ReminderRepositoryError("EventKitCLI returned invalid JSON")
    elif stderr:
        error_msg = stderr.decode("utf-8")
        if "permission" in error_msg.lower() or "authoriz" in error_msg.lower():
            raise PermissionError(_permission_help_text())
        raise ReminderRepositoryError(f"EventKitCLI error: {error_msg}")
    else:
        raise ReminderRepositoryError("EventKitCLI returned no output")

    if result.get("status") == "error":
        message = result.get("message", "Unknown error")
        if "permission" in message.lower() or "authoriz" in message.lower():
            raise PermissionError(f"{message}\n\n{_permission_help_text()}")
        raise ReminderRepositoryError(message)

    return result.get("result", result)


async def find_all_lists() -> list[ReminderList]:
    """Fetch all available reminder lists."""
    result = await _execute_cli(["--action", "read-lists"])
    return [ReminderList.model_validate(l) for l in result]


async def find_reminders(
    list_name: str | None = None,
    show_completed: bool = False,
    search: str | None = None,
    due_within: str | None = None,
) -> list[Reminder]:
    """Fetch reminders with optional filters."""
    args = ["--action", "read", "--showCompleted", "true"]
    if list_name:
        args.extend(["--filterList", list_name])
    if search:
        args.extend(["--search", search])
    if due_within:
        args.extend(["--dueWithin", due_within])

    result = await _execute_cli(args)
    reminders_data = result.get("reminders", [])
    
    reminders = [Reminder.model_validate(r) for r in reminders_data]
    
    if not show_completed:
        reminders = [r for r in reminders if not r.is_completed]
    
    return reminders


async def find_reminder_by_id(reminder_id: str) -> Reminder:
    """Fetch a single reminder by ID."""
    reminders = await find_reminders(show_completed=True)
    for reminder in reminders:
        if reminder.id == reminder_id:
            return reminder
    raise ReminderRepositoryError(f"Reminder with ID '{reminder_id}' not found.")


async def create_reminder(data: CreateReminderData) -> Reminder:
    """Create a new reminder."""
    args = ["--action", "create", "--title", data.title]
    if data.list:
        args.extend(["--targetList", data.list])
    if data.notes:
        args.extend(["--note", data.notes])
    if data.url:
        args.extend(["--url", data.url])
    if data.due_date:
        args.extend(["--dueDate", data.due_date])

    result = await _execute_cli(args)
    return Reminder.model_validate(result)


async def update_reminder(data: UpdateReminderData) -> Reminder:
    """Update an existing reminder."""
    args = ["--action", "update", "--id", data.id]
    if data.new_title:
        args.extend(["--title", data.new_title])
    if data.list:
        args.extend(["--targetList", data.list])
    if data.notes:
        args.extend(["--note", data.notes])
    if data.url:
        args.extend(["--url", data.url])
    if data.is_completed is not None:
        args.extend(["--isCompleted", str(data.is_completed).lower()])
    if data.due_date:
        args.extend(["--dueDate", data.due_date])

    result = await _execute_cli(args)
    return Reminder.model_validate(result)


async def delete_reminder(reminder_id: str) -> None:
    """Delete a reminder."""
    await _execute_cli(["--action", "delete", "--id", reminder_id])


async def create_reminder_list(name: str) -> ReminderList:
    """Create a new reminder list."""
    result = await _execute_cli(["--action", "create-list", "--name", name])
    return ReminderList.model_validate(result)


async def update_reminder_list(current_name: str, new_name: str) -> ReminderList:
    """Rename a reminder list."""
    result = await _execute_cli([
        "--action", "update-list",
        "--name", current_name,
        "--newName", new_name,
    ])
    return ReminderList.model_validate(result)


async def delete_reminder_list(name: str) -> None:
    """Delete a reminder list."""
    await _execute_cli(["--action", "delete-list", "--name", name])


async def preflight_permissions(auto_bootstrap: bool = True) -> tuple[bool, str | None]:
    """Verify Reminders access and optionally trigger permission bootstrap."""
    try:
        await find_all_lists()
        return True, None
    except PermissionError as exc:
        if auto_bootstrap:
            bootstrapped, bootstrap_error = _bootstrap_reminders_prompt()
            if bootstrapped:
                try:
                    await find_all_lists()
                    return True, "Reminders permission bootstrap succeeded."
                except PermissionError:
                    pass
            elif bootstrap_error:
                return False, f"{exc}\n\nBootstrap attempt failed: {bootstrap_error}"
        return False, str(exc)
    except ReminderRepositoryError as exc:
        return False, str(exc)
