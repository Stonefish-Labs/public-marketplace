# Hook Best Practices

## Hook Design

- **Always use `${CLAUDE_PLUGIN_ROOT}`** for script paths in plugins.
- **Always use `$CLAUDE_PROJECT_DIR`** for script paths in project hooks.
- **Utilize new hook types**: Use `prompt` and `agent` hooks (instead of just `command`) to dynamically alter Claude's system prompt or spawn agents based on events.
- **Make scripts executable**: `chmod +x` every `.sh` file.
- **Include shebang lines**: `#!/usr/bin/env bash` at the top of every script.
- **Handle stdin gracefully**: Hook scripts receive JSON on stdin.
- **Exit codes matter**: 0 = success, 2 = block the action.
- **Keep hooks fast**: Slow hooks block Claude's execution. Background `command` hooks can use `async: true` if they shouldn't block.

## General

- **Use deterministic Python scripting**: Use the scaffolding script (`scripts/scaffold_hook.py`) to generate files rather than writing them by hand.
- **Self-contained**: Never reference files outside the plugin directory.
- **No absolute paths**: Use `${CLAUDE_PLUGIN_ROOT}` for all internal references.
