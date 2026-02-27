---
name: tetris-ui-effects-spec
description: Specifies single-player Tetris UI/options/effects compliance from the 2009 guideline: interface elements, defaults, notifications, pause behavior, audio requirements, and non-interference rules.
---

# Tetris UI/Effects Spec (Single-Player v1)

Use this skill for interface and polish compliance, separate from core engine logic.

## Scope

Included:
- Required game-screen interface regions
- Player-facing options and default states
- Action notifications and pause behavior
- Minimum sound effects coverage
- BGM baseline requirements
- Background non-interference constraints

Excluded in v1:
- Multiplayer layout requirements beyond single-player relevance

## Workflow

1. Read [`references/checklist-ui.md`](references/checklist-ui.md).
2. Map each UI rule to concrete UI components and settings.
3. Validate defaults on first launch/new profile.
4. Verify visibility/readability under typical gameplay pace.
5. Capture screenshots or UI test artifacts for compliance evidence.

## Critical UI Defaults

- Hold option default: on
- Ghost option default: on
- BGM default: on
- SFX default: on
- Pause must hide matrix, next queue, and hold queue contents

## Compliance Priority

1. Gameplay legibility (matrix/queue/readability)
2. Behavioral correctness of options and pause semantics
3. Audio/notification parity with guideline
4. Cosmetic polish
