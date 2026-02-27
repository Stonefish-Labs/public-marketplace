---
name: mcp-testing
description: >
  Test MCP servers using in-memory clients and pytest. Use this skill when writing
  tests for an MCP server, setting up pytest for FastMCP, creating test fixtures,
  mocking external dependencies in MCP tools, or when someone asks "test my MCP
  server", "how to test FastMCP tools", "MCP testing patterns", or "in-memory MCP
  testing". Covers in-memory client testing, direct function testing, parametrized
  tests, elicitation testing, and integration testing.
---

# MCP Testing — FastMCP 3.x

In-memory testing is the preferred approach — zero network, zero subprocess, full
debugger support. FastMCP 3.x decorators return the original function, so you can
also test business logic directly without any MCP overhead.

## In-Memory Testing (Preferred)

Pass your `FastMCP` instance to `Client(transport=mcp)`:

```python
import pytest
from fastmcp.client import Client
from server import mcp

@pytest.fixture
async def client():
    async with Client(transport=mcp) as c:
        yield c

async def test_list_tools(client):
    tools = await client.list_tools()
    assert len(tools) > 0

async def test_call_tool(client):
    result = await client.call_tool("add", {"a": 1, "b": 2})
    assert result.data == 3
```

## pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
```

## Direct Function Testing

In 3.x, `@mcp.tool` returns the original function — test it directly:

```python
@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

def test_greet():
    assert greet("World") == "Hello, World!"
```

Use direct testing for pure logic. Use in-memory client when you need to verify
MCP protocol behavior (schema generation, structured output, error handling).

## Testing Text Output

Most tools default to `text_response()`. Assert on the text content directly:

```python
async def test_status_text(client):
    result = await client.call_tool("status", {"service": "api"})
    # text_response() returns content blocks, not structured data
    assert result.content[0].text == "**api** is healthy (uptime 99.9%)"

async def test_search_text_contains(client):
    result = await client.call_tool("search", {"query": "widgets"})
    assert "Found" in result.content[0].text
```

For tools that return structured data (programmatic consumers), use `result.data`
as shown in the examples below.

## Parametrized Tests

```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3), (0, 0, 0), (-1, 1, 0), (100, 200, 300),
])
async def test_add(a, b, expected, client):
    result = await client.call_tool("add", {"a": a, "b": b})
    assert result.data == expected
```

## Mocking External Dependencies

```python
from unittest.mock import AsyncMock, patch

async def test_api_tool(client):
    with patch("server.httpx.AsyncClient") as mock:
        instance = AsyncMock()
        instance.get.return_value.json.return_value = {"status": "ok"}
        mock.return_value.__aenter__.return_value = instance

        result = await client.call_tool("fetch_api", {"url": "/data"})
        assert result.data["status"] == "ok"
```

## Testing Elicitation

Read `references/testing-elicitation.md` for patterns on testing tools that use
`ctx.elicit()`, including auto-accept and auto-decline handlers.

## Integration Testing (HTTP)

For deployment validation only — not unit tests:

```python
async def test_deployed():
    async with Client("http://localhost:8000/mcp/") as client:
        await client.ping()
        tools = await client.list_tools()
        assert len(tools) > 0
```

## Ad-Hoc Testing

Use the `scripts/test_client_template.py` script for interactive testing of any
MCP server via stdio transport. Copy it, edit the config, and run.
