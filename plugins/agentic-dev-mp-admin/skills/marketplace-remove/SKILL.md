---
name: marketplace-remove
description: Remove a plugin entry from an existing marketplace.json catalog. Optionally removes from the beta channel too. Use when the user wants to "remove a plugin from the marketplace", "unlist a plugin", or "delete a catalog entry".
disable-model-invocation: true
argument-hint: <marketplace-dir> <plugin-name>
---

# Remove Plugin from Marketplace

Remove a plugin entry from an existing `marketplace.json` catalog.

## Input

- `$ARGUMENTS[0]` — Path to marketplace directory (must contain `.claude-plugin/marketplace.json`)
- `$ARGUMENTS[1]` — Name of the plugin to remove (the `name` field in the catalog entry)

Ask the user for any missing arguments.

## Steps

### 1. Validate Marketplace

- Confirm `.claude-plugin/marketplace.json` exists at the marketplace path
- Parse and confirm it is valid JSON
- Extract the full list of plugin names for reference

### 2. Find the Entry

Search the `plugins` array for an entry where `name` exactly matches `$ARGUMENTS[1]`.

If not found:
- Report: "No plugin named `<name>` found in this marketplace."
- List all available plugin names so the user can correct the name
- Stop

### 3. Confirm Removal

Show the full plugin entry that will be removed:

```
About to remove:
  name:    <plugin-name>
  source:  <source>
  version: <version>

Confirm removal? (yes/no)
```

Wait for explicit confirmation. If the user says no, cancel and report "Removal cancelled."

### 4. Remove from Stable Catalog

- Remove the matched entry from the `plugins` array
- Write the updated `marketplace.json` back with 2-space indentation
- Confirm the resulting JSON parses correctly

### 5. Check Beta Channel

If `channels/beta/.claude-plugin/marketplace.json` exists:
- Check if it contains an entry with the same plugin name
- If yes, ask: "This plugin is also in the beta channel. Remove it from beta too?"
- If yes: remove it from the beta catalog and write back
- If no: leave the beta entry intact

### 6. Report

Output:
- Plugin name that was removed
- Which catalogs were updated (stable only, or stable + beta)
- New total plugin count in the stable catalog
- Reminder: "Run `/mp-admin:marketplace-publish` to commit and push these changes."

## Notes

- This only removes the catalog entry — it does not delete the actual plugin repository or local directory
- If the plugin is in the marketplace's `plugins/` directory (monorepo style), the directory is left untouched; inform the user they may want to delete it manually
