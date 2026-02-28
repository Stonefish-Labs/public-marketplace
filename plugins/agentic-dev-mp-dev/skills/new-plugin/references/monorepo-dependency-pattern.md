# Monorepo and Bundle Pattern for Plugin Organization

When developing complex plugins or tools, organizing your codebase effectively is crucial for performance, maintainability, and user experience. This guide explains the Monorepo/Bundle pattern.

## Monolithic Plugins vs. Bundles/Monorepos

### Monolithic Plugins
A **monolithic plugin** structure places all skills, hooks, agents, and MCP servers into a single root directory (a single `plugin.json` file at the root). When a user installs this plugin, they get everything, regardless of whether they need all the features.

### Bundles / Monorepos
A **bundle or monorepo** pattern involves housing multiple, distinct sub-plugins within a single repository. Instead of a single root `plugin.json`, each subdirectory has its own `.claude-plugin/plugin.json` (or root `plugin.json` within that sub-folder).

For example:
```text
fastmcp-dev/ (Repository Root)
├── mp-fastmcp-core/
│   └── .claude-plugin/plugin.json
├── mp-fastmcp-advanced/
│   └── .claude-plugin/plugin.json
└── mp-fastmcp-testing/
    └── .claude-plugin/plugin.json
```

## Why Split Plugins Granularly?

Splitting monolithic plugins into granular sub-plugins within a single repository offers two major advantages:

1. **Context Window Management:** Large plugins consume significant token space in the LLM's context window. By breaking a massive plugin into smaller, domain-specific plugins (like `core`, `advanced`, and `testing`), users only load the context they actively need for their current task. This keeps the LLM focused and reduces token usage.
2. **User Specialization:** Users have different needs. A beginner might only need the `core` plugin, while a power user might need `advanced` features. Granular plugins allow users to tailor their environment to their specific workflow without being overwhelmed by irrelevant tools or skills.

## Handling Shared Skills

A common challenge in monorepos is sharing skills or tools between sub-plugins. The official `plugin.json` schema does **not** support a `dependencies` field for inter-plugin dependencies. Instead, use one of these patterns:

### Option 1: Symlinks
Use symbolic links to reference shared skills from a common library directory into each sub-plugin that needs them. Symlinks are honored during the plugin copy/cache process.

```bash
# Inside mp-fastmcp-advanced/skills/
ln -s ../../shared/skills/common-utils.md ./common-utils.md
```

### Option 2: Copy shared components
For simplicity, copy shared skills into each sub-plugin that needs them. This trades some duplication for straightforward packaging.

### Option 3: Marketplace-level composition
If using a marketplace, list sub-plugins as separate entries. Users can install only the sub-plugins they need. Document which sub-plugins are prerequisites for others in the plugin's README.

## Handling Shared MCP Servers

When multiple sub-plugins need the same MCP server, there are two approaches. **Ask the user which they prefer before packaging.**

### Option 1: Bundle the server into each plugin (simple)

Copy or symlink the MCP server into each sub-plugin that needs it. The server is self-contained and versioned with the plugin. Best when:
- The server is small and tightly coupled to the plugin's functionality
- You want the plugin to be fully self-contained
- You don't expect the server to be shared outside this monorepo

### Option 2: Host the server separately on GitHub (shared/decoupled)

Publish the MCP server as a standalone Python package in its own GitHub repository. Each plugin references it by URL in its `.mcp.json` rather than bundling a copy. Best when:
- Multiple plugins share the same server
- You want to update the server independently of the plugins
- You want each plugin to pin to a specific tested version

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["git+https://github.com/your-org/my-mcp-server@a1b2c3d4e5f6"]
    }
  }
}
```

**Pinning options:**
- `@main` — always latest on the branch (floating, auto-updates)
- `@v1.2.0` — a release tag
- `@a1b2c3d4e5f6` — exact commit hash (fully pinned, recommended for stability)

**Configuration:** Since the server isn't bundled, you can't include config files from the server's repo. Configure the server entirely through CLI args and environment variables in `.mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["git+https://github.com/your-org/my-mcp-server@a1b2c3d4e5f6", "--port", "8080"],
      "env": {
        "API_KEY": "${MY_API_KEY}",
        "SOME_SETTING": "value"
      }
    }
  }
}
```

This means the MCP server should be designed to accept all configuration via args/env rather than reading from a bundled config file.

**Note:** Git submodules are not supported. The plugin cache does not initialize submodules on install.
