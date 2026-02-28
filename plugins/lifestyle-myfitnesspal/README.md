# mcp-myfitnesspal

Plugin wrapper for the MyFitnessPal MCP server.

## Components

- `.claude-plugin/plugin.json` plugin manifest
- `.mcp.json` MCP server wiring for Claude clients
- `mcp-servers/mcp-myfitnesspal/` Python FastMCP 3.x runtime

## Runtime

The server runtime lives at:

- `mcp-servers/mcp-myfitnesspal/server.py`

The plugin starts it with:

- `uv run server`

from working directory:

- `${CLAUDE_PLUGIN_ROOT}/mcp-servers/mcp-myfitnesspal`

## Local Validation

From repo root:

```bash
python3 .cursor/skills/validate-plugin/scripts/validate_plugin.py "staging/mcp_to_upgrade/mcp-myfitnesspal"
```

From runtime directory:

```bash
python3 -m pytest
```
