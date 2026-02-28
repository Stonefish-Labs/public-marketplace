---
name: version-bump
description: Bump the semantic version in a plugin's plugin.json OR a marketplace's metadata.version. Optionally updates CHANGELOG.md. Use when the user wants to "bump version", "release a new version", "increment version", or "update the version".
disable-model-invocation: true
argument-hint: <target-dir> [major|minor|patch]
---

# Version Bump

Bump the semantic version of a plugin or marketplace catalog.

## Input

- `$ARGUMENTS[0]` — Path to the directory to bump (default: current directory)
- `$ARGUMENTS[1]` — Bump type: `major`, `minor`, or `patch` (default: `patch`)

## Steps

### 1. Parse Arguments

- Resolve `$ARGUMENTS[0]` as a directory path (default: `.`)
- Validate `$ARGUMENTS[1]` is one of `major`, `minor`, `patch` (default to `patch` if not provided)

### 2. Detect What to Bump

Check what the target directory contains:

| Condition | Action |
|---|---|
| Has `.claude-plugin/marketplace.json`, no `plugin.json` | Bump `metadata.version` in `marketplace.json` |
| Has `.claude-plugin/plugin.json`, no `marketplace.json` | Bump `version` in `plugin.json` |
| Has both | Report error: "Ambiguous target — both plugin.json and marketplace.json found. Please specify which file to edit." |
| Has neither | Report error: "No plugin.json or marketplace.json found in `.claude-plugin/` at `<path>`." |

### 3. Read and Parse Current Version

Read the version from the appropriate file:
- Plugin: top-level `"version"` field in `plugin.json`
- Marketplace: `metadata.version` field in `marketplace.json`

Parse into `major.minor.patch` components. If the version is missing, not a string, or not valid semver, report a clear error and stop:
```
Error: version field is "<value>" — expected semver format (e.g., "1.2.3")
```

### 4. Calculate New Version

| Bump Type | Rule | Example |
|---|---|---|
| `patch` | Increment patch, keep major.minor | 1.2.3 → 1.2.4 |
| `minor` | Increment minor, reset patch to 0 | 1.2.3 → 1.3.0 |
| `major` | Increment major, reset minor and patch to 0 | 1.2.3 → 2.0.0 |

### 5. Write Updated Version

Update the version field in the file:
- Preserve all other fields and their formatting
- Use 2-space indentation
- Validate the resulting JSON parses correctly after writing

### 6. Update CHANGELOG (plugin only)

If bumping a plugin and a `CHANGELOG.md` file exists in the plugin root directory:

Prepend the following block at the top of the file (after any existing title line, or at the very top if no title):

```markdown
## [<new-version>] - <YYYY-MM-DD>

### Changed

- (add your changes here)

```

Do not modify any existing changelog entries.

If no `CHANGELOG.md` exists, skip this step silently.

### 7. Report

Output:
- `<old-version>` → `<new-version>`
- Which file was updated (and its path)
- Whether CHANGELOG.md was updated
- Reminder: "Commit this version bump before publishing."

**If a plugin was bumped**, also suggest:
```
If this plugin is listed in a marketplace, run `/mp-admin:marketplace-sync` to check for version mismatches.
```

**If a marketplace was bumped**, note:
```
Marketplace catalog version updated. Run `/mp-admin:marketplace-publish` to push changes.
```

## Notes

- Version bumps are purely local file edits — nothing is committed or pushed automatically
- Marketplace `metadata.version` tracks the catalog schema version, not the version of any individual plugin
- After bumping a plugin version, users who have the plugin installed will receive the update on next `/plugin marketplace update`
