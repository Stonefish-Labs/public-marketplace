---
name: process-observability
description: >
  Inspect top running processes by CPU and memory when users ask "what is slowing
  this machine down", "high CPU", "memory pressure", or "what is running right
  now". Use this skill for runtime diagnostics only. Default output is privacy
  minimized: process paths and command lines are excluded unless explicitly needed
  for forensic debugging. Use this before broad system reports when performance is
  the primary concern.
---

# Process Observability

Use `scripts/processes.py`.

## Safety

- Default mode omits executable and command-line paths.
- Include paths only with `--include-paths` when the user explicitly asks.
