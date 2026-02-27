---
name: project-import
description: >
  Import an existing project from an external directory into the PM system.
  Scans the source, classifies it through conversation, fills missing fields,
  and creates properly formatted files in the correct lifecycle folder.
  Use when the user wants to migrate an old project, says "import", or uses /import-project.
---

# Project Import

Imports an existing project from an external directory into this PM system. The source may be messy, incomplete, or use a different format. The agent scans what's there, talks through classification and missing fields with the user, and generates compliant files in the right lifecycle folder.

## Prerequisites

Before starting, read these shared reference files (relative to this skill):

1. **../_shared/FORMAT.md** -- Full format spec for PROPOSAL.md, PROJECT.md, and RETRO.md.
2. **../_shared/AGENT_GUIDE.md** -- Behavioral rules, especially `Creating Projects`, `Status Changes`, and `Modifying Frontmatter`.

If you're unsure how to classify the incoming project, read `references/classification-guide.md` for heuristics.

## Tone

Pragmatic and efficient. This is a migration task, not a vetting exercise. The user already committed to these projects (or already killed them). Don't run the skeptical intake interview -- focus on getting the data right and filling gaps fast. Ask what you need, skip what you don't.

That said, don't fabricate data. If something is unknown, say so and capture it honestly. A work log entry that says "Imported -- original start date unknown" is better than a made-up date.

## Import Flow

### Step 0: Scan the Source

The user provides a path to the source directory. Run the scan script:

```bash
python3 scripts/scan_source.py <source-directory>
```

Present the findings to the user:
- What files exist (docs, code, assets)
- Contents of any README, markdown docs, or text files found
- Suggested `project_id` from the directory name

Give your initial read: "This looks like [description]. Here's what I found."

If the directory doesn't exist or is empty, say so and stop.

### Step 1: Classification

Based on the scan and user context, determine the target status. Ask the user directly: "What state was this in? Was it active, stalled, finished, just an idea?"

Present the options plainly:

| If it was...                        | It imports as... | Goes to...  |
|-------------------------------------|------------------|-------------|
| Just an idea, no real work done     | `proposed`       | `Proposed/` |
| Vetted/planned but not started      | `on-deck`        | `On-Deck/`  |
| Actively being worked on            | `active`         | `Active/`   |
| Blocked on something external       | `waiting`        | `Paused/`   |
| Lost momentum, user drifted away    | `stalled`        | `Paused/`   |
| Deliberately shelved, not now       | `parked`         | `Paused/`   |
| Done, met its goals                 | `completed`      | `Archive/`  |
| Killed, not doing this              | `cancelled`      | `Archive/`  |

Make a recommendation based on what you scanned, but the user decides. If the status is `waiting`, `stalled`, `parked`, or `cancelled`, get the reason -- it's required for the work log.

### Step 2: Core Fields

The required fields depend on whether we're creating a proposal or a project.

**If `proposed`:** Walk through the PROPOSAL.md fields. Pull what you can from the scanned docs. Ask for what's missing:
- `project_id` and `title`
- Problem, Desired Outcome, Why This Why Now, What If I Don't, Rough Effort
- Open Questions
- Assess readiness gates honestly based on what exists

Don't force the full skeptical interview. If the scanned content clearly answers a field, pre-fill it and confirm. If it doesn't, ask briefly and move on.

**If anything else (project):** Walk through the PROJECT.md fields:
- `project_id` and `title`
- `goal` -- derive from scanned docs or ask
- `done_when` -- derive or ask
- `importance` (low/moderate/high) and `importance_reason` -- ask, don't guess. If the user is uncertain, offer the Three-Way Test as a lens: Is it good for *you*? Good for *others* (people you care about, collaborators, users)? Good for *the greater good*? Projects that hit all three tend to justify their slot. This isn't a scoring system -- just a quick gut-check to help calibrate.
- `urgent` and `urgency_reason` -- ask
- `group` -- ask if applicable
- `working_paths` -- include the source path by default, ask about others
- `milestones` -- derive from scanned docs or ask. Can be empty for imports.
- `scope`, `obstacles`, `open_questions` -- optional, capture if available

For completed/cancelled projects, also ask for `date_completed` if the user remembers it.

Be pragmatic about what to ask vs. skip. A completed project from two years ago doesn't need a detailed urgency assessment -- set `urgent: false` with a note. An active project needs more care.

### Step 3: History

