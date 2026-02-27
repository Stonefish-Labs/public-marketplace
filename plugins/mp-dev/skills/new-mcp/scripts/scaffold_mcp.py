#!/usr/bin/env python3
"""Scaffold a new FastMCP 3.x MCP server.

Usage:
    python scripts/scaffold_mcp.py --name my-server --target-dir ./mcp-servers
    python scripts/scaffold_mcp.py --name my-server --target-dir . --link-to-plugin plugin.json
"""
import argparse
import json
import os
import shutil
import sys

# Locate the assets directory relative to this script.
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)
ASSETS_DIR = os.path.join(SKILL_DIR, "assets")


def render_template(src_path: str, replacements: dict) -> str:
    """Read a template file and substitute {{KEY}} placeholders."""
    with open(src_path, "r") as f:
        content = f.read()
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def scaffold_mcp(name: str, target_dir: str, link_to_plugin: str | None = None) -> None:
    server_dir = os.path.join(target_dir, name)
    os.makedirs(server_dir, exist_ok=True)

    replacements = {
        "SERVER_NAME": name,
        "DESCRIPTION": f"MCP server for {name}",
    }

    # --- server.py ---
    server_py = render_template(
        os.path.join(ASSETS_DIR, "server_template.py"), replacements
    )
    with open(os.path.join(server_dir, "server.py"), "w") as f:
        f.write(server_py)

    # --- pyproject.toml ---
    pyproject_toml = render_template(
        os.path.join(ASSETS_DIR, "pyproject_template.toml"), replacements
    )
    with open(os.path.join(server_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject_toml)

    # --- .mcp.json  (uses `uv run` so no global install needed) ---
    mcp_config = {
        "mcpServers": {
            name: {
                "command": "uv",
                "args": ["run", "server"],
                "cwd": "${CLAUDE_PLUGIN_ROOT}/" + name,
                "env": {},
            }
        }
    }
    with open(os.path.join(server_dir, ".mcp.json"), "w") as f:
        json.dump(mcp_config, f, indent=2)

    print(f"Scaffolded FastMCP 3.x server '{name}' in {server_dir}")
    print(f"  server.py         — FastMCP server entry point")
    print(f"  pyproject.toml    — uv project config (fastmcp>=3.0.0)")
    print(f"  .mcp.json         — MCP host configuration")
    print()
    print("Next steps:")
    print(f"  cd {server_dir}")
    print(f"  uv sync           # install dependencies")
    print(f"  uv run server     # test the server")

    if link_to_plugin:
        _link_to_plugin(name, server_dir, link_to_plugin)


def _link_to_plugin(name: str, server_dir: str, plugin_path: str) -> None:
    if not os.path.exists(plugin_path):
        print(f"Warning: plugin file '{plugin_path}' not found — skipping link.", file=sys.stderr)
        return
    try:
        with open(plugin_path, "r") as f:
            plugin_data = json.load(f)

        plugin_data.setdefault("mcpServers", [])

        if any(m.get("name") == name for m in plugin_data["mcpServers"]):
            print(f"MCP server '{name}' already linked in {plugin_path}")
            return

        plugin_data["mcpServers"].append({"name": name, "path": server_dir})
        with open(plugin_path, "w") as f:
            json.dump(plugin_data, f, indent=2)
        print(f"Linked '{name}' to plugin at {plugin_path}")
    except Exception as e:
        print(f"Failed to link to plugin '{plugin_path}': {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a FastMCP 3.x MCP server.")
    parser.add_argument("--name", required=True, help="Name of the MCP server (kebab-case)")
    parser.add_argument("--target-dir", default=".", help="Directory to create the server in")
    parser.add_argument("--link-to-plugin", metavar="PLUGIN_JSON", help="Path to plugin.json to register this server")
    args = parser.parse_args()

    scaffold_mcp(args.name, args.target_dir, args.link_to_plugin)
