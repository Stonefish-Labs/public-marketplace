# Project Management Format Specification

This document defines the format and conventions for this project management system.

## Folder Structure

```
pm-project/
  Proposed/            # ideas, not yet vetted
  On-Deck/             # vetted, ready to be scheduled
  Active/              # currently being worked on
  Paused/              # parked, stalled, or waiting (substatus in frontmatter)
  Archive/             # completed or cancelled (substatus in frontmatter)
  Groups/              # parent project grouping (no status, never "done")
    {group-id}/
      GROUP.md
      resources/
```

Five top-level folders map to broad lifecycle phases. The `status` field in frontmatter carries the granular state. Projects move between folders when their status changes.

`Paused/` holds parked, stalled, and waiting projects. `Archive/` holds completed and cancelled. The specific substatus lives in the frontmatter.

### Project Folder Layout

Each project is a folder inside its status folder. The contents depend on where the project is in its lifecycle:

**Proposed/ (pre-project):**

```
{project-id}/
  PROPOSAL.md          # the proposal file (required)
  assets/              # images, diagrams, etc. (created on demand)
  resources/           # supporting documents (created on demand)
  scripts/             # automation, agent skills (created on demand)
```

**On-Deck/ and beyond (active project):**

```
{project-id}/
  PROJECT.md           # the project file (required)
  PROPOSAL.md          # original proposal (carried forward from Proposed/)
  RETRO.md             # retrospective (optional, Archive/ only)
  assets/              # images, diagrams, etc. (created on demand)
  resources/           # supporting documents (created on demand)
  scripts/             # automation, agent skills (created on demand)
```

Subdirectories (assets/, resources/, scripts/) are only created when there is content to place in them. Do not create empty placeholder directories.

The folder name must be kebab-case and must match the `project_id` field in PROPOSAL.md or PROJECT.md.

---

## Statuses

| Status    | Folder    | Meaning                                                           |
|-----------|-----------|-------------------------------------------------------------------|
| proposed  | Proposed/ | An idea captured as PROPOSAL.md. Must clear readiness gates before promotion. |
| on-deck   | On-Deck/  | Vetted. Has enough clarity and merit to be scheduled.             |
| active    | Active/   | Currently being worked on.                                        |
| waiting   | Paused/   | Blocked on something external (a person, a shipment, a decision). |
| stalled   | Paused/   | Internal blocker -- lost momentum, hit a wall, needs intervention.|
| parked    | Paused/   | Deliberately deprioritized. Not blocked, just not now.            |
| completed | Archive/  | Met "Done When" criteria. Terminal state.                         |
| cancelled | Archive/  | Not doing this. Terminal state. Reason required in work log.      |

### Why distinguish waiting / stalled / parked?

Understanding *why* something stopped determines the intervention:

- **Stalled** -- you need to push through or get unstuck.
- **Waiting** -- you need to follow up with someone or something external.
- **Parked** -- it's fine where it is. Revisit later.

### Status Transitions

Any status can transition to `cancelled`. Otherwise the typical flow is:

```
proposed -> on-deck -> active -> completed
   |                     |
   +-> killed            +-> waiting  -> active (when unblocked)
   (deleted, no trace)   +-> stalled  -> active (when unstuck)
                         +-> parked   -> active (when reprioritized)
```

The `proposed -> on-deck` transition is a gate: all readiness criteria in PROPOSAL.md must be met, and a PROJECT.md is generated at promotion time. See the PROPOSAL.md Format section for details.

Proposals can also be **killed** -- deleted entirely with no archive. This happens during triage or by explicit user request. Killed proposals leave no trace; if the idea was real, it will resurface on its own.

Every transition must be logged in the Work Log with a date. Transitions to `parked`, `stalled`, `waiting`, and `cancelled` require a reason.

---

## PROJECT.md Format

### Frontmatter (YAML)

