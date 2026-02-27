---
name: tetris-reviewer
description: Reviews a Tetris implementation against the distilled 2009 single-player core guideline and outputs deterministic weighted compliance results with evidence, including PASS/FAIL/UNKNOWN per rule and overall verdict.
---

# Tetris Compliance Reviewer

Use this skill to audit an existing Tetris project and score compliance against the staged single-player v1 specification.

## Inputs

Follow this input contract exactly:

- `target_path` (required): repository or project path to audit
- `platform_hint` (optional): `ios | unity | generic`
- `evidence_mode`: `code_only | code_and_runtime`
- `strictness`: `strict | balanced` (default `balanced`)

If any optional field is missing, apply defaults and state them in the report.

## Required Output Behavior

Produce:
- Per-rule status: `PASS`, `FAIL`, or `UNKNOWN`
- Weighted category scores
- Overall score from 0-100
- Severity-ranked findings
- Concrete evidence references (file path + line, behavior trace, test output)

Use the schemas in:
- [`references/rubric.md`](references/rubric.md)
- [`references/report-template.md`](references/report-template.md)

## Review Procedure

1. Load target code and identify gameplay engine, input handling, scoring, and UI modules.
2. Evaluate all rubric rules, recording evidence for each.
3. Assign status by rule:
- `PASS`: explicit implementation and behavior align with rule
- `FAIL`: contradicted behavior or missing mandatory behavior
- `UNKNOWN`: insufficient observable evidence
4. Compute weighted category and total score.
5. Generate deterministic report from template.

## Scoring and Determinism Rules

- Do not skip rules because evidence is sparse; mark `UNKNOWN`.
- Use the same weight table every run.
- Normalize score to 0-100.
- Under `strict`, downgrade ambiguous partial matches to `UNKNOWN` or `FAIL`.
- Under `balanced`, allow partial implementation to pass only when behavior is clearly compliant.

## Severity Ranking

Rank failed findings by impact:
1. Core gameplay integrity (RNG, lock-down, scoring, game over)
2. Player control fidelity (movement/rotation/drop timing)
3. UI/options correctness
4. Audio/polish requirements

## Scope Limits (v1)

- Evaluate single-player core only.
- Multiplayer appendix is out of scope and should be listed as deferred if present.
- Legal/logo usage is informational unless explicit misuse is found in target assets or text.
