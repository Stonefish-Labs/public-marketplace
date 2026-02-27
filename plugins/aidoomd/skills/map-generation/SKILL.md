---
name: map-generation
description: >
  Convert map designs into valid IR JSON for the aidoomd compiler. Triggers when the
  user has a map design ready and wants to generate the intermediate representation —
  use for "generate the IR", "create the map JSON", "build the IR from this design",
  "convert my design to IR", or when handed a design document from map-design-consultation.
  Do NOT use for creative brainstorming (use map-design-consultation) or for validation
  (use map-qa-validation or map-qa-reviewer agent).
---

# Doom Map IR Generation

Convert natural language map designs into valid IR JSON that the compiler can turn into
a playable WAD file.

## Why This Skill Exists

The IR schema is strict — invalid JSON wastes compiles. This skill ensures generated IR
passes validation by encoding the schema rules and constraints directly into the generation
process. For the full schema reference, see `references/ir-schema.md`.

## Generation Workflow

### 1. Parse the Design

Extract from the design document:
- Room count and intended templates
- Thing placements per room
- Connections between rooms
- Any keys or locked doors

### 2. Assign Room IDs

Use descriptive snake_case: `start`, `arena`, `hell_hall`, `key_room`, `exit_chamber`.

### 3. Select Templates

Match described spaces to templates (see `references/ir-schema.md` for full list).

| If design says... | Use template |
|-------------------|--------------|
| "small closet/alcove" | `small_room` |
| "standard room" | `medium_room` |
| "large chamber" | `large_room` |
| "big arena/final fight" | `arena` |
| "outdoor area" | `small_outdoor` or `large_outdoor` |

### 4. Place Things

Critical rules:
- **Exactly one `player_start`** in the first room
- **Weapons before hard fights** — don't make players fight imps with a pistol
- **Health near encounters** — not in random corners
- **Monster count matches room size** — an arena with 2 imps feels wrong

### 5. Define Connections

Connect adjacent rooms. The compiler places rooms in sequence based on connection order.

```json
{"from_room": "start", "to_room": "hall", "width": 64}
```

Width range: 48-128. Wider = more open hallway.

### 6. Set Light Levels

| Level | Use Case |
|-------|----------|
| 192-255 | Bright, outdoor, safe areas |
| 144-176 | Normal indoor lighting |
| 112-136 | Dim, atmospheric |
| 80-104 | Dark, scary, hellish |

## Quick Reference

For full schema details, see `references/ir-schema.md`.

To print the schema programmatically:
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/map-generation/scripts/generate.py schema
```

**Minimal valid IR:**
```json
{
  "name": "MAP01",
  "title": "Map Title",
  "rooms": [
    {"id": "start", "template": "medium_room", "things": [{"type": "player_start", "count": 1}]}
  ],
  "connections": []
}
```

## Validation

After generating IR, validate with the QA skill's script:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/map-qa-validation/scripts/validate.py output.json
```

## Generation

To compile IR to WAD:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/map-generation/scripts/generate.py from-ir output.json -o map.wad
```

## Handoff

Valid IR → use `map-qa-validation` skill for quick checks, or delegate to the
`map-qa-reviewer` agent for thorough review before compilation.