```yaml
---
project_id: my-project
title: "My Project"
status: active
importance: moderate
importance_reason: "Needed for X but not catastrophic if delayed"
urgent: false
urgency_reason: ""
group:
date_created: 2026-02-22
last_updated: 2026-02-22
date_completed:
tags: []
working_paths: []
---
```

#### Field Reference

| Field             | Required | Type    | Description                                                        |
|-------------------|----------|---------|--------------------------------------------------------------------|
| project_id        | yes      | string  | Kebab-case. Must match folder name.                                |
| title             | yes      | string  | Human-readable project name.                                       |
| status            | yes      | enum    | One of the 8 statuses above.                                       |
| importance        | yes      | enum    | `low`, `moderate`, or `high`.                                      |
| importance_reason | yes      | string  | One-liner explaining why this importance level.                    |
| urgent            | yes      | boolean | `true` or `false`.                                                 |
| urgency_reason    | conditional | string | Required when `urgent: true`. Why is this time-sensitive?       |
| group             | no       | string  | `group_id` of the parent group, if any.                            |
| date_created      | yes      | date    | YYYY-MM-DD. When the project was first created.                    |
| last_updated      | yes      | date    | YYYY-MM-DD. Updated on any meaningful change.                      |
| date_completed    | conditional | date  | Set when status becomes `completed` or `cancelled`.                |
| tags              | no       | list    | Freeform categorization.                                           |
| working_paths     | no       | list    | Filesystem paths related to this project.                          |

#### Importance + Urgency

These two fields replace a single "priority" value. This is an Eisenhower Matrix approach -- it forces a deliberate assessment of *why* something matters and whether it's time-sensitive, instead of everything drifting to "high priority" on gut feel.

The `_reason` fields are one-liners that give future-you (and agents) context for reassessment.

#### date_completed

Kept separate from `last_updated` because `last_updated` can change after completion (typo fix, adding a retrospective note) and because `date_completed` is useful for velocity calculations.

---

### Body Sections

#### Required Sections

These must exist in every PROJECT.md. Content can be brief.

**Goal** -- 1-3 sentences. What does this project achieve? Why does it matter?

**Done When** -- Concrete, observable completion criteria. When you hit these, you're done.

**Milestones** -- A markdown table tracking progress:

| Column    | Description                                           |
|-----------|-------------------------------------------------------|
| #         | Sequential number. Stays sorted ascending.            |
| Milestone | Name or short description.                            |
| Due       | Target date (YYYY-MM-DD). Can be blank if uncommitted.|
| Status    | `pending`, `in-progress`, `done`, or `skipped`.       |
| Completed | Date completed (YYYY-MM-DD). Blank until done.        |

**Work Log** -- Reverse chronological dated entries. Always at the bottom of the file, below a horizontal rule (`---`). See Work Log Conventions below.

#### Optional Sections

Include as needed:

- **Scope** -- What's in, what's out.
- **Obstacles** -- Known blockers, risks, hard parts. Update as they're resolved.
- **Open Questions** -- Bulleted questions with dated sub-bullet answers when resolved.
- Any freeform sections the project needs.

#### Section Order

```
[YAML frontmatter]
# {Title}
## Goal
## Scope                (optional)
## Done When
## Obstacles            (optional)
## Milestones
## Open Questions       (optional)
[any freeform sections]
---
## Work Log
```

Structured content at the top, freeform in the middle, work log at the bottom.

---

### Work Log Conventions

Each entry is an H3 date header (`### YYYY-MM-DD`) with bullet points underneath.

**Entry types:**

- **Status changes** -- Italicized with arrow notation: `- *Status: proposed -> active*`. Reason required for transitions to parked, stalled, waiting, and cancelled.
- **Milestone completions** -- `- *Milestone 2 completed: "Build prototype"*`
- **Plain updates** -- Regular bullet points. Progress notes, decisions, things learned. No special formatting.

**Rules:**

- Reverse chronological (newest at top of the log section).
- Multiple entries on the same date go under the same date header.
- Work log entries are append-only. Never edit or delete past entries.

