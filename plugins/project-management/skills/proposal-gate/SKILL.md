---
name: proposal-gate
description: Review proposals for readiness, promote to On-Deck, or run triage across all proposals. Use when reviewing a specific proposal, promoting one to On-Deck, triaging stale proposals, killing proposals, or using /review-proposal.
---

# Proposal Gate

Reviews proposals for readiness and manages the `Proposed/ -> On-Deck/` promotion gate. Operates in three modes: single review, triage sweep, and kill.

## Prerequisites

Before starting, read these shared reference files (relative to this skill):

1. **../_shared/FORMAT.md** -- Read the `PROPOSAL.md Format` section for the template, readiness gate definitions, and the `PROJECT.md Format` section for the promotion target.
2. **../_shared/AGENT_GUIDE.md** -- Read the `Proposals`, `Creating Projects`, and `Status Changes` subsections.

## Mode Selection

- **Single Review**: When the user targets a specific proposal (by name or path). Default mode.
- **Triage**: When invoked without a specific proposal, or when the user explicitly asks for a sweep/triage/review of all proposals. Read `references/triage-and-kill.md` for detailed procedure.
- **Kill**: When the user explicitly asks to kill/delete a proposal, or as an outcome of triage. Read `references/triage-and-kill.md` for the kill procedure.

---

## Single Review Mode

### Step 1: Read the Proposal

Read the target PROPOSAL.md. Note the current state of each readiness gate and the Readiness Assessment section.

### Step 2: Gate-by-Gate Evaluation

Walk through each of the five gates, checking the corresponding body section:

**If the gate is currently `false`:**
- Identify what's missing or weak.
- Ask the user targeted questions to fill the gap. Be specific.
- If the user provides a strong answer, update the section and flip the gate to `true`.
- If the answer is still weak, leave the gate `false` and explain why in the Readiness Assessment.

**If the gate is currently `true`:**
- Quick sanity check for contradictions (e.g., effort says Small but 6 open questions exist, or "What If I Don't" says nothing bad happens but motivation_justified is true).
- If a previously-passed gate no longer holds up, flip it back to `false` with an explanation.

### Step 3: Update the Proposal

After reviewing all gates:
- Update the readiness booleans in frontmatter.
- Rewrite the Readiness Assessment section with current gate status and rationale.
- Update `last_updated` to today.

### Step 4: Promotion Decision

**If all five gates are `true`:**

1. Tell the user all gates pass and ask if they want to promote to On-Deck.
2. If yes, prompt for the PROJECT.md fields that don't exist in the proposal:
   - `importance` (low / moderate / high) with `importance_reason`. If the user is uncertain about importance, offer the Three-Way Test as a lens: Is it good for *you*? Good for *others*? Good for *the greater good*? Projects hitting all three tend to justify high importance. Not a scoring system -- just a gut-check.
   - `urgent` (true / false) with `urgency_reason` if true
   - `group` (if applicable)
   - `working_paths` (if applicable)
3. Generate PROJECT.md by piping the collected data to the generation script:

```bash
echo '<json>' | python3 scripts/generate_project.py
```

The JSON input requires: `proposal_path`, `importance`, `importance_reason`, `urgent`, `urgency_reason` (if urgent), `group`, `working_paths`.

4. Move the folder from `Proposed/` to `On-Deck/`:

```bash
python3 ../_shared/scripts/pm.py move-project <project-folder> --to-status on-deck
```

5. Show the user the generated PROJECT.md for confirmation.

**If gates fail:**

Report what's missing directly: "3 out of 5 gates pass. Here's what's still missing: [list]. This isn't ready for On-Deck."

Do not offer to promote anyway. The gates exist for a reason.

---

## Edge Cases

- **Empty Proposed/ folder**: Say so and stop. "Nothing in Proposed/. Either you've been disciplined or you haven't had any ideas. Both are fine."
- **User wants to promote without all gates passing**: Refuse. "The gates exist because you asked for them. 3/5 isn't 5/5."
- **Proposal created manually with minimal content**: Treat it as a first review -- walk through gates from scratch.
- **User wants to kill a non-flagged proposal**: Their prerogative. Run kill mode. Don't argue against killing.
