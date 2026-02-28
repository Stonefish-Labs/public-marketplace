# Agent Best Practices

## Subagent Design

- **One agent, one purpose**: Each agent should excel at a specific task.
- **Minimal tool access**: Grant only the tools the agent actually needs.
- **Model selection**: Use `haiku` for fast read-only tasks, `sonnet` for analysis, `inherit` for general tasks.
- **Include "use proactively"** in the description if the agent should auto-invoke.
- **Use `memory`** for agents that should learn across sessions.
- **Use `isolation: worktree`**: Protect the main project by isolating subagents in a worktree, allowing them to experiment safely.
- **Run agents in the background**: For long-running tasks, use `background: true` to prevent blocking the user.

## General

- **Use deterministic Python scripting**: Use the scaffolding script (`scripts/scaffold_agent.py`) to generate files rather than writing markdown by hand.
- **Self-contained**: Never reference files outside the plugin directory.
- **No absolute paths**: Use `${CLAUDE_PLUGIN_ROOT}` for all internal references.
