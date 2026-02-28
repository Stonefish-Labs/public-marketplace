---
name: map-design-consultation
description: >
  Creative consultation for Doom map design. Triggers when the user wants to brainstorm,
  plan, or discuss map ideas before generating IR — use for questions like "help me design
  a doom map", "I want to make a hell-themed level", "what should my map flow look like",
  "plan a tech base map", or "brainstorm encounter ideas". Use even if the user has only
  a vague idea — this skill helps them crystallize their vision into a concrete design.
  Do NOT use when the user already has a complete design ready for IR generation.
---

# Doom Map Design Consultation

Guide users through the creative process of designing a Doom map. You're a collaborative
consultant, not a directive author — help them discover what they want.

## Why This Skill Exists

Design decisions made before generation save iteration cycles. A 5-minute consultation
prevents generating 3 maps that don't match the user's vision. This skill focuses on
high-level creative direction; the actual IR generation happens in `map-generation`.

## Consultation Process

### 1. Establish the Vision

Ask about:
- **Feeling**: What emotion should the map evoke? (tense, empowering, overwhelming)
- **Reference**: Any Doom maps or games they loved? What worked?
- **Audience**: Who's playing? (casual, speedrunners, UV-or-die)

### 2. Theme & Setting

Common themes:

| Theme | Visual Language | Best For |
|-------|-----------------|----------|
| Tech base | Computers, lights, metal | Introduction maps |
| Hell | Fire, flesh, blood | Climactic encounters |
| Outdoor | Sky, rocks, water | Exploratory maps |
| Hybrid | Tech corrupted by hell | Progression storytelling |

### 3. Room Planning

Recommend from available templates:

**Rectangles**: `small_room`, `medium_room`, `large_room`, `arena`
**L-shaped**: `small_l`, `medium_l`, `large_l`
**Round**: `small_octagon`, `medium_octagon`, `large_octagon`
**Outdoor**: `small_outdoor`, `large_outdoor`

Match room size to encounter intensity. An arena with 3 imps feels empty; a small_room
with a cyberdemon is impossible.

### 4. Encounter Pacing

| Phase | Monsters | Player State |
|-------|----------|--------------|
| Opening | Zombiemen, imps | Pistol/shotgun, learning the space |
| Building | Demons, cacodemons, shotgun guys | Shotgun/chaingun, confident |
| Climax | Hell knights, revenants, barons | Full arsenal, desperate |

### 5. Item Economy

- **Weapons before fights** — enable the player, don't punish them
- **Health before/after hard encounters** — telegraph difficulty
- **Secrets for power items** — reward exploration, don't gate progression

## Output

After consultation, summarize as a design document:

```
Map: [Title]
Theme: [One-line description]
Difficulty: [Casual/Normal/UV/Challenge]

Rooms:
- [room_id]: [template] - [purpose, things, notes]
- ...

Flow: [Linear/Hub/Exploratory]
Keys: [None/Blue/Red/Yellow and where]
Signature moment: [The memorable encounter]
```

This design document becomes input for the `map-generation` skill.

## Next Steps

After consultation, hand off to:
1. **map-generation** skill — convert design to IR JSON
2. **map-qa-validation** skill — quick validation check
3. **map-qa-reviewer** agent — thorough review (if needed)
