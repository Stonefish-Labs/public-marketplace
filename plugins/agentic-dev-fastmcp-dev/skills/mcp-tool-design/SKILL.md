---
name: mcp-tool-design
description: >
  Design and register tools for FastMCP 3.x servers. Use this skill when adding
  tools to an MCP server, designing tool schemas, choosing between sync and async,
  setting up dependency injection, or using tool annotations. Also use when someone
  asks "how do I register a tool", "add a tool to my MCP server", "MCP tool best
  practices", "tool annotations", or "FastMCP context access". Covers registration
  patterns, type annotations, structured output, error handling, and dynamic
  tool management.
---

# MCP Tool Design — FastMCP 3.x

Tools are the primary interface agents use. Type annotations generate the schema,
docstrings become descriptions, and return types control output format. Get these
right and agents will use your tools correctly without extra prompting.

## Registration

```python
# Basic — name and description from function
@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

# Custom name
@mcp.tool("search_products")
def internal_search(query: str, limit: int = 10) -> list[dict]:
    """Search the product catalog."""
    return []

# Full configuration
@mcp.tool(
    name="delete_record",
    description="Permanently delete a database record.",
    tags={"database", "destructive"},
    timeout=30.0,
    version="1.0",
    annotations={"destructiveHint": True, "readOnlyHint": False, "idempotentHint": False},
)
async def delete_record(record_id: str, ctx: Context = CurrentContext()) -> dict:
    """Delete a record by ID."""
    ...

# Programmatic (no decorator)
mcp.tool(existing_function)
mcp.tool(existing_function, name="custom_name")
```

If you are distilling core business logic into reusable packages (rather than tying it directly to `@mcp.tool`), review the **`mcp-hybrid-architecture`** skill for Library-First patterns.

Read `references/advanced-patterns.md` for class method registration, dependency
injection, version filtering, and dynamic enable/disable patterns.

## Type Annotations

Type annotations are essential — they generate the schema agents see.

```python
from typing import Literal, Annotated
from pydantic import Field, BaseModel

@mcp.tool
def process(
    text: str,                                              # Required
    count: int = 10,                                        # Optional with default
    format: Literal["json", "csv", "xml"] = "json",         # Enum
    max_rows: Annotated[int, Field(ge=1, le=10000)] = 100,  # Constrained
) -> dict:
    """Process data with options."""
    return {"text": text, "count": count}

# Complex input with Pydantic
class SearchFilter(BaseModel):
    query: str
    category: str | None = None
    min_price: float = 0.0

@mcp.tool
def search(filters: SearchFilter) -> list[dict]:
    """Search with structured filters."""
    return []
```

## Context Access

Three methods — `CurrentContext()` is preferred in 3.x:

```python
from fastmcp import Context
from fastmcp.dependencies import CurrentContext

@mcp.tool
async def my_tool(data: str, ctx: Context = CurrentContext()) -> str:
    await ctx.info("Processing")                         # Logging
    await ctx.report_progress(progress=50, total=100)    # Progress
    await ctx.set_state("key", "value")                  # State (async!)
    result = await ctx.elicit("Confirm?", response_type=["yes", "no"])  # Input
    return "done"
```

## Output

**Default to text.** Most consumers are agents — they read formatted text
directly without parsing overhead. Only return structured data when a concrete
programmatic consumer needs it.

- **Text (default)** → return `ToolResult` via `text_response()` (see `mcp-response-format`)
- **Structured data** → return `dict` or dataclass — only for programmatic consumers
- **Both** → return `ToolResult` via `structured_response()` — text for agents, data for automation

```python
from utils import text_response

@mcp.tool
def get_stats() -> ToolResult:
    """Text output the agent reads directly."""
    return text_response("**Users:** 100\n**Active:** 42")

@mcp.tool
def get_stats_json() -> dict:
    """Structured output — only if automation consumes this."""
    return {"users": 100, "active": 42}
```

## Async vs Sync

Start with sync. FastMCP 3.x auto-dispatches sync functions to a thread pool.
Use async only when you have actual I/O (HTTP calls, database queries):

```python
@mcp.tool
def compute(data: str) -> str:            # Sync — fine for CPU work
    return hashlib.sha256(data.encode()).hexdigest()

@mcp.tool
async def fetch(url: str) -> dict:        # Async — for I/O
    async with httpx.AsyncClient() as c:
        return (await c.get(url)).json()
```

## Error Handling

Let exceptions bubble naturally. Use `ToolError` only for agent-specific guidance:

```python
from fastmcp.exceptions import ToolError

@mcp.tool
def process(filename: str) -> dict:
    if not filename.endswith(".txt"):
        raise ToolError("Only .txt files supported. Convert your file first.")
    return {"status": "processed"}
```

## Annotations

Signal tool behavior so clients handle them correctly:

| Annotation | Meaning |
|---|---|
| `readOnlyHint: True` | Does not modify state — safe to auto-approve |
| `destructiveHint: True` | Irreversible — clients should confirm first |
| `idempotentHint: True` | Safe to retry on failure |
| `openWorldHint: True` | Accesses external systems |
