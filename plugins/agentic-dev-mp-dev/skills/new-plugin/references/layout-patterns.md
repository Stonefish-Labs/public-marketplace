# Layout Patterns Reference

Standard directory structures for marketplace-compliant plugins. All plugins must follow these patterns to be accepted into the marketplace.

## Official Plugin Structure (Anthropic Standard)

```
plugin-name/
├── .claude-plugin/           # Metadata directory
│   └── plugin.json           # Plugin manifest (ONLY file in this dir)
├── skills/                   # Skills at plugin root
│   └── skill-name/
│       ├── SKILL.md          # Skill entrypoint (required)
│       ├── references/       # Supporting docs (optional)
│       └── scripts/          # Helper scripts (optional)
├── agents/                   # Subagent definitions
│   └── agent-name.md
├── hooks/                    # Hook configurations
│   └── hooks.json
├── .mcp.json                 # MCP server definitions
├── scripts/                  # Shared scripts for hooks/MCP, validators, and scaffolding (e.g. scaffold_*.py, validate_*.py)
├── README.md
├── LICENSE
└── .gitignore
```

**Critical rule:** Only `plugin.json` goes in `.claude-plugin/`. All component directories (`skills/`, `agents/`, `hooks/`) must be at the plugin root.

## Default Exclusions

These files always stay at root and are never moved during scaffolding:

```
.git, .github, .gitignore, .gitattributes, .gitmodules,
CODEOWNERS, LICENSE, LICENSE.md, LICENSE.txt,
README.md, README.rst, CONTRIBUTING.md, CHANGELOG.md,
.editorconfig, .pre-commit-config.yaml, .claude-plugin/
```

---

## Single Skill Plugin

```
my-skill-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── my-skill/
│       ├── SKILL.md
│       └── scripts/          # optional
├── README.md
├── LICENSE
└── .gitignore
```

## Single Hook Plugin

```
my-hook-plugin/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── hooks.json
├── scripts/
│   └── hook-handler.sh
├── README.md
├── LICENSE
└── .gitignore
```

## Single Agent Plugin

```
my-agent-plugin/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── my-agent.md
├── README.md
├── LICENSE
└── .gitignore
```

## Single MCP Server Plugin

```
my-mcp-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── mcp-servers/
│   └── my-server/
│       ├── server.py
│       └── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Multi-Asset Bundle Plugin

```
my-bundle/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── skill-one/
│   │   └── SKILL.md
│   └── skill-two/
│       ├── SKILL.md
│       └── references/
├── agents/
│   ├── reviewer.md
│   └── analyzer.md
├── hooks/
│   └── hooks.json
├── .mcp.json
├── scripts/
│   ├── on-file-change.sh
│   └── validate.sh
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

## Quick Reference

| Component | Directory | Key File | Config |
|---|---|---|---|
| Skill | `skills/<name>/` | `SKILL.md` | frontmatter |
| Agent | `agents/` | `<name>.md` | frontmatter |
| Hook | `hooks/` | `hooks.json` | JSON |
| MCP Server | `.mcp.json` (config) | `server.py`/`index.ts` (source) | JSON |
