---
name: map-qa-validation
description: >
  Quick validation checks for Doom map IR and WAD files. Triggers when the user wants
  to verify a generated map works correctly — use for "validate this map", "check if
  this IR is valid", "test the map", "quick check on the IR", or "does this look right?".
  For thorough design review with scoring, delegate to the map-qa-reviewer agent instead.
  This skill handles mechanical validation; the agent handles quality assessment.
---

# Doom Map QA Validation

Run quick mechanical checks on generated IR and WAD files. This is a fast validation
pass, not a thorough design review — for that, use the `map-qa-reviewer` agent.

## Why This Skill Exists

Validation catches structural errors before the user wastes time loading a broken map.
This skill focuses on "does it work" — the agent handles "is it good".

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package runner
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Validation Steps

### 1. IR Schema Validation

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/map-qa-validation/scripts/validate.py <ir.json>
```

Checks:
- JSON structure matches schema
- All room IDs are unique
- All connections reference valid rooms
- Thing types are recognized
- Exactly one player_start exists

**If this fails**: Fix the IR before proceeding. The error messages are specific.

### 2. WAD Generation Test

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/map-generation/scripts/generate.py from-ir <ir.json> -o /tmp/test.wad
```

Watch for:
- Geometry errors (shouldn't happen with templates)
- Unknown thing type warnings
- Missing player start

**If this fails**: The IR passed schema but has semantic issues. Check thing types.

### 3. In-Engine Test (Optional)

If a source port is available:

```bash
/Applications/uzdoom.app/Contents/MacOS/uzdoom -file /tmp/test.wad -iwad DOOM.WAD +map MAP01
```

Verify:
- [ ] Player spawns at correct position
- [ ] Can walk through all doorways/hallways
- [ ] Monsters spawn and can be killed
- [ ] Items are collectible
- [ ] No visual glitches (HOM effect)

## Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Unknown thing type" | Typo in thing name | Use underscores: `shotgun_guy` |
| Player falls into void | Geometry bug | Shouldn't happen — report if it does |
| Rooms not connected | Hallway generation issue | Rooms placed in grid, connect adjacent |
| Missing textures | DOOM.WAD vs DOOM2.WAD | Cosmetic only, map still plays |

## Quick Checklist

- [ ] `uv run scripts/validate.py` passes
- [ ] `uv run ../map-generation/scripts/generate.py from-ir` produces WAD without errors
- [ ] Map loads in source port
- [ ] Player spawns correctly
- [ ] All rooms reachable
- [ ] No console errors on load

## When to Escalate

If validation passes but the map has design problems (bad pacing, unfair encounters,
confusing layout), hand off to the `map-qa-reviewer` agent for a thorough review.
