---
description: Upgrade an MCP server to FastMCP 3.x with componentized architecture and safety/test gates
argument-hint: <server-path> [mode:auto|python|js-ts]
---

# upgrade-mcp-fastmcp3

## Context

- !`pwd`
- !`ls -la "$1"`

## Files

- @skills/mcp-server-upgrade/SKILL.md
- @skills/mcp-server-upgrade/references/breaking-changes.md
- @skills/mcp-server-upgrade/references/js-conversion.md
- @skills/mcp-server-create/SKILL.md
- @skills/mcp-hybrid-architecture/SKILL.md
- @skills/mcp-tool-design/SKILL.md
- @skills/mcp-response-format/SKILL.md
- @skills/mcp-startup-patterns/SKILL.md
- @skills/mcp-secrets/SKILL.md
- @skills/mcp-hitl-checkpoints/SKILL.md
- @skills/mcp-elicitations/SKILL.md
- @skills/mcp-testing/SKILL.md

## Task

Upgrade the MCP server at `$1` to **Python FastMCP 3.x**. Follow all phases in order.  
`$2` selects mode: `auto` (default), `python`, or `js-ts`.

Stop immediately on critical failures and report exactly what blocked progress.

Invocation examples:
- `/upgrade-mcp-fastmcp3 ./mcp-servers/findmy-server`
- `/upgrade-mcp-fastmcp3 ./mcp-servers/legacy-python python`
- `/upgrade-mcp-fastmcp3 ./mcp-servers/legacy-js js-ts`

---

### Phase 0: Discovery and Mode Selection

1. Validate `$1` exists and is a server root (or contains one).
2. Detect server type:
   - Python FastMCP 2.x indicators: `from mcp.server.fastmcp import FastMCP`, old 2.x APIs.
   - JS/TS indicators: `package.json`, MCP handlers in JS/TS files, zod schemas.
3. Resolve mode:
   - If `$2` provided, honor it.
   - If `auto`, infer from code and explain why.
4. Print a short plan preview before edits:
   - Migration path
   - Files likely touched
   - Risks and gates that will be enforced

---

### Phase 1: Core Migration Engine

Always use the **mcp-server-upgrade** skill.

#### If mode is `python`

Perform a 2.x -> 3.x migration and apply the full breaking-changes checklist.

#### If mode is `js-ts`

1. Use **mcp-server-upgrade** JS/TS conversion guidance.
2. Use **mcp-server-create** to scaffold a proper Python FastMCP 3.x envelope where needed.
3. Port JS/TS MCP handlers to typed Python tools.
4. Ensure final state is Python FastMCP 3.x only (no partial JS/TS runtime left behind unless explicitly requested).

---

### Phase 2: Mandatory 17-Point Breaking-Change Gate

You must verify and resolve all 17 items from `breaking-changes.md` before proceeding:

1. Import path (`from fastmcp import FastMCP`)
2. WSTransport removal (`StreamableHttpTransport`)
3. Auth providers explicit env loading
4. Component control moved to server-level enable/disable
5. Listing APIs return lists (`list_tools`, etc.)
6. `PromptMessage` -> `Message`
7. Async state management (`await ctx.get_state/set_state`)
8. State serialization rules (`serializable=False` for non-JSON objects)
9. `mount(prefix=...)` -> `mount(namespace=...)`
10. Tag filtering -> enable/disable
11. Tool serializer -> `ToolResult`
12. Tool transformations -> transforms API
13. Proxy creation -> `create_proxy`
14. Metadata namespace `_meta.fastmcp`
15. Env rename `FASTMCP_SHOW_SERVER_BANNER`
16. Decorator return behavior understood (direct calls valid)
17. Constructor migration (`app=AppConfig(...)`)

If any item is not applicable, mark it `N/A` with reason.

---

### Phase 3: Componentized Architecture Uplift

Use **mcp-hybrid-architecture** to refactor toward library-first components where beneficial:

1. Extract core business logic into reusable Python modules.
2. Keep MCP-specific concerns in thin envelope/wrapper layers.
3. Preserve behavior while improving testability and reuse.
4. Skip heavy refactor only if server is truly tiny; justify skip explicitly.

---

### Phase 4: Tool Contract and Response Quality

Apply **mcp-tool-design** and **mcp-response-format**:

1. Ensure every tool has strong type annotations and accurate docstrings.
2. Use `CurrentContext()` pattern in 3.x paths where context is needed.
3. Add tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) where appropriate.
4. Default outputs to clean text responses for agents.
5. Use structured output only for clear programmatic consumers.
6. Remove token-waste anti-patterns (bare strings, over-nested structures).

---

### Phase 5: Startup, Secrets, HITL, and Elicitation Safety

Apply these skills as mandatory safety gates:
- **mcp-startup-patterns**
- **mcp-secrets**
- **mcp-hitl-checkpoints**
- **mcp-elicitations**

Required outcomes:

1. No blocking initialization before MCP handshake.
2. No OAuth or interactive auth in lifespan startup before `yield`.
3. Secret handling uses secure storage patterns; never return or log secrets.
4. Destructive/external/sensitive operations include confirmation checkpoints.
5. Any user data collection uses explicit elicitation action handling (`accept/decline/cancel`).
6. Multi-step, branching data collection uses a wizard pattern when complexity requires it.

---

### Phase 6: Verification and Completion Gate

Use **mcp-testing** as a hard gate:

1. Add or update in-memory client tests for key tool paths.
2. Run targeted tests and report failures clearly.
3. Run deprecation surfacing (for example with warnings enabled) and fix remaining migration warnings where practical.
4. Confirm upgraded server starts and responds correctly.

Do not claim completion until verification passes or remaining failures are clearly documented.

---

### Phase 7: Deliverables and Final Report

Return a concise migration report:

```text
Server:           <path>
Mode:             <python|js-ts|auto-resolved>
Result:           <complete|partial|blocked>
Files changed:    <count + key paths>
Breaking changes:
  Fixed:          <n>/17
  N/A:            <n>/17
  Remaining:      <n>/17
Architecture:     <hybrid applied|kept monolith with reason>
Safety gates:
  Startup:        <pass|fail>
  Secrets:        <pass|fail>
  HITL:           <pass|fail>
  Elicitations:   <pass|fail>
Testing:
  In-memory:      <pass|fail>
  Deprecations:   <pass|fail>
Residual risks:   <bulleted list or none>
```

If blocked, include a minimal unblock plan with exact next actions.