**Example:**

```markdown
---
## Work Log

### 2026-02-24
- Got the auth module working. Switched from JWT to session tokens because of the iframe constraint.
- Refactored the database schema to support multi-tenant queries.

### 2026-02-22
- *Status: on-deck -> active*
- Kicked off initial work. Set up project folder and defined milestones.

### 2026-02-20
- *Milestone 1 completed: "Define requirements"*
- Finished requirements doc after reviewing competitor approaches.

### 2026-02-18
- *Status: proposed -> on-deck*
- Fleshed out scope and milestones. Ready to schedule.
```

---

## PROPOSAL.md Format

A proposal is the intake document for new ideas. It lives in `Proposed/{project-id}/` and must clear five readiness gates before the idea can be promoted to `On-Deck/` and receive a full PROJECT.md. The bar for promotion is deliberately high -- the proposal system exists to filter out half-baked ideas before they consume real time and energy.

When a proposal is promoted, PROPOSAL.md stays in the project folder as a historical record of why the project was started.

### Frontmatter (YAML)

```yaml
---
project_id: my-idea
title: "My Idea"
date_proposed: 2026-02-22
last_updated: 2026-02-22
review_by: 2026-03-24
tags: []
readiness:
  problem_defined: false
  outcome_clear: false
  effort_estimated: false
  motivation_justified: false
  alternatives_considered: false
---
```

#### Field Reference

| Field              | Required | Type   | Description                                                                 |
|--------------------|----------|--------|-----------------------------------------------------------------------------|
| project_id         | yes      | string | Kebab-case. Must match folder name.                                         |
| title              | yes      | string | Human-readable name for the idea.                                           |
| date_proposed      | yes      | date   | YYYY-MM-DD. When the proposal was first captured.                           |
| last_updated       | yes      | date   | YYYY-MM-DD. Updated on any meaningful change.                               |
| review_by          | yes      | date   | YYYY-MM-DD. Defaults to 30 days from `date_proposed`. Triage deadline.      |
| tags               | no       | list   | Freeform categorization.                                                    |
| readiness          | yes      | object | Five boolean gates. All must be `true` for promotion to On-Deck.            |

#### Readiness Gates

These are the criteria a proposal must satisfy before it can become a project. The gates are set by the reviewing agent based on the *quality* of the user's answers, not just whether a section has text. A vague answer does not pass a gate.

| Gate                      | What it checks                                                                                    | Why it matters                                                        |
|---------------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `problem_defined`         | Is there a specific, articulable problem? Not "it would be cool" -- an actual pain point or need. | Prevents solution-seeking without a problem.                          |
| `outcome_clear`           | Can you describe what "done" looks like concretely?                                               | If you can't picture the end state, you're not ready.                 |
| `effort_estimated`        | Is there a rough t-shirt size (S/M/L/XL) with rationale?                                         | Catches "quick weekend project" delusions early.                      |
| `motivation_justified`    | Is there a compelling answer to "why this, why now?"                                              | The ADHD filter. Novelty is not motivation.                           |
| `alternatives_considered` | Has "what if I just don't do this?" been honestly answered?                                       | The kill switch. If nothing bad happens by not doing it, maybe don't. |

#### review_by

Defaults to 30 days from `date_proposed`. When this date passes without all readiness gates being met, the proposal is flagged during triage for a keep-or-kill decision. If the user chooses to invest, `review_by` is extended by 30 days. There is no indefinite limbo.

### Body Sections

All sections are required. Content can be brief during initial capture, but gates won't pass on vague or empty sections.

**Problem** -- What's broken, missing, or painful? Be specific. "It would be cool to have X" is not a problem.

**Desired Outcome** -- What does the world look like after this is done? Concrete and observable.

**Why This, Why Now?** -- Why does this deserve your finite time and energy? What's the cost of delay vs. the cost of doing it? Novelty and excitement are not valid answers.

