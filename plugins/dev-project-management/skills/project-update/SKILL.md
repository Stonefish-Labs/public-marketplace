---
name: project-update
description: Log progress on a project -- add work log entries, update milestones, change status. Use when the user wants to record what they've done, mark milestones complete, or transition a project's status, or uses /project-update.
---

# Project Update

Handles status updates for active projects. The user comes to log what happened, update milestones, or change a project's status. This is the day-to-day workhorse skill.

## Prerequisites

Before starting, read:

1. **../_shared/AGENT_GUIDE.md** -- Skim the `Status Changes` and `Modifying Frontmatter` subsections for decision rules (when to ask for reasons, what needs user approval).
2. The target project's **PROJECT.md** -- current status, milestones, recent work log entries.

## Tone

Efficient, low-friction. The user is here to record progress, not have a conversation about it. Ask what's needed, capture it accurately, confirm, done.

That said, if something doesn't add up (marking a milestone done that has no prior work log entries, or jumping from on-deck to completed), ask about it.

## Update Flow

### Step 0: Identify the Project

If the user specifies a project by name or path, read its PROJECT.md.

If they don't specify, check what's in Active/. If there's only one active project, confirm: "Updating {title}?" If there are multiple, ask which one.

If the target is in Proposed/, redirect: "That's still a proposal. Did you mean to run a review on it instead?"

### Step 1: What Happened?

Ask the user what they want to log. Common scenarios:

- **Progress notes** -- "I worked on X today, got Y done."
- **Milestone update** -- "Milestone 3 is done" or "I started working on milestone 2."
- **Status change** -- "Park this for now" or "I'm blocked on Z."
- **File attachment** -- "Here's a diagram for the project" or "I wrote a helper script."
- **Combination** -- Any mix of the above.

If the user just dumps a stream of consciousness, parse it into the right update types.

### Step 2: Apply Updates

Use the shared PM CLI (`../_shared/scripts/pm.py`, paths relative to this skill) to apply all changes. The scripts handle formatting, ordering, and frontmatter updates automatically.

**Work Log entries:**

```bash
python3 ../_shared/scripts/pm.py add-worklog <PROJECT.md> \
  --date YYYY-MM-DD \
  --entry "Plain progress note" \
  --status-change "old -> new" \
  --milestone-complete 'Milestone N completed: "name"'
```

Use `--entry` (repeatable) for plain updates. Use `--status-change` and `--milestone-complete` for formatted entries. Omit `--date` to default to today.

**Milestone updates:**

```bash
python3 ../_shared/scripts/pm.py update-milestone <PROJECT.md> \
  --num N --status done
```

Valid statuses: `pending`, `in-progress`, `done`, `skipped`. Completed date auto-fills for `done`.

**Status transitions:**

- Never change status without the user's explicit approval.
- Transitions to `parked`, `stalled`, `waiting`, and `cancelled` require a reason. If the user doesn't provide one, ask.
- When status changes, move the project folder:

```bash
python3 ../_shared/scripts/pm.py move-project <project-folder> --to-status <status>
```

This moves the folder, updates `status` in frontmatter, and sets `date_completed` for terminal statuses automatically.

- Also add a work log entry for the transition using `add-worklog --status-change`.

**File attachments:**

When the user provides a file (image, document, script, etc.), determine the right subdirectory:
- `assets/` -- images, diagrams, screenshots, visual artifacts
- `resources/` -- supporting documents, reference material, specs
- `scripts/` -- automation, helper scripts

If the subdirectory doesn't exist, create it. Copy or write the file there. Add a work log entry noting what was added: `- Added {filename} to {subdirectory}/`.

### Step 3: Completion Check

After applying updates, check if the project might be done:

- Are all milestones `done` or `skipped`?
- Does the current state match the "Done When" criteria?

If yes, mention it: "All milestones are done and the Done When criteria look met. Want to mark this completed?" Don't change the status yourself -- just flag it.

### Step 4: Confirm

Show the user a summary of what was changed. Keep it brief -- if it was just a simple progress note, a one-liner confirmation is enough.

## Edge Cases

- **User wants to update a project that doesn't exist**: Say so. Don't create anything. Point them to `/new-idea`.
- **User wants to backdate a work log entry**: Allow it. Use `--date` with their specified date. Don't question unless the date is in the future.
- **User wants to edit a past work log entry**: Refuse. Work log entries are append-only. They can add a correction as a new entry.
- **User marks a project completed but Done When criteria aren't met**: Point it out. Accept their decision either way.
- **Bulk update across multiple projects**: Handle sequentially. Confirm each one.
- **Status change to on-deck from active (demotion)**: Unusual but allowed. Ask for context and log it.
