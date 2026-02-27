from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path
import sys

import pytest
from fastmcp.client import Client
from fastmcp.client.elicitation import ElicitResult

sys.path.append(str(Path(__file__).resolve().parents[1]))
from cache import clear_cache
from server import mcp


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache()


@pytest.fixture
async def client_accepting():
    async def accept_all(_message, response_type, _params, _context):
        if response_type is str:
            return ElicitResult(action="accept", data="test-api-key")
        return ElicitResult(action="accept")

    async with Client(transport=mcp, elicitation_handler=accept_all) as client:
        yield client


@pytest.fixture
async def client_declining():
    async def decline_all(_message, _response_type, _params, _context):
        return ElicitResult(action="decline")

    async with Client(transport=mcp, elicitation_handler=decline_all) as client:
        yield client


@pytest.mark.asyncio
async def test_list_tools(client_accepting):
    tools = await client_accepting.list_tools()
    tool_names = {tool.name for tool in tools}
    assert "maps_geocode" in tool_names
    assert "maps_directions" in tool_names


@pytest.mark.asyncio
async def test_maps_geocode_success(client_accepting):
    fake_json = {
        "status": "OK",
        "results": [
            {
                "geometry": {"location": {"lat": 1.23, "lng": 4.56}},
                "formatted_address": "Test Address",
                "place_id": "abc123",
            }
        ],
    }

    with patch("google_maps_client.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        mock_response = Mock()
        mock_response.json.return_value = fake_json
        instance.get = AsyncMock(return_value=mock_response)

        result = await client_accepting.call_tool("maps_geocode", {"address": "hello"})
        assert "Geocoding Result" in result.content[0].text
        assert "Test Address" in result.content[0].text


@pytest.mark.asyncio
async def test_maps_geocode_declined_external_call(client_declining):
    result = await client_declining.call_tool("maps_geocode", {"address": "hello"})
    assert "Error" in result.content[0].text
    assert "declined external API call" in result.content[0].text