**What If I Don't?** -- Honest answer. What actually happens if you never do this? This is the hardest section and the most important one. If the answer is "nothing, really" then this idea probably shouldn't be on your plate.

**Rough Effort** -- T-shirt size (S/M/L/XL) with a sentence justifying it. If you can't estimate, explain why and list what you'd need to know first.

**Open Questions** -- Same format as PROJECT.md. Bulleted questions with dated sub-bullet answers when resolved.

**Readiness Assessment** -- Agent-generated summary. Lists which gates pass, which fail, and why. Updated each time the proposal is reviewed. The user does not write this section directly.

### Section Order

```
[YAML frontmatter]
# {Title}
## Problem
## Desired Outcome
## Why This, Why Now?
## What If I Don't?
## Rough Effort
## Open Questions
## Readiness Assessment
```

### Example

```markdown
---
project_id: garage-workshop-buildout
title: "Garage Workshop Buildout"
date_proposed: 2026-02-15
last_updated: 2026-02-18
review_by: 2026-03-17
tags: [home, workshop]
readiness:
  problem_defined: true
  outcome_clear: true
  effort_estimated: false
  motivation_justified: true
  alternatives_considered: true
---

# Garage Workshop Buildout

## Problem

I have no dedicated workspace for hardware projects. Tools are scattered across three rooms, the garage has no workbench, and I keep putting off electronics projects because setup and teardown takes longer than the actual work.

## Desired Outcome

A functional workshop in the garage with a permanent workbench, tool wall, adequate lighting, and at least two dedicated outlets on their own circuit. I can walk in and start working on a project in under 2 minutes.

## Why This, Why Now?

I have three hardware projects queued up that I keep deferring because of the workspace situation. The longer I wait, the more those projects pile up and the more frustrated I get. Winter is ending, so garage temps will be workable soon.

## What If I Don't?

Hardware projects keep getting deferred. I keep doing the setup/teardown dance on the kitchen table, which annoys everyone. Not catastrophic, but it's a persistent friction that degrades quality of life and blocks other work.

## Rough Effort

**L (Large)** -- Need to research workbench options, potentially run a new electrical circuit (may need an electrician), mount pegboard, install lighting. Multiple weekends of work plus lead time on materials.

## Open Questions

- Do I need a permit for adding a circuit in the garage?
- What's the right workbench depth for electronics work?

## Readiness Assessment

**3/5 gates passed.** Last reviewed: 2026-02-18.

- **problem_defined**: PASS. Clear, specific pain point with concrete examples.
- **outcome_clear**: PASS. Observable criteria -- workbench, tool wall, lighting, outlets, 2-minute start time.
- **effort_estimated**: FAIL. T-shirt size given but the electrical work is a wildcard. Need to answer the permit question and get a rough quote before this is a real estimate.
- **motivation_justified**: PASS. Unblocks three other projects. Cost of delay is measurable.
- **alternatives_considered**: PASS. "What if I don't" has an honest answer -- continued friction, deferred projects.
```

### Killing Proposals

Proposals can be killed at any time by explicit user request or during triage. A killed proposal is **deleted entirely** -- the folder is removed from `Proposed/` with no move to Archive. There is no record. If the idea had real merit, it will resurface naturally.

---

## RETRO.md Format

A retrospective document created when a project moves to `Archive/` (completed or cancelled). Optional but recommended. Lives alongside `PROJECT.md` in the project folder.

The retrospective is not a rehash of the work log -- it's a reflective narrative written in hindsight. The work log captures *what happened when*. The retro captures *what it meant*.

### Frontmatter (YAML)

```yaml
---
project_id: my-project
retro_date: 2026-02-22
outcome: completed
---
```

| Field      | Required | Type   | Description                                                    |
|------------|----------|--------|----------------------------------------------------------------|
| project_id | yes      | string | Must match the project's `project_id`.                         |
| retro_date | yes      | date   | YYYY-MM-DD. When the retrospective was conducted.              |
| outcome    | yes      | enum   | `completed` or `cancelled`. Mirrors the project's terminal status. |

