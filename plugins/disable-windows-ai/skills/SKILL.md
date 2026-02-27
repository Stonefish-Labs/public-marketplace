---
name: disable-windows-ai
description: Disable Windows 11 AI features including Copilot, Recall, AI in Paint/Notepad/Edge, typing data harvesting, and more. When user mentions disabling Copilot, Recall, Windows AI, or Microsoft AI features, present the available options and ask which to disable.
---

# Disable Windows AI Features

Comprehensive tool to nuke Microsoft's AI infestation from Windows 11. Based on [zoicware/RemoveWindowsAI](https://github.com/zoicware/RemoveWindowsAI).

## How to Run Scripts (IMPORTANT - Elevation Required)

These scripts require Administrator privileges. **Always use this pattern to run them:**

```powershell
# This prompts the user for UAC elevation and runs the script in an elevated window
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -Command "& ''SCRIPT_PATH'' SWITCHES"'
```

**Examples:**

```powershell
# Disable ALL AI features (prompts for admin)
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -Command "& ''<SKILL_PATH>\scripts\disable-windows-ai.ps1'' -All"'

# Disable just Copilot and Edge
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -Command "& ''<SKILL_PATH>\scripts\disable-windows-ai.ps1'' -Copilot -Edge"'

# Re-enable everything
Start-Process powershell -Verb RunAs -ArgumentList '-NoExit -ExecutionPolicy Bypass -Command "& ''<SKILL_PATH>\scripts\enable-windows-ai.ps1'' -All"'
```

The `-NoExit` flag keeps the window open so the user can see the output.

**Check status (no elevation needed):**
```powershell
powershell -ExecutionPolicy Bypass -File "<SKILL_PATH>\scripts\check-windows-ai-status.ps1"
```

## When User Asks About Disabling AI

When the user mentions disabling Copilot, Recall, or any Windows AI features, **present these options and ask which they want disabled:**

### 🎯 Available Features to Disable

| Category | Feature | What It Does |
|----------|---------|--------------|
| **Copilot** | Windows Copilot | The main AI assistant popup, taskbar button, system tray |
| **Copilot** | Copilot in Edge | Sidebar, page context sharing, AI compose, browsing history sharing |
| **Copilot** | Copilot in Search | AI suggestions in Windows Search, "Ask Copilot" button |
| **Copilot** | Copilot Key | Hardware Copilot key remapping (if you have that cursed keyboard) |
| **Copilot** | Copilot Nudges | Those annoying "try Copilot" popups |
| **Recall** | Windows Recall | Screenshot surveillance that captures everything you do |
| **Recall** | Recall Tasks | Scheduled tasks that keep Recall running |
| **Recall** | Click-to-Do | AI actions from Recall screenshots |
| **Paint** | Image Creator | AI image generation in Paint |
| **Paint** | Cocreator | AI-assisted drawing |
| **Paint** | Generative Fill/Erase | AI fill and background removal |
| **Notepad** | Rewrite | AI rewriting suggestions in Notepad |
| **Office** | Office AI Training | Microsoft harvesting your documents to train AI |
| **Input** | Input Insights | Typing pattern analysis |
| **Input** | Typing Data Harvesting | Sending what you type to Microsoft |
| **Voice** | Voice Access AI | AI-powered voice features |
| **Voice** | AI Voice Effects | NPU-powered voice processing |
| **Settings** | AI in Settings Search | AI-powered settings recommendations |
| **Settings** | Settings Agent | AI that "helps" configure your PC |
| **System** | AI Components | Hidden AI packages and services |
| **System** | Generative AI Access | Apps accessing local AI models |

### 🔥 Quick Options

- **"Nuke Everything"** - Disable ALL AI features listed above
- **"Just Copilot"** - Disable Copilot everywhere (Windows, Edge, Search, taskbar)
- **"Just Recall"** - Disable Recall and related surveillance
- **"Custom"** - Pick specific features to disable

## Requirements

- Windows 11 (any edition, Pro/Enterprise/Education recommended)
- **Administrator privileges required** for most operations
- Some features require TrustedInstaller for complete removal

## Scripts

All scripts in `scripts/` directory.

### Disable AI Features

**Run as Administrator:**
```powershell
# Disable everything (interactive prompts)
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1

# Disable everything without prompts
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -All

# Disable specific categories
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Copilot
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Recall
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Paint
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Notepad
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Edge
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Typing
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Office

# Combine multiple
powershell -ExecutionPolicy Bypass -File scripts/disable-windows-ai.ps1 -Copilot -Recall -Edge
```

### Re-enable AI Features

```powershell
# Revert everything
powershell -ExecutionPolicy Bypass -File scripts/enable-windows-ai.ps1 -All

# Revert specific categories
powershell -ExecutionPolicy Bypass -File scripts/enable-windows-ai.ps1 -Copilot
```

### Check Status

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-windows-ai-status.ps1
```

## Quick One-Liners (Elevated CMD/PowerShell)

**Kill Copilot completely:**
```cmd
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f && reg add "HKCU\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f && reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v IsCopilotAvailable /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v CopilotDisabledReason /t REG_SZ /d "FeatureIsDisabled" /f
```

**Kill Recall:**
```cmd
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v DisableAIDataAnalysis /t REG_DWORD /d 1 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v AllowRecallEnablement /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v TurnOffSavingSnapshots /t REG_DWORD /d 1 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v DisableClickToDo /t REG_DWORD /d 1 /f
```

**Kill Copilot in Edge:**
```cmd
reg add "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v HubsSidebarEnabled /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v CopilotPageContext /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v ComposeInlineEnabled /t REG_DWORD /d 0 /f && reg add "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v ShareBrowsingHistoryWithCopilotSearchAllowed /t REG_DWORD /d 0 /f
```

**Kill AI in Paint:**
```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint" /v DisableImageCreator /t REG_DWORD /d 1 /f && reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint" /v DisableCocreator /t REG_DWORD /d 1 /f && reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint" /v DisableGenerativeFill /t REG_DWORD /d 1 /f && reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint" /v DisableGenerativeErase /t REG_DWORD /d 1 /f
```

## Elevation Notes

The scripts in this skill modify HKLM registry keys and system policies, which require Administrator privileges.

**Key point:** When running via `Start-Process -Verb RunAs`, the elevated process runs in a separate window. The AI assistant cannot see output from elevated processes, so `-NoExit` is used to keep the window open for the user to see results.

After running disable/enable scripts, always run the status check (which doesn't need elevation) to verify the changes took effect.

## Notes

- Changes take effect after Explorer restart or logout
- Windows Updates may re-enable some features - run again after major updates
- Some features require removing AppX packages for complete removal (use full RemoveWindowsAI script)
- Home edition lacks some Group Policy support but registry methods still work
- For complete removal including CBS packages, use the full [RemoveWindowsAI](https://github.com/zoicware/RemoveWindowsAI) script

## Why This Matters

Microsoft is cramming AI into every corner of Windows 11:
- **Copilot** watches what you're doing and "helps" (harvests data)
- **Recall** literally screenshots your entire computer usage
- **Input Insights** analyzes your typing patterns
- **Edge Copilot** reads your browser content
- **AI in apps** means your data goes to Microsoft's servers

This skill helps you reclaim your privacy.
