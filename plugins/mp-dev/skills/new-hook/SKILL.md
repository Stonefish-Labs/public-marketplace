---
name: new-hook
description: Scaffold a new standalone hook configuration by collecting parameters and executing the hook scaffolding script. Use this skill when the user explicitly requests to "create a hook", "build a new hook", "scaffold a hook event", or generate a pre-tool/post-tool hook. It prompts the user for the hook event name, type (command, prompt, agent), async flag, and target directory. It generates the required `.json` configuration and shell scripts. Do not use this for generating regular skills, agents, or MCP servers.
disable-model-invocation: true
---

# Create New Standalone Hook

Generate a new standalone hook configuration using the deterministic python script.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder to review naming conventions and design best practices before prompting the user.
1. Ask the user for the following parameters:
   - `event`: Hook event name (e.g., WorktreeCreate, PreToolUse, PostToolUse).
   - `target-dir`: "Where would you like to create this component? (e.g. library/hooks, or .)"
   - `type`: Type of hook (command, prompt, agent).
   - `async-flag`: Whether to set the async flag for command hooks (boolean, only applicable if type is "command").

2. Execute the python scaffolding script:
   ```bash
   python scripts/scaffold_hook.py --event <event> --type <type> --target-dir <target-dir> [--async-flag] [--link-to-plugin]
   ```
   *(Note: include the optional flags based on the user's responses)*

4. Report what was created based on the script's output. Do not update `plugin.json` by default.
