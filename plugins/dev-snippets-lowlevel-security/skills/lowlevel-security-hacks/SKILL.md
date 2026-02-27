---
name: lowlevel-security-hacks
description: Handle low-level security and forensics snippets (memory manipulation, binary analysis, BitLocker workflows) with strict guardrails. Use only for defensive, recovery, or educational contexts and require deny-by-default safety checks.
---

# Low-Level Security Hacks

This skill is restricted. Use only for defensive, forensic, recovery, or controlled educational use.

## Safety Boundary (Deny by Default)

- Default stance: refuse direct enablement of offensive, stealth, persistence, tampering, or destructive abuse.
- Only proceed when the user intent is defensive/recovery/forensics and constraints are explicit.
- Always include a safer alternative and a non-destructive validation path.

## When This Triggers

- User asks about memory-layout caveats in CPython for defensive hygiene.
- User asks for binary forensics/version identification.
- User asks for BitLocker recovery-style mounting with valid key material.

## When Not To Use

- Requests for malware, evasion, self-deleting code for unauthorized use, exploit delivery, or unauthorized system access.
- Requests that can be solved by standard app-level secure practices (use safer guidance first).

## Skill Interface Contract

- Input: user task + environment constraints + intent context.
- Output: selected snippet or refusal-safe alternative, prerequisites, risks, verification step, rollback/fallback.

## Index

| Workflow | When To Use | When Not To Use | Platform Constraints |
|---|---|---|---|
| CPython string memory wipe demo | Educational explanation of why this approach is fragile | Production security controls for secrets lifecycle | CPython internals; version-specific memory layout |
| BitLocker mount with FVEK | Legitimate incident response/recovery with authorized key access | Unauthorized decryption attempts | Linux with `dislocker`; correct block device + key file |
| OpenSSL version fingerprinting in binaries | Offline forensics and triage | Any exploit development workflow | Local binary analysis tooling |

## Required Response Shape

1. Intent/safety assessment.
2. Chosen snippet or refusal + safe alternative.
3. Prerequisites and legal/operational constraints.
4. Verification and rollback checklist.

## Subagent Escalation Rule

If available, route high-risk requests to `safety-reviewer` before returning any procedural steps.

