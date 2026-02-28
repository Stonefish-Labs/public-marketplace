# MCP Server Best Practices

## Framework

- **Use FastMCP 3.x** (`fastmcp>=3.0.0`). Do not hand-roll JSON-RPC. Do not use the old `mcp.server.fastmcp` import path — the correct import is `from fastmcp import FastMCP`.
- **Use `uv`** as the package manager. Declare dependencies in `pyproject.toml` with `requires-python = ">=3.12"`.
- **Use `on_duplicate="error"`** on the `FastMCP` constructor to catch registration bugs at startup.

## Tool Design

- **One function per tool.** Use `@mcp.tool` (no parens for bare decorator in 3.x). The function name becomes the tool name; the docstring becomes the description.
- **Type every parameter.** FastMCP generates the JSON Schema from Python type annotations. Use `str`, `int`, `bool`, `Literal["a","b"]`, and Pydantic `BaseModel` for complex inputs. Unannotated parameters produce poor schemas.
- **Write tool descriptions for dynamic search.** Claude's MCP Tool Search activates when tool definitions exceed 10% of the context window — at that point only server `instructions` and tool docstrings are used to find relevant tools. Write docstrings that clearly state *what* the tool does and *when* to use it. Avoid generic descriptions like "A useful tool."
- **Set `instructions=` on the server.** This is the primary signal Claude uses to decide when to search your server's tools. Three sentences: what the server does, when to use it, any constraints.

## Transports

- **Stdio (default)** for plugin-bundled servers and local tools. Launch via `uv run server` — no global install required.
- **Streamable HTTP** for remote/shared deployments. Support it by reading `PORT` from the environment:
  ```python
  port = os.getenv("PORT")
  if port:
      mcp.run(transport="streamable-http", host=os.getenv("HOST", "127.0.0.1"), port=int(port))
  else:
      mcp.run()  # stdio
  ```
- **SSE transport is deprecated.** Do not use it for new servers.

## Configuration (`.mcp.json`)

Plugin-bundled servers go in `.mcp.json` at the plugin root, or inline in `plugin.json` under `"mcpServers"`.

Use `uv run server` as the command so the environment is self-contained:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "server"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}/my-server",
      "env": {}
    }
  }
}
```

Use `${CLAUDE_PLUGIN_ROOT}` for all plugin-relative paths. Never hardcode absolute paths.

For standalone (non-plugin) servers registered via `claude mcp add`:
```bash
# stdio (local process)
claude mcp add --transport stdio my-server -- uv run --directory /path/to/server server

# HTTP (remote)
claude mcp add --transport http my-server https://my-server.example.com/mcp
```

### Scopes for `claude mcp add`
- `local` (default): stored in `~/.claude.json`, visible only to you in the current project.
- `project`: stored in `.mcp.json` at the repo root, checked into version control, shared with the team.
- `user`: stored in `~/.claude.json`, available across all your projects.

## Response Formatting

- Return `dict` or a dataclass for structured data — FastMCP auto-produces `structuredContent`.
- Return plain `str` only for short human-readable messages.
- Never return raw secrets. Return `{"api_key_set": True}` instead.

## Startup Safety

MCP clients send `initialize` immediately after launching the server and expect a
response within ~5 seconds. **Any blocking code before `mcp.run()` can service that
handshake causes a client timeout.** See the `mcp-startup-patterns` skill for full
examples.

**Never do this at module level or in `lifespan` startup:**

```python
# ❌ Blocks the initialize handshake — Cursor/Claude Desktop will time out
@asynccontextmanager
async def lifespan(server):
    token = await do_oauth_browser_flow()  # minutes of user interaction
    yield {"token": token}

# ❌ Also wrong — blocks before mcp.run() is even called
token = asyncio.run(fetch_token())  # never at module level
```

**Correct approach by situation:**

| Situation | Pattern |
|---|---|
| First-time OAuth / no stored token | Lazy singleton — init inside a `get_client(ctx)` helper called from tools |
| Token refresh using a stored refresh_token | `asyncio.create_task()` in lifespan — fires after `yield`, server already up |
| HTTP client pool, DB connection | Safe in lifespan — fast, non-interactive |

```python
# ✅ Lazy singleton — server starts instantly, auth on first tool call
_client = None
_lock = None

def _get_lock():
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock

async def get_client(ctx):
    global _client
    if _client is not None:
        return _client
    async with _get_lock():
        if _client is None:
            creds = secrets.get("token") or await _prompt_and_store(ctx)
            _client = MyClient(creds["token"])
    return _client
```

## Safety

- **Self-contained**: never reference files outside the server directory.
- **No absolute paths** in config files — always use `${CLAUDE_PLUGIN_ROOT}` or relative paths.
- Mark destructive tools with `annotations={"destructiveHint": True}` so clients can prompt for confirmation.
- Mark read-only tools with `annotations={"readOnlyHint": True}` so clients can auto-approve them.

## Scaffolding

Use the scaffolding script to generate the project structure rather than writing files by hand:
```bash
python scripts/scaffold_mcp.py --name my-server --target-dir ./mcp-servers
```

This produces `server.py`, `pyproject.toml`, and `.mcp.json` with the correct FastMCP 3.x patterns.
