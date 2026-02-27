# HITL Implementation Patterns

<!-- Version-safe note: All elicitation results are handled via result.action
     ("accept" | "decline" | "cancel"). Do NOT import AcceptedElicitation /
     DeclinedElicitation / CancelledElicitation from fastmcp — they are not
     reliably re-exported across all FastMCP 3.x builds. -->

## Elicitation Confirmation

```python
from fastmcp import Context, CurrentContext

@mcp.tool(annotations={"destructiveHint": True})
async def delete_records(
    table: str, condition: str, ctx: Context = CurrentContext()
) -> dict:
    """Delete records matching a condition. Requires confirmation."""
    count = await db.count(table, condition)

    result = await ctx.elicit(
        f"Permanently delete {count} records from '{table}' where {condition}?",
        response_type=["yes, delete them", "no, cancel"]
    )

    if result.action == "accept" and result.data == "yes, delete them":
        await db.delete(table, condition)
        return {"status": "deleted", "count": count}
    else:
        return {"status": "cancelled", "reason": "User declined"}
```

## Two-Phase: Preview → Execute

Split into safe preview and confirmed execution:

```python
@mcp.tool(annotations={"readOnlyHint": True})
def preview_changes(config_path: str) -> dict:
    """Preview changes. Read-only — no modifications made."""
    current = load_config(config_path)
    proposed = compute_changes(current)
    return {
        "current": current,
        "proposed": proposed,
        "diff": compute_diff(current, proposed),
        "next_step": "Call apply_changes() to execute"
    }

@mcp.tool(annotations={"destructiveHint": True})
async def apply_changes(config_path: str, ctx: Context = CurrentContext()) -> dict:
    """Apply changes. Requires confirmation."""
    diff = compute_diff(load_config(config_path), compute_changes(load_config(config_path)))

    result = await ctx.elicit(
        f"Apply {len(diff)} changes to {config_path}?",
        response_type=None  # Confirmation Modal
    )

    if result.action == "accept":
        apply_config(config_path)
        return {"status": "applied", "changes": len(diff)}
    else:
        return {"status": "cancelled"}
```

## Tool Annotations

Signal behavior to clients so they prompt users appropriately:

```python
# Read-only — clients can auto-approve
@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False})
def list_files(directory: str) -> list[str]:
    return os.listdir(directory)

# Destructive — clients should confirm
@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False})
async def drop_table(table: str, ctx: Context = CurrentContext()) -> dict:
    result = await ctx.elicit(
        f"DANGER: Drop '{table}'? All data permanently lost.",
        response_type=["I understand, drop it", "cancel"]
    )

    if result.action == "accept" and result.data == "I understand, drop it":
        return {"status": "dropped"}
    else:
        return {"status": "cancelled"}
```

## Audit Trail

Log all HITL decisions for accountability:

```python
import json
from datetime import datetime, timezone

async def log_hitl_decision(action: str, decision: str, details: dict, ctx: Context):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": ctx.session_id,
        "request_id": ctx.request_id,
        "action": action,
        "decision": decision,
        "details": details,
    }
    await ctx.info(f"HITL: {action} -> {decision}")
    with open("hitl_audit.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

@mcp.tool(annotations={"destructiveHint": True})
async def send_notification(
    recipient: str, message: str, ctx: Context = CurrentContext()
) -> dict:
    result = await ctx.elicit(
        f"Send to {recipient}?\n\n{message}",
        response_type=None  # Confirmation Modal
    )

    decision = "approved" if result.action == "accept" else "denied"

    await log_hitl_decision("send_notification", decision,
        {"recipient": recipient, "length": len(message)}, ctx)

    if decision == "denied":
        return {"status": "cancelled"}
    return {"status": "sent", "recipient": recipient}
```

## Agent Evaluator Integration

### Structured Output for Evaluation

Design responses that automated evaluators can assess:

```python
@mcp.tool
async def risky_op(target: str, ctx: Context = CurrentContext()) -> dict:
    return {
        "status": "completed",
        "target": target,
        "risk_level": "high",
        "reversible": False,
        "hitl_triggered": True,
        "user_approved": True,
    }
```

### Confidence Scoring

```python
@mcp.tool
def classify(content: str) -> dict:
    result = run_classifier(content)
    return {
        "category": result.label,
        "confidence": result.score,
        "requires_review": result.score < 0.8,
        "alternatives": result.top_3,
    }
```

## Anti-Patterns

### Silent Destructive Actions

```python
# BAD
@mcp.tool
def delete_all() -> str:
    db.execute("DELETE FROM users")
    return "Done"

# GOOD
@mcp.tool(annotations={"destructiveHint": True})
async def delete_all(ctx: Context = CurrentContext()) -> dict:
    count = db.count("users")
    result = await ctx.elicit(f"Delete ALL {count} users?",
        response_type=["yes, delete all", "cancel"])

    if result.action == "accept" and result.data == "yes, delete all":
        db.execute("DELETE FROM users")
        return {"status": "deleted", "count": count}
    else:
        return {"status": "cancelled"}
```

### Confirmation Fatigue

```python
# BAD — don't confirm read-only operations
@mcp.tool
async def read_file(path: str, ctx: Context = CurrentContext()) -> str:
    await ctx.elicit(f"Read {path}?", ...)  # Unnecessary

# GOOD — just do it
@mcp.tool(annotations={"readOnlyHint": True})
def read_file(path: str) -> str:
    return open(path).read()
```
