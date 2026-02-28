# System Elevation

Execute commands as `NT AUTHORITY\SYSTEM` — the highest privilege level on Windows, above Administrator.

## ⚠️ Warning

**This is a dangerous skill.** SYSTEM privileges can modify anything on the machine — registry, services, protected files, security policies. 

- **Do not install globally.** Only enable when actively needed.
- **Watch your agents.** Review what commands are being executed.
- **Audit after use.** Check what changes were made to your system.

## Overview

This skill enables AI agents to run commands with SYSTEM-level privileges on Windows using Task Scheduler. Use it when admin elevation isn't enough — for modifying protected registry keys, accessing SYSTEM-only resources, or performing deep Windows service manipulation.

## Usage

Trigger phrases:
- "run as SYSTEM"
- "need SYSTEM privileges"
- "admin elevation isn't enough"
- "highest Windows privilege"

The skill uses Windows Task Scheduler to execute commands as SYSTEM. Output is captured via files due to Session 0 Isolation (SYSTEM runs in a non-interactive session).

## Requirements

- Windows operating system
- Administrator terminal (required to create SYSTEM tasks)
- PowerShell 5.1+

## License

MIT
