---
name: composition-review
description: Review a project's components and determine optimal composition -- whether each piece should be an MCP server, skill, hook, script, subagent, or standalone tool. Use when auditing existing projects, evaluating architecture decisions, or determining if something should be retooled.
---

# Composition Review

Review a project and determine whether its components are built as the right primitive -- MCP server, skill, hook, script, subagent, programmatic code, or reference material -- based on established design philosophy principles. The goal is to identify mis-categorized components and recommend what they should be.

## Workflow

Follow these steps in order. Use the todo list to track progress.

```
Task Progress:
- [ ] Step 1: Discover -- inventory the project
- [ ] Step 2: Characterize -- profile each component
- [ ] Step 3: Apply decision framework
- [ ] Step 4: Produce recommendations
- [ ] Step 5: Identify anti-patterns
```

### Step 1: Discover

Explore the target project thoroughly. Inventory everything that exists:

- Source code files (servers, libraries, CLI tools)
- Markdown and documentation files
- Configuration files (package.json, pyproject.toml, MCP configs, etc.)
- Skill definitions (SKILL.md files)
- Scripts (standalone or bundled)
- Hook definitions
- Server entry points
- Test files
- Any other artifacts

For each component, classify what it **currently is**:

| Category | Indicators |
|----------|-----------|
| MCP server | Exposes tools via MCP protocol, has server entry point, tool schemas |
| Skill | Has SKILL.md, bundles instructions and optionally scripts |
| Hook | Fires on lifecycle events, no agent decision involved |
| Script | Standalone executable, invoked via shell |
| Subagent workflow | Delegates to other agents, staged handoffs |
| Programmatic code | Fixed pipeline, no LLM reasoning in the loop |
| Reference material | Markdown docs, knowledge base content, guides |
| CLI tool | Command-line application with flags and subcommands |
| Library | Importable module, no standalone execution |

If the project is just markdown files with no code, note that -- it may be reference material that needs a retrieval strategy, or it may be skill/doc content that should be restructured.

### Step 2: Characterize

For each component identified in Step 1, answer these profiling questions:

**Tooling characteristics:**
- Does it maintain state between calls?
- Is it shared across multiple agents or skills?
- Does it need typed schemas for its interface?
- Is it fire-and-forget (no return value needed)?
- Is it portable (works without external config)?
- Does the agent need to *decide* to use it, or should it be automatic?
- Is it simple and stateless?
- Could the agent need to modify or improvise with it?
- Does it need persistent secrets (API keys, tokens, webhook URLs)? If yes, that alone does not justify MCP -- scripts can use file-based secrets.

**Architecture characteristics:**
- Is the workflow path known in advance?
- Is a human needed during execution?
- What's the acceptable failure mode?
- Does it require different cognitive modes at different stages?
- Does it have reuse value outside its current workflow?

**Knowledge characteristics (for reference material):**
- How large is the corpus?
- Is it structured or organic?
- Does it need discovery (agent doesn't know it exists) or just lookup?
- Who consumes it -- one agent or many?

Record these characteristics. They feed directly into the decision framework.

### Step 3: Apply Decision Framework

Run each component through the decision matrix in [references/decision-matrix.md](references/decision-matrix.md). Work through the heuristics in order:

1. **Check native tools first.** Does the runtime already handle this? If yes, the component may be unnecessary.
2. **Check if it should be a hook.** Should the agent never have to think about whether to use it? If yes, it's a hook.
3. **Check if it should be an MCP server.** Shared across agents? Needs typed schemas and state? Permission gating? If yes, MCP.
4. **Check if it should be a script.** Simple, stateless, portable, agent might improvise? If yes, script.
5. **Check if it should be a skill.** Bundles capabilities with progressive disclosure, portable across orchestration architectures? If yes, skill.
6. **Check decomposition boundaries.** Does the workflow shift cognitive modes? Are there natural phase boundaries with clear handoff contracts? If yes, subagent decomposition.
7. **Check knowledge architecture.** Is this reference material? Evaluate retrieval approach: full context, index + on-demand, MCP search, or RAG.
8. **Check architecture position.** Is this even an agent component? If the workflow is fully known and needs no reasoning, it's programmatic code.

### Step 4: Produce Recommendations

For each component where the current form differs from the recommended form, produce a recommendation. Use the template in [assets/review-template.md](assets/review-template.md).

For components that are already the right primitive, say so explicitly -- confirmation is valuable.

Every recommendation must cite which design principle drives it. Don't just say "this should be a skill" -- say *why* based on the characteristics identified in Step 2 and the heuristic that matched in Step 3.

### Step 5: Identify Anti-Patterns

Scan for these known anti-patterns across the project as a whole:

- **Over-decentralization**: Too many separate tools/servers when related capabilities should be grouped
- **Fashion-driven architecture**: Built as an MCP server or agent because it's trendy, not because the characteristics demand it
- **Premature autonomy**: Autonomous workflow without a termination spec or quality gates
- **Missing fallbacks**: Skills that depend on MCP servers with no script fallback
- **Scope confusion**: Capability layer confused with orchestration layer
- **Monolithic cramming**: One agent prompt trying to handle multiple cognitive modes
- **MCP-for-secrets**: Built as an MCP server purely because it needs an API key or token, when it's otherwise stateless and single-consumer -- scripts can use file-based secrets
- **CLI-as-tool**: Agent shelling out to CLI apps when a purpose-built library would remove known failure modes
- **No retrieval strategy**: Reference material dumped into a directory with no index, no progressive disclosure, no awareness mechanism
- **Decomposing for the sake of decomposition**: Subagent boundaries that don't align with cognitive boundaries
- **Schema-as-quality**: Structured outputs treated as sufficient for correctness when rubric evaluation is needed

## Key Principles

Hold these in mind throughout the review. They're the compressed decision rules.

| Signal | Recommended Form |
|--------|-----------------|
| Agent shouldn't decide to use it | **Hook** |
| Shared across agents, typed schemas, stateful | **MCP server** |
| Portable, self-contained, agent might improvise | **Script** |
| Bundles capabilities with progressive disclosure | **Skill** |
| Workflow shifts cognitive modes at a boundary | **Subagent** delegation point |
| Runtime already handles it | **Native tool** -- don't rebuild it |
| Known pipeline, no reasoning needed | **Programmatic code** -- not an agent component |
| Reference material for agents | Evaluate through **knowledge architecture** lens |

## Mis-Categorization Signals

These are red flags that a component is built as the wrong thing:

- An MCP server used by only one agent with no shared state -- probably a script or skill-bundled script
- A skill that can't function without a specific MCP server running -- coupling issue, needs a script fallback or the logic should live in the MCP server
- A script that runs automatically on every session -- should be a hook
- Markdown docs in a directory with no index or retrieval mechanism -- needs knowledge architecture
- An agent workflow with no termination spec running autonomously -- needs human-in-the-loop or a spec
- Forty MCP tools that could be three coherent services -- over-decentralization
- A purpose-built MCP server that just wraps a single CLI command -- the overhead isn't justified
- An MCP server that exists purely because the tool needs an API key -- if it's otherwise stateless, single-consumer, and doesn't need typed schemas, it should be a script with file-based secrets
- A monolithic agent prompt handling capture, review, and execution -- decompose on cognitive boundaries
- A component that requires OS-level installation in every environment -- should be a library or bundled dependency
- Reference material injected fully into context when it's too large -- needs tiered retrieval

## Output

Produce the review using the template in [assets/review-template.md](assets/review-template.md). The review should be actionable -- someone should be able to read it and know exactly what to change and why.

If no changes are needed, say so. "This is correctly composed" is a valid and useful conclusion.
