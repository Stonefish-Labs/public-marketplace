---
name: mcp-server-upgrade
description: >
  Upgrade an existing MCP server to Python FastMCP 3.x. Use this skill when migrating
  a FastMCP 2.x server to 3.x, converting a JavaScript or TypeScript MCP server to
  Python FastMCP, or when someone asks "upgrade my MCP server", "migrate to FastMCP 3",
  "convert this JS MCP server to Python", or "port this TypeScript MCP to FastMCP".
  Covers the full 2.x→3.x breaking changes checklist and JS/TS→Python conversion
  patterns. All MCP servers should be Python FastMCP 3.x — never leave them in JS.
---

# Upgrade or Convert to FastMCP 3.x

Two migration paths covered here: Python 2.x→3.x and JS/TS→Python.
Read `references/breaking-changes.md` for the complete 17-item checklist.
Read `references/js-conversion.md` for JavaScript/TypeScript conversion patterns.

## Python 2.x → 3.x: Quick Start

The three changes you'll hit immediately:

```python
# 1. Import changed
from fastmcp import FastMCP          # NOT: from mcp.server.fastmcp import FastMCP

# 2. State is async now
await ctx.set_state("key", "value")  # NOT: ctx.set_state(...)
value = await ctx.get_state("key")   # NOT: ctx.get_state(...)

# 3. Listing returns lists, not dicts
tools = await server.list_tools()    # NOT: server.get_tools()
```

Then update dependencies:

```bash
uv add "fastmcp>=3.0.0"
```

## JS/TS → Python: Quick Start

The core mapping is simple — JS has monolithic handlers, Python has one function
per tool with type annotations replacing zod schemas:

```javascript
// JS: One giant handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_weather") { ... }
});
```

```python
# Python: One decorated function per tool
@mcp.tool
def get_weather(city: str, units: Literal["celsius", "fahrenheit"] = "celsius") -> dict:
    """Get weather for a city."""
    return fetch_weather(city, units)
```

Read `references/js-conversion.md` for the full dependency mapping table and
pattern-by-pattern conversion guide.

## After Migration

1. Run `uv run python -W all server.py` to surface deprecation warnings
2. Test all tools with the in-memory client — see `mcp-testing` skill
3. Adopt new 3.x features: tool timeouts, versioning, `fastmcp.json`, `CurrentContext()`
