"""Pydantic models for reminders and reminder lists."""

import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


SAFE_TEXT_PATTERN = re.compile(r"^[\u0020-\u007E\u00A0-\uFFFF\n\r\t]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}.*$")
URL_PATTERN = re.compile(
    r"^https?://(?!(?:127\.|192\.168\.|10\.|localhost|0\.0\.0\.0))"
    r"[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
    r"(?:\/[^\s<>\"{}|\\^`[\]]*)?$",
    re.IGNORECASE,
)


class Validation:
    MAX_TITLE_LENGTH = 200
    MAX_NOTE_LENGTH = 2000
    MAX_LIST_NAME_LENGTH = 100
    MAX_SEARCH_LENGTH = 100
    MAX_URL_LENGTH = 500


def validate_safe_text(value: str, field_name: str, max_length: int) -> str:
    if len(value) == 0:
        raise ValueError(f"{field_name} cannot be empty")
    if len(value) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    if not SAFE_TEXT_PATTERN.match(value):
        raise ValueError(
            f"{field_name} contains invalid characters. "
            "Only alphanumeric, spaces, and basic punctuation allowed"
        )
    return value


def validate_optional_safe_text(value: str | None, field_name: str, max_length: int) -> str | None:
    if value is None:
        return None
    if len(value) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    if not SAFE_TEXT_PATTERN.match(value):
        raise ValueError(f"{field_name} contains invalid characters")
    return value


def validate_date(value: str, field_name: str = "Date") -> str:
    if not DATE_PATTERN.match(value):
        raise ValueError(
            f"{field_name} must be in format 'YYYY-MM-DD', 'YYYY-MM-DD HH:mm:ss', or ISO 8601"
        )
    return value


def validate_url(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) > Validation.MAX_URL_LENGTH:
        raise ValueError(f"URL cannot exceed {Validation.MAX_URL_LENGTH} characters")
    if not URL_PATTERN.match(value):
        raise ValueError("URL must be a valid HTTP or HTTPS URL")
    return value


SafeTitle = Annotated[
    str,
    Field(
        min_length=1,
        max_length=Validation.MAX_TITLE_LENGTH,
        description="The title of the reminder",
    ),
]

SafeTitleOptional = Annotated[
    str | None,
    Field(
        default=None,
        min_length=1,
        max_length=Validation.MAX_TITLE_LENGTH,
        description="The title of the reminder",
    ),
]

SafeNote = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_NOTE_LENGTH,
        description="Additional notes for the reminder",
    ),
]

SafeListName = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_LIST_NAME_LENGTH,
        description="The name of the reminder list",
    ),
]

SafeListNameRequired = Annotated[
    str,
    Field(
        min_length=1,
        max_length=Validation.MAX_LIST_NAME_LENGTH,
        description="The name of the reminder list",
    ),
]

SafeSearch = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_SEARCH_LENGTH,
        description="Search term to filter reminders",
    ),
]

SafeUrl = Annotated[
    str | None,
    Field(default=None, description="A URL to associate with the reminder"),
]

DueWithinOption = Literal["today", "tomorrow", "this-week", "overdue", "no-date"]


class ReminderList(BaseModel):
    id: str
    title: str


class Reminder(BaseModel):
    id: str
    title: str
    is_completed: bool = Field(alias="isCompleted")
    list: str
    notes: str | None = None
    url: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")


class RemindersReadResult(BaseModel):
    lists: list[ReminderList]
    reminders: list[Reminder]


class CreateReminderData(BaseModel):
    title: str
    notes: str | None = None
    url: str | None = None
    list: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")


class UpdateReminderData(BaseModel):
    id: str
    new_title: str | None = Field(default=None, alias="newTitle")
    notes: str | None = None
    url: str | None = None
    is_completed: bool | None = Field(default=None, alias="isCompleted")
    list: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")
