---
name: project-retrospective
description: Conduct a retrospective interview for a completed or cancelled project and generate a RETRO.md document. Use when archiving a project, when the user asks to do a retrospective, or when referencing an archived project that lacks a RETRO.md.
---

# Project Retrospective

Conducts a structured interview to produce a `RETRO.md` for a project entering (or already in) `Archive/`. The format spec lives in `../_shared/FORMAT.md` (relative to this skill) -- read the `RETRO.md Format` section for the canonical template.

## Prerequisites

Before starting, read these files:

1. **PROJECT.md** (from the target project folder) -- Pull the title, project_id, status, goal, milestones, and work log. This is your raw material for asking informed questions.
2. **../_shared/FORMAT.md** (relative to this skill) -- Read the `RETRO.md Format` section for the current template and field reference.
3. **../_shared/AGENT_GUIDE.md** (relative to this skill) -- Read the `Retrospectives` subsection for behavioral rules.

If the project status is not `completed` or `cancelled`, stop and confirm with the user before proceeding.

## Interview Flow

Walk through each section **one at a time**. Don't batch all questions into a single prompt. Let the user talk -- your job is to listen, ask follow-ups, and synthesize.

Use the project's work log and milestones to ask specific, grounded questions rather than generic ones.

### Step 1: Summary

Ask the user to walk you through what happened with this project. Prompt ideas (adapt based on PROJECT.md):
- "This started as [goal]. Walk me through what actually happened -- the short version."
- "I can see from the work log that [notable event]. How did that shape the rest of the project?"
- For cancelled projects: "What led to the decision to cancel this?"

Draft a narrative paragraph from their answer. Show it to them for approval before moving on.

### Step 2: What Went Right

Ask what worked well. Reference specific milestones that landed on time. Capture as bullet points.

### Step 3: What Went Wrong

Ask what was painful. Reference milestones that slipped, obstacles, or status changes to stalled/waiting. Capture as bullet points. For cancelled projects, spend extra time here.

### Step 4: Lessons Learned

Ask for portable takeaways that generalize beyond this specific project.

### Step 5: What Would I Change?

Ask for project-specific hindsight -- scope, approach, timing, tools.

## Generating RETRO.md

After completing the interview, pipe the collected answers to the creation script:

```bash
echo '<json>' | python3 scripts/create_retro.py
```

The JSON input requires: `project_folder`, `project_id`, `outcome` (completed/cancelled), `summary`, `went_right` (list), `went_wrong` (list), `lessons` (list), `would_change` (list). Optionally include `retro_date` (defaults to today).

Then add a work log entry to PROJECT.md:

```bash
python3 ../_shared/scripts/pm.py add-worklog <PROJECT.md> \
  --entry "Retrospective completed."
```

Show the user the final RETRO.md and confirm it looks right.

## Edge Cases

- **Project already has a RETRO.md**: Don't overwrite. Ask the user if they want to append new thoughts or leave it as-is.
- **User doesn't want a full interview**: Respect it. Take what they give and format it. A sparse retro is better than no retro.
- **Project was cancelled early with little history**: Keep it short. A 3-sentence Summary and a couple bullets under What Went Wrong is fine.
