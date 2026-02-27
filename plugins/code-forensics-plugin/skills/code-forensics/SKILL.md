---
name: code-forensics
description: Run end-to-end codebase reconnaissance for unfamiliar repositories, with a security-first workflow that maps evidence-backed findings to OWASP categories, highlights high-risk hotspots in authentication, validation, data handling, and dependencies, and returns a structured report suitable for engineering triage, security review, and follow-on remediation planning.
---

# Code Forensics

Use this skill for deep codebase reconnaissance with security posture analysis.

## Quick Start

1. Confirm workspace path and analysis focus.
2. Use `references/forensics-workflow.md`.
3. Produce the report template from `references/forensics-report-template.md`.
4. Include explicit assumptions and unresolved questions.

## Output Contract

Return:

- `project_overview`
- `risk_findings[]`
- `owasp_mapping[]`
- `unknowns[]`

## When To Use

- User asks for reconnaissance of an unfamiliar codebase.
- Security risk hotspots or OWASP mapping are requested.

## When Not To Use

- User only wants a narrow bug fix in one file.
- Security review depth is not required.

## Subagent Delegation

Delegate to `code-forensics-analyst` for isolated, reproducible handoff artifacts.

Subagent contract: `agents/code-forensics-analyst.md`.
