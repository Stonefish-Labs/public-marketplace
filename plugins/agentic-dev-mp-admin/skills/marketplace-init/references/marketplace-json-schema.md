# Marketplace JSON Schema Reference

Reference for the marketplace.json format used by Claude Code plugin marketplaces.

## File Location

```
<marketplace-repo>/
  .claude-plugin/
    marketplace.json    <- This file
```

## Top-Level Schema

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Owner Name",
    "email": "optional@email.com"
  },
  "metadata": {
    "description": "Brief marketplace description",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [...]
}
```

### Required Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Marketplace identifier (kebab-case). Users see this: `plugin-name@marketplace-name` |
| `owner` | object | Maintainer info. `name` required, `email` optional |
| `plugins` | array | List of plugin entries |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `metadata.description` | string | Brief marketplace description |
| `metadata.version` | string | Marketplace catalog version |
| `metadata.pluginRoot` | string | Base directory for relative source paths |

### Reserved Marketplace Names

The following names are reserved by Anthropic and cannot be used:
- `claude-code-marketplace`
- `claude-code-plugins`
- `claude-plugins-official`
- `anthropic-marketplace`
- `anthropic-plugins`
- `agent-skills`
- `life-sciences`

Names that impersonate official marketplaces are also blocked (e.g., `official-claude-plugins`).

## Plugin Entry Schema

Each entry in the `plugins` array:

```json
{
  "name": "plugin-name",
  "source": "./plugins/plugin-name",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Author Name"
  },
  "keywords": ["skill", "bash"],
  "category": "developer-tools",
  "tags": ["searchable-tag"],
  "strict": true
}
```

### Required Plugin Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Plugin identifier (kebab-case). Users install with: `/plugin install name@marketplace` |
| `source` | string or object | Where to fetch the plugin |

### Optional Plugin Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | Brief plugin description |
| `version` | string | Plugin version (semver) |
| `author` | object | Author info (`name` required, `email` optional) |
| `homepage` | string | Documentation URL |
| `repository` | string | Source code URL |
| `license` | string | SPDX license identifier |
| `keywords` | array | Discovery tags |
| `category` | string | Organization category |
| `tags` | array | Searchability tags |
| `strict` | boolean | Whether plugin.json is authority for components (default: true) |

## Source Formats

### Relative Path (monorepo)

```json
"source": "./plugins/my-plugin"
```

Only works with Git-based marketplace distribution. Must start with `./`.

### GitHub

```json
"source": {
  "source": "github",
  "repo": "Stonefish-Labs/plugin-name",
  "ref": "v1.0.0",
  "sha": "a1b2c3d4..."
}
```

`ref` and `sha` are optional. `ref` pins to a branch/tag. `sha` pins to an exact commit.

### Git URL

```json
"source": {
  "source": "url",
  "url": "https://gitlab.com/team/plugin.git",
  "ref": "main"
}
```

URL must end with `.git`.

### npm

```json
"source": {
  "source": "npm",
  "package": "package-name",
  "version": "^1.0.0"
}
```

### pip

```json
"source": {
  "source": "pip",
  "package": "package-name",
  "version": ">=1.0.0"
}
```

## Version Resolution

- If version is set in both marketplace.json and the plugin's plugin.json, the plugin manifest wins silently
- For relative-path plugins: set version in marketplace entry
- For all other sources: set version in plugin's plugin.json
- Two refs/commits must have different manifest versions or Claude Code skips the update

## Release Channels

Use separate marketplace definitions for stable/beta:

**Stable:** `.claude-plugin/marketplace.json`
**Beta:** `channels/beta/.claude-plugin/marketplace.json`

Each channel is its own marketplace with its own name (e.g., `my-marketplace` and `my-marketplace-beta`). Assign channels to user groups via `extraKnownMarketplaces` in managed settings.
