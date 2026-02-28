---
name: tetris-core-spec
description: Distills the 2009 Tetris Design Guideline into implementation-ready single-player core gameplay rules (engine, generation, controls, lock-down, scoring, T-spin, game-over, and core variants). Use when building or correcting Tetris core mechanics for compliance.
---

# Tetris Core Spec (Single-Player v1)

Use this skill to translate the 2009 guideline into concrete implementation checks and decisions for core gameplay.

## Scope

Included:
- Matrix and buffer-zone model
- Tetrimino generation/orientation and bag RNG
- Core controls and manipulation rules
- Lock-down rules (Extended default, Infinite, Classic)
- Fall/drop timings and level interaction
- Scoring and Back-to-Back rules
- T-Spin and Mini T-Spin recognition baseline
- Core game-over conditions
- Marathon/Sprint/Ultra baseline behavior

Excluded in v1:
- Multiplayer line-attack and counter-attack appendix

## Workflow

1. Read [`references/constants.md`](references/constants.md) and adopt values exactly unless a platform constraint is explicit.
2. Read [`references/checklist-core.md`](references/checklist-core.md) and map each rule to an implementation unit (state machine, system, or function).
3. Implement or audit in this order:
- Engine lifecycle and generation
- Movement/rotation/drop/hold/lock-down
- Scoring and level/goal progression
- T-Spin classification and game-over handling
- Variant completion conditions
4. For each completed rule, preserve a test or trace proving behavior.

## Required Defaults (v1)

- Matrix: 10x20
- Buffer zone: 20 rows above skyline
- Default lock-down mode: Extended Placement
- Lock-down timer: 0.5s for natural/soft landing
- Hard drop lock: immediate (~0.0001s fall-to-lock)
- Soft drop speed: 20x normal fall speed
- Hold default: on, and cannot be chained without an intervening lock
- Ghost default: on
- Random generation: 7-bag

## Output Expectation

When asked to produce an implementation plan or audit summary, return:
- Rules implemented/audited
- Rules pending
- Rule IDs with evidence locations (file/test)
- Explicit callout of any intentional deviations
