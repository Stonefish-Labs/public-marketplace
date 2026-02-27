#!/usr/bin/env python3
import os
import json
import argparse

def scaffold_hook(event, hook_type, async_flag, target_dir=".", link_to_plugin=None):
    """Scaffold a new hook configuration based on its event and type."""
    os.makedirs(target_dir, exist_ok=True)
    
    hook_entry = {
        "type": hook_type
    }
    
    if hook_type == "command":
        script_name = f"hook_{event.lower()}.sh"
        script_path = os.path.join(target_dir, script_name)
        hook_entry["command"] = f"bash {script_path}"
        if async_flag:
            hook_entry["async"] = True
            
        if not os.path.exists(script_path):
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"# Command hook for {event}\n")
                f.write("echo 'Hook executed'\n")
            os.chmod(script_path, 0o755)
            print(f"Created command script at {script_path}")
            
    elif hook_type == "prompt":
        hook_entry["prompt"] = f"Prompt for {event} event"
    elif hook_type == "agent":
        hook_entry["agent"] = "architect"
        
    raw_hook_file = os.path.join(target_dir, f"hook_{event.lower()}.json")
    with open(raw_hook_file, "w") as f:
        json.dump({event: [hook_entry]}, f, indent=2)
    
    print(f"Raw hook configuration for {event} scaffolded in {raw_hook_file}")

    if link_to_plugin:
        plugin_dir = os.path.dirname(link_to_plugin) if link_to_plugin != "." else "."
        if plugin_dir == "":
            plugin_dir = "."
        claude_plugin_dir = os.path.join(plugin_dir, ".claude-plugin")
        os.makedirs(claude_plugin_dir, exist_ok=True)
        hooks_file = os.path.join(claude_plugin_dir, "hooks.json")
        
        if os.path.exists(hooks_file):
            try:
                with open(hooks_file, "r") as f:
                    hooks = json.load(f)
            except Exception:
                hooks = {}
        else:
            hooks = {}
        
        if event not in hooks:
            hooks[event] = []
            
        if hook_type == "command":
            linked_script_path = os.path.join(claude_plugin_dir, script_name)
            hook_entry["command"] = f"bash {linked_script_path}"
            if not os.path.exists(linked_script_path):
                import shutil
                shutil.copy2(script_path, linked_script_path)
                print(f"Copied command script to {linked_script_path}")
                
        hooks[event].append(hook_entry)
        
        with open(hooks_file, "w") as f:
            json.dump(hooks, f, indent=2)
            
        print(f"Hook linked for event {event} in {hooks_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new hook.")
    parser.add_argument("--event", required=True, help="Hook event name (e.g., WorktreeCreate)")
    parser.add_argument("--type", required=True, choices=["command", "prompt", "agent"], help="Type of hook")
    parser.add_argument("--async-flag", action="store_true", help="Set async flag for command hooks")
    parser.add_argument("--target-dir", default=".", help="Target directory for the hook")
    parser.add_argument("--link-to-plugin", help="Path to plugin.json to link this hook")
    args = parser.parse_args()
    
    scaffold_hook(args.event, args.type, args.async_flag, args.target_dir, args.link_to_plugin)
