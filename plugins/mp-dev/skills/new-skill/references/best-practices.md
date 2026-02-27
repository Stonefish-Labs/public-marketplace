# Plugin Best Practices

## Skill Design

- **Write clear descriptions**: Claude uses the `description` field to auto-invoke skills. Be specific about when to use the skill.
- **Keep SKILL.md under 500 lines**: Move detailed reference material to separate files.
- **Use `disable-model-invocation: true`** for skills with side effects (publish, deploy, delete).
- **Use `context: fork`** for skills that need isolation (long research, large output).
- **Use `allowed-tools`** to restrict what Claude can do during skill execution.
- **Use `$ARGUMENTS`** for dynamic input rather than hardcoding values.

## Subagent Design

- **One agent, one purpose**: Each agent should excel at a specific task.
- **Minimal tool access**: Grant only the tools the agent actually needs.
- **Model selection**: Use `haiku` for fast read-only tasks, `sonnet` for analysis, `inherit` for general tasks.
- **Include "use proactively"** in the description if the agent should auto-invoke.
- **Use `memory`** for agents that should learn across sessions.
- **Use `isolation: worktree`**: Protect the main project by isolating subagents in a worktree, allowing them to experiment safely.
- **Run agents in the background**: For long-running tasks, use `background: true` to prevent blocking the user.

## Hook Design

- **Always use `${CLAUDE_PLUGIN_ROOT}`** for script paths in plugins.
- **Always use `$CLAUDE_PROJECT_DIR`** for script paths in project hooks.
- **Utilize new hook types**: Use `prompt` and `agent` hooks (instead of just `command`) to dynamically alter Claude's system prompt or spawn agents based on events.
- **Make scripts executable**: `chmod +x` every `.sh` file.
- **Include shebang lines**: `#!/usr/bin/env bash` at the top of every script.
- **Handle stdin gracefully**: Hook scripts receive JSON on stdin.
- **Exit codes matter**: 0 = success, 2 = block the action.
- **Keep hooks fast**: Slow hooks block Claude's execution. Background `command` hooks can use `async: true` if they shouldn't block.

## MCP Server Design

- **Use stdio transport** for plugin-bundled servers.
- **Implement all required methods**: `initialize`, `tools/list`, `tools/call`, `ping`.
- **Provide clear tool descriptions**: Claude uses these to understand tool capabilities. **Optimize for dynamic MCP Tool Search:** Write high-quality descriptions because Claude dynamically searches and loads tools when the available tools exceed 10% of the context window.
- **Type your input schemas**: Use JSON Schema for tool parameters.

## General

- **Use deterministic Python scripting**: Strongly emphasize the new deterministic Python scripting approach (`scripts/scaffold_*.py`) for generating files over the old LLM markdown parsing approach.
- **Self-contained**: Never reference files outside the plugin directory.
- **No absolute paths**: Use `${CLAUDE_PLUGIN_ROOT}` for all internal references.
- **No path traversal**: Never use `../` in configs or scripts.
- **Version everything**: Include `version` in plugin.json for cache management.
- **Document**: Include README.md with install instructions, usage examples, and component inventory.
- **License**: Include LICENSE file for distribution.
- **Test locally**: Use `claude --plugin-dir ./` before publishing.
