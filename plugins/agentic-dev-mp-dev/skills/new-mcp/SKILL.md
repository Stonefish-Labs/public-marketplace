---
name: new-mcp
description: Scaffold a new independent MCP server using FastMCP 3.x. Use this skill when the user asks to "create an MCP server", "build a new Model Context Protocol server", or "scaffold an MCP integration". Asks for server name and target directory, then generates a ready-to-run FastMCP 3.x project (server.py, pyproject.toml, .mcp.json). Do not use this for standard Claude skills or agents.
disable-model-invocation: true
argument-hint: <server-name>
---

# Create New Independent MCP Server

Generate a new FastMCP 3.x MCP server using the deterministic Python scaffolding script.

## Input

`$ARGUMENTS` is the name for the new server (kebab-case). If not provided, ask the user.

## Steps

0. **Review Best Practices**: Read `references/best-practices.md` before prompting the user.

1. Ask for any missing parameters:
   - `name`: Server name (kebab-case, e.g. `my-weather-server`).
   - `target-dir`: Where to create it (e.g. `./mcp-servers` or `.`).

2. Run the scaffolding script:
   ```bash
   python scripts/scaffold_mcp.py --name <name> --target-dir <target-dir>
   ```
   Add `--link-to-plugin plugin.json` only if the user explicitly asks to register it in the plugin.

3. Report what was created:
   - `<name>/server.py` — FastMCP 3.x entry point with an example tool
   - `<name>/pyproject.toml` — uv project config (`fastmcp>=3.0.0`, Python 3.12+)
   - `<name>/.mcp.json` — MCP host configuration using `uv run server`

4. Show the user the next steps printed by the script (`uv sync`, `uv run server`).

## What gets generated

The scaffold produces a minimal but complete FastMCP 3.x project:

- **`server.py`** uses `from fastmcp import FastMCP`, `@mcp.tool` decorator, `on_duplicate="error"`, and a `main()` that supports both stdio (default) and HTTP (`PORT` env var).
- **`pyproject.toml`** uses `uv` with `fastmcp>=3.0.0` and optional pytest dev dependencies.
- **`.mcp.json`** launches via `uv run server` so no global install is required.

Edit `server.py` to replace the example tool with real tools. See `assets/server_template.py` for the canonical template.
