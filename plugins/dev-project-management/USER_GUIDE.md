# Project Management Bundle: User Guide

Welcome to the Project Management bundle! This guide explains how to use the bundle to manage your projects, from initial idea to final completion. The system is entirely file-based, meaning your projects are just folders and Markdown files. There is no database, no syncing, and no vendor lock-in. 

## The Project Lifecycle

Projects move through five top-level folders that represent their lifecycle phase:

1. **`Proposed/`**: New ideas start here as `PROPOSAL.md` files. They aren't projects yet. They must clear readiness gates before becoming real projects.
2. **`On-Deck/`**: Vetted proposals that have been promoted to projects (`PROJECT.md`). They are ready to be worked on but haven't started yet.
3. **`Active/`**: Projects you are currently working on.
4. **`Paused/`**: Projects that are blocked, stalled, or deliberately deprioritized.
5. **`Archive/`**: Projects that are completed or cancelled.

## How to Create a Project

Every project starts as a **proposal**. This acts as a filter to prevent half-baked ideas from consuming your time and energy.

1. **Submit an Idea**: When you have an idea, you can use the system to create a proposal. This will create a folder in `Proposed/` containing a `PROPOSAL.md` file.
2. **The Readiness Gates**: Your proposal must pass five readiness gates to become a project:
   - **Problem Defined**: Is there a specific, articulable problem?
   - **Outcome Clear**: Can you describe what "done" looks like concretely?
   - **Effort Estimated**: Is there a rough T-shirt size (S/M/L/XL) with a rationale?
   - **Motivation Justified**: Is there a compelling answer to "why this, why now?"
   - **Alternatives Considered**: Has "what if I just don't do this?" been honestly answered?
3. **Promotion**: Once an agent or you assess that all five gates are passed, you can approve the promotion. The system will generate a `PROJECT.md` file and move the folder to `On-Deck/`. 

## Statuses Explained

While the folder determines the broad phase, the `status` field in the frontmatter of your `PROJECT.md` tracks the exact state.

- **`proposed`** (`Proposed/`): An idea that needs vetting.
- **`on-deck`** (`On-Deck/`): Ready to be scheduled.
- **`active`** (`Active/`): Currently being worked on.
- **`waiting`** (`Paused/`): Blocked on something external (e.g., waiting for an email reply or a delivery).
- **`stalled`** (`Paused/`): Internal blocker (e.g., lost momentum, hit a wall, needs intervention).
- **`parked`** (`Paused/`): Deliberately deprioritized for now.
- **`completed`** (`Archive/`): Met its "Done When" criteria.
- **`cancelled`** (`Archive/`): Decided not to do this.

*Note: Any time a project moves to `parked`, `stalled`, `waiting`, or `cancelled`, a reason is required in the Work Log.*

## Folder Structure

A typical project folder looks like this once it reaches the `On-Deck` phase:

```text
{project-id}/
  PROJECT.md           # The main project file
  PROPOSAL.md          # The original proposal (kept for history)
  assets/              # Images, diagrams, etc.
  resources/           # Supporting documents
  scripts/             # Automation, agent skills
```

You can also group related projects inside the `Groups/` folder using a `GROUP.md` file. Groups are organizational containers and don't have statuses or milestones.

## The Work Log

The Work Log lives at the bottom of your `PROJECT.md` file. It's an append-only, reverse-chronological record of everything that happens in the project.

- **Timestamped**: Every entry is grouped under an `### YYYY-MM-DD` header.
- **Automated Logging**: Status changes and milestone completions are automatically logged with italicized formatting (e.g., `- *Status: active -> parked*`).
- **Manual Updates**: You can add your own regular bullet points to track progress, note decisions, or capture things you've learned.

## Milestones

Progress is tracked via a Milestones table in `PROJECT.md`.

- Milestones are numbered sequentially.
- Statuses can be `pending`, `in-progress`, `done`, or `skipped`.
- Target (`Due`) dates can be left blank if you haven't committed to a deadline.
- When a milestone is marked `done`, the `Completed` date is filled in, and an entry is added to the Work Log.

## Retrospectives

When a project moves to `Archive/` (either `completed` or `cancelled`), you can optionally conduct a retrospective. This generates a `RETRO.md` file in the project folder.

A retrospective isn't a timeline of what happened—it's a reflection on *why* it happened and what it meant. It covers:
- **Summary**: The narrative arc of the project.
- **What Went Right**: Decisions or habits that paid off.
- **What Went Wrong**: Pain points or bad calls.
- **Lessons Learned**: Generalizable takeaways for future projects.
- **What Would I Change?**: Hindsight specific to this project.

## Working with Agents

Agents act as your project managers. They can:
- Interview you to help flesh out proposals and evaluate readiness gates.
- Handle the mechanics of promoting a proposal to a project.
- Safely change a project's status, update frontmatter, and move folders.
- Add entries to your Work Log.
- Ask probing questions to help you write a meaningful retrospective.

Agents will always default to asking for your input and approval, especially for status changes, importance ratings, or cancellations. They will not unilaterally change the trajectory of your project.
