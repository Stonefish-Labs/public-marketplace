from types import SimpleNamespace

import pytest
from fastmcp.client import Client
from fastmcp.client.elicitation import ElicitResult

from apple_reminders.server import mcp
from apple_reminders.tools import reminders as reminders_tools


async def _accept_elicitation(_message, _response_type, _params, _context):
    return ElicitResult(action="accept")


async def _cancel_elicitation(_message, _response_type, _params, _context):
    return ElicitResult(action="cancel")


@pytest.mark.asyncio
async def test_tool_annotations_are_registered():
    async with Client(transport=mcp) as client:
        tools = await client.list_tools()

    by_name = {tool.name: tool for tool in tools}

    assert by_name["list_reminders"].annotations.readOnlyHint is True
    assert by_name["list_reminders"].annotations.idempotentHint is True
    assert by_name["create_reminder"].annotations.readOnlyHint is False
    assert by_name["create_reminder"].annotations.destructiveHint is False
    assert by_name["delete_reminder"].annotations.destructiveHint is True
    assert by_name["delete_reminder_list"].annotations.destructiveHint is True


@pytest.mark.asyncio
async def test_list_reminders_returns_text(monkeypatch):
    fake_reminders = [
        SimpleNamespace(
            id="r1",
            title="Buy milk",
            is_completed=False,
            list="Personal",
            notes="2%",
            url=None,
            due_date="2026-03-01",
        )
    ]

    async def fake_find_reminders(**_kwargs):
        return fake_reminders

    monkeypatch.setattr(reminders_tools.repository, "find_reminders", fake_find_reminders)

    async with Client(transport=mcp) as client:
        result = await client.call_tool("list_reminders", {})

    assert "### Reminders" in result.content[0].text
    assert "Buy milk" in result.content[0].text


@pytest.mark.asyncio
async def test_create_reminder_cancelled(monkeypatch):
    called = False

    async def fake_create_reminder(_data):
        nonlocal called
        called = True
        return SimpleNamespace(
            id="r2",
            title="Should not be created",
            is_completed=False,
            list="Personal",
            notes=None,
            url=None,
            due_date=None,
        )

    monkeypatch.setattr(reminders_tools.repository, "create_reminder", fake_create_reminder)

    async with Client(transport=mcp, elicitation_handler=_cancel_elicitation) as client:
        result = await client.call_tool("create_reminder", {"title": "Cancel me"})

    assert called is False
    assert result.content[0].text == "Reminder creation cancelled."


@pytest.mark.asyncio
async def test_create_reminder_accepts_and_writes(monkeypatch):
    async def fake_create_reminder(_data):
        return SimpleNamespace(
            id="r3",
            title="Created",
            is_completed=False,
            list="Personal",
            notes=None,
            url=None,
            due_date=None,
        )

    monkeypatch.setattr(reminders_tools.repository, "create_reminder", fake_create_reminder)

    async with Client(transport=mcp, elicitation_handler=_accept_elicitation) as client:
        result = await client.call_tool("create_reminder", {"title": "Created"})

    assert "Successfully created reminder" in result.content[0].text
    assert '"Created"' in result.content[0].text
