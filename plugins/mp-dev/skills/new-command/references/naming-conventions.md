# Slash Command Naming Conventions

## Command Names

- **Format**: kebab-case (lowercase letters, numbers, hyphens)
- **Style**: Action verbs or verb phrases — the command *does* something
- **Max length**: 64 characters (keep it short; users type these)
- **Examples**: `review-pr`, `fix-issue`, `deploy`, `test`, `code-review`, `git-commit`
- **Avoid**: Nouns without action context (`config`, `data`), single ambiguous letters, abbreviations that aren't universally known

## Namespace Directories

- **Format**: kebab-case
- **Style**: Domain or layer names — where in the project the commands apply
- **Examples**: `frontend/`, `backend/`, `db/`, `infra/`, `ci/`
- **Avoid**: Deep nesting (one level max), names that duplicate the command name

The subdirectory appears in `/help` descriptions as a grouping label but does **not** change the invocation syntax. `/frontend/component.md` is invoked as `/component`, not `/frontend/component`.

## File Names

- **Format**: `<command-name>.md` — always `.md` extension
- **Exactly matches** the command name (no prefix, no suffix)
- **Examples**: `review-pr.md`, `fix-issue.md`, `test.md`

## Argument Hints

- **Format**: Bracket-wrapped descriptors in the `argument-hint` frontmatter field
- **Style**: Descriptive of the expected value, not the variable name
- **Examples**:
  - `[issue-number]`
  - `[issue-number] [priority]`
  - `[test-pattern]`
  - `[file-path] [branch]`
- **Avoid**: Technical variable names (`$1`, `arg1`), overly generic hints (`[args]`)

## Placeholders in the Command Body

| Placeholder | Meaning |
|---|---|
| `$ARGUMENTS` | Full argument string as typed by the user |
| `$1`, `$2`, ... | Positional arguments split by whitespace |

Use `$ARGUMENTS` when the command accepts free-form input. Use positional `$1`/`$2` when argument order is significant and documented.

## Scope Naming

| Scope | Location | When to Use |
|---|---|---|
| `project` | `<root>/.claude/commands/` | Project-specific workflows; commit to version control |
| `user` | `~/.claude/commands/` | Personal macros; applies across all projects |

There is no "global" or "system" scope beyond these two.
