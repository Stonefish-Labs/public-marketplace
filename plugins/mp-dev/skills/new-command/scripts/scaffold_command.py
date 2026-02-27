#!/usr/bin/env python3
import os
import sys
import re
import argparse


def validate_name(name):
    """Validate that the command name is kebab-case."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Command name '{name}' must be kebab-case (lowercase letters, numbers, hyphens only).")
        sys.exit(1)


def validate_no_xml(text, field_name):
    """Validate that the given text does not contain XML tags."""
    if text and ('<' in text or '>' in text):
        print(f"Error: XML tags (< or >) are not allowed in the {field_name}.")
        sys.exit(1)


def scaffold_command(
    name,
    description,
    target_dir=".",
    scope="project",
    allowed_tools=None,
    model=None,
    argument_hint=None,
    namespace=None,
    bash_commands=None,
    file_refs=None,
    link_to_plugin=None,
):
    """Scaffold a new slash command as a markdown file."""
    validate_name(name)
    validate_no_xml(description, "description")

    # Resolve output directory: project scope -> target_dir/.claude/commands/
    # user scope -> ~/.claude/commands/
    if scope == "user":
        commands_dir = os.path.expanduser("~/.claude/commands")
    else:
        # Default to .claude/commands/ inside target_dir
        commands_dir = os.path.join(target_dir, ".claude", "commands")

    # If a namespace subdirectory is requested, nest inside it
    if namespace:
        validate_name(namespace)
        commands_dir = os.path.join(commands_dir, namespace)

    os.makedirs(commands_dir, exist_ok=True)

    file_path = os.path.join(commands_dir, f"{name}.md")

    with open(file_path, "w") as f:
        # Write YAML frontmatter
        has_frontmatter = any([description, allowed_tools, model, argument_hint])
        if has_frontmatter:
            f.write("---\n")
            if description:
                f.write(f"description: {description}\n")
            if allowed_tools:
                validate_no_xml(allowed_tools, "allowed-tools")
                f.write(f"allowed-tools: {allowed_tools}\n")
            if model:
                validate_no_xml(model, "model")
                f.write(f"model: {model}\n")
            if argument_hint:
                validate_no_xml(argument_hint, "argument-hint")
                f.write(f"argument-hint: {argument_hint}\n")
            f.write("---\n\n")

        # Command body
        f.write(f"# {name}\n\n")

        # Bash context blocks (executed at load time)
        if bash_commands:
            f.write("## Context\n\n")
            for cmd in bash_commands:
                f.write(f"- !`{cmd}`\n")
            f.write("\n")

        # File references
        if file_refs:
            f.write("## Files\n\n")
            for ref in file_refs:
                f.write(f"- @{ref}\n")
            f.write("\n")

        # Task body
        f.write("## Task\n\n")
        if argument_hint:
            f.write("Arguments: `$ARGUMENTS`\n\n")
        f.write("<!-- Describe what this command should do. -->\n")
        f.write("Replace this placeholder with the command's instructions.\n")

    print(f"Command '/{name}' scaffolded at {file_path}")
    print(f"Scope: {scope}")
    if namespace:
        print(f"Namespace: {namespace}")

    if link_to_plugin:
        import json
        if os.path.exists(link_to_plugin):
            try:
                with open(link_to_plugin, 'r') as f:
                    plugin_data = json.load(f)

                if "commands" not in plugin_data:
                    plugin_data["commands"] = []

                if not any(c.get("name") == name for c in plugin_data["commands"]):
                    plugin_data["commands"].append({
                        "name": name,
                        "path": file_path,
                    })
                    with open(link_to_plugin, 'w') as f:
                        json.dump(plugin_data, f, indent=2)
                    print(f"Linked command '{name}' to plugin at {link_to_plugin}")
                else:
                    print(f"Command '{name}' already linked in {link_to_plugin}")
            except Exception as e:
                print(f"Failed to link to plugin {link_to_plugin}: {e}")
        else:
            print(f"Plugin file {link_to_plugin} not found. Skipping linking.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new slash command markdown file.")
    parser.add_argument("--name", required=True, help="Kebab-case name of the command (becomes /name)")
    parser.add_argument("--description", required=True, help="Short description shown in /help listings")
    parser.add_argument(
        "--target-dir",
        default=".",
        help="Root directory for project-scope commands (creates .claude/commands/ inside it). Ignored for user scope.",
    )
    parser.add_argument(
        "--scope",
        choices=["project", "user"],
        default="project",
        help="'project' -> <target-dir>/.claude/commands/, 'user' -> ~/.claude/commands/",
    )
    parser.add_argument(
        "--allowed-tools",
        help="Comma-separated list of allowed tools (e.g. 'Read, Grep, Bash(git diff:*)')",
    )
    parser.add_argument(
        "--model",
        help="Model override (e.g. claude-opus-4-6, claude-haiku-4-5-20251001)",
    )
    parser.add_argument(
        "--argument-hint",
        help="Hint displayed for arguments (e.g. '[issue-number] [priority]')",
    )
    parser.add_argument(
        "--namespace",
        help="Optional subdirectory namespace inside commands/ (e.g. 'frontend', 'backend')",
    )
    parser.add_argument(
        "--bash-commands",
        nargs="+",
        help="Bash commands to embed as !`cmd` context blocks (executed at load time)",
    )
    parser.add_argument(
        "--file-refs",
        nargs="+",
        help="File paths to embed as @path references",
    )
    parser.add_argument(
        "--link-to-plugin",
        help="Path to plugin.json to register this command",
    )
    args = parser.parse_args()

    scaffold_command(
        name=args.name,
        description=args.description,
        target_dir=args.target_dir,
        scope=args.scope,
        allowed_tools=getattr(args, "allowed_tools", None),
        model=args.model,
        argument_hint=getattr(args, "argument_hint", None),
        namespace=args.namespace,
        bash_commands=getattr(args, "bash_commands", None),
        file_refs=getattr(args, "file_refs", None),
        link_to_plugin=getattr(args, "link_to_plugin", None),
    )
