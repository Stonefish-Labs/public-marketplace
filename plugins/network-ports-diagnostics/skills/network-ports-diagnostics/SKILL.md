---
name: network-ports-diagnostics
description: >
  Diagnose local networking state and listening services on macOS, Linux, and
  Windows. Use this for prompts like "show my interfaces", "DNS and gateway",
  "what ports are open", "what is listening on port X", and "network connectivity
  checks". This skill is local-only and does not perform public-IP lookups or any
  external web request. For public IP address detection, use the separate
  `external-ip` skill.
---

# Network and Ports Diagnostics

Run:

- `scripts/network.py` for local interfaces, gateway, DNS, VPN heuristic, and traffic counters.
- `scripts/ports.py` for listening ports and active connection summaries.
