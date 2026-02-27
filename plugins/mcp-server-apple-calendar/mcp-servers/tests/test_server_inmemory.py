# pyright: reportMissingImports=false

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.client import Client
from fastmcp.client.elicitation import ElicitResult
from mcp.types import TextContent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from apple_calendar.server import mcp


def first_text(result) -> str:
    block = result.content[0]
    assert isinstance(block, TextContent)
    return block.text


@pytest.mark.asyncio
async def test_inmemory_lists_expected_tools() -> None:
    async with Client(transport=mcp) as client:
        tools = await client.list_tools()

    tool_names = {tool.name for tool in tools}
    assert tool_names == {
        "list_calendar_events",
        "get_calendar_event",
        "create_calendar_event",
        "update_calendar_event",
        "delete_calendar_event",
        "list_calendars",
    }


@pytest.mark.asyncio
async def test_list_calendars_returns_text_output() -> None:
    calendars = [
        SimpleNamespace(title="Home", id="cal_home"),
        SimpleNamespace(title="Work", id="cal_work"),
    ]
    with patch(
        "apple_calendar.tools.calendars.repository.find_all_calendars",
        new=AsyncMock(return_value=calendars),
    ):
        async with Client(transport=mcp) as client:
            result = await client.call_tool("list_calendars")

    assert result.is_error is False
    assert "### Calendars (Total: 2)" in first_text(result)
    assert "- Home (ID: cal_home)" in first_text(result)


@pytest.mark.asyncio
async def test_create_event_accept_path_executes_repository_call() -> None:
    async def accept_create(*_args, **_kwargs):
        return ElicitResult(action="accept", content={"value": "yes, create event"})

    created_event = SimpleNamespace(title="Planning", id="evt_123")

    with patch(
        "apple_calendar.tools.events.repository.create_event",
        new=AsyncMock(return_value=created_event),
    ) as create_event_mock:
        async with Client(transport=mcp, elicitation_handler=accept_create) as client:
            result = await client.call_tool(
                "create_calendar_event",
                {
                    "title": "Planning",
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-01",
                },
            )

    assert create_event_mock.await_count == 1
    assert result.is_error is False
    assert "Successfully created event \"Planning\"." in first_text(result)


@pytest.mark.asyncio
async def test_delete_event_cancel_path_does_not_delete() -> None:
    async def cancel_delete(*_args, **_kwargs):
        return ElicitResult(action="cancel", content={})

    existing_event = SimpleNamespace(
        title="Old Meeting",
        calendar="Work",
        start_date="2026-03-05",
    )

    with patch(
        "apple_calendar.tools.events.repository.find_event_by_id",
        new=AsyncMock(return_value=existing_event),
    ), patch(
        "apple_calendar.tools.events.repository.delete_event",
        new=AsyncMock(),
    ) as delete_event_mock:
        async with Client(transport=mcp, elicitation_handler=cancel_delete) as client:
            result = await client.call_tool("delete_calendar_event", {"event_id": "evt_1"})

    assert delete_event_mock.await_count == 0
    assert result.is_error is False
    assert first_text(result) == "Event deletion cancelled."
