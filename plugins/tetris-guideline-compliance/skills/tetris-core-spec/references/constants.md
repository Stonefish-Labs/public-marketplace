# Core Constants (2009 Guideline, Single-Player v1)

Use these constants as normative defaults for compliance scoring.

## Geometry and Spawn

- `matrix_width = 10`
- `matrix_height = 20`
- `buffer_height = 20`
- `spawn_facing = NORTH`
- Spawn rows: 21st/22nd logical rows above visible matrix
- 3-wide pieces (`T, L, J, S, Z`) spawn centered over columns 4-6
- `I` spawns across columns 4-7 on row 21
- `O` spawns centered on columns 5-6

## RNG and Queue

- Generator model: shuffled 7-bag
- Each bag must contain exactly one of each piece
- Bag refills and reshuffles only when exhausted

## Timing and Movement

- Initial generation delay after lock: ~0.2s (platform-adjustable)
- Immediate post-generation drop attempt: 1 row if clear
- Auto-repeat horizontal behavior:
- Initial delay: ~0.3s
- Full traverse target: about 0.5s across matrix
- Hard drop fall-to-lock time: ~0.0001s
- Soft drop speed multiplier: `20x` normal fall speed
- Natural/soft landing lock timer: `0.5s`

## Lock-Down Modes

### Extended Placement (default)
- Lock timer starts at surface contact (0.5s)
- Move/rotate resets lock timer
- Cap: 15 move/rotate reset events at current lowest reached row
- Counter resets only if piece reaches a new lower row than previous minimum

### Infinite Placement
- Lock timer resets on valid move/rotate with no reset cap

### Classic
- Timer reset requires a decrease in y (piece falls lower)

## Hold / Ghost / Next Defaults

- Hold: enabled by default
- Hold restriction: must lock at least one piece between holds
- Ghost: enabled by default
- Next queue: present (count platform-customizable)

## Fall Speed Formula

Normal fall speed (sec/row):
- `(0.8 - ((level - 1) * 0.007))^(level - 1)`

Representative levels:
- L1: 1.0
- L5: 0.355
- L10: 0.064
- L15: 0.007

## Scoring (level-scaled unless noted)

- Single: `100 * level`
- Double: `300 * level`
- Triple: `500 * level`
- Tetris (4-line): `800 * level`
- Mini T-Spin (no clear): `100 * level`
- Mini T-Spin Single: `200 * level`
- T-Spin (no clear): `400 * level`
- T-Spin Single: `800 * level`
- T-Spin Double: `1200 * level`
- T-Spin Triple: `1600 * level`
- Back-to-Back bonus: `0.5 * action_total` for qualifying actions
- Soft drop: `1 * n` (n dropped rows)
- Hard drop: `2 * m` (m dropped rows)

## Back-to-Back (B2B)

Qualifying chain actions:
- Tetris
- T-Spin line clears
- Mini T-Spin line clears

Chain breaks on:
- Single, Double, or Triple line clear

Chain does not break on:
- Lock with no line clear
- Hold actions
- No-line-clear T-Spin / Mini T-Spin (these do not start B2B)

## Game Over

- Lock Out: entire locked piece above skyline
- Block Out: spawn position obstructed by existing block
- Top Out: blocks forced above top of 20-line buffer (typically multiplayer-driven)
