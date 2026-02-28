# Testing Tools with Elicitation

## Auto-Accept Handler

For automated tests, create a handler that accepts all elicitation requests:

```python
from fastmcp.client.elicitation import ElicitResult

async def auto_accept_handler(message, response_type, params, context):
    """Accept all elicitation requests with a default value."""
    if response_type is None:
        return ElicitResult(action="accept")
    # Try constructing with a default value
    try:
        return response_type(value="test-input")
    except Exception:
        return ElicitResult(action="accept")
```

## Auto-Decline Handler

Test the cancellation path:

```python
async def auto_decline_handler(message, response_type, params, context):
    return ElicitResult(action="decline")

async def auto_cancel_handler(message, response_type, params, context):
    return ElicitResult(action="cancel")
```

## Using in Tests

```python
from fastmcp import FastMCP, Context
from fastmcp.client import Client

async def test_tool_accepts_input():
    server = FastMCP("Test")

    @server.tool
    async def needs_input(ctx: Context) -> str:
        result = await ctx.elicit("Enter value:", response_type=str)
        if result.action == "accept":
            return f"Got: {result.data}"
        return "Cancelled"

    client = Client(transport=server, elicitation_handler=auto_accept_handler)
    async with client:
        result = await client.call_tool("needs_input", {})
        assert "Got:" in result.data


async def test_tool_handles_cancel():
    server = FastMCP("Test")

    @server.tool
    async def needs_input(ctx: Context) -> str:
        result = await ctx.elicit("Enter value:", response_type=str)
        if result.action == "cancel":
            return "Cancelled"
        return f"Got: {result.data}"

    client = Client(transport=server, elicitation_handler=auto_cancel_handler)
    async with client:
        result = await client.call_tool("needs_input", {})
        assert result.data == "Cancelled"
```

## Parametrized Elicitation

Test different user responses:

```python
@pytest.mark.parametrize("handler, expected", [
    (auto_accept_handler, "Got: test-input"),
    (auto_decline_handler, "Declined"),
    (auto_cancel_handler, "Cancelled"),
])
async def test_elicitation_paths(handler, expected):
    server = FastMCP("Test")

    @server.tool
    async def interactive(ctx: Context) -> str:
        result = await ctx.elicit("Input:", response_type=str)
        if result.action == "accept":
            return f"Got: {result.data}"
        elif result.action == "decline":
            return "Declined"
        return "Cancelled"

    client = Client(transport=server, elicitation_handler=handler)
    async with client:
        result = await client.call_tool("interactive", {})
        assert result.data == expected
```
