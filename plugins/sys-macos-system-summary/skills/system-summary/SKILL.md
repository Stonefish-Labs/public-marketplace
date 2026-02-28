---
name: system-summary
description: >
  Collect baseline machine identity and hardware diagnostics on macOS, Linux, and
  Windows. Use this skill for questions like "what machine is this", "show system
  specs", "CPU/RAM/GPU details", "battery health", or "uptime". Prefer this skill
  before deeper diagnostics because it is lower sensitivity than process, ports, or
  environment inspection. It is the default entry point for broad system health
  checks when users have not asked for runtime or network details.
---

# System Summary

Run one of these scripts:

- `scripts/summary.py` for quick identity, CPU/RAM, and uptime.
- `scripts/hardware.py` for deeper CPU, memory, GPU, battery, and uptime details.

## Safety

- Serial numbers are not emitted.
- Output is local-only and does not require outbound network calls.
