---
name: new-agent
description: Scaffold a new independent agent component by collecting parameters and executing the agent scaffolding script. Use this skill when the user asks to "create an agent", "build a new agent", or "generate an independent agent". It walks the user through collecting the agent name, target directory, scope, isolation mode, and background flag, then builds a spec-compliant single markdown file for the agent. Do not use this for generating skills, hooks, or MCP servers.
disable-model-invocation: true
argument-hint: <agent-name>
---

# Create New Independent Agent

Generate a new independent agent definition using the deterministic python script.

## Input

`$ARGUMENTS` is the name for the new agent (kebab-case). If not provided, ask the user.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder to review naming conventions and design best practices before prompting the user.
1. Ask the user for the following parameters if not provided:
   - `name`: Kebab-case name of the agent.
   - `target-dir`: "Where would you like to create this component? (e.g. library/agents, or .)"
   - `scope`: Scope of the agent (user or project, defaults to project).
   - `background`: Set background agent flag (boolean).
   - `isolation`: Isolation mode (worktree or none).

2. Execute the python scaffolding script:
   ```bash
   python scripts/scaffold_agent.py --name <name> --target-dir <target-dir> [--scope <scope>] [--background] [--isolation <isolation>] [--link-to-plugin]
   ```
   *(Note: include the optional flags based on the user's responses)*

4. Report what was created based on the script's output. Do not update `plugin.json` by default.
