---
name: mcp-elicitations
description: Essential framework rules for implementing user data collection forms, progressive disclosure workflows, and conditional UI elicitations using FastMCP 3. Use when asked to "create a form", "gather user input", "use ctx.elicit", or "build a wizard". Covers both single-turn rich elicitations and multi-step wizards.
---

# FastMCP 3 Elicitation Architecture

**Deep Dive References:**
* 📖 **[UI Controls & Typing](references/ui_controls.md)**: Exhaustive list of how to generate text boxes, dropdowns, and checkboxes using Python types.
* 📖 **[Advanced Architecture](references/advanced_architecture.md)**: Details on security boundaries (URL Mode), Docket background tasks, and explicit action handling.
* 📖 **[Client Implementation](references/client_implementation.md)**: Guide on how MCP Clients should implement an `elicitation_handler` to render UI controls.

## Decision Matrix: Progressive Disclosure for the AI
Before implementing an elicitation workflow, evaluate the user's design requirements:

1. **Is the task a single, straightforward data gathering request?** (e.g., asking for a configuration object, or a couple of related fields at once).
   * **Action**: Use **Native Rich Elicitation**.
   * **Reference**: Read `assets/basic_elicitation.py` for standard implementation details, and `assets/auth_patterns.py` for lazy-authentication caching and parameter clarification patterns.
   * **Mechanism**: Use standard `ctx.elicit()` with SEP-1330 mappings and Pydantic BaseModels.

2. **Does the task require branching logic, progressive disclosure, or multiple dependent steps?** (e.g., "Ask for environment -> If prod, ask for advanced config -> validate -> provision").
   * **Action**: Use the **Progressive Form Wizard**.
   * **Reference**: Read `assets/wizard_skeleton.py` for implementation details.
   * **Mechanism**: Use the `fastmcp-wizard` library provided in the `scripts/fastmcp-wizard/` package directory of this skill. 

---

## 1. Native Rich Elicitation (Single-Turn)
The FastMCP 3 framework natively translates Python type annotations into SEP-1330 compliant UI schemas for `ctx.elicit(response_type=...)`. 

**UI Type Mappings:**
* `str`, `int`, `bool`: Scalar Input (Text box, Spinner, Toggle)
* `["low", "high"]`: Single-Select Dropdown (Untitled)
* `{"low": {"title": "Low Priority"}}`: Single-Select Dropdown (Titled)
* `[["bug", "feature"]]`: Multi-Select Checklist (Untitled)
* `[{"low": {"title": "Low Priority"}}]`: Multi-Select Checklist (Titled)
* Pydantic `BaseModel`: Complex Structured Composite Form
* `None`: Pure Action (Confirmation Modal: Accept/Decline)

**Explicit Protocol Action Handling:**
You MUST handle the returned action explicitly. Use `result.action` string checks —
**do not** import `AcceptedElicitation` / `DeclinedElicitation` / `CancelledElicitation`
from `fastmcp.server.elicitation`; they are not reliably re-exported across all
FastMCP 3.x builds and will cause `ImportError` at server startup.

```python
# ✅ Version-safe — works across all FastMCP 3.x builds
if result.action == "accept":
    user_data = result.data
    ...
elif result.action == "decline":
    ...
elif result.action == "cancel":
    ...
```

---

## 2. Progressive Form Wizard (Multi-Step)
For complex workflows, you MUST utilize the internal `FormWizard` library located within the complete package at `scripts/fastmcp-wizard/`. This package abstracts the FastMCP session state (`ctx.get_state` / `ctx.set_state`) and handles Pydantic `ValidationError` self-correction automatically.

**Key Components:**
* **WizardManager**: Orchestrates the state machine across distributed sessions.
* **FormStep**: Encapsulates a single `ctx.elicit` call. Use the `condition` parameter (a lambda function) to dynamically bypass or show steps based on previous data.
* **UrlElicitationRequiredError**: Raise this exception if the workflow attempts to gather highly sensitive out-of-band secrets (OAuth tokens, API keys).

**Usage:**
If you need to implement a multi-step wizard, you should utilize the `scripts/fastmcp-wizard/` package. The package contains its own `pyproject.toml` and examples in `scripts/fastmcp-wizard/examples/basic_wizard.py` to show full context. Then, implement your tool following the pattern in `assets/wizard_skeleton.py`.