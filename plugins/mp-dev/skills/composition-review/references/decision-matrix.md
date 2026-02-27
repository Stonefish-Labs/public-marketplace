# Decision Matrix

Condensed heuristics from the design philosophy documents. Work through these in order for each component under review.

## 1. Tooling Mechanism

*Covers: tooling mechanisms (native tools, hooks, MCP, scripts) and the encode-what-you-know principle.*

Check native tools first, then hooks, then MCP, then scripts. When multiple rows match, consider hybrid layering.

| Question | If Yes | Mechanism |
|----------|--------|-----------|
| Does your runtime already handle this well? | Stop here | **Native tool** |
| Does it need UI, editor state, or agent orchestration? | Build one if runtime lacks it | **Native tool** |
| Does the agent need to *decide* to use it? | If no | **Hook** |
| Is it fire-and-forget with no return value needed? | | **Hook** |
| Should it run automatically at a lifecycle event? | | **Hook** |
| Does it need typed schemas and shared state? | | **MCP server** |
| Is it shared across multiple skills or agents? | | **MCP server** |
| Do you need permission gating or elicitation? | | **MCP server** |
| Does a persistent process avoid cold-start overhead? | | **MCP server** |
| Do multiple agents need shared access or coordination? | | **MCP server** |
| Is it simple, stateless, and self-contained? | | **Script** |
| Does the agent need to improvise with it? | | **Script** |
| Must it work without external config? | | **Script** |
| Does it need persistent secrets (API keys, tokens, webhook URLs)? | | **Script** with file-based secrets -- secrets alone don't justify MCP |
| Does portability matter (zero setup for recipients)? | | **Script** |
| Do you want progressive disclosure of capabilities? | | **Script** (bundled in a skill) |

### Hybrid Layering

Sometimes the right answer is multiple mechanisms covering different needs. Layering is justified when each mechanism addresses a distinct **timing** (automatic vs. on-demand) or **audience** (local workspace vs. portable skill).

- Hook handles the baseline (what the agent should always know)
- MCP handles structured on-demand operations (type safety and state)
- Script provides a portable fallback (no infrastructure assumed)

Only layer when each layer covers a distinct need. Redundant layers add maintenance for no gain.

### Tooling Philosophy Check

For any component that involves the agent executing commands or interacting with external systems:

- Is the agent constructing raw CLI commands? **Red flag.** Purpose-built tool calls remove known failure modes.
- Does the agent have access to more capability surface than it needs? **Red flag.** Least privilege -- expose only needed operations.
- Are credentials managed by a CLI tool the agent shells out to? **Red flag.** Own your secret management.
- Could this be a high-level tool call instead of a generated command? If yes, encode it.

Core principle: **If you know what the agent should do, encode it into tooling. Don't make the agent rediscover it at runtime.**

## 2. Architecture Position

*Covers: orchestration authority, termination conditions, control surface, model capability constraints.*

Determine where the component sits on the orchestration spectrum.

| Question | If Yes | Architecture |
|----------|--------|-------------|
| Is the workflow path fully known in advance? | | **Programmatic** -- code it, don't agent it |
| Is there no LLM reasoning needed? | | **Programmatic** -- not an agent component |
| Is the workflow path unknown or open-ended? | | **Agentic** -- let the model reason |
| Is a human available and needed during execution? | | **Assistant** pattern |
| Must it run without human supervision? | | **Autonomous** -- needs termination spec |
| Can you write a precise termination specification? | | **Autonomous** is viable |
| Is termination a judgment call? | | **Assistant** -- human is the termination condition |
| Do you need the managed agent loop without building tools? | | **Agent SDK** |
| Do you need control between tool boundaries? | | **Pure programmatic** |
| Is the workflow well-understood enough that agent reasoning adds no value? | | **Pure programmatic** -- agent loop is overhead |

### Model Capability Check

| Model Tier | Reliable Architecture |
|-----------|----------------------|
| Frontier (Opus, GPT-4.1) | Full spectrum available |
| Mid-tier (Sonnet, Flash) | Programmatic with agentic subtasks |
| Smaller/open | Programmatic with structured outputs |
| Classification/extraction with known categories | Not an LLM task -- use classifiers, rules, regex |

## 3. Decomposition Boundaries

*Covers: monolithic vs. staged handoffs, cognitive boundaries, handoff contracts, reuse value.*

Determine whether a workflow should be monolithic or decomposed into subagents.

| Question | If Yes | Approach |
|----------|--------|----------|
| Does the entire workflow fit comfortably in one context window? | | **Monolithic** |
| Are there distinct phases with clear input/output contracts? | | **Staged handoffs** |
| Do individual stages have reuse value outside this workflow? | | **Staged handoffs** or delegation |
| Is there a quality gate or review step? | | **Separate review agent** |
| Does a stage require a different persona or instruction set? | | **Separate agent** |
| Does failure in one stage need isolated recovery? | | **Staged handoffs** |
| Does a stage touch external systems with failure risk? | | **Separate agent** -- isolate the blast radius |
| Is the total token budget a concern? | | **Staged handoffs** -- fresh window per stage |

### Decomposition Cost Check

Decomposition adds 3-6K tokens overhead per stage. Worth it when:
- Workflow exceeds 10K tokens total
- 3+ distinct cognitive phases exist
- Individual stages have reuse value
- Failure isolation matters

Not worth it when:
- Workflow completes in under 5K tokens
- No reuse case for any stage
- No external system calls that could fail
- No meaningful quality gate

### Handoff Contract Check

If decomposing, each boundary needs:
- A structured artifact with a defined schema (not raw conversation dumps)
- Completeness for the downstream stage's needs
- Minimality beyond that -- don't pass internal reasoning or conversational scaffolding

