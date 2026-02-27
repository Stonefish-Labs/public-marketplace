# UI and Effects Compliance Checklist (Single-Player v1)

Use `PASS`, `FAIL`, or `UNKNOWN` per rule.

## Category UI-A: Core Screen Elements

- `UI-A01`: Matrix displayed as primary gameplay region.
- `UI-A02`: Active piece is clearly distinct from locked blocks.
- `UI-A03`: Next queue visible.
- `UI-A04`: Hold queue visible when enabled.
- `UI-A05`: Ghost piece is visually distinct (outline or translucent).
- `UI-A06`: Background does not interfere with gameplay readability.
- `UI-A07`: Key game info fields are present (score, level, lines/goal/time as variant requires).

## Category UI-B: Options and Defaults

- `UI-B01`: Hold can be toggled; default is ON.
- `UI-B02`: Ghost can be toggled; default is ON.
- `UI-B03`: Next queue count can be configured (platform-appropriate).
- `UI-B04`: BGM can be toggled; default is ON.
- `UI-B05`: SFX can be toggled; default is ON.
- `UI-B06`: BGM/SFX volumes are adjustable.

## Category UI-C: Notifications and Pause

- `UI-C01`: Line clear/action notifications use explicit action naming.
- `UI-C02`: Notification placement avoids obscuring high-speed play.
- `UI-C03`: Pause immediately halts gameplay.
- `UI-C04`: Pause screen prominently indicates paused state.
- `UI-C05`: Pause hides matrix + next queue + hold queue contents.
- `UI-C06`: Unpause resumes gameplay cleanly.

## Category UI-D: Audio Expectations

Minimum SFX coverage:
- `UI-D01`: rotate/move/land/lock/line-clear/game-over sounds available.

Recommended extended SFX coverage:
- `UI-D02`: distinct SFX for single/double/triple/tetris.
- `UI-D03`: SFX for spin categories and back-to-back.
- `UI-D04`: soft drop/hard drop/hold/move-fail/rotate-fail/level-up.

BGM:
- `UI-D05`: Default soundtrack includes required Russian melody arrangement as baseline requirement.
- `UI-D06`: Additional selectable tracks allowed.

## Evidence Guidance

Preferred evidence:
- UI integration tests and state snapshots
- Screen recordings of option toggles and pause flow
- Audio event mapping table from code
- Defaults verification from clean install/profile