### Body Sections

All sections are required. Content can be brief, but should be present.

**Summary** -- The arc of the project from inception to end. A narrative, not a bullet list. What was the project, what actually happened, and how did it end?

**What Went Right** -- Decisions, tools, approaches, or habits that paid off. What should be repeated?

**What Went Wrong** -- Pain points, bad calls, things that cost time or quality. What should be avoided?

**Lessons Learned** -- Concrete, portable takeaways. What would you tell yourself before starting this project? These should generalize beyond this specific project.

**What Would I Change?** -- Project-specific hindsight. If you could rewind and start over, what would you do differently? Scope, approach, timing, tools, priorities.

### Section Order

```
[YAML frontmatter]
# Retrospective: {Title}
## Summary
## What Went Right
## What Went Wrong
## Lessons Learned
## What Would I Change?
```

### Example

```markdown
---
project_id: home-network-overhaul
retro_date: 2026-03-20
outcome: completed
---

# Retrospective: Home Network Overhaul

## Summary

Replaced the consumer-grade home network with a UniFi-based VLAN-segmented setup over about two months. The project went smoothly overall -- hardware research was quick, the UniFi ecosystem was well-documented, and most milestones landed on or ahead of schedule. The one real snag was the back office dead zone, which needed a MoCA adapter that added a week of waiting. End result: full coverage, proper segmentation, and no more dropped video calls.

## What Went Right

- Choosing a single-vendor ecosystem (UniFi) avoided compatibility headaches.
- Doing hardware research as a formal milestone prevented impulse purchases.
- Separating cameras onto their own VLAN early saved a painful migration later.
- Coming in under budget by $150.

## What Went Wrong

- Didn't account for the MoCA adapter lead time. Should have ordered it with the first batch.
- Underestimated how many IoT devices needed manual reconnection -- took a full weekend.
- Didn't document the old network before tearing it down, which made rollback planning harder.

## Lessons Learned

- Order long-lead items first, even if they're for a later milestone.
- When migrating infrastructure, document the existing state *before* touching anything.
- Budget a full day for device reconnection per 20 devices.

## What Would I Change?

- Would have started with the back office AP instead of saving it for last, since it was the highest-risk piece.
- Would have created a spreadsheet of every device and its VLAN assignment upfront instead of sorting it out on the fly.
```

---

## GROUP.md Format

Groups are parent projects -- lightweight containers for related projects. They have no status, no milestones. They never "complete."

### Group Folder Layout

```
Groups/
  {group-id}/
    GROUP.md             # the group file (required)
    resources/           # shared resources across child projects
```

### Frontmatter

```yaml
---
group_id: legacy-conversion
title: "Legacy Conversion"
date_created: 2026-02-22
tags: []
---
```

| Field        | Required | Type   | Description                            |
|--------------|----------|--------|----------------------------------------|
| group_id     | yes      | string | Kebab-case. Must match folder name.    |
| title        | yes      | string | Human-readable group name.             |
| date_created | yes      | date   | YYYY-MM-DD.                            |
| tags         | no       | list   | Freeform categorization.               |

### Body Sections

- **Purpose** -- Why this group exists. What ties these projects together.
- **Projects** -- List of child `project_id` values. Auto-maintained by agents.
- **Notes** -- Freeform content, shared context, high-level goals.

### Example

```markdown
---
group_id: legacy-conversion
title: "Legacy Conversion"
date_created: 2026-01-15
tags: [infrastructure, migration]
---

# Legacy Conversion

## Purpose

Migrating all legacy systems to the new platform. Each system gets its own project, but they share infrastructure work and migration tooling.

## Projects

- legacy-auth-migration
- legacy-db-migration
- legacy-api-conversion

## Notes

Shared migration scripts live in `resources/`. All child projects should reference these rather than rolling their own.
```
