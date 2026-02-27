# Agent Guide

Reference document for any agent, skill, or slash command that operates on this project management system. Read FORMAT.md for the format specification itself -- this document covers *how to behave* when working with it.

---

## Design Principles

These drove every format decision. Internalize them.

**Low friction to create.** A valid project can be ~15 lines. Only a handful of required fields. Don't add barriers to capturing ideas. If someone has an idea, they should be able to create a `proposed` project in under a minute.

**Agent-parseable.** YAML frontmatter, consistent heading structure, table format for milestones. You should be able to read and modify any project programmatically without fragile regex hacks.

**Human-scannable.** Open the file, glance at frontmatter for status, read Goal to remember what this is, check Milestones for progress, scroll to Work Log for recent activity. The file tells its own story.

**Status changes are events, not just state.** Every transition is logged with a timestamp and reason in the Work Log. This gives velocity tracking and decision history for free. The frontmatter says *where it is*. The work log says *how it got there*.

**The folder is the dashboard.** Open `Active/` to see what's being worked on. Open `Paused/` to see what's stuck. No app, no database, no sync issues. Just files.

**The human is the decision-maker.** Agents propose, validate, and maintain. They do not unilaterally change status, importance, or urgency without the user's input. When in doubt, ask.

---

## Behavioral Rules

### Creating Projects

New ideas start as **proposals**, not projects. A PROJECT.md is only generated when a proposal clears all readiness gates and is promoted to On-Deck.

- Generate `project_id` in kebab-case from the title (or let the user specify one).
- Create the project folder in `Proposed/` with a PROPOSAL.md (see FORMAT.md for the spec).
- Only create subdirectories (`assets/`, `resources/`, `scripts/`) when there is content to put in them. Do not create empty placeholder directories.
- Set `review_by` to 30 days from `date_proposed`.
- Walk through the PROPOSAL.md body sections with the user. Do not pre-fill answers from assumptions.
- After the interview, honestly assess each readiness gate and fill in the Readiness Assessment section.

When a proposal is promoted to On-Deck (all gates pass, user approves):

- Generate a PROJECT.md from the proposal content (Problem -> Goal, Desired Outcome -> Done When, etc.).
- Prompt the user for `importance`, `importance_reason`, `urgent`, and `urgency_reason` -- don't guess these.
- Move the folder from `Proposed/` to `On-Deck/`. PROPOSAL.md stays alongside PROJECT.md.
- Add an initial Work Log entry: `- *Status: proposed -> on-deck*` with context.

### Adding Files to a Project

When the user provides a file to attach to a project (a diagram, a document, a script, etc.), place it in the appropriate subdirectory:

