---
name: python-utilities
description: Use Python snippets for system keyring secret storage, HTML-to-Markdown conversion, and sync/async compatibility wrappers. Use for Python-first utility logic with explicit caveats, validation, and fallback guidance.
---

# Python Utilities

Use this skill for Python utility tasks that are local, reusable, and mostly stateless.

## When This Triggers

- User asks for secure credential storage in Python.
- User needs HTML converted to Markdown in-memory.
- User needs async function compatibility across sync and async callers.

## When Not To Use

- Task is primarily shell operations (`linux-bash-snippets`).
- Task involves binary tampering, memory poking, or offensive techniques (`lowlevel-security-hacks` with safety review).
- Requirement is multi-agent shared state with strict typed runtime APIs (consider MCP).

## Skill Interface Contract

- Input: user task + environment constraints.
- Output: selected snippet, adapted code, prerequisites, risks, verification step, rollback/fallback.

## Index

| Workflow | When To Use | When Not To Use | Platform Constraints |
|---|---|---|---|
| System keyring secret storage | Need OS-native secure storage for token/password material | Cross-host non-interactive secrets sync is required | macOS Keychain, Windows Credential Manager, Linux `libsecret` |
| HTML to Markdown (memory-only) | Need conversion without temp files | Need full browser rendering or JS-heavy page execution | Python env with `markitdown[all]` |
| Sync/async compatible decorator | Need one callable API from sync and async contexts | High-throughput async paths where thread-per-call overhead is unacceptable | Python `asyncio`, thread support |

## Procedure

1. Read [references/utilities.md](references/utilities.md).
2. Choose the smallest snippet that solves the task.
3. Include caveats for platform/runtime behavior.
4. Add a verification step and a fallback option.

## Output Requirements

Every response from this skill must include:
- prerequisites,
- caveats,
- one validation command or assertion,
- rollback/fallback guidance.

