---
name: technical-editor
description: Perform rigorous technical editorial review for specs, docs, and summaries by identifying exact problematic text, classifying issues with a consistent taxonomy, and producing high-signal recommendations that improve clarity, precision, and information density without rewriting whole documents prematurely.
---

# Technical Editor

Use this skill when text quality needs rigorous critique before rewrite or publication.

## Quick Start

1. Request target text and audience mode.
2. Apply the issue taxonomy in `references/issue-taxonomy.md`.
3. Return structured issues with:
   - exact quote
   - issue category
   - what is wrong
   - recommendation (`REMOVE`, `REWORD`, `KEEP`)
   - suggested revision for `REWORD`

## When To Use

- Documentation, specs, summaries, or reports require precision upgrades.
- User asks for critical editorial feedback instead of simple rewrite.

## When Not To Use

- User only asks for tone polishing.
- User requires creative writing rather than technical clarity.

## Subagent Delegation

Delegate to `technical-editor-reviewer` when technical review is one stage in a larger pipeline.

Subagent contract: `agents/technical-editor-reviewer.md`.
