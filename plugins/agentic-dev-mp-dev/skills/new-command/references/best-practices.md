# Slash Command Best Practices

## Command Design

- **Write a clear `description`**: This text appears in `/help` listings. Make it scannable — one sentence max.
- **Keep the command body focused**: Each command should do one thing well. Split complex workflows into multiple commands.
- **Use `$ARGUMENTS` for dynamic input**: Prefer `$ARGUMENTS` (full string) for flexible input, or `$1`/`$2` for positional args when order matters.
- **Provide an `argument-hint`**: Always set `argument-hint` when the command accepts arguments — it guides users in the CLI.
- **Restrict tools with `allowed-tools`**: Don't grant more tools than the command needs. Bash should be scoped to specific commands (e.g. `Bash(git diff:*)`).
- **Choose the right model**: Use `claude-haiku-4-5-20251001` for fast, read-only tasks; `claude-opus-4-6` for deep reasoning; omit the field to inherit the session default.

## Context Injection

- **Use `!`cmd`` for live context**: Bash blocks run at invocation time. Ideal for `git status`, `git diff`, timestamps, test output, or environment variables.
- **Use `@path` for static context**: File references inject file contents at invocation time. Best for config files, templates, or reference docs that rarely change.
- **Keep context tight**: Injecting too much context wastes tokens and slows responses. Only include what's directly relevant to the task.

## Scope and Organization

- **Project scope by default**: Use `.claude/commands/` for project-specific workflows. Commit these to version control so the whole team benefits.
- **User scope for personal macros**: Use `~/.claude/commands/` for commands that apply across all projects (personal review style, preferred commit format, etc.).
- **Use namespaces for large projects**: Subdirectories like `frontend/` or `backend/` keep `/help` output readable. The command name itself stays flat.
- **Don't over-namespace**: If you have fewer than ~5 commands, namespacing adds friction without benefit.

## Relationship to Skills

- **Skills vs. Commands**: Skills are plugin artifacts with rich metadata, lifecycle hooks, and tool configurations. Commands are lightweight prompt templates. Use skills for reusable components that travel with a plugin; use commands for project or personal workflows.
- **Skills can scaffold commands**: A skill's script can create `.claude/commands/*.md` files as part of project setup. This is a valid and recommended pattern.
- **Commands inside plugins**: Register commands in `plugin.json` using `--link-to-plugin` when they should be distributed as part of a plugin bundle.

## Authoring the Task Body

- **Don't leave placeholders**: The scaffold generates a placeholder `## Task` section. Always replace it with real instructions before committing.
- **Write instructions, not descriptions**: The body tells Claude *what to do*, not what the command *is*. Use imperative language.
- **Structure with headers**: For multi-step commands, use `##` sections (Context, Checklist, Task, etc.) to make the flow legible.
- **Include success criteria**: Tell Claude what "done" looks like, especially for commands that modify files or run processes.

## Security

- **Never embed secrets**: Don't put API keys, tokens, or credentials in command files. Use environment variables accessed via `!`echo $MY_VAR``.
- **Scope Bash carefully**: Use `Bash(specific-cmd:*)` patterns rather than unrestricted `Bash` to limit blast radius.
- **Audit user-scope commands**: Personal commands in `~/.claude/commands/` run in every project. Be conservative with what they can access.
