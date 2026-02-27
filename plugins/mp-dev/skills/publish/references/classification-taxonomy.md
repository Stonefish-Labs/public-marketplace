# Classification Taxonomy

Reference for the publish skill's asset detection logic and topic tagging strategy.

## Marketplace Eligibility

A directory is **marketplace-eligible** only if it contains `.claude-plugin/plugin.json`.
Standalone components (no `plugin.json`) can be published to GitHub but cannot be listed
in a `marketplace.json` plugins array. They must be bundled into a plugin first.

## Asset Detection Signals

| Asset Type | Detection Signal |
|---|---|
| `skill` | `skills/*/SKILL.md` exists |
| `agent` | `agents/*.md` with YAML frontmatter (starts with `---`) |
| `hook` | `.claude-plugin/hooks.json`, `hooks/hooks.json`, or `.hooks.json` |
| `mcp` | `.mcp.json` or `mcp-servers/` directory |
| `command` | `commands/*.md` exists |

## GitHub Topic Tags

### Asset Type Topics

| Asset | Topic Tag |
|---|---|
| `skill` | `skill` |
| `agent` | `subagent` |
| `hook` | `hook` |
| `mcp` | `mcp-server` |
| `command` | `command` |

### Marketplace Tag

`agent-marketplace` — applied only when the directory is a plugin (has `plugin.json`).

### Language Tags

Added only when source files of that type are detected in the directory tree:

| Language | File Pattern |
|---|---|
| `python` | `*.py` |
| `bash` | `*.sh` |
| `javascript` | `*.js` |
| `typescript` | `*.ts` |

## Topic Budget

Topics are applied in this order, capped at GitHub's 20-topic limit:

1. `agent-marketplace` (plugin only)
2. Asset type tags (one per detected type)
3. Language tags (one per detected language)

## Primary Classification (for reference)

| Signal | Class | Marketplace Eligible |
|---|---|---|
| Has `plugin.json` + any asset | `marketplace-item` | Yes |
| No `plugin.json`, has asset files | `standalone-component` | No |
| Markdown docs only | `knowledge-article` | No |
