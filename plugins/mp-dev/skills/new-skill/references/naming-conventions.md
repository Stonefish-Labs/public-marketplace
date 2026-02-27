# Naming Conventions

## Plugin Names

- **Format**: kebab-case (lowercase letters, numbers, hyphens)
- **Max length**: 64 characters
- **Examples**: `code-formatter`, `deployment-tools`, `security-scanner`
- **Avoid**: Generic names (`utils`, `tools`, `helpers`), single words, abbreviations

Plugin names become the namespace prefix for all skills: `plugin-name:skill-name`.

## Skill Names

- **Format**: kebab-case
- **Style**: Action verbs or verb phrases
- **Examples**: `scaffold`, `validate`, `deploy`, `review-pr`, `fix-issue`
- **Avoid**: Nouns without action context (`data`, `config`, `status`)

## Agent Names

- **Format**: kebab-case
- **Style**: Role-oriented nouns
- **Examples**: `code-reviewer`, `security-analyst`, `data-scientist`, `plugin-architect`
- **Avoid**: Generic names (`helper`, `assistant`, `worker`)

## Hook Script Names

- **Format**: kebab-case with `.sh` extension
- **Style**: Descriptive of what the hook does
- **Examples**: `on-file-change.sh`, `validate-command.sh`, `format-code.sh`

## MCP Server Names

- **Format**: kebab-case
- **Style**: Descriptive of the service or data source
- **Examples**: `project-db`, `api-client`, `file-analyzer`

## GitHub Repository Names

- **Format**: kebab-case, matching the plugin name
- **Examples**: `mp-dev`, `code-formatter`, `security-scanner`

## Topic Tags

- **Format**: kebab-case
- **Categories**: See classification-taxonomy.md
- **Always include**: `agent-marketplace`
- **Budget**: 3-8 total

## Reserved Names

These marketplace names are reserved by Anthropic:
- `claude-code-marketplace`
- `claude-code-plugins`
- `claude-plugins-official`
- `anthropic-marketplace`
- `anthropic-plugins`
- `agent-skills`
- `life-sciences`

Do not use names that impersonate official marketplaces.
