---
name: linux-bash-snippets
description: Apply Linux and Bash snippets for packaging ELF dependencies, resilient downloads, and shell troubleshooting. Use when the task is shell-centric, stateless, and needs portable command workflows plus verification and rollback.
---

# Linux Bash Snippets

Use this skill for Linux shell tasks where a short command workflow is the right tool.

## When This Triggers

- User asks for Bash/Linux command snippets.
- Task needs bundling shared libraries for an ELF binary.
- Task needs resilient TOR-backed download commands.
- The workflow is stateless and should run via shell commands.

## When Not To Use

- Requests require persistent service state or typed multi-agent APIs (consider MCP).
- Requests are primarily Python application logic (use `python-utilities`).
- Requests are memory/binary tampering or offensive security (use `lowlevel-security-hacks` and safety review).

## Skill Interface Contract

- Input: user task + environment constraints.
- Output: selected snippet, adapted command(s), prerequisites, risks, verification step, rollback/fallback.

## Index

| Workflow | When To Use | When Not To Use | Platform Constraints |
|---|---|---|---|
| Resilient TOR download | Need anonymous + resumable download retries | No TOR network, compliance forbids anonymizing proxies | Linux with `torsocks` and `wget` installed |
| Copy ELF dependencies from `ldd` | Bundle runtime libraries next to binary | Statically linked binary or container image workflow is preferred | Linux ELF binaries, `ldd`, `awk`, `cp` |

## Procedure

1. Read [references/snippets.md](references/snippets.md) and select the matching workflow.
2. Adapt commands minimally for paths and filenames.
3. Always include:
   - prerequisites check,
   - verification command,
   - rollback/fallback.
4. If uncertainty remains, choose the least destructive command sequence first.

## Verification and Rollback Policy

- Verification must be explicit (for example: `ldd`, `ls`, checksum, or dry-run style checks).
- Rollback must remove only artifacts created by this workflow (for example: `libs/` output dir).

