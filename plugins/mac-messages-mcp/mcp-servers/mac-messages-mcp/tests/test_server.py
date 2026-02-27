from pathlib import Path

import pytest
from fastmcp.client import Client

from mac_messages_mcp import server


@pytest.fixture
async def client() -> Client:
    async with Client(transport=server.mcp) as c:
        yield c


async def test_list_tools(client: Client) -> None:
    tools = await client.list_tools()
    names = {tool.name for tool in tools}
    assert "send_message" in names
    assert "get_runtime_policy" in names


async def test_get_runtime_policy_tool(client: Client, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    profile_path = tmp_path / ".config" / "mac-messages-mcp" / "profiles" / "default.toml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text('confirmation_policy = "external-only"\n')

    result = await client.call_tool("get_runtime_policy", {})
    text = result.content[0].text
    assert "confirmation_policy: external-only" in text
