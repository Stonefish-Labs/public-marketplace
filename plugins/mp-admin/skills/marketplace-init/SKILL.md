---
name: marketplace-init
description: Create a new marketplace repository from scratch with the standard directory structure, stable and beta marketplace.json files, and optional GitHub publish. Use when the user wants to "create a marketplace", "new marketplace", or "init a marketplace".
disable-model-invocation: true
argument-hint: <marketplace-name>
---

# Initialize Marketplace

Create a new Claude Code plugin marketplace with the standard structure.

## Input

`$ARGUMENTS` is the marketplace name (kebab-case). Ask the user if not provided.

## Steps

### 1. Resolve and Validate Name

- Use `$ARGUMENTS` as the marketplace name, or ask: "What should the marketplace be named? (kebab-case, e.g. my-plugins)"
- Validate:
  - Kebab-case only: lowercase letters, numbers, hyphens. No spaces or underscores.
  - Not a reserved Anthropic name (see `references/marketplace-json-schema.md` for the reserved list)
  - Max 64 characters
- If invalid, explain the problem and ask for a corrected name.

### 2. Gather Metadata

Ask the following:
- **Owner name**: "What is the owner name for this marketplace? (your name or org name)"
- **Description**: "Brief description of this marketplace:"
- **GitHub org/username**: "Which GitHub org or username will host this? (needed if you want to publish now)"

### 3. Create Directory Structure

Create the following layout under the current working directory:

```
<marketplace-name>/
  .claude-plugin/
    marketplace.json
  plugins/
  channels/
    beta/
      .claude-plugin/
        marketplace.json
  README.md
```

### 4. Write Stable marketplace.json

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "<marketplace-name>",
  "owner": {
    "name": "<owner-name>"
  },
  "metadata": {
    "description": "<description>",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": []
}
```

### 5. Write Beta Channel marketplace.json

Create `channels/beta/.claude-plugin/marketplace.json`:

```json
{
  "name": "<marketplace-name>-beta",
  "owner": {
    "name": "<owner-name>"
  },
  "metadata": {
    "description": "Beta channel for <marketplace-name>",
    "version": "1.0.0",
    "pluginRoot": "../../plugins"
  },
  "plugins": []
}
```

### 6. Write README.md

Create `README.md` in the marketplace root:

```markdown
# <marketplace-name>

<description>

## Add This Marketplace

```shell
/plugin marketplace add <github-org>/<marketplace-name>
```

## Install Plugins

```shell
/plugin install <plugin-name>@<marketplace-name>
```

## Available Plugins

This marketplace currently has no plugins. Use `/mp-admin:marketplace-add` to add plugins.

## Beta Channel

A beta channel is available for testing pre-release plugins:

```shell
/plugin marketplace add <github-org>/<marketplace-name> --ref channels/beta
```
```

### 7. Ask About Git and GitHub

Ask: "Would you like to initialize git and publish this marketplace to GitHub now?"

If yes:
```bash
cd <marketplace-name>
git init
git add -A
git commit -m "chore: initialize marketplace <marketplace-name>"
gh repo create <github-org>/<marketplace-name> --public --source=. --push --description "<description>"
gh repo edit <github-org>/<marketplace-name> --add-topic claude-marketplace
```

If `gh` is not installed or authenticated, report the error clearly and provide the manual steps.

If no: skip this step.

### 8. Report

Output:
- Confirmation of the directory structure created
- GitHub URL (if published)
- Stable install command: `/plugin marketplace add <github-org>/<marketplace-name>`
- Beta install command: `/plugin marketplace add <github-org>/<marketplace-name> --ref channels/beta`
- Next step: use `/mp-admin:marketplace-add` to add plugins

## Notes

- The `plugins/` directory is where monorepo-style plugins live (when using relative-path sources)
- Plugins from external GitHub repos do not need to be copied into `plugins/`
- Use `/mp-admin:marketplace-add` to add both local and GitHub-sourced plugins
- Use `/mp-admin:marketplace-publish` to push future changes to GitHub