If you can't describe the handoff as a schema with named fields and types, the boundary isn't clean enough.

## 4. Knowledge Architecture

*Covers: retrieval mechanisms, discovery vs. lookup, enrichment, tiered architecture.*

For components that are reference material, documentation, or knowledge bases.

| Question | If Yes | Approach |
|----------|--------|----------|
| Does the entire corpus fit in context (<100K tokens)? | | **Full context injection** |
| Is the corpus stable, well-bounded, <500 docs? | | **Index + on-demand files** |
| Do multiple agents need the same corpus? | | **MCP search server** |
| Is it maintained by another team? | | **MCP wrapping their API** -- own your enrichment |
| Does retrieval quality need tuning beyond keyword search? | | **Custom RAG** |
| Does the agent need to discover non-obvious connections? | | **Index in context** -- passive awareness |
| Do citations need specific section references? | | **Full documents on demand** -- don't chunk |

### Enrichment Check

Regardless of retrieval mechanism, does the material have:
- Applicability metadata (environments, teams, domains)?
- Known exceptions documented?
- Cross-references to related material?
- Agent-specific notes (common misapplications, gotchas)?

If not, enrichment is the highest-leverage improvement, independent of architecture.

### Discovery vs. Lookup

- **Lookup** (agent knows it needs info): search quality problem -- improve retrieval
- **Discovery** (agent doesn't know relevant info exists): awareness problem -- improve orchestration and context design

Most teams over-invest in search quality and under-invest in awareness. If the material exists but agents don't find it, the problem is orchestration, not retrieval.

## 5. Output Determinism

*Covers: format compliance, coverage determinism, content accuracy, semantic quality.*

For components that produce output consumed by other systems or agents.

| Layer | Question | Mechanism |
|-------|----------|-----------|
| Format compliance | Is the output consumed by a parser/API? | **Constrained decoding** |
| Format compliance | Is it consumed by a human? | **Free generation** |
| Coverage determinism | Is the task scope-bounded with known categories? | **Structured outputs** -- schema enforces coverage |
| Coverage determinism | Does coverage vary unpredictably between runs? | **Structured outputs** |
| Content accuracy | Is "wrong but valid" the dangerous failure mode? | **Verification layer** -- grounding, tool-assisted checks |
| Semantic quality | Does quality have subjective dimensions? | **Rubric evaluation** |
| Semantic quality | Would a senior reviewer have opinions beyond format? | **Rubric** -- capture that review as criteria |

### Composition Patterns

| Pattern | When to Use |
|---------|-------------|
| Constrained decoding alone | Low reasoning complexity, strict format, machine-consumed |
| Free generation then constrained extraction | Complex reasoning needed, structured result required |
| Constrained decoding + rubric | High-stakes artifacts, both machines and humans consume |
| Full composition (free + extract + rubric) | Complex artifacts where reasoning, format, and quality all matter |

## 6. Anti-Patterns Checklist

Aggregated from all design philosophy documents. Flag any that apply.

| Anti-Pattern | Domain | Signal |
|-------------|--------|--------|
| Fashion-driven architecture | Architecture | Built as agent/MCP because trendy, not because characteristics demand it |
| Premature autonomy | Architecture | Autonomous workflow without understanding the decision tree first |
| Over-decentralization | Architecture | Too many separate tools/servers; agent needs a meta-agent to manage capabilities |
| Capability/orchestration confusion | Architecture | "We use MCP therefore we have agent architecture" |
| Removing human without adding infrastructure | Architecture | No durable execution, no failure policies, no termination spec |
| Decomposing for decomposition's sake | Decomposition | Subagent boundaries that don't align with cognitive boundaries |
| Raw conversation as handoff | Decomposition | Dumping conversation history instead of structured artifacts |
| Stages too granular | Decomposition | Single-sentence tasks as separate agents instead of function calls |
| No handoff contracts | Decomposition | Undefined output format between stages |
| CLI-as-tool | Tooling | Agent shelling out to CLI when purpose-built library removes failure modes |
| Excess capability surface | Tooling | Agent has access to full CLI surface when it only needs three operations |
| MCP-for-secrets | Tooling | Chose MCP purely because the tool needs an API key or token, not because it needs state, typed schemas, or multi-agent sharing. Scripts can use file-based secrets. |
| No retrieval strategy | Knowledge | Reference material exists with no index, no search, no awareness mechanism |
| Over-relying on query formulation | Knowledge | Assuming agent will proactively search without triggers |
| Schema-as-quality | Output quality | Treating valid structured output as correct output |
| Self-evaluation bias | Output quality | Model judging its own output without a separate review step |
| Constrained decoding for complex reasoning | Output quality | Forcing schema during reasoning instead of split approach |

## Quick Reference: Component Type at a Glance

For rapid classification when the full heuristics aren't needed:

```
Does the agent decide to use it?
  No  --> Hook
  Yes --> Continue

Does it need state, typed schemas, or is it shared across agents?
  Yes --> MCP server
  No  --> Continue

Is it a bundle of related capabilities with docs?
  Yes --> Skill (with bundled scripts if needed)
  No  --> Continue

Is it simple, stateless, self-contained?
  Yes --> Script
  No  --> Continue

Does the workflow shift cognitive modes at this point?
  Yes --> Subagent boundary
  No  --> Continue

Is it a known pipeline with no reasoning needed?
  Yes --> Programmatic code (not an agent component)
  No  --> Continue

Is it reference material?
  Yes --> Evaluate through knowledge architecture
  No  --> Reassess -- may need hybrid approach
```
