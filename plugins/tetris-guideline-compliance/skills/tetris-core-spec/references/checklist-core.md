# Core Compliance Checklist (Single-Player v1)

Use `PASS`, `FAIL`, or `UNKNOWN` per rule.

## Category A: Field Geometry and Generation

- `CORE-A01`: Matrix is 10x20 visible playfield.
- `CORE-A02`: Buffer zone of 20 rows exists above skyline.
- `CORE-A03`: All pieces generate North-facing.
- `CORE-A04`: Spawn columns/rows match guideline centering.
- `CORE-A05`: Post-generation immediate one-row drop attempt occurs if unobstructed.

## Category B: RNG / Queue / Hold / Ghost

- `CORE-B01`: 7-bag piece randomizer implemented.
- `CORE-B02`: Bag refill only after exhaustion.
- `CORE-B03`: Next queue present and consumed in order.
- `CORE-B04`: Hold enabled by default.
- `CORE-B05`: Cannot hold twice without a lock-down in between.
- `CORE-B06`: Ghost enabled by default and shows landing projection.

## Category C: Movement, Rotation, and Drops

- `CORE-C01`: Horizontal movement is one-cell discrete with collision blocking.
- `CORE-C02`: Auto-repeat has initial delay (~0.3s).
- `CORE-C03`: Horizontal auto-repeat throughput is approx. side-to-side in 0.5s.
- `CORE-C04`: Rotation supports SRS-style permissive behavior near wall/floor.
- `CORE-C05`: Hard drop locks immediately.
- `CORE-C06`: Soft drop is 20x normal fall speed.
- `CORE-C07`: Soft drop continues while held and persists across next active piece.

## Category D: Lock-Down Behavior

- `CORE-D01`: Natural/soft landing lock timer is 0.5s.
- `CORE-D02`: Default lock-down mode is Extended Placement.
- `CORE-D03`: Extended mode reset cap is 15 moves/rotations per lowest-row segment.
- `CORE-D04`: Infinite and Classic modes are behaviorally distinct if available.
- `CORE-D05`: Hard drop bypasses timer and locks immediately.

## Category E: Scoring and Leveling

- `CORE-E01`: Single/Double/Triple/Tetris values scale by level.
- `CORE-E02`: T-Spin and Mini T-Spin values scale by level.
- `CORE-E03`: Soft/hard drop points are constant multipliers by rows.
- `CORE-E04`: B2B bonus is 0.5x action total for qualifying actions.
- `CORE-E05`: B2B broken only by Single/Double/Triple line clears.
- `CORE-E06`: No-line-clear spins do not start B2B and do not break an active B2B.

## Category F: T-Spin Recognition

- `CORE-F01`: T-Spin requires rotational entry into valid T-Slot context.
- `CORE-F02`: Mini T-Spin distinguished from full T-Spin.
- `CORE-F03`: Spin classification affects scoring category correctly.

## Category G: Game Over and Variants

- `CORE-G01`: Block Out correctly detected when spawn is obstructed.
- `CORE-G02`: Lock Out correctly detected when whole piece locks above skyline.
- `CORE-G03`: Top Out rule represented (even if unreachable in pure single-player).
- `CORE-G04`: Marathon/Sprint/Ultra baseline completion conditions are present.

## Evidence Guidance

Preferred evidence per rule:
- Unit/integration tests with assertions
- Engine source locations with line references
- Runtime traces/logs for timing-sensitive behavior
- Deterministic replays for scoring chains (B2B/T-Spin)
