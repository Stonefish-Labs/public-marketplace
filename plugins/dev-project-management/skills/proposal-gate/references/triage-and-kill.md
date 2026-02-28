# Triage & Kill Reference

Detailed procedures for triage sweeps and killing proposals. Read this when operating in Triage or Kill mode.

## Triage Mode

### Step 1: Scan All Proposals

Run the triage scan script to get structured data:

```bash
python3 scripts/triage_scan.py [workspace_root]
```

### Step 2: Present the Summary

Show the user a table from the scan output:

```
| Proposal | Age | Gates | Review By | Status |
|----------|-----|-------|-----------|--------|
| garage-workshop-buildout | 34 days | 3/5 | 2026-03-17 (OVERDUE) | Flagged |
| learn-rust | 12 days | 0/5 | 2026-04-01 | OK |
```

Flag proposals that are:
- Past their `review_by` date
- Over 30 days old with zero gate progress (0/5)

### Step 3: Force Decisions on Flagged Proposals

For each flagged proposal, present a binary choice:

**Invest** -- The user commits to filling in the missing gates. `review_by` is extended by 30 days. This is not a free pass -- if the next review comes and there's still no progress, it gets flagged again.

**Kill** -- The folder is deleted. See Kill Mode below.

There is no "maybe later" option. That's how proposals rot.

### Step 4: Quick Check on Non-Flagged Proposals

For proposals that aren't flagged, briefly note their status. If any are close to their review date with low gate counts, mention it as a heads-up.

---

## Kill Mode

When a proposal is killed (during triage, by explicit user request, or as a recommendation):

1. State clearly what will happen: "This will permanently delete the `{project-id}` folder and everything in it. There is no archive, no undo."
2. Ask for confirmation once. Accept "yes," "do it," "kill it," or similar affirmatives.
3. On confirmation, delete the entire project folder from `Proposed/`.
4. Confirm deletion: "Gone. If the idea had legs, it'll come back on its own."

If the user hesitates or asks to keep it, leave it in `Proposed/` and move on. But don't let hesitation become a habit. If they hesitate on the same proposal twice across triages, point that out: "You hesitated on this last time too. Either invest or kill it."
