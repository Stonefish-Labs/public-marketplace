---
name: research-operations
description: Run comprehensive research workflows with source-quality controls and structured synthesis. Use when users need deep topic investigation, evidence tables, and forward-looking analysis.
---

# Research Operations

Use this skill for broad-to-deep research work that requires consistent structure, source quality checks, and synthesis.

## Quick Start

1. Confirm topic, scope boundaries, constraints, and citation expectations.
2. Follow the protocol in `references/research-protocol.md`.
3. Validate source quality with `references/source-quality-checklist.md`.
4. Return findings in this format:
   - `summary`
   - `key_entities`
   - `evidence_table`
   - `open_questions`

## When To Use

- The user asks for comprehensive research, not a quick lookup.
- Multiple perspectives and counterarguments are required.
- Historical context, current state, and future trends are needed.

## When Not To Use

- The request is narrow and fact lookup is sufficient.
- The user only needs brainstorming with no evidence requirement.

## Subagent Delegation

Delegate to `deep-research-analyst` when:

- Investigation is long-running or tool-heavy.
- A strict handoff artifact is required for downstream stages.

Subagent contract: `agents/deep-research-analyst.md`.

## Examples

- "Research edge AI inference economics across hardware vendors."
- "Compare open-source policy frameworks and map consensus and disagreement."