- **assets/** -- images, diagrams, screenshots, visual artifacts
- **resources/** -- supporting documents, reference material, PDFs, specs
- **scripts/** -- automation, helper scripts, agent tooling

If the target subdirectory doesn't exist yet, create it. This is the only time these directories should be created -- on demand, when there's something to put in them.

When adding a file, mention it in a Work Log entry so there's a record: `- Added {filename} to {subdirectory}/`.

### Modifying Frontmatter

- Always update `last_updated` to the current date when making any meaningful change.
- Never change `date_created`.
- Set `date_completed` when (and only when) status becomes `completed` or `cancelled`.
- When the user provides importance or urgency ratings without a reason, prompt for the `_reason` field. Don't let it slide -- the reason is the whole point.

### Proposals

- **Default to skepticism.** When evaluating a proposal, your job is to poke holes, not validate. The user's ADHD brain will generate plenty of ideas -- your job is to make sure only the ones with real substance get through.
- **Readiness gates are honest assessments.** Do not mark a gate as `true` to be encouraging. If the user's answer is vague, the gate stays `false` with a note in the Readiness Assessment explaining what's missing. A weak "Why This, Why Now?" that boils down to "it would be cool" does not pass `motivation_justified`.
- **Never promote a proposal without explicit user approval.** Even if all five gates are `true`, the user decides when something moves to On-Deck.
- **`review_by` is a hard deadline.** Defaults to 30 days from `date_proposed`. When it passes, the proposal is flagged during triage. The user must either invest (extend 30 more days and commit to filling gaps) or kill it. There is no "maybe later."
- **Killing means deleting.** When a proposal is killed -- during triage or by explicit request -- delete the entire folder from `Proposed/`. No archive. No record. Gone. Confirm once with the user before deleting.
- **Triage forces binary decisions.** When reviewing all proposals, present a summary (title, age, gates passed, review status) and force a keep-or-kill on every flagged item. Do not let stale proposals linger.

### Status Changes

- Every status change gets a Work Log entry: `- *Status: {old} -> {new}*` followed by context.
- Transitions to `parked`, `stalled`, `waiting`, and `cancelled` **require** a reason in the log entry. If the user doesn't provide one, ask for it.
- The `proposed -> on-deck` transition is a gate:
  - All five readiness criteria in PROPOSAL.md must be `true`.
  - The user must explicitly approve the promotion.
  - A PROJECT.md is generated from the proposal at promotion time.
  - The work log entry goes in the new PROJECT.md, not in PROPOSAL.md.
- When changing status, move the project folder to the correct top-level status folder:
  - `proposed` -> `Proposed/`
  - `on-deck` -> `On-Deck/`
  - `active` -> `Active/`
  - `waiting`, `stalled`, `parked` -> `Paused/`
  - `completed`, `cancelled` -> `Archive/`
- Update the `status` field in frontmatter to match.
- Never change a project's status without the user's explicit approval.

### Work Log

- Entries are append-only. Prepend new entries to maintain reverse chronological order.
- Never edit or delete past entries.
- Use the H3 date header format: `### YYYY-MM-DD`.
- If an entry already exists for today's date, add bullets under the existing header rather than creating a duplicate.
- Status change entries use italicized arrow notation: `- *Status: old -> new*`
- Milestone completion entries: `- *Milestone N completed: "name"*`
- Plain updates are regular bullet points with no special formatting.

### Milestones

- Keep the table sorted by the `#` column (ascending). Don't reorder.
- When adding milestones, assign the next sequential number.
- When a milestone is completed, set its `Status` to `done`, fill in the `Completed` date, and add a Work Log entry.
- `Due` dates can be blank if uncommitted. Don't invent deadlines.
- Valid statuses: `pending`, `in-progress`, `done`, `skipped`.

### Open Questions

- When the user raises a question, add it as a bullet under Open Questions.
- When a question is answered, add a dated sub-bullet: `  - **YYYY-MM-DD**: Answer text.`
- Don't delete answered questions -- the history is valuable.

### Completed / Cancelled Projects

- Never modify a completed or cancelled project's substance without explicit user request.
- Typo fixes and adding retrospective notes to the Work Log are fine.
- Don't move them out of `Archive/`.
- When archiving a project, offer to conduct a retrospective if one doesn't already exist. Don't force it -- just ask.

### Retrospectives

- A retrospective produces a `RETRO.md` in the project folder. See FORMAT.md for the full spec.
- The user drives the content. The agent's job is to ask good questions, not fill in answers from assumptions. Read the PROJECT.md first (goal, milestones, work log) so you can ask informed, specific follow-up questions.
- Walk through each section one at a time: Summary, What Went Right, What Went Wrong, Lessons Learned, What Would I Change. Don't rush through them in a single prompt.
- For cancelled projects, lean harder on Summary and What Went Wrong. Understanding why something got killed is the whole point.
- After generating RETRO.md, add a Work Log entry to PROJECT.md: `- *Retrospective completed.*`
- RETRO.md is append-only after creation. Don't edit or rewrite a retro -- if the user has new thoughts later, they can add to it, but the original reflection stands.

### Groups

- Groups live in `Groups/{group-id}/` with a `GROUP.md`.
- Keep the Projects list in GROUP.md current when child projects are created, moved, or cancelled.
- Groups have no status. They're organizational containers.

---

## Validation Checklist

### Proposals (PROPOSAL.md in Proposed/)

- [ ] `project_id` is kebab-case and matches the folder name
- [ ] `date_proposed` is a valid YYYY-MM-DD date
- [ ] `last_updated` >= `date_proposed`
- [ ] `review_by` is a valid YYYY-MM-DD date
- [ ] `readiness` contains all five boolean gates
- [ ] All required body sections exist: Problem, Desired Outcome, Why This Why Now, What If I Don't, Rough Effort, Open Questions, Readiness Assessment
- [ ] Readiness Assessment reflects the current state of the gates
- [ ] Folder is in `Proposed/`

### Projects (PROJECT.md in On-Deck/ and beyond)

- [ ] `project_id` is kebab-case and matches the folder name
- [ ] `status` is one of: on-deck, active, waiting, stalled, parked, completed, cancelled
- [ ] `importance` is one of: low, moderate, high
- [ ] `urgent` is a boolean (true/false)
- [ ] `importance_reason` is non-empty
- [ ] `urgency_reason` is non-empty when `urgent` is true
- [ ] `date_created` is a valid YYYY-MM-DD date
- [ ] `last_updated` >= `date_created`
- [ ] `date_completed` is set if and only if status is completed or cancelled
- [ ] Project folder is in the correct top-level status folder for its status
- [ ] All required sections exist: Goal, Done When, Milestones, Work Log
- [ ] Work Log has at least one entry
- [ ] Milestone table `#` column is sorted ascending
- [ ] If `group` is set, the referenced group exists in `Groups/`
- [ ] PROPOSAL.md exists alongside PROJECT.md (carried forward from Proposed/)

---

## Conventions

### Dates

All dates use `YYYY-MM-DD` format. No exceptions.

### IDs

All IDs (project_id, group_id) use kebab-case and must match their folder name exactly.

### File Encoding

All files are UTF-8 markdown.

### Asking vs Assuming

When the user's intent is ambiguous -- especially around status changes, importance ratings, or cancellation -- ask. A bad automated decision costs more than a quick clarifying question.
