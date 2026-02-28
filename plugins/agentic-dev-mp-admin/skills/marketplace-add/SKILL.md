---
name: marketplace-add
description: Add a plugin entry to an existing marketplace.json catalog. Supports both local directory (relative-path) and GitHub (owner/repo) sources. Use when the user wants to "add a plugin to the marketplace", "register a plugin", or "list a plugin in the catalog".
disable-model-invocation: true
argument-hint: <marketplace-dir> <plugin-source>
---

# Add Plugin to Marketplace

Add a single plugin entry to an existing `marketplace.json` catalog.

## Input

- `$ARGUMENTS[0]` — Path to marketplace directory (must contain `.claude-plugin/marketplace.json`)
- `$ARGUMENTS[1]` — Plugin source: a local directory path OR a GitHub `owner/repo` reference

Ask the user for any missing arguments.

## Steps

### 1. Read References

Read `references/marketplace-json-schema.md` to understand the plugin entry schema before building any entries.

### 2. Validate Marketplace

- Confirm `.claude-plugin/marketplace.json` exists at the marketplace path
- Parse and confirm it is valid JSON
- Extract existing plugin names from the `plugins` array (to use for duplicate detection)
- Note the `metadata.pluginRoot` value (typically `"./plugins"`)

### 3. Resolve Plugin Source

**If source is a local directory path:**

Read `.claude-plugin/plugin.json` from that directory. Extract:
- `name`, `description`, `version`, `author`, `keywords`

Determine the source format:
- If the local directory is inside `<marketplace-dir>/plugins/`: use relative path source `"./plugins/<plugin-name>"`
- If the local directory is outside the marketplace: ask the user whether they want to:
  a. Copy the plugin directory into `<marketplace-dir>/plugins/` (then use relative path)
  b. Use a GitHub source instead (ask for the `owner/repo`)

**If source is a GitHub reference (`owner/repo` format):**

Fetch and parse the plugin's manifest:
```bash
gh api repos/<owner>/<repo>/contents/.claude-plugin/plugin.json --jq '.content' | base64 -d
```

Extract: `name`, `description`, `version`, `author`, `keywords`

Use GitHub source format:
```json
{
  "source": "github",
  "repo": "<owner>/<repo>"
}
```

Ask the user if they want to pin to a specific ref or SHA. If yes, ask for the value and add `"ref": "<value>"` to the source object.

### 4. Check for Duplicates

If a plugin with the same `name` already exists in the `plugins` array:
- Warn the user: "A plugin named `<name>` already exists in this marketplace."
- Offer to: (a) update the existing entry or (b) cancel

### 5. Determine Category

If `keywords` contains recognizable category signals, suggest a category. Otherwise ask:
"What category best describes this plugin? (e.g., developer-tools, security, productivity, automation)"

### 6. Build Plugin Entry

Construct the entry per the schema in `references/marketplace-json-schema.md`:

```json
{
  "name": "<plugin-name>",
  "source": "<resolved-source>",
  "description": "<from-manifest>",
  "version": "<from-manifest>",
  "author": {
    "name": "<from-manifest>"
  },
  "keywords": ["<from-manifest>"],
  "category": "<detected-or-user-provided>"
}
```

Include `homepage` and `repository` fields if present in the source manifest.

### 7. Add to Marketplace

- Read current `marketplace.json`
- Append the new entry to the `plugins` array
- Write back with 2-space indentation
- Confirm the resulting JSON parses correctly

### 8. Optionally Add to Beta Channel

If `channels/beta/.claude-plugin/marketplace.json` exists:
- Ask: "Would you like to also add this plugin to the beta channel?"
- If yes: append the same entry to the beta marketplace and write it back

### 9. Report

Output:
- Plugin name and source type (relative path / GitHub)
- Marketplace it was added to
- Total plugin count in the catalog
- Reminder: "Run `/mp-admin:marketplace-publish` to commit and push these changes."

## Notes

- For GitHub sources, the plugin's `plugin.json` is the version authority — do not set `version` in the marketplace entry separately
- For relative-path (monorepo) sources, set `version` in the marketplace entry to match the plugin's `plugin.json`
- Do not add the `strict` field unless the user explicitly requests it
- If `gh` is not available or not authenticated, report clearly and stop
