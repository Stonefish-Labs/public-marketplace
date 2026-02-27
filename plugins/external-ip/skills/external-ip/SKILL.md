---
name: external-ip
description: >
  Determine the machine's public internet IP address when users explicitly ask
  "what is my public IP", "external IP", "WAN IP", or "egress IP". This skill
  performs outbound HTTPS requests to third-party IP reflector services and should
  be treated as intentional network egress. Use only when public-IP information is
  specifically requested; for local interface, gateway, or DNS checks use
  `network-ports-diagnostics` instead.
---

# External IP

Run `scripts/external_ip.py`.

## Safety

- This script calls external services over HTTPS.
- Use only on explicit user request for public IP data.
