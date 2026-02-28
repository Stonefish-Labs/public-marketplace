from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest
from fastmcp.client import Client

import server
from config import ConfigError


@dataclass
class FakeEntry:
    name: str
    quantity: float
    unit: str
    nutrition_information: dict


@dataclass
class FakeMeal:
    name: str
    totals: dict
    entries: list[FakeEntry]


@dataclass
class FakeExerciseGroup:
    entries: list[FakeEntry]


@dataclass
class FakeDay:
    date: date
    totals: dict
    goals: dict
    water: float
    complete: bool
    meals: list[FakeMeal]
    exercises: list[FakeExerciseGroup]


class FakeClient:
    def __init__(self, day: FakeDay) -> None:
        self._day = day

    def get_day(self, target_date: date) -> FakeDay:
        return FakeDay(
            date=target_date,
            totals=self._day.totals,
            goals=self._day.goals,
            water=self._day.water,
            complete=self._day.complete,
            meals=self._day.meals,
            exercises=self._day.exercises,
        )

    def get_date_range(self, start_date: date, end_date: date):
        current = start_date
        while current <= end_date:
            yield self.get_day(current)
            current = current.fromordinal(current.toordinal() + 1)


def first_text(result) -> str:
    block = result.content[0]
    return getattr(block, "text", "")


@pytest.fixture
def fake_day() -> FakeDay:
    return FakeDay(
        date=date(2026, 1, 1),
        totals={
            "calories": 2100,
            "carbohydrates": 220,
            "fat": 70,
            "protein": 150,
            "fiber": 30,
        },
        goals={
            "calories": 2400,
            "carbohydrates": 250,
            "fat": 80,
            "protein": 170,
            "fiber": 35,
        },
        water=1800,
        complete=True,
        meals=[
            FakeMeal(
                name="Breakfast",
                totals={"calories": 600, "carbohydrates": 60, "fat": 20, "protein": 35},
                entries=[
                    FakeEntry(
                        name="Greek Yogurt",
                        quantity=1,
                        unit="cup",
                        nutrition_information={
                            "calories": 220,
                            "carbohydrates": 12,
                            "fat": 4,
                            "protein": 22,
                        },
                    )
                ],
            )
        ],
        exercises=[
            FakeExerciseGroup(
                entries=[
                    FakeEntry(
                        name="Running",
                        quantity=1,
                        unit="session",
                        nutrition_information={"minutes": 30, "calories burned": 320},
                    )
                ]
            )
        ],
    )


@pytest.fixture
async def client():
    async with Client(transport=server.mcp) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_global_client():
    server._client = None
    yield
    server._client = None


@pytest.mark.asyncio
async def test_list_tools(client):
    tools = await client.list_tools()
    names = {tool.name for tool in tools}
    assert "get_daily_summary" in names
    assert "get_date_range_summary" in names


@pytest.mark.asyncio
async def test_get_daily_summary(client, fake_day, monkeypatch):
    monkeypatch.setattr(server, "get_client", lambda: FakeClient(fake_day))
    result = await client.call_tool("get_daily_summary", {"date": "2026-01-02"})
    text = first_text(result)
    assert "Daily Summary for January 02, 2026" in text
    assert "Consumed" in text


@pytest.mark.asyncio
async def test_date_range_summary(client, fake_day, monkeypatch):
    monkeypatch.setattr(server, "get_client", lambda: FakeClient(fake_day))
    result = await client.call_tool(
        "get_date_range_summary",
        {"start_date": "2026-01-01", "end_date": "2026-01-03"},
    )
    text = first_text(result)
    assert "Date Range Summary" in text
    assert "(3 days)" in text


@pytest.mark.asyncio
async def test_invalid_date_error(client):
    result = await client.call_tool("get_daily_summary", {"date": "2026/01/01"})
    assert "Invalid date format" in first_text(result)


@pytest.mark.asyncio
async def test_config_error_is_generic(client, monkeypatch):
    def _raise_config_error():
        raise ConfigError("env var not set")

    monkeypatch.setattr(server, "get_client", _raise_config_error)
    result = await client.call_tool("get_daily_summary", {})
    text = first_text(result)
    assert "configuration setup needed" in text
    assert "env var not set" in text


def test_decorated_tool_direct_call(fake_day, monkeypatch):
    monkeypatch.setattr(server, "get_client", lambda: FakeClient(fake_day))
    result = server.get_daily_summary("2026-01-02")
    assert "Daily Summary for January 02, 2026" in first_text(result)