Capture what's known about the project's timeline. Ask:
- "When did this start, roughly?"
- "Any major milestones worth recording?"
- "What happened? Give me the highlights."

Build work log entries from the user's answers. Every import gets at minimum:

```
### {today}
- *Status: imported as {status}*
- Imported from {source_path}. {any context about original state}
```

If the user provides historical entries, add them with their approximate dates below the import entry (older entries go below, maintaining reverse chronological order).

For projects imported as `waiting`/`stalled`/`parked`/`cancelled`, the import work log entry must include the reason:

```
### {today}
- *Status: imported as stalled*
- Imported from /path/to/old/project. Originally stalled because {reason}.
```

### Step 4: Generate

Pipe the collected data to the import script:

```bash
echo '<json>' | python3 scripts/import_project.py
```

The JSON structure depends on mode:

**Proposal mode** (`target_status` = `proposed`):

| Field                | Type   | Required |
|----------------------|--------|----------|
| project_id           | string | yes      |
| title                | string | yes      |
| target_status        | string | yes      |
| tags                 | list   | no       |
| source_path          | string | yes      |
| problem              | string | yes      |
| desired_outcome      | string | yes      |
| why_now              | string | yes      |
| what_if_not          | string | yes      |
| effort               | string | yes      |
| open_questions       | list   | no       |
| readiness            | dict   | yes      |
| readiness_assessment | string | yes      |

**Project mode** (`target_status` = anything else):

| Field              | Type   | Required                               |
|--------------------|--------|----------------------------------------|
| project_id         | string | yes                                    |
| title              | string | yes                                    |
| target_status      | string | yes                                    |
| tags               | list   | no                                     |
| source_path        | string | yes                                    |
| goal               | string | yes                                    |
| done_when          | string | yes                                    |
| importance         | string | yes                                    |
| importance_reason  | string | yes                                    |
| urgent             | bool   | yes                                    |
| urgency_reason     | string | if urgent                              |
| group              | string | no                                     |
| working_paths      | list   | no                                     |
| milestones         | list   | no                                     |
| work_log_entries   | list   | no                                     |
| scope              | string | no                                     |
| obstacles          | string | no                                     |
| open_questions     | list   | no                                     |
| date_created       | string | no (defaults to today)                 |
| date_completed     | string | if completed/cancelled                 |
| pause_reason       | string | if waiting/stalled/parked              |
| cancel_reason      | string | if cancelled                           |

After generation, validate:

```bash
python3 ../_shared/scripts/pm.py validate <generated-file> --type <proposal|project>
```

Show the user the generated files and validation result. If validation fails, fix the issues before confirming.

### Step 5: Post-Import

**For Archive imports (completed/cancelled):** Offer to run the retrospective skill: "This is archived. Want to do a quick retro while it's fresh in your mind?"

**For all imports:** Confirm completion: "Imported `{title}` as `{status}` in `{folder}/`."

Then ask: "Want me to delete the original source directory at `{source_path}`?" If the user says yes, remove the source directory. If they decline or are unsure, leave it alone. Don't push -- just offer once.

If the project has a `group` set, update the GROUP.md projects list.
When creating or updating a group during import, do not leave `GROUP.md` as just a title + project list. Ensure it has a real **Purpose** statement that explains what ties the child projects together and what shared outcome the group is driving. If the existing Purpose is vague, replace it with concrete language from the source docs and user context.

For grouped imports, also keep **Notes** useful (shared assumptions, architecture constraints, or sequencing context), not generic filler.

## Edge Cases

- **Source directory doesn't exist**: Say so, stop. Don't create anything.
- **project_id already exists in the system**: Say so, ask if the user wants a different ID or wants to skip this import.
- **User wants to batch-import many projects**: Handle one at a time. After each, ask "Next one?" Don't try to parallelize the conversation.
- **Source has its own PROJECT.md or similar structured file**: Great -- mine it for data. Pre-fill as much as possible and confirm with the user.
- **User can't remember details about an old project**: That's fine. Capture what they know, mark unknowns honestly. A sparse import is better than no import.
- **User wants to copy assets from the source**: Ask which files and where they belong (`assets/` for images/diagrams, `resources/` for documents/specs, `scripts/` for automation). Create the target subdirectory if it doesn't exist, then copy the files in. Log what was copied in the import work log entry.
- **The imported project conflicts with an existing proposal**: Surface it. The user decides whether to merge, skip, or replace.
