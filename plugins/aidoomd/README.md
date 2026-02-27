# AI Doom Map Generator

Generate playable Doom WAD files from AI-friendly JSON descriptions.

## Project Structure

```
aidoomd/
├── skills/
│   ├── map-design-consultation/   # Brainstorm map ideas
│   ├── map-generation/            # IR → WAD compiler
│   │   ├── scripts/generate.py    # Generation tool
│   │   └── references/ir-schema.md
│   └── map-qa-validation/         # Validate IR JSON
│       └── scripts/validate.py
└── agents/
    └── map-qa-reviewer.md         # Thorough QA review agent
```

## Quick Start

```bash
# Generate demo map
uv run skills/map-generation/scripts/generate.py demo -o my_map.wad

# Play it
/Applications/uzdoom.app/Contents/MacOS/uzdoom -file my_map.wad -iwad DOOM.WAD +map MAP01
```

## How It Works

```
[AI/LLM] → IR JSON → [Compiler] → UDMF → [WAD Builder] → .wad file
```

1. **AI generates IR** - High-level room/connection descriptions
2. **Compiler handles geometry** - Ensures valid closed sectors
3. **WAD packager** - Creates playable .wad file

## Scripts

### Generate (map-generation)

```bash
# Demo map
uv run skills/map-generation/scripts/generate.py demo -o output.wad

# From IR JSON
uv run skills/map-generation/scripts/generate.py from-ir my_map.json -o output.wad

# Print schema
uv run skills/map-generation/scripts/generate.py schema
```

### Validate (map-qa-validation)

```bash
uv run skills/map-qa-validation/scripts/validate.py my_map.json

# Print schema
uv run skills/map-qa-validation/scripts/validate.py --schema
```

## Example IR

```json
{
  "name": "MAP01",
  "title": "Tech Incursion",
  "rooms": [
    {
      "id": "start",
      "template": "medium_room",
      "things": [
        {"type": "player_start", "count": 1},
        {"type": "shotgun", "count": 1}
      ]
    },
    {
      "id": "arena",
      "template": "large_octagon",
      "things": [
        {"type": "imp", "count": 5},
        {"type": "stimpack", "count": 2}
      ]
    }
  ],
  "connections": [
    {"from_room": "start", "to_room": "arena", "width": 64}
  ]
}
```

## Room Templates

- `small_room`, `medium_room`, `large_room`, `arena` - Rectangles
- `small_l`, `medium_l`, `large_l` - L-shaped
- `small_octagon`, `medium_octagon`, `large_octagon` - Rounder
- `small_outdoor`, `large_outdoor` - Open sky

## Agent Skills

| Skill | Purpose |
|-------|---------|
| **map-design-consultation** | Brainstorm themes, difficulty, flow |
| **map-generation** | Convert designs to valid IR JSON |
| **map-qa-validation** | Quick validation checks |

## Agent

| Agent | Purpose |
|-------|---------|
| **map-qa-reviewer** | Thorough scored review with design feedback |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package runner
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## TODO

- [ ] GZDoom extended thing types
- [ ] Custom texture themes/presets
- [ ] Door mechanics
- [ ] Lifts and stairs
- [ ] Secret sector tagging
