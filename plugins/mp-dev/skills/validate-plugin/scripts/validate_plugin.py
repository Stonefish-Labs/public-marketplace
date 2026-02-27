#!/usr/bin/env python3
import os
import json
import sys
from validate_skill import validate_skill
from validate_agent import validate_agent
from validate_command import validate_command
from validate_hook import validate_hook
from validate_mcp import validate_mcp


def _resolve_manifest_path(plugin_dir):
    nested = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
    root = os.path.join(plugin_dir, "plugin.json")
    if os.path.exists(nested):
        return nested
    if os.path.exists(root):
        return root
    return None


def _collect_mcp_config_paths(plugin_dir, plugin_data):
    paths = []

    manifest_mcp = plugin_data.get("mcpServers")
    if isinstance(manifest_mcp, str):
            paths.append(os.path.normpath(os.path.join(plugin_dir, manifest_mcp)))
    elif isinstance(manifest_mcp, list):
        for entry in manifest_mcp:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                paths.append(os.path.normpath(os.path.join(plugin_dir, entry["path"])))
    elif isinstance(manifest_mcp, dict):
        # Inline object style is valid; root .mcp.json is optional in this case.
        pass

    root_mcp = os.path.normpath(os.path.join(plugin_dir, ".mcp.json"))
    if os.path.exists(root_mcp):
        paths.append(root_mcp)

    # preserve insertion order while deduplicating
    seen = set()
    unique = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique

def validate_plugin(plugin_dir="."):
    errors = []
    plugin_data = {}
    
    # Check plugin.json
    manifest_path = _resolve_manifest_path(plugin_dir)
    if not manifest_path:
        errors.append("Missing plugin.json manifest")
    else:
        try:
            with open(manifest_path, "r") as f:
                plugin_data = json.load(f)
        except json.JSONDecodeError:
            errors.append("Invalid JSON in plugin.json")
            plugin_data = {}

    # Check hooks.json
    hooks_path = os.path.join(plugin_dir, "hooks", "hooks.json")
    if os.path.exists(hooks_path):
        success, msg = validate_hook(hooks_path)
        if not success:
            errors.append(msg)
            
    # Check skills if directory exists
    skills_dir = os.path.join(plugin_dir, "skills")
    if os.path.exists(skills_dir) and os.path.isdir(skills_dir):
        for root, _, files in os.walk(skills_dir):
            for file in files:
                if file.endswith('.md'):
                    success, msg = validate_skill(os.path.join(root, file))
                    if not success:
                        errors.append(msg)
                        
    # Flag slash commands placed inside .claude/commands/ (wrong location)
    misplaced_commands_dir = os.path.join(plugin_dir, ".claude", "commands")
    if os.path.isdir(misplaced_commands_dir):
        errors.append(
            "Slash commands must not be placed in .claude/commands/; "
            "use commands/ at the plugin root instead"
        )

    # Check slash commands in valid command directories
    for cmd_dir_name in ("commands", "slash-commands", "slash_commands"):
        cmd_dir = os.path.join(plugin_dir, cmd_dir_name)
        if os.path.exists(cmd_dir) and os.path.isdir(cmd_dir):
            for file in os.listdir(cmd_dir):
                if file.endswith(".md"):
                    success, msg = validate_command(os.path.join(cmd_dir, file))
                    if not success:
                        errors.append(msg)

    # Check agents if directory exists
    agents_dir = os.path.join(plugin_dir, "agents")
    if os.path.exists(agents_dir) and os.path.isdir(agents_dir):
        for root, _, files in os.walk(agents_dir):
            for file in files:
                if file.endswith('.md'):
                    success, msg = validate_agent(os.path.join(root, file))
                    if not success:
                        errors.append(msg)
                        
    # Enforce .claude-plugin contents
    claude_plugin_dir = os.path.join(plugin_dir, ".claude-plugin")
    if os.path.isdir(claude_plugin_dir):
        unexpected = [
            item for item in os.listdir(claude_plugin_dir) if item != "plugin.json"
        ]
        if unexpected:
            errors.append(
                "Only plugin.json is allowed in .claude-plugin/; found: "
                + ", ".join(sorted(unexpected))
            )

    # Check MCP servers from manifest and/or root .mcp.json
    for mcp_config_path in _collect_mcp_config_paths(plugin_dir, plugin_data):
        success, msg = validate_mcp(mcp_config_path, plugin_dir=plugin_dir)
        if not success:
            errors.append(msg)

    if errors:
        print("Validation Failed:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)
    else:
        print("Plugin validation passed.")
        sys.exit(0)

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    validate_plugin(target_dir)
