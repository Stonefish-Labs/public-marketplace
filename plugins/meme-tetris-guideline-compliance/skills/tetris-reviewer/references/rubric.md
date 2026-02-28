# Tetris Compliance Rubric (Single-Player v1)

This rubric is used by `tetris-reviewer` for deterministic scoring.

## Input Contract

```yaml
target_path: string                # required
platform_hint: ios|unity|generic   # optional, default generic
evidence_mode: code_only|code_and_runtime
strictness: strict|balanced        # optional, default balanced
```

## Rule Record Schema

```yaml
rule_id: string
category: string
weight: number
description: string
verification_method: string
status: PASS|FAIL|UNKNOWN
evidence:
  - type: file|test|trace|note
    ref: string
notes: string
```

## Categories and Weights (sum = 100)

- `CORE_ENGINE`: 30
- `SCORING_SPINS`: 25
- `CONTROLS_LOCKDOWN`: 20
- `GAME_OVER_VARIANTS`: 10
- `UI_OPTIONS_EFFECTS`: 15

## Category Rule Weights

### CORE_ENGINE (30)
- `R-ENG-01` (6): Matrix = 10x20
- `R-ENG-02` (4): Buffer zone = 20 rows
- `R-ENG-03` (6): 7-bag generator
- `R-ENG-04` (5): Spawn orientation/location matches baseline
- `R-ENG-05` (5): Hold/next/ghost semantics (including hold-lock restriction)
- `R-ENG-06` (4): Immediate post-generation drop attempt

### SCORING_SPINS (25)
- `R-SCR-01` (6): Line clear scoring scales by level
- `R-SCR-02` (4): Drop scoring constants (soft/hard)
- `R-SCR-03` (6): T-Spin + Mini T-Spin scoring and recognition separation
- `R-SCR-04` (5): Back-to-Back qualification and break rules
- `R-SCR-05` (4): No-line-clear spin behavior in B2B lifecycle

### CONTROLS_LOCKDOWN (20)
- `R-CTL-01` (4): Left/right movement and collision behavior
- `R-CTL-02` (3): Auto-repeat delay/throughput behavior
- `R-CTL-03` (4): Rotation supports SRS-like permissive behavior
- `R-CTL-04` (5): Lock timer and lock-down modes (Extended default, 15-cap logic)
- `R-CTL-05` (4): Soft/hard drop timing behavior (20x and immediate lock)

### GAME_OVER_VARIANTS (10)
- `R-GOV-01` (4): Block Out detection
- `R-GOV-02` (3): Lock Out detection
- `R-GOV-03` (1): Top Out represented/documented
- `R-GOV-04` (2): Marathon/Sprint/Ultra baseline completion behavior

### UI_OPTIONS_EFFECTS (15)
- `R-UIE-01` (4): Required game-screen UI elements and legibility
- `R-UIE-02` (4): Options defaults (hold/ghost/bgm/sfx)
- `R-UIE-03` (3): Pause behavior hides matrix/next/hold and resumes correctly
- `R-UIE-04` (2): Action notifications are explicit and non-obstructive
- `R-UIE-05` (2): Minimum SFX/BGM baseline coverage exists

## Status Scoring

Per rule score contribution:
- `PASS`: full weight
- `FAIL`: 0
- `UNKNOWN`:
- `balanced`: 0.4 * weight
- `strict`: 0.2 * weight

Overall score:
- `sum(rule_contribution)` across all rules
- Already normalized because total weights = 100

## Verdict Thresholds

- `>= 90`: High compliance
- `75-89`: Moderate compliance
- `< 75`: Low compliance

## Finding Severity

For failed rules:

- `P1`: gameplay integrity blockers (`R-ENG-03`, `R-SCR-01`, `R-SCR-03`, `R-CTL-04`, `R-GOV-01`, `R-GOV-02`)
- `P2`: major behavior gaps
- `P3`: quality/polish gaps

Sort findings by `P1` -> `P2` -> `P3`, then by descending rule weight.

## Assumptions

- Single-player core only in v1
- Multiplayer appendix excluded
- Trademark/legal sections are informational, not hard-fail unless explicit misuse is identified
