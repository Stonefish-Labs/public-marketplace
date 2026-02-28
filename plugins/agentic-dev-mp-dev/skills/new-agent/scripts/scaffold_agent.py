#!/usr/bin/env python3
import os
import sys
import re
import argparse

def validate_agent_name(name):
    """Validate that the agent name is strictly kebab-case."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Agent name '{name}' must be kebab-case.")
        sys.exit(1)

def scaffold_agent(name, scope, background, isolation, target_dir=".", link_to_plugin=None):
    """Scaffold a new agent as a single markdown file."""
    validate_agent_name(name)
    
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, f"{name}.md")
    
    with open(file_path, "w") as f:
        f.write("---\n")
        f.write(f"name: {name}\n")
        f.write(f"description: Agent {name}\n")
        if background:
            f.write("background: true\n")
        if isolation:
            f.write(f"isolation: {isolation}\n")
        f.write("---\n\n")
        f.write(f"You are the {name} sub-agent.\n\n")
        f.write("Describe your instructions and role here.\n")
    
    print(f"Agent '{name}' scaffolded at {file_path}")

    if link_to_plugin:
        import json
        if os.path.exists(link_to_plugin):
            try:
                with open(link_to_plugin, 'r') as f:
                    plugin_data = json.load(f)
                
                if "agents" not in plugin_data:
                    plugin_data["agents"] = []
                
                if not any(a.get("name") == name for a in plugin_data["agents"]):
                    plugin_data["agents"].append({
                        "name": name,
                        "path": file_path
                    })
                    with open(link_to_plugin, 'w') as f:
                        json.dump(plugin_data, f, indent=2)
                    print(f"Linked agent '{name}' to plugin at {link_to_plugin}")
                else:
                    print(f"Agent '{name}' already linked in {link_to_plugin}")
            except Exception as e:
                print(f"Failed to link to plugin {link_to_plugin}: {e}")
        else:
            print(f"Plugin file {link_to_plugin} not found. Skipping linking.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new agent.")
    parser.add_argument("--name", required=True, help="Kebab-case name of the agent")
    parser.add_argument("--scope", choices=["user", "project"], default="project", help="Scope of the agent")
    parser.add_argument("--background", action="store_true", help="Set background agent flag")
    parser.add_argument("--isolation", choices=["worktree", "none"], help="Isolation mode")
    parser.add_argument("--target-dir", default=".", help="Target directory for the agent")
    parser.add_argument("--link-to-plugin", help="Path to plugin.json to link this agent")
    args = parser.parse_args()
    
    scaffold_agent(args.name, args.scope, args.background, args.isolation, args.target_dir, args.link_to_plugin)
