"""Pydantic models for calendar events and calendars."""

import re
from typing import Annotated

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
    MAX_CALENDAR_NAME_LENGTH = 100
    MAX_SEARCH_LENGTH = 100
    MAX_URL_LENGTH = 500
    MAX_LOCATION_LENGTH = 200


def validate_safe_text(value: str, field_name: str, max_length: int) -> str:
    if len(value) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    if not SAFE_TEXT_PATTERN.match(value):
        raise ValueError(
            f"{field_name} contains invalid characters. "
            "Only alphanumeric, spaces, and basic punctuation allowed"
        )
    return value


def validate_date(value: str, field_name: str) -> str:
    if not DATE_PATTERN.match(value):
        raise ValueError(
            f"{field_name} must be in format 'YYYY-MM-DD', 'YYYY-MM-DD HH:mm:ss', or ISO 8601"
        )
    return value


def validate_url(value: str) -> str:
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
        description="The title of the event",
    ),
]

SafeTitleOptional = Annotated[
    str | None,
    Field(
        default=None,
        min_length=1,
        max_length=Validation.MAX_TITLE_LENGTH,
        description="The title of the event",
    ),
]

SafeNote = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_NOTE_LENGTH,
        description="Additional notes for the event",
    ),
]

SafeCalendarName = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_CALENDAR_NAME_LENGTH,
        description="The name of the calendar",
    ),
]

SafeLocation = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_LOCATION_LENGTH,
        description="Location for the event",
    ),
]

SafeUrl = Annotated[
    str | None,
    Field(default=None, description="A URL to associate with the event"),
]

SafeSearch = Annotated[
    str | None,
    Field(
        default=None,
        max_length=Validation.MAX_SEARCH_LENGTH,
        description="Search term to filter events",
    ),
]


class Calendar(BaseModel):
    id: str
    title: str


class Event(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    calendar: str
    start_date: str = Field(alias="startDate")
    end_date: str = Field(alias="endDate")
    notes: str | None = None
    location: str | None = None
    url: str | None = None
    is_all_day: bool = Field(default=False, alias="isAllDay")


class EventsReadResult(BaseModel):
    calendars: list[Calendar]
    events: list[Event]


class CreateEventData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    start_date: str = Field(alias="startDate")
    end_date: str = Field(alias="endDate")
    calendar: str | None = None
    notes: str | None = None
    location: str | None = None
    url: str | None = None
    is_all_day: bool | None = Field(default=None, alias="isAllDay")


class UpdateEventData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str | None = None
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    calendar: str | None = None
    notes: str | None = None
    location: str | None = None
    url: str | None = None
    is_all_day: bool | None = Field(default=None, alias="isAllDay")
