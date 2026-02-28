---
name: project-briefing
description: Read a project or proposal folder and produce a concise catch-up briefing. Use when the user hasn't touched a project in a while and needs to get back up to speed, or uses /project-brief. Read-only -- changes nothing.
---

# Project Briefing

Reads a project folder and produces a structured briefing so the user can get caught up quickly. This is a read-only operation -- you do not modify any files.

## Prerequisites

Before starting, read these shared reference files (relative to this skill):

1. **../_shared/FORMAT.md** -- Understand the document structures so you know where to find information.
2. **../_shared/AGENT_GUIDE.md** -- Understand the lifecycle and status meanings.

Then read the target project or proposal folder. What you read depends on where it lives:

- **Proposed/**: Read PROPOSAL.md.
- **On-Deck/ and beyond**: Read PROJECT.md. Also read PROPOSAL.md if it exists (for historical context).
- **Archive/**: Read PROJECT.md and RETRO.md if it exists.
- If the project has `working_paths` in frontmatter, note them -- the user may want you to look at those too.

## Tone

Concise, informational, no fluff. You're a briefing officer, not a storyteller. State facts, flag issues, move on. Only editorialize when something is clearly wrong (stale dates, contradictory status, overdue milestones).

## Producing the Briefing

Read `references/briefing-structure.md` for the full section-by-section template. The briefing covers: Identity, What Is This, Key Dates, Priority Context, Milestone Progress, Recent Activity, Open Questions, and Things to Watch. Skip sections that don't apply.

## Multi-Project Briefing

If the user asks for a briefing across multiple projects (or "brief me on everything"), produce a condensed version for each:

- One-line summary: `{title} ({status}) -- {goal summary} -- last touched {date}`
- Flag any that need attention
- Group by status folder (Active first, then On-Deck, Paused, Proposed)

Keep it scannable. The user can ask for a deep dive on any specific project.

## Edge Cases

- **Empty project folder or missing files**: Report what's missing. "This folder has a PROPOSAL.md but no PROJECT.md, and it's in Active/. Something's wrong."
- **User doesn't specify a project**: List what's available across all status folders and ask which one they want briefed. Or offer the multi-project briefing.
- **Archived project with no RETRO.md**: Mention it: "No retrospective on file. Want to do one?"
- **Project has working_paths**: Note them in the briefing. Don't read them proactively unless they're small.
