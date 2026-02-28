# sandals-mcp

Plugin wrapper for the Sandals BoujieBot MCP server.

## Components

- `.claude-plugin/plugin.json` plugin manifest
- `.mcp.json` MCP server wiring for Claude clients
- `mcp-servers/sandals-mcp/` Python FastMCP runtime

## Runtime

The server runtime lives at:

- `mcp-servers/sandals-mcp/server.py`

The plugin starts it with:

- `uv run server`

from working directory:

- `${CLAUDE_PLUGIN_ROOT}/mcp-servers/sandals-mcp`

## Local Validation

From repo root:

```bash
python3 .cursor/skills/validate-plugin/scripts/validate_plugin.py "staging/mcp_to_upgrade/sandals_mcp"
```

From runtime directory:

```bash
python3 -m pytest
```
