#!/usr/bin/env python3

import argparse
import json
import shutil
import sys
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_copy(src: Path, dest: Path) -> None:
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store", ".venv"))
        return
    ensure_dir(dest.parent)
    shutil.copy2(src, dest)


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").exists()


def is_agent_file(path: Path) -> bool:
    return path.is_file() and path.suffix == ".md"


def is_hook_file(path: Path) -> bool:
    return path.is_file() and path.name == "hooks.json"


def looks_like_mcp_server_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    runtime_markers = ["server.py", "index.ts", "index.js"]
    return any((path / marker).exists() for marker in runtime_markers)


def default_mcp_config(server_name: str) -> dict:
    return {
        "command": "uv",
        "args": ["run", "server"],
        "cwd": f"${{CLAUDE_PLUGIN_ROOT}}/mcp-servers/{server_name}",
        "env": {},
    }


def classify_and_copy_component(src: Path, output_dir: Path, state: dict) -> None:
    if is_skill_dir(src):
        dest = output_dir / "skills" / src.name
        safe_copy(src, dest)
        state["skills"].append(f"skills/{src.name}/SKILL.md")
        return

    if src.is_file() and src.name == "SKILL.md":
        skill_dir = src.parent
        dest = output_dir / "skills" / skill_dir.name
        safe_copy(skill_dir, dest)
        state["skills"].append(f"skills/{skill_dir.name}/SKILL.md")
        return

    if is_hook_file(src):
        if state["has_hooks"]:
            raise ValueError("Multiple hooks.json inputs are not supported")
        dest = output_dir / "hooks" / "hooks.json"
        safe_copy(src, dest)
        state["has_hooks"] = True
        return

    if src.is_dir() and (src / "hooks.json").exists():
        if state["has_hooks"]:
            raise ValueError("Multiple hooks.json inputs are not supported")
        dest = output_dir / "hooks" / "hooks.json"
        safe_copy(src / "hooks.json", dest)
        state["has_hooks"] = True
        return

    if src.is_file() and src.name == ".mcp.json":
        with src.open("r", encoding="utf-8") as f:
            config = json.load(f)
        mcp_servers = config.get("mcpServers", {})
        if isinstance(mcp_servers, dict):
            state["mcp_servers"].update(mcp_servers)
        return

    if looks_like_mcp_server_dir(src):
        server_name = src.name
        dest = output_dir / "mcp-servers" / server_name
        safe_copy(src, dest)
        state["mcp_servers"].setdefault(server_name, default_mcp_config(server_name))
        return

    if is_agent_file(src):
        dest = output_dir / "agents" / src.name
        safe_copy(src, dest)
        state["agents"].append(f"agents/{src.name}")
        return

    if src.is_dir() and src.name == "agents":
        for agent_file in src.glob("*.md"):
            dest = output_dir / "agents" / agent_file.name
            safe_copy(agent_file, dest)
            state["agents"].append(f"agents/{agent_file.name}")
        return

    if src.is_dir() and src.name == "commands":
        for command_file in src.rglob("*.md"):
            relative = command_file.relative_to(src)
            dest = output_dir / "commands" / relative
            safe_copy(command_file, dest)
            state["commands"].append(f"commands/{relative.as_posix()}")
        return

    raise ValueError(f"Unsupported component path: {src}")


def write_manifest(plugin_name: str, output_dir: Path, state: dict) -> None:
    manifest = {
        "name": plugin_name,
        "version": "1.0.0",
        "description": f"Bundled plugin: {plugin_name}",
        "skills": sorted(set(state["skills"])),
        "agents": sorted(set(state["agents"])),
    }

    if state["commands"]:
        manifest["commands"] = sorted(set(state["commands"]))
    if state["has_hooks"]:
        manifest["hooks"] = "./hooks/hooks.json"
    if state["mcp_servers"]:
        manifest["mcpServers"] = "./.mcp.json"

    plugin_manifest_path = output_dir / ".claude-plugin" / "plugin.json"
    with plugin_manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def write_mcp_config(output_dir: Path, state: dict) -> None:
    if not state["mcp_servers"]:
        return

    config = {"mcpServers": dict(sorted(state["mcp_servers"].items()))}
    config_path = output_dir / ".mcp.json"
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Package standalone components into a marketplace-compliant plugin.")
    parser.add_argument("--name", required=True, help="Plugin name (kebab-case)")
    parser.add_argument("--output", required=True, help="Output plugin directory")
    parser.add_argument("--components", nargs="+", default=[], help="Component paths to include")
    args = parser.parse_args()

    plugin_name = args.name.strip()
    if not plugin_name:
        print("Error: --name cannot be empty", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output).resolve()
    ensure_dir(output_dir)
    ensure_dir(output_dir / ".claude-plugin")

    state = {
        "skills": [],
        "agents": [],
        "commands": [],
        "has_hooks": False,
        "mcp_servers": {},
    }

    component_paths = [Path(c).resolve() for c in args.components]
    if not component_paths:
        print("Error: at least one component must be provided via --components", file=sys.stderr)
        sys.exit(1)

    try:
        for src in component_paths:
            if not src.exists():
                raise FileNotFoundError(f"Component path not found: {src}")
            classify_and_copy_component(src, output_dir, state)
        write_manifest(plugin_name, output_dir, state)
        write_mcp_config(output_dir, state)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully bundled plugin '{plugin_name}' to {output_dir}")
    print(f"Manifest: {output_dir / '.claude-plugin' / 'plugin.json'}")
    if state["mcp_servers"]:
        print(f"MCP config: {output_dir / '.mcp.json'}")


if __name__ == "__main__":
    main()
