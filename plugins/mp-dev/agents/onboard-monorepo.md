---
description: Onboard a folder as a plugin and add it to a marketplace
argument-hint: <folder-path> <marketplace-name>
---

# onboard-monorepo

## Context

- !`ls marketplaces/ | grep -v descriptions.md`

## Files

- @marketplaces/descriptions.md

## Task

Onboard `$1` into `$2` using marketplace-compliant plugin boundaries. This is a multi-phase pipeline — run each phase sequentially and stop if any phase fails critically.

**Available marketplaces:** the-reef, tidepool, the-trench (see descriptions.md for details).

Validate that `$2` matches one of those names before proceeding. The marketplace directory is `marketplaces/$2`.

---

### Phase 0: Resolve Target Plugin Set

Determine whether `$1` is a single plugin root or a monorepo container.

1. If `$1/.claude-plugin/plugin.json` exists, treat `$1` as a **single plugin target**.
2. Otherwise, if `$1` itself contains plugin components at its own root (for example `skills/`, `agents/`, `hooks/`, `.mcp.json`, `.claude/commands/`, or `SKILL.md`), treat `$1` as a **single plugin target**.
   - If root-level component folders are present (for example both `skills/` and `agents/`), keep them together in one plugin. Do not split root components into separate plugins.
3. Otherwise, scan immediate child directories of `$1` and build `TARGETS` from children that look like standalone plugins:
   - already has `.claude-plugin/plugin.json`, OR
   - contains plugin components at its own root (for example `skills/`, `agents/`, `hooks/`, `.mcp.json`, `.claude/commands/`, or `SKILL.md`).
4. If 2+ child targets are found, treat `$1` as a **monorepo container** and onboard each child independently.
5. **Do not create a wrapper parent plugin at `$1`** when onboarding multiple child targets.
6. If no valid target is found, stop and report what paths were checked.

---

### Phase 1: Package Each Target Plugin

For each target plugin directory in `TARGETS`, use the **new-plugin** skill to package that target in place.

- Use **Monolithic Pattern** only for that target directory (plugin is created in-place at the target root).
- If `target/.claude-plugin/plugin.json` already exists, skip packaging for that target and move to Phase 2.
- Scan each target's contents to auto-detect ALL component types and feed them to the packager:
  - `skills/*/SKILL.md` — Skills
  - `agents/*.md` — Subagents
  - `hooks/hooks.json` — Hooks
  - MCP servers (detect if ANY of these are present):
    - `.mcp.json`
    - `mcp-servers/`
    - Runtime files at plugin root (`server.py`, `index.ts`, `index.js`, `pyproject.toml`, `requirements.txt`, `package.json`, `uv.lock`)
  - `.claude/commands/**/*.md` — Slash commands
- If there are MCP servers, default to bundling them unless the user says otherwise.

---

### Phase 2: Review & Refine All Components (Per Target)

Scan each target plugin for every component type. Review and fix each one found.

#### Skills (`skills/*/SKILL.md`)

For each skill:
1. Run the **refine-skill** skill to score it.
2. If overall score is **below 7.0** or there are **must-fix** items, apply fixes and re-score.
3. Pass at 7.0+ with no must-fix items.

#### Agents (`agents/*.md`)

For each agent file:
1. Read the **new-agent** skill's `references/best-practices.md` and `references/naming-conventions.md`.
2. Check: valid YAML frontmatter (`name`, `description`), kebab-case filename matches `name`, description is specific and under 1024 chars, body uses imperative style, no dead file references.
3. Fix any violations in-place.

#### Hooks (`hooks/hooks.json`)

If hooks exist:
1. Validate JSON structure — must be an array of hook objects with `event`, `command`, and optional `pattern` fields.
2. Verify every script referenced in `command` fields actually exists under `scripts/` and is executable.
3. Check for common issues: missing shebang lines in shell scripts, no error handling (`set -euo pipefail`).
4. Fix what you can, flag what needs manual intervention.

#### MCP Servers (`.mcp.json` + source under `mcp-servers/`)

If MCP servers exist:
1. Validate `.mcp.json` structure — each entry needs `command` and `args` at minimum.
2. Read each server's source entry point. Check for:
   - Proper tool name formatting and descriptions
   - Input validation on tool parameters
   - Error handling (not swallowing exceptions silently)
   - Dependencies listed in `requirements.txt` or `package.json`
3. Reference the **mcp-tool-design** and **mcp-response-format** skills for quality standards.
4. Fix naming, descriptions, and structural issues. Flag deep logic bugs for the user.

#### Slash Commands (`.claude/commands/**/*.md`)

If commands exist:
1. Check YAML frontmatter: `description` present, `argument-hint` if it uses `$ARGUMENTS`.
2. Verify the `## Task` section is filled in (not a scaffold placeholder).
3. Check that any `@path` file references resolve and `!`cmd`` blocks use safe, scoped commands.
4. Fix frontmatter issues and flag empty task bodies.

If no components of a given type exist, skip that section silently.

---

### Phase 3: Validate Each Target Plugin

Run the **validate-plugin** skill against each target plugin directory.

Use the deterministic validator script directly (do not skip this):

```bash
python3 .cursor/skills/validate-plugin/scripts/validate_plugin.py "<target-plugin-dir>"
```

- If validation passes cleanly for a target, proceed.
- If validation reports errors, fix them and re-validate. Repeat up to 3 times per target.
- If any target still fails after 3 attempts, stop and report remaining issues for that target.

---

### Phase 4: Add Each Validated Target to Marketplace

Run the **marketplace-add** skill for each validated target plugin in `marketplaces/$2`.

- Source is each target's local directory.
- When asked about copying vs GitHub source: copy into the marketplace's `plugins/` directory.
- Category defaults:
  - Use `agent-development` when the plugin's primary purpose is building/refining agent ecosystems (agents, skills, plugin scaffolding, composition workflows).
  - Otherwise use keyword-based category detection.
  - If still ambiguous, ask the user.
- If a beta channel exists, add to beta as well.

---

### Summary

After all phases complete, print one block per onboarded plugin:

```
Plugin:         <name>
Source:         <target-plugin-dir>
Marketplace:    $2
Components:
  Skills:       <count> (<refined count> refined)
  Agents:       <count> (<fixed count> fixed)
  Hooks:        <count> (<fixed count> fixed)
  MCP Servers:  <count> (<fixed count> fixed)
  Commands:     <count> (<fixed count> fixed)
Validation:     PASS
Status:         Added to marketplace
```
