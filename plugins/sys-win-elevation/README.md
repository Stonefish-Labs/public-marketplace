# Windows Elevation Skill

Run admin commands on Windows while keeping stdout/stderr visible for AI agents.

## The Problem

Standard elevation (`Start-Process -Verb RunAs`) opens a new window, breaking the output stream. Agents see nothing.

## The Solution

Windows 11 24H2+ has native `sudo`. Configure **inline mode** to keep output in the current terminal.

## Installation

```bash
# Cursor
cp -r windows-elevation ~/.cursor/skills/

# Claude Code
cp -r windows-elevation ~/.claude/skills/

# Codex
cp -r windows-elevation ~/.codex/skills/

# Roo
cp -r windows-elevation ~/.roo/skills/
```

## Setup

Enable inline sudo (Windows 11 24H2+):
```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Sudo" /v Enabled /t REG_DWORD /d 3 /f
```

Or install gsudo for older Windows:
```powershell
winget install gsudo
```

## Usage

```powershell
sudo Optimize-VHD -Path "C:\path\to\disk.vhdx" -Mode Full
```

UAC prompt appears, user clicks Yes, output streams back to agent.

## License

MIT
