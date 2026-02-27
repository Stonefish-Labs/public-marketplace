# Disable Windows AI

Comprehensive tool to disable Microsoft's AI features in Windows 11 including Copilot, Recall, AI in Paint/Notepad/Edge, typing data harvesting, and more.

## Overview

This skill provides PowerShell scripts to disable Windows 11's AI features through registry modifications. Based on [zoicware/RemoveWindowsAI](https://github.com/zoicware/RemoveWindowsAI).

## Usage

### Disable AI Features

```powershell
# Disable all AI features (requires admin)
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -Command "& ''<SKILL_PATH>\scripts\disable-windows-ai.ps1'' -All"'

# Disable specific features
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Copilot -Recall -Edge
```

### Available Switches

- `-All` - Disable everything
- `-Copilot` - Windows Copilot (taskbar, search, system tray)
- `-Recall` - Screenshot surveillance
- `-Edge` - Copilot in Edge
- `-Paint` - AI in Paint
- `-Notepad` - Rewrite AI
- `-Typing` - Typing data harvesting
- `-Office` - Office AI training
- `-Voice` - Voice AI features

### Check Status

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-windows-ai-status.ps1
```

### Re-enable Features

```powershell
powershell -ExecutionPolicy Bypass -File scripts/enable-windows-ai.ps1 -All
```

## Requirements

- Windows 11 (any edition)
- Administrator privileges for disable/enable operations

## License

MIT
