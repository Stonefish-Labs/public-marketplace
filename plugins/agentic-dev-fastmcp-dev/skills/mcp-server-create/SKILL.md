---
name: mcp-server-create
description: >
  Scaffold and build a new MCP server with Python FastMCP 3.x. Use this skill when
  creating a new MCP server project from scratch, setting up server boilerplate,
  generating pyproject.toml for an MCP project, or when someone asks "create an MCP
  server", "new MCP project", "scaffold an MCP tool server", or "set up FastMCP".
  Covers project init, server entrypoint, tool registration, configuration files,
  and MCP host setup. Always produces Python FastMCP 3.x — never JavaScript.
---

# Create a New MCP Server

Scaffold a FastMCP 3.x server project with correct structure, entrypoint, and
configuration. Every MCP server follows the same pattern — this skill ensures
you start right so you don't fight the framework later.

## 1. Determine Architecture Pattern

Before scaffolding, **ask the user** which architecture they prefer:
1. **Monolithic Server**: Simple, all logic defined within `@mcp.tool` decorators in `server.py`. Best for simple specific integrations.
2. **Hybrid (Library-First) Architecture**: Core business logic is written in decoupled Python modules, and `server.py` acts only as an MCP envelope. Best if the user wants to reuse the logic in other scripts/CLIs. (See `mcp-hybrid-architecture` skill).

## 2. Scaffolding Steps

```bash
mkdir my-mcp-server && cd my-mcp-server
uv init --python 3.12
uv add "fastmcp>=3.0.0"
# Add dependencies as needed: uv add httpx pydantic etc.
```

## Server Entrypoint

Use the template in `assets/server_template.py` as the starting point. Key rules:

1. Import as `from fastmcp import FastMCP` — never `from mcp.server.fastmcp`
2. Set `on_duplicate="error"` to catch registration bugs early
3. Write `instructions=` for agents — one sentence each: purpose, use case, constraints
4. Support both stdio (default) and streamable-http via `PORT` env var

## Tool Registration

Register tools with `@mcp.tool` decorator. Type annotations are essential — they
generate the schema agents use to call your tools. Docstrings become tool descriptions.

```python
from utils import text_response

@mcp.tool
def my_tool(query: str, limit: int = 10) -> ToolResult:
    """Search for items matching the query."""
    results = search(query, limit)
    return text_response(f"Found {len(results)} items for '{query}'")
```

See the `mcp-tool-design` skill for full registration patterns, annotations,
dependency injection, and context access.

## Response Formatting

**Default to text output.** Most consumers are agents — they read formatted text
directly. Only return structured data when a programmatic consumer needs it.

- **Text (default)** → use `text_response()` helper from `mcp-response-format` skill
- **Structured data** → return `dict` or dataclass — only for programmatic consumers
- **Both** → use `structured_response()` helper — text for agents, data for automation

## Configuration

Read `references/configuration.md` for:
- `fastmcp.json` — the canonical FastMCP 3.x deployment config
- MCP host configs for Claude Desktop, VS Code, Cursor, LM Studio
- Provider selection guide (LocalProvider vs FileSystemProvider vs OpenAPIProvider)

## Checklist

Before shipping, verify:

- [ ] `from fastmcp import FastMCP` (not the old 2.x import)
- [ ] All tools have type annotations and docstrings
- [ ] `on_duplicate="error"` is set
- [ ] Destructive tools have `destructiveHint=True` annotation
- [ ] No hardcoded secrets — use `mcp-secrets` skill patterns
- [ ] **No blocking I/O at startup** — OAuth/auth uses lazy init or background task (see `mcp-startup-patterns` skill)
- [ ] In-memory tests pass — see `mcp-testing` skill
- [ ] MCP host config documented with correct paths
