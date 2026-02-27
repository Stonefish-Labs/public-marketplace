---
name: mcp-response-format
description: >
  Format MCP tool responses for maximum agent efficiency. Use this skill when
  deciding how an MCP tool should return data, choosing between text and structured
  output, avoiding token-wasting response patterns, or when someone asks "how
  should my MCP tool return data", "text vs structured response", "ToolResult
  format", "response formatting for agents", or "efficient MCP responses".
  Includes text_response() and structured_response() helper functions.
---

# MCP Response Formatting

**Default to text.** Most MCP tool consumers are agents that read clean,
formatted text far more efficiently than parsing JSON. Only return structured
data when a concrete programmatic consumer needs it.

## Decision Matrix

| Scenario | Return | Format |
|---|---|---|
| **Default / agent consumption** | `text_response("...")` | Markdown text — headers, tables, bold for scanning |
| Programmatic consumer needs machine-parseable data | `dict` or dataclass | Flat structured data |
| Both agent + programmatic consumer | `structured_response(text, data)` | Text summary + structured data |
| **Uncertain who consumes it** | `text_response("...")` | Default to text; switch to structured only if asked |

## Helper Functions

Copy `scripts/utils.py` into your server project:

```python
from utils import text_response, structured_response

@mcp.tool
def status(service: str) -> ToolResult:
    """Check service health."""
    return text_response(f"# {service}\n\n**Status:** healthy\n**Uptime:** 99.9%")

@mcp.tool
def search(query: str) -> ToolResult:
    """Search — returns text for agents, structured data for automation."""
    results = do_search(query)
    summary = f"Found {len(results)} results for '{query}'"
    return structured_response(summary, {"query": query, "results": results})
```

## Rules

1. **Default to `text_response()`** — unless you have a concrete programmatic
   consumer, return clean text. Agents read it directly without parsing overhead.
2. **Never return bare strings** — `return "Done"` becomes `{"result": "Done"}`,
   wasting tokens. Use `text_response()` instead.
3. **Use markdown in text** — headers, tables, bold for scanning:
   ```python
   text_response(f"# Report\n\n**Status:** healthy\n**Uptime:** 99.9%")
   ```
4. **Keep structures flat** — when you do return structured data, one level of
   nesting is usually enough.
5. **Never return secrets** — return `"api_key_set": True`, never the actual value.

## Anti-Patterns

```python
# BAD: Dict by default — agent wastes tokens parsing JSON it doesn't need
@mcp.tool
def get_status(service: str) -> dict:
    return {"service": service, "status": "healthy", "uptime": 99.9}

# GOOD: Clean text the agent reads directly
@mcp.tool
def get_status(service: str) -> ToolResult:
    return text_response(f"**{service}** is healthy (uptime 99.9%)")

# BAD: Auto-wrapped primitive
@mcp.tool
def process(text: str) -> str:
    return f"Processed: {text}"  # -> {"result": "Processed: ..."}

# GOOD: Clean text
@mcp.tool
def process(text: str) -> ToolResult:
    return text_response(f"Processed: {text}")

# BAD: Deep nesting
def get_info() -> dict:
    return {"data": {"response": {"result": {"value": 42}}}}

# GOOD: Flat (when structured is actually needed)
def get_info() -> dict:
    return {"value": 42}
```
