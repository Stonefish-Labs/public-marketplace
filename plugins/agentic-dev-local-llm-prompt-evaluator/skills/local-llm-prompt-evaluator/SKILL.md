---
name: local-llm-prompt-evaluator
description: Evaluates prompts, system instructions, and agentic workflows for local LLM fitness. Identifies quality and consistency issues specific to running models locally (Ollama, LM Studio, etc.) and produces a structured report with categorized findings and rewrite recommendations. Use when a user asks to review, evaluate, audit, or improve a prompt, system prompt, agent instruction, or workflow intended for a local LLM. Also triggers on: "is this prompt good for local models", "why is my local LLM giving bad results", "evaluate this for ollama/lm studio", "prompt quality check".
---

# Local LLM Prompt Evaluator

## Why This Exists

Local LLMs differ from cloud models in two critical ways: their weights are fixed (no adaptive reasoning layers), and smaller parameter counts make them literal readers of input. Cloud models silently patch vague prompts; local models surface every ambiguity as degraded output. This skill catches those gaps before you run the model.

## Invocation Workflow

### Step 1 — Gather Context

Before evaluating, ask the user these four questions. Ask them all at once in a single message; do not spread across turns.

1. **Target model/runner**: Ollama, LM Studio, or other? Approximate parameter count if known (e.g., 7B, 13B, 70B)?
2. **Content type**: System prompt, user prompt, agent instruction chain, or full multi-step workflow?
3. **Intended use case**: Coding, writing, data extraction, analysis, classification, other?
4. **Output expectations**: Is the model expected to return structured output (JSON, table, list, specific format)?

If the user already provided answers in their request, skip to Step 2.

### Step 2 — Evaluate

Analyze the submitted content against the 7 dimensions in `references/evaluation-criteria.md`. For each dimension, assign a score of 1–5 and note specific findings with line/section references where possible.

Severity classification:
- **Critical** — will likely produce wrong or degraded output on local models
- **Warning** — may cause inconsistent or unpredictable behavior
- **Info** — optimization opportunity, low risk

### Step 3 — Produce Report

Fill the template in `assets/report-template.md` with your findings. Always include:
- At least one before/after rewrite snippet for every Critical finding
- A concrete recommendation (not "be more specific" — show the specific fix)
- A score card with per-dimension scores and a weighted overall

## Quick Scoring Reference

| Dimension | Weight | Fail Signal |
|---|---|---|
| Specificity & Clarity | 1.5x | Vague verbs, undefined success criteria |
| Structure & Delimiters | 1.0x | No step numbering, inconsistent or absent delimiters |
| Output Format Spec | 1.5x | No format, length, or schema defined |
| Role & Context | 1.0x | No system prompt, no background, no persona |
| Inference Burden | 1.5x | Model expected to guess intent, fill gaps, or infer format |
| Few-Shot Examples | 1.0x | Missing examples where output shape is non-obvious |
| Token Efficiency | 0.5x | Redundant instructions, contradictions, filler preamble |

Overall = weighted sum / 9.0

## Behavior Notes

- Be blunt about Critical findings. Do not soften them.
- If the content is a multi-part workflow, evaluate each part separately, then give an aggregate verdict.
- If context window size is a concern (prompt is very long), flag it as a Warning under Token Efficiency.
- If the model target is very small (≤7B), apply stricter standards — these models tolerate almost no ambiguity.

## Additional Resources

- Detailed scoring rubric and local LLM failure examples: [references/evaluation-criteria.md](references/evaluation-criteria.md)
- Report output template: [assets/report-template.md](assets/report-template.md)
