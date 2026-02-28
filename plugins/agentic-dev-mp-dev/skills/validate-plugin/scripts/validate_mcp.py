#!/usr/bin/env python3
import os
import sys
import json


def _extract_server_workdir(server_config):
    cwd = server_config.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return cwd.strip()

    args = server_config.get("args", [])
    if isinstance(args, list) and "--directory" in args:
        idx = args.index("--directory")
        if idx + 1 < len(args) and isinstance(args[idx + 1], str):
            return args[idx + 1].strip()
    return None

def validate_mcp(path, plugin_dir=None):
    if not os.path.exists(path):
        return False, f"MCP path not found: {path}"

    config_path = path
    if os.path.isdir(path):
        config_path = os.path.join(path, ".mcp.json")

    if not os.path.exists(config_path):
        return False, f"MCP configuration (.mcp.json) missing: {config_path}"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in MCP config {config_path}: {e}"
    except Exception as e:
        return False, f"Error reading MCP config {config_path}: {e}"

    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        return False, f"MCP config must contain non-empty 'mcpServers' object: {config_path}"

    errors = []
    for server_name, server_config in servers.items():
        if not isinstance(server_config, dict):
            errors.append(f"mcpServers.{server_name} must be an object")
            continue
        command = server_config.get("command")
        if not isinstance(command, str) or not command.strip():
            errors.append(f"mcpServers.{server_name} missing required 'command' string")
        if not isinstance(server_config.get("args"), list):
            errors.append(f"mcpServers.{server_name} missing required 'args' array")

        workdir = _extract_server_workdir(server_config)
        if isinstance(workdir, str) and workdir == "${CLAUDE_PLUGIN_ROOT}":
            errors.append(
                f"mcpServers.{server_name} points to plugin root; use ${'{CLAUDE_PLUGIN_ROOT}'}/mcp-servers/<server-name>"
            )
        if isinstance(workdir, str) and "${CLAUDE_PLUGIN_ROOT}/mcp-servers/" not in workdir:
            errors.append(
                f"mcpServers.{server_name} should run from mcp-servers/; found workdir '{workdir}'"
            )

    if plugin_dir:
        mcp_servers_dir = os.path.join(plugin_dir, "mcp-servers")
        if not os.path.isdir(mcp_servers_dir):
            errors.append("MCP plugin must contain root directory: mcp-servers/")

        flat_runtime_files = [
            "server.py",
            "index.ts",
            "index.js",
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "uv.lock",
        ]
        flat_hits = [name for name in flat_runtime_files if os.path.exists(os.path.join(plugin_dir, name))]
        if flat_hits:
            errors.append(
                "MCP runtime files must live under mcp-servers/<server-name>/, not plugin root: "
                + ", ".join(sorted(flat_hits))
            )

    if errors:
        return False, " ; ".join(errors)

    return True, f"MCP config valid: {config_path}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_mcp.py <path_to_mcp_directory>")
        sys.exit(1)
        
    success, message = validate_mcp(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
