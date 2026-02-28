import pytest
from fastmcp.client import Client

import server


@pytest.fixture
async def client():
    async with Client(transport=server.mcp) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_list_workout_dates_filters_range(client, monkeypatch):
    monkeypatch.setattr(
        server,
        "get_workout_history",
        lambda: ["2025-10-15", "2025-10-17", "2025-10-19"],
    )

    result = await client.call_tool(
        "list_workout_dates",
        {"start_date": "2025-10-16", "end_date": "2025-10-18"},
    )
    assert result.data == ["2025-10-17"]


@pytest.mark.asyncio
async def test_get_workout_info_no_data_returns_text(client, monkeypatch):
    monkeypatch.setattr(server, "get_workout_for_date", lambda _: {"data": []})
    monkeypatch.setattr(server, "get_exercise_db", lambda: {})

    result = await client.call_tool("get_workout_info", {"date": "2025-10-17"})
    assert "No workout found for this date." in result.content[0].text


@pytest.mark.asyncio
async def test_get_batch_workouts_sorts_dates(client, monkeypatch):
    data_by_date = {
        "2025-10-17": {
            "data": [
                {
                    "date": 1760659200,
                    "total_time": 1800,
                    "total_weight": 5000,
                    "logs": [
                        {
                            "exercise_id": "ex1",
                            "log_sets": [{"weight": 100, "reps": 8}],
                        }
                    ],
                }
            ]
        },
        "2025-10-15": {"data": []},
    }

    monkeypatch.setattr(server, "get_workout_for_date", lambda date: data_by_date[date])
    monkeypatch.setattr(
        server,
        "get_exercise_db",
        lambda: {"ex1": {"name": "Bench Press", "body_parts": ["Chest"], "equipment": ["Barbell"]}},
    )

    result = await client.call_tool(
        "get_batch_workouts",
        {"dates": ["2025-10-17", "2025-10-15"]},
    )
    text = result.content[0].text
    assert text.index("# Workout for 2025-10-15") < text.index("# Workout for 2025-10-17")
    assert "Bench Press" in text
