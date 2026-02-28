# Advanced Tool Patterns — FastMCP 3.x

## Class Method Registration

```python
from fastmcp.tools import tool

class Calculator:
    def __init__(self, precision: int = 2):
        self.precision = precision

    @tool()
    def divide(self, a: float, b: float) -> float:
        """Divide with configured precision."""
        return round(a / b, self.precision)

calc = Calculator(precision=4)
mcp.add_tool(calc.divide)
```

## Dependency Injection

Hide server-injected parameters from the tool schema:

```python
from fastmcp.dependencies import Depends

def get_current_user() -> str:
    return "user_123"

@mcp.tool
def get_profile(user_id: str = Depends(get_current_user)) -> dict:
    """user_id is injected — not exposed in schema."""
    return {"id": user_id, "name": "Alice"}
```

## Tool Versioning

Expose multiple versions of a tool for backward compatibility:

```python
@mcp.tool(version="1.0")
def calculate(x: int, y: int) -> int:
    return x + y

@mcp.tool(version="2.0")
def calculate(x: int, y: int, z: int = 0) -> int:
    return x + y + z
```

Clients see v2.0 by default. Request v1.0 via `_meta`:

```json
{"x": 1, "y": 2, "_meta": {"fastmcp": {"version": "1.0"}}}
```

Remove a specific version:

```python
mcp.local_provider.remove_tool("calculate", version="1.0")
```

## Dynamic Enable/Disable

Control tool visibility at runtime:

```python
# Server-level
mcp.disable(names={"admin_tool"}, components=["tool"])
mcp.disable(tags={"admin"})
mcp.enable(tags={"public"}, only=True)  # Allowlist mode

# Per-session via context
@mcp.tool
async def elevate(ctx: Context = CurrentContext()) -> str:
    await ctx.enable_components(names={"admin_tool"}, components=["tool"])
    return "Admin tools enabled for this session"
```

## Strict Validation Mode

Reject type-coerced inputs (e.g., `"10"` for `int`):

```python
mcp = FastMCP("Strict", strict_input_validation=True)
```

## Duplicate Handling

```python
mcp = FastMCP(
    name="MyServer",
    on_duplicate="error",    # "warn", "error", "replace", "ignore"
)
```

## Separation of Concerns

Keep business logic MCP-free. Register at startup:

```python
# logic.py — pure business logic
def process_document(content: str, format: str = "json") -> dict:
    """Process document. No MCP imports needed."""
    return {"processed": content.upper(), "format": format}

# server.py — MCP registration only
from logic import process_document
mcp.tool(process_document)
```

## Media Returns

```python
from fastmcp.utilities.types import Image, Audio, File

@mcp.tool
def get_chart() -> Image:
    return Image(path="chart.png")
```

## ToolResult for Full Control

```python
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

@mcp.tool
def detailed_result() -> ToolResult:
    return ToolResult(
        content=[TextContent(type="text", text="Summary text")],
        structured_content={"users": 100, "active": 42},
        meta={"execution_time_ms": 145}
    )
```

## Context Capabilities Reference

```python
@mcp.tool
async def full_context_demo(ctx: Context = CurrentContext()) -> dict:
    # Logging
    await ctx.info("Info message")
    await ctx.warning("Warning message")

    # Progress
    await ctx.report_progress(progress=50, total=100)

    # State (async in 3.x)
    await ctx.set_state("key", "value")
    val = await ctx.get_state("key")
    await ctx.set_state("client", obj, serializable=False)  # Non-serializable

    # Transport detection
    transport = ctx.transport  # "stdio" | "sse" | "streamable-http" | None

    # Session identifiers
    sid = ctx.session_id
    cid = ctx.client_id
    rid = ctx.request_id

    # Resource access
    resource = await ctx.read_resource("config://settings")

    # Elicitation (see mcp-elicitation skill)
    result = await ctx.elicit("Confirm?", response_type=["yes", "no"])

    # LLM sampling
    response = await ctx.sample("Summarize this", temperature=0.7)

    # Notifications
    import mcp.types
    await ctx.send_notification(mcp.types.ToolListChangedNotification())

    return {"done": True}
```
