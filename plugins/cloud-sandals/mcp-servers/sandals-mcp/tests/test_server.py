"""
In-memory tests for SandalsBoujieBot MCP Server (FastMCP 3.x)
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

# Add parent directory to path so imports resolve
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp.client import Client
from server import mcp, availability_checker, price_monitor


@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c


# ---------------------------------------------------------------------------
# Tool listing
# ---------------------------------------------------------------------------


async def test_list_tools(client):
    tools = await client.list_tools()
    tool_names = {t.name for t in tools}
    expected = {
        "search_resorts",
        "get_resort_details",
        "get_resort_restaurants",
        "get_resort_rooms",
        "get_room_details",
        "get_restaurant_menu",
        "find_rooms_by_class",
        "check_room_availability",
        "find_flexible_dates",
        "add_price_watch",
        "list_price_watches",
        "remove_price_watch",
        "check_price_watches",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


async def test_tool_count(client):
    tools = await client.list_tools()
    assert len(tools) == 13


# ---------------------------------------------------------------------------
# Resort lookup tools (local data, no mocking needed)
# ---------------------------------------------------------------------------


async def test_search_resorts_no_filter(client):
    result = await client.call_tool("search_resorts", {})
    text = result.content[0].text
    assert "resort(s) found" in text or "No resorts" in text


async def test_search_resorts_by_island(client):
    result = await client.call_tool("search_resorts", {"island": "Jamaica"})
    text = result.content[0].text
    assert "Jamaica" in text or "No resorts" in text


async def test_search_resorts_adults_only(client):
    result = await client.call_tool("search_resorts", {"kids_allowed": False})
    text = result.content[0].text
    assert "resort(s) found" in text or "No resorts" in text


async def test_get_resort_details_invalid(client):
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool("get_resort_details", {"resort_code": "ZZZZZ"})


async def test_get_resort_rooms_no_filter(client):
    result = await client.call_tool("get_resort_rooms", {"resort_code": "SMB"})
    text = result.content[0].text
    assert "room" in text.lower() or "No rooms" in text


async def test_get_resort_restaurants(client):
    result = await client.call_tool(
        "get_resort_restaurants", {"resort_code": "SMB"}
    )
    text = result.content[0].text
    assert "restaurant" in text.lower() or "No restaurants" in text


async def test_get_room_details_invalid(client):
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool(
            "get_room_details", {"resort_code": "SMB", "room_code": "ZZZZ"}
        )


async def test_get_restaurant_menu_invalid(client):
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool(
            "get_restaurant_menu",
            {"resort_code": "SMB", "restaurant_name": "Nonexistent Place"},
        )


async def test_find_rooms_by_class(client):
    result = await client.call_tool(
        "find_rooms_by_class", {"room_class": "BUTLER"}
    )
    text = result.content[0].text
    assert "BUTLER" in text or "No rooms" in text


# ---------------------------------------------------------------------------
# Availability tools (mock external API)
# ---------------------------------------------------------------------------


async def test_check_room_availability_mocked(client):
    mock_result = {
        "success": True,
        "resort_code": "SMB",
        "check_in": "2026-06-01",
        "check_out": "2026-06-08",
        "adults": 2,
        "children": 0,
        "data": [
            {
                "roomCategoryCode": "DL",
                "available": True,
                "availableRooms": 5,
                "adultRate": 300,
                "totalPrice": 300,
                "totalPriceForEntireLengthOfStay": 2100,
                "avgPriceAdultsAndKids": 300,
                "length": 7,
                "date": "2026-06-01",
                "unavailableDays": None,
            }
        ],
    }

    with patch.object(
        availability_checker,
        "check_availability",
        return_value=mock_result,
    ):
        result = await client.call_tool(
            "check_room_availability",
            {
                "resort_code": "SMB",
                "check_in_date": "2026-06-01",
                "check_out_date": "2026-06-08",
            },
        )
        text = result.content[0].text
        assert "Availability" in text
        assert "DL" in text
        assert "$2,100" in text


# ---------------------------------------------------------------------------
# Price watch tools
# ---------------------------------------------------------------------------


async def test_list_price_watches_unconfigured(client):
    """Without DISCORD_WEBHOOK_URL, price watches should report error."""
    with patch.object(price_monitor, "is_enabled", return_value=False):
        with patch.object(
            price_monitor,
            "list_watches",
            return_value={
                "error": "Price monitoring not configured. Set DISCORD_WEBHOOK_URL environment variable.",
                "watches": [],
                "total": 0,
            },
        ):
            with pytest.raises(ToolError, match="not configured"):
                await client.call_tool("list_price_watches", {})


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------


async def test_list_resources(client):
    resources = await client.list_resources()
    uris = {str(r.uri) for r in resources}
    assert "sandals://resorts/all" in uris


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


async def test_list_prompts(client):
    prompts = await client.list_prompts()
    names = {p.name for p in prompts}
    assert "plan_vacation" in names
