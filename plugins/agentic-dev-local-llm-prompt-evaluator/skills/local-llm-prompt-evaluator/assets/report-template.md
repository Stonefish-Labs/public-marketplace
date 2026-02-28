# Local LLM Prompt Evaluation Report

## Context

| Field | Value |
|---|---|
| Model / Runner | <!-- e.g., Ollama / Mistral 7B --> |
| Content Type | <!-- system prompt / user prompt / agent chain / full workflow --> |
| Use Case | <!-- coding / writing / extraction / classification / other --> |
| Structured Output Expected | <!-- yes / no / format: JSON, table, list, etc. --> |
| Evaluated On | <!-- date --> |

---

## Verdict

> **[ Fit / Needs Work / Not Fit for Local LLM ]**

One-sentence summary of the overall fitness and the single most impactful issue.

---

## Findings

| Severity | Dimension | Issue | Recommendation |
|---|---|---|---|
| 🔴 Critical | | | |
| 🟡 Warning | | | |
| 🔵 Info | | | |

_Add rows as needed. Remove placeholder rows that have no findings._

---

## Rewrites

Provide a before/after rewrite for every **Critical** finding. Skip dimensions with no Critical issues.

### [Dimension Name] — Issue Title

**Before:**
```
[Paste the original problematic section here]
```

**After:**
```
[Paste the improved rewrite here]
```

**Why this works better for local LLMs:**
[One or two sentences on the specific local LLM failure mode this addresses]

---
<!-- Repeat the above block for each Critical finding -->

---

## Score Card

| Dimension | Score (1–5) | Weight | Weighted |
|---|---|---|---|
| Specificity & Clarity | | 1.5x | |
| Structure & Delimiters | | 1.0x | |
| Output Format Spec | | 1.5x | |
| Role & Context | | 1.0x | |
| Inference Burden | | 1.5x | |
| Few-Shot Examples | | 1.0x | |
| Token Efficiency | | 0.5x | |
| **Overall** | | **/9.0** | |

**Score interpretation:**
- 4.5–5.0: Fit — well-structured for local LLM use
- 3.5–4.4: Needs Work — functional but likely to produce inconsistent results
- 2.5–3.4: High Risk — significant ambiguity; local model will likely underperform
- < 2.5: Not Fit — requires substantial rewrite before local LLM use
