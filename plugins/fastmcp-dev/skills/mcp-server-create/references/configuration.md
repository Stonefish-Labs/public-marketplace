# MCP Server Configuration Reference

## fastmcp.json

The canonical FastMCP 3.x deployment config. Place at project root:

```json
{
    "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
    "source": {
        "path": "server.py",
        "entrypoint": "mcp"
    },
    "environment": {
        "python": ">=3.12",
        "dependencies": ["httpx>=0.25"]
    },
    "deployment": {
        "transport": "http",
        "host": "0.0.0.0",
        "port": 8000,
        "path": "/mcp/",
        "log_level": "INFO",
        "env": {
            "API_KEY": "${API_KEY}"
        }
    }
}
```

Run with: `fastmcp run` (auto-detects) or `fastmcp run server.py`

Development: `fastmcp run server.py --reload`

## MCP Host Configuration

### Claude Desktop / Claude Code (stdio)

```json
{
  "mcpServers": {
    "myServer": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/my-mcp-server", "python", "server.py"]
    }
  }
}
```

### With Environment Variables

```json
{
  "mcpServers": {
    "myServer": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/my-mcp-server", "python", "server.py"],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

### HTTP Transport (Remote)

```json
{
  "mcpServers": {
    "myServer": {
      "type": "http",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

### Config File Locations

| Host | Location |
|---|---|
| Claude Desktop | `claude_desktop_config.json` |
| Claude Code | `.claude/mcp.json` (project) or user settings |
| VS Code | `.vscode/mcp.json` (project) or user settings |
| Cursor | `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` |
| LM Studio | `~/.lmstudio/mcp.json` |

## Provider Selection

| Provider | When to Use |
|---|---|
| **LocalProvider** (default) | Standard server with tools defined via decorators — no config needed |
| **FileSystemProvider** | Modular tools in separate files with optional hot-reload |
| **OpenAPIProvider** | Wrapping an existing REST API as MCP tools |
| **ProxyProvider** | Bridging a remote MCP server to local-only clients |

### FileSystemProvider Example

```python
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider

mcp = FastMCP("MyServer", providers=[
    FileSystemProvider(Path(__file__).parent / "tools", reload=True)
])
```

Tool files use standalone decorators:

```python
# tools/math_tools.py
from fastmcp.tools import tool

@tool(name="add", description="Add two numbers.")
def add(a: float, b: float) -> float:
    return a + b
```

### ProxyProvider Example

```python
from fastmcp.server import create_proxy

proxy = create_proxy("http://remote-server.com/mcp", name="RemoteProxy")
proxy.run()  # Exposes remote via stdio locally
```

## Project Structure

### Minimal

```
my-mcp-server/
├── server.py
├── pyproject.toml
└── tests/
    └── test_tools.py
```

### With Business Logic

```
my-mcp-server/
├── server.py          # FastMCP server + registration
├── logic.py           # Business logic (no MCP imports)
├── utils.py           # Response helpers
├── pyproject.toml
├── fastmcp.json       # Deployment config
└── tests/
    ├── conftest.py    # Shared fixtures
    ├── test_tools.py  # In-memory MCP tests
    └── test_logic.py  # Direct function tests
```
