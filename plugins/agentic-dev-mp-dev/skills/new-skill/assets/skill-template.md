---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
license: {{LICENSE}} # Optional: License for open-source (e.g., MIT)
compatibility: {{COMPATIBILITY}} # Optional: Indicates environment requirements
metadata:
  author: {{AUTHOR}}
  version: 1.0.0
  mcp-server: {{MCP_SERVER}}
  category: {{CATEGORY}}
  tags: [{{TAGS}}]
user-invocable: {{USER_INVOCABLE}} # true or false
allowed-tools: [] # Optional list of tools allowed
---

# {{SKILL_NAME}}

## Overview
What this skill does and when an agent should use it.

## Instructions

1. First step
2. Second step
3. Verify result

## Context & Invocation

- **Dynamic Context Injection**: Use `!command` syntax to inject dynamic context. For example: `!python my_script.py` inside the skill markdown.
- **Subagent Execution**: Use `context: fork` to run this skill in a subagent. Optionally, specify an agent using `agent: <name>` (e.g., `context: fork` \n `agent: Explore`).
- **String Substitutions**: The following string substitutions are available when invoking skills:
  - `$ARGUMENTS[N]` or `$N`: Substitutes the Nth argument passed to the skill.
  - `${CLAUDE_SESSION_ID}`: Substitutes the current session ID.

## Examples

### Example 1: Basic Usage
```
User asks: "..."
Agent should: ...
```

## Reference
- Links to relevant docs or APIs

## Checklist
- [ ] Step 1 complete
- [ ] Step 2 complete
- [ ] Result verified
