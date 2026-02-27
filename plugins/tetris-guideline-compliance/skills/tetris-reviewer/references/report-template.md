# Compliance Report Template

Use this exact structure for deterministic outputs.

```yaml
summary:
  target_path: string
  platform_hint: ios|unity|generic
  evidence_mode: code_only|code_and_runtime
  strictness: strict|balanced
  overall_score: number
  verdict: High compliance|Moderate compliance|Low compliance
  scope: single-player-core-v1

category_scores:
  - category: CORE_ENGINE
    score: number
    max: 30
  - category: SCORING_SPINS
    score: number
    max: 25
  - category: CONTROLS_LOCKDOWN
    score: number
    max: 20
  - category: GAME_OVER_VARIANTS
    score: number
    max: 10
  - category: UI_OPTIONS_EFFECTS
    score: number
    max: 15

failed_rules:
  - rule_id: string
    severity: P1|P2|P3
    why: string
    evidence:
      - type: file|test|trace|note
        ref: string

unknown_rules:
  - rule_id: string
    why_unknown: string
    missing_evidence: string

recommendations:
  - priority: P1|P2|P3
    action: string
    maps_to_rules:
      - string

appendix:
  rules:
    - rule_id: string
      category: string
      weight: number
      status: PASS|FAIL|UNKNOWN
      score_contribution: number
      description: string
      verification_method: string
      evidence:
        - type: file|test|trace|note
          ref: string
      notes: string
```

## Rendering Notes

- Always include all rules in `appendix.rules`.
- Keep evidence references concrete (absolute or repo-relative paths + line when possible).
- If no runtime evidence was collected under `code_only`, explicitly state that in `summary` notes.
- If strictness defaults were applied, mention defaults in `summary`.
