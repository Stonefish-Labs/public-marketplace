---
name: mcp-hitl-checkpoints
description: >
  Identify and implement human-in-the-loop checkpoints for agent safety. Use this
  skill when deciding which MCP tool actions need human confirmation, designing
  destructive operation safeguards, implementing two-phase preview-then-execute
  patterns, adding audit trails, or when someone asks "should this tool require
  confirmation", "human in the loop for MCP", "agent safety checkpoints",
  "destructive action confirmation", or "HITL patterns". Applicable beyond MCP
  to any agent workflow where autonomy boundaries matter.
---

# Human-in-the-Loop Checkpoints

Agents operating autonomously can cause irreversible harm. HITL checkpoints
create boundaries — humans approve critical decisions, agents handle routine
work. The cost of a false pause is seconds; the cost of a missed checkpoint
can be data loss or security breaches.

## Decision Framework

Before any tool action, evaluate:

```
Is it REVERSIBLE?     → No  → Require confirmation
Affects EXTERNAL?     → Yes → Require confirmation
Exposes SENSITIVE?    → Yes → Require confirmation
Intent CLEAR?         → No  → Clarify first
All yes/no above?     → Safe to proceed autonomously
```

## Checkpoint Taxonomy

| Category | Examples | Action |
|---|---|---|
| Destructive ops | File delete, DB drop, account removal | Always confirm |
| External comms | Email, API post, webhook, notification | Confirm content + recipient |
| Financial | Purchase, billing change, subscription | Always confirm with details |
| Auth decisions | Grant access, change perms, gen token | Confirm scope + target |
| Data exposure | Export PII, share sensitive data | Confirm what + where |
| Config changes | Production config, DNS, infrastructure | Confirm change + impact |
| Ambiguous intent | Unclear request, multiple interpretations | Clarify first |

## Implementation

Read `references/implementation.md` for full code examples covering:

- Elicitation confirmation before destructive actions
- Two-phase preview → confirm → execute pattern
- Tool annotations (`destructiveHint`, `readOnlyHint`)
- Audit trail logging
- Agent evaluator integration with confidence scoring

## Quick Pattern

```python
from fastmcp import Context, CurrentContext

# Version-safe: use result.action ("accept" | "decline" | "cancel") — do NOT
# import AcceptedElicitation from fastmcp; it is not reliably exported across
# all FastMCP 3.x builds and will cause ImportError at server startup.

@mcp.tool(annotations={"destructiveHint": True})
async def dangerous_action(target: str, ctx: Context = CurrentContext()) -> dict:
    result = await ctx.elicit(
        f"This will permanently affect {target}. Proceed?",
        response_type=None  # Pure action confirmation modal
    )

    if result.action == "accept":
        # Execute...
        return {"status": "completed"}
    else:
        return {"status": "cancelled"}
```

## Checklist for Tool Authors

- [ ] Irreversible action? → Add confirmation
- [ ] Sends data externally? → Confirm content + destination
- [ ] Modifies production? → Add preview + confirm
- [ ] Exposes sensitive data? → Confirm scope
- [ ] `destructiveHint` annotation set correctly?
- [ ] Audit trail for the decision?
