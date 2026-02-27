# Review Template

Use this template when producing a composition review. Fill in every section. If a section doesn't apply, say so explicitly rather than omitting it.

---

```markdown
# Composition Review: [Project Name]

## Project Summary

[One paragraph describing what this project does, who it's for, and its current form.]

## Component Inventory

| # | Component | Current Form | Description |
|---|-----------|-------------|-------------|
| 1 | [name/path] | [MCP server / skill / hook / script / programmatic code / reference material / CLI tool / library / other] | [Brief description of what it does] |
| 2 | ... | ... | ... |

## Recommendations

For each component where the current form differs from the recommended form, or where the current form is correct but worth confirming:

### [Component Name]

- **Currently:** [what it is now]
- **Should be:** [what it should be -- or "Correct as-is" if no change needed]
- **Rationale:** [why, citing the specific design principle and heuristic that applies]
- **Key characteristics:** [the profiling answers that drove this recommendation -- e.g., "stateless, single consumer, portable, agent needs to improvise"]
- **Migration effort:** Low / Medium / High
- **Priority:** Critical / High / Medium / Low / None (if correct as-is)
- **Migration notes:** [any specific guidance on how to make the change, or "N/A" if correct as-is]

[Repeat for each component]

## Anti-Patterns Identified

[List any anti-patterns found, with specifics. For each:]

### [Anti-Pattern Name]

- **Where:** [which component or project-wide]
- **What:** [what's happening]
- **Why it matters:** [the consequence, citing the design philosophy]
- **Fix:** [what to do about it]

[If no anti-patterns found, state: "No anti-patterns identified."]

## Architecture Notes

[Cross-cutting observations about the project as a whole:]

- **Spectrum position:** [Where does this project sit on the programmatic <-> autonomous spectrum? Is that the right position?]
- **Composability:** [Are components orchestration-agnostic? Could they be reused in different contexts?]
- **Knowledge architecture:** [If reference material exists, is the retrieval strategy appropriate for the corpus size and consumer count?]
- **Output quality:** [If the project produces artifacts, are the right layers of output determinism in place?]
- **Overall assessment:** [One sentence -- is this project well-composed, needs minor adjustments, or needs significant retooling?]
```

---

## Usage Notes

- Every recommendation must cite a design principle. "This should be X" without "because Y" is incomplete.
- "Correct as-is" is a valid and valuable recommendation. Don't force changes where none are needed.
- Migration effort should account for the actual work, not just the conceptual change. Rewriting an MCP server as a skill-bundled script is low effort. Decomposing a monolithic agent into staged handoffs with handoff contracts is high effort.
- Priority should reflect impact. A mis-categorized hook-that-should-be-a-script is low priority. An autonomous workflow with no termination spec is critical.
- Architecture notes should address the project holistically, not just repeat per-component findings.
