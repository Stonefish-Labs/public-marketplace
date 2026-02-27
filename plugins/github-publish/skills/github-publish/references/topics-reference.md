# GitHub Topics Reference

Common topics for repository discoverability.

## Agent/AI Topics

| Topic | Use When |
|-------|----------|
| `ai-agents` | Any AI agent tooling |
| `agent-skills` | Agent skill packages |
| `skills` | Skill-related projects |
| `mcp` | Model Context Protocol projects |
| `cursor` | Works with Cursor IDE |
| `claude-code` | Works with Claude Code |
| `codex` | Works with Codex |
| `roo` | Works with Roo |
| `ai` | General AI projects |
| `llm` | LLM-related projects |
| `automation` | Automation tooling |

## Language Topics

| Topic | Use When |
|-------|----------|
| `python` | Python code |
| `typescript` | TypeScript code |
| `javascript` | JavaScript code |
| `rust` | Rust code |
| `go` | Go code |
| `shell` | Shell scripts |
| `bash` | Bash scripts |

## Domain Topics

| Topic | Use When |
|-------|----------|
| `developer-tools` | Dev tooling |
| `cli` | Command-line interfaces |
| `knowledge-management` | Note/knowledge systems |
| `documentation` | Doc generation/management |
| `workflow` | Workflow automation |
| `productivity` | Productivity tools |
| `devops` | DevOps tooling |
| `api` | API-related |
| `markdown` | Markdown processing |
| `yaml` | YAML processing |

## Best Practices

### How Many Topics?

- 5-10 topics is ideal
- Don't over-tag — only relevant topics
- Mix general and specific

### Topic Selection Strategy

1. **Language/tech**: What's it built with?
2. **Domain**: What problem space?
3. **Platform**: Where does it run?
4. **Audience**: Who uses it?

### Example Selections

**Agent skill repo (Python):**
```bash
gh repo edit owner/repo \
  --add-topic ai-agents \
  --add-topic agent-skills \
  --add-topic skills \
  --add-topic python \
  --add-topic cursor \
  --add-topic claude-code \
  --add-topic automation
```

**MCP server:**
```bash
gh repo edit owner/repo \
  --add-topic mcp \
  --add-topic ai-agents \
  --add-topic python \
  --add-topic api \
  --add-topic automation
```

**Knowledge management skills:**
```bash
gh repo edit owner/repo \
  --add-topic agent-skills \
  --add-topic knowledge-management \
  --add-topic markdown \
  --add-topic yaml \
  --add-topic notes \
  --add-topic cursor \
  --add-topic claude-code
```

**Developer tool:**
```bash
gh repo edit owner/repo \
  --add-topic developer-tools \
  --add-topic cli \
  --add-topic productivity \
  --add-topic python
```

## Removing Topics

```bash
gh repo edit owner/repo --remove-topic old-topic
```

## Viewing Current Topics

```bash
gh repo view owner/repo --json repositoryTopics
```
