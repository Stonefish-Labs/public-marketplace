---
name: new-command
description: Scaffold a new slash command markdown file by collecting parameters and executing the scaffolding script. Use this skill when the user wants to "create a slash command", "add a custom command", "build a /command", or "scaffold a command". It walks through collecting the command name, description, scope (project or user), optional tool restrictions, model override, argument hints, namespace, bash context blocks, and file references, then generates a spec-compliant .md file in the correct .claude/commands/ location. Do not use this for creating skills, agents, hooks, or MCP servers.
disable-model-invocation: true
argument-hint: <command-name>
---

# Create New Slash Command

Generate a new slash command markdown file using the deterministic Python script.

## Background

Slash commands are markdown files placed in `.claude/commands/` (project-scoped) or `~/.claude/commands/` (user-scoped). They are distinct from Skills:

- **Skills** are plugin artifacts with rich metadata, tool restrictions, and lifecycle hooks — consumed by the Claude plugin system.
- **Slash commands** are lightweight prompt templates invoked via `/command-name` — surfaced by the SDK's `slash_commands` list and directly in the Claude Code CLI.

Skills can *include* slash commands as part of their output (e.g., a skill that provisions a project's `.claude/commands/` folder). They are complementary, not competing.

## Input

`$ARGUMENTS` is the name for the new command (kebab-case, no leading slash). If not provided, ask the user.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder before prompting the user.

1. Ask the user for the following parameters if not provided:

   - `name`: Kebab-case name (the command becomes `/name`). No leading slash.
   - `description`: Short description shown in `/help` listings. No XML tags.
   - `scope`: Where the command lives:
     - `project` (default) → `<target-dir>/.claude/commands/` — available only in this project
     - `user` → `~/.claude/commands/` — available across all projects
   - `target-dir`: Root directory for project-scoped commands (default `.`). Ignored for user scope.
   - `namespace`: Optional subdirectory inside `commands/` for grouping (e.g. `frontend`, `backend`). The subdirectory appears in descriptions but does not change the command name.
   - `allowed-tools`: Comma-separated tool restrictions (e.g. `Read, Grep, Bash(git diff:*)`). Optional.
   - `model`: Model override. Optional (e.g. `claude-opus-4-6`, `claude-haiku-4-5-20251001`).
   - `argument-hint`: Hint text for arguments displayed to users (e.g. `[issue-number] [priority]`). Optional. Use `$ARGUMENTS` or positional `$1`, `$2` in the command body.
   - `bash-commands`: Bash commands to embed as `!`cmd`` context blocks — executed at load time to inject live context. Optional (space-separated list).
   - `file-refs`: File paths to embed as `@path` references for static context injection. Optional.

2. Execute the Python scaffolding script:

   ```bash
   python scripts/scaffold_command.py \
     --name "<name>" \
     --description "<description>" \
     --scope "<scope>" \
     --target-dir "<target-dir>" \
     [--namespace "<namespace>"] \
     [--allowed-tools "<allowed-tools>"] \
     [--model "<model>"] \
     [--argument-hint "<argument-hint>"] \
     [--bash-commands <cmd1> <cmd2> ...] \
     [--file-refs <path1> <path2> ...] \
     [--link-to-plugin "<path-to-plugin.json>"]
   ```

3. After the script runs, open the generated `.md` file and help the user fill in the `## Task` section with the actual command instructions. The script intentionally leaves this as a placeholder — the command's purpose should be authored, not auto-generated.

4. Report the final file location and how to invoke the command (`/name` or `/namespace:name` if namespaced).

## Notes

- Commands support `$ARGUMENTS` (full argument string) or positional `$1`, `$2`, etc.
- Bash context blocks (`!`cmd``) run at invocation time — ideal for injecting `git status`, timestamps, or environment state.
- File references (`@path`) inject static file contents — ideal for config files or templates.
- Namespacing groups commands visually in `/help` but the command name itself stays flat (e.g. `/component`, not `/frontend/component`).
- To include a command inside a plugin, use `--link-to-plugin` to register it in `plugin.json`.
