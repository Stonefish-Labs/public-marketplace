---
name: marketplace-sync
description: Audit all catalog entries in a marketplace for broken sources, version mismatches, missing metadata, and stale repositories. Offers to apply fixes. Use when the user wants to "sync", "audit", "check", or "validate" a marketplace catalog.
disable-model-invocation: true
argument-hint: [marketplace-dir]
---

# Marketplace Sync

Audit a marketplace catalog to find broken sources, version mismatches, stale plugins, and metadata gaps.

## Input

`$ARGUMENTS` is the path to the marketplace directory (default: current directory).

## Steps

### 1. Resolve Marketplace

- Use `$ARGUMENTS` as the marketplace path, or default to current directory
- Read and parse `.claude-plugin/marketplace.json`
- Report an error and stop if the file does not exist or is invalid JSON
- Note total plugin count before checking

### 2. Check Each Plugin Entry

For every entry in the `plugins` array, run:

```bash
python3 scripts/sync_marketplace.py --marketplace <marketplace-dir> --plugin '<entry-json>'
```

The script checks each entry and outputs a JSON result with status, issues, and suggested fixes.

Per entry, the script verifies:

**Source Existence:**
- Relative path (`"./plugins/..."`) → check the directory exists and contains `.claude-plugin/plugin.json`
- GitHub source → `gh repo view <owner>/<repo> --json name 2>/dev/null` (non-zero exit = unreachable)
- Git URL source → `git ls-remote <url> 2>/dev/null` (non-zero exit = unreachable)
- Unreachable sources are reported as `[ERROR]`

**Version Consistency:**
- Relative path: compare catalog entry `version` vs `plugin.json` `version` in the source directory
- GitHub source: fetch remote `plugin.json` and compare versions:
  ```bash
  gh api repos/<owner>/<repo>/contents/.claude-plugin/plugin.json --jq '.content' | base64 -d
  ```
- Mismatches are reported as `[WARN]`

**Metadata Completeness:**
- Required: `name`, `source` (already validated by catalog existence)
- Flag as `[INFO]` if missing: `description`, `version`, `author`, `keywords`

**Staleness (GitHub sources only):**
- Check last push date: `gh api repos/<owner>/<repo> --jq '.pushed_at'`
- Flag as `[WARN]` if not updated in more than 6 months

### 3. Check Beta Channel

If `channels/beta/.claude-plugin/marketplace.json` exists:
- Run the same checks on every beta entry
- Additional cross-reference: note any entry that is in beta but not in stable (normal during rollout — report as `[INFO]`)

### 4. Print Structured Report

```
Marketplace Sync: <marketplace-name>
════════════════════════════════════

Total: N  Healthy: N  Warnings: N  Errors: N

Errors:
  [ERROR] plugin-x — source not found: ./plugins/plugin-x
  [ERROR] plugin-y — GitHub repo unreachable: owner/plugin-y

Warnings:
  [WARN]  plugin-z — version mismatch: catalog=1.0.0, source=1.1.0
  [WARN]  plugin-w — last updated 8 months ago (2024-06-10)

Info:
  [INFO]  plugin-a — missing: keywords, author
  [INFO]  beta: plugin-b is in beta but not in stable (pending promotion)

Beta Channel: <N> entries checked, <N> issues
```

If everything is healthy, report: "All N plugins healthy. No issues found."

### 5. Offer Fixes

For each fixable issue, offer to apply the fix. Present fixes one at a time, or group them if the user says "fix all":

| Issue | Offered Fix |
|---|---|
| Version mismatch | Update catalog entry version to match source |
| Missing metadata | Pull `description`, `author`, `keywords` from source `plugin.json` |
| Dead entry (source not found) | Remove the entry from `marketplace.json` |

Apply only what the user explicitly approves. After any fix, confirm the resulting JSON is valid.

### 6. Final Reminder

If any fixes were applied:
- Remind user: "Run `/mp-admin:marketplace-publish` to commit and push these changes."

## Notes

- The script requires `gh` CLI to be installed and authenticated for GitHub source checks
- Staleness is a warning only — stale repos are not automatically removed
- Version mismatches for GitHub sources are expected if the plugin was updated but the marketplace entry wasn't re-added
