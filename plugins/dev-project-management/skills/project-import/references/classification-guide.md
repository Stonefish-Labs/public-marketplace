# Import Classification Guide

How to map an old project's state to the PM system's lifecycle statuses. Use these heuristics when the scan results are ambiguous or the user isn't sure what status fits.

## Decision Tree

**Was real work done on this?**

- **No** -- It's a **proposal**. Drop it in `Proposed/` and let the gates sort it out.
- **Yes** -- Keep going.

**Is the work finished?**

- **Yes, it met its goals** -- `completed`. Archive it.
- **Yes, but it was abandoned/killed** -- `cancelled`. Archive it. Get the reason.
- **No** -- Keep going.

**Is it currently being worked on?**

- **Yes, actively** -- `active`.
- **No** -- Keep going.

**Why did it stop?**

- **Blocked on something external** (a person, a delivery, a decision, a dependency) -- `waiting`.
- **Hit a wall internally** (lost momentum, stuck on a hard problem, ran out of ideas) -- `stalled`.
- **Deliberately deprioritized** (not blocked, just not now) -- `parked`.
- **Planned but never started** (was ready to go, just hasn't kicked off) -- `on-deck`.

## Common Old-System Mappings

| Old system label         | Maps to     | Notes                                              |
|--------------------------|-------------|----------------------------------------------------|
| "Someday/Maybe"          | `proposed`  | Unless real work happened, then `parked`            |
| "Backlog"                | `on-deck`   | If it was triaged and accepted as worth doing       |
| "Backlog" (untriaged)    | `proposed`  | If it was just a dump of ideas                      |
| "In Progress"            | `active`    | Straightforward                                     |
| "On Hold"                | `parked`    | Unless there's a specific blocker, then `waiting`   |
| "Blocked"                | `waiting`   | External dependency                                 |
| "Stuck"                  | `stalled`   | Internal blocker                                    |
| "Done" / "Complete"      | `completed` | Verify it actually met goals, not just abandoned    |
| "Cancelled" / "Won't Do" | `cancelled` | Get the reason                                      |
| "Archived" (ambiguous)   | Ask         | Could be completed or cancelled -- clarify with user|
| "Draft" / "WIP"          | `proposed`  | If it's still at the idea stage                     |
| "Next Up"                | `on-deck`   | Vetted and ready                                    |

## Red Flags During Classification

- **"Completed" but no deliverables exist.** Probably cancelled or stalled. Ask what actually got delivered.
- **"Active" but nothing happened for months.** That's stalled, not active. Call it out.
- **"On hold" with no reason.** Dig for the reason. The distinction between waiting, stalled, and parked matters for determining the right intervention.
- **Everything marked "high priority."** Ignore old priority labels. Reassess importance and urgency fresh during import.
- **Multiple old projects that are really the same thing.** Suggest consolidating into one import. Or use a Group if they're related but distinct.

## When In Doubt

Ask the user. A wrong classification wastes more time than a quick clarifying question. The status can always be changed after import, but getting it right the first time means the project lands in the right folder and gets the right kind of attention.
