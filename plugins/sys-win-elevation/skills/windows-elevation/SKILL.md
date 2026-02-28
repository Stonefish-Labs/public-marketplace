---
name: windows-elevation
description: Run elevated (admin) commands on Windows while preserving stdout/stderr visibility for AI agents. Uses Windows 11 native sudo in inline mode, with gsudo fallback for older systems.
---

# Windows Process Elevation

Run administrator commands without losing output visibility. Essential for AI agents that need to see command results.

## The Problem

Standard elevation methods (`Start-Process -Verb RunAs`, `Optimize-VHD`, etc.) open a new window, breaking the stdout/stderr connection. The agent sees nothing.

## Solution: Inline Sudo

Windows 11 24H2+ has native `sudo`. Configure it for **inline mode** to keep output in the current terminal.

### Step 1: Enable Inline Sudo

**Option A: Via Settings UI**
1. Open **Settings** > **System** > **For Developers**
2. Toggle **Enable Sudo** to **On**
3. Change dropdown to **"Inline"** (not "In a new window")

**Option B: Via Registry**
```powershell
# Set inline mode (value 3 = inline)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Sudo" /v Enabled /t REG_DWORD /d 3 /f
```

**Option C: Via elevated terminal**
```powershell
sudo config --enable normal
```

### Step 2: Verify Setup

```powershell
sudo whoami
```

Should return `nt authority\system` or your admin account **in the same terminal** (no new window).

## Usage

Once configured, prefix any admin command with `sudo`:

```powershell
# Single command
sudo Optimize-VHD -Path "C:\path\to\disk.vhdx" -Mode Full

# Multi-command (wrap in powershell -Command)
sudo powershell -Command "wsl.exe --shutdown; Start-Sleep 5; Optimize-VHD -Path '$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx' -Mode Full"
```

The UAC prompt appears on user's screen. After clicking "Yes", output streams to the agent.

## Fallback: gsudo (Windows 10 / older Win11)

If native sudo isn't available (requires Windows 11 Build 26052+ / Version 24H2):

**Install:**
```powershell
winget install gsudo
```

**Use:**
```powershell
gsudo powershell -Command "your-admin-command-here"
```

Behaves identically to native inline sudo.

## Detection Script

Check which elevation method is available:

```powershell
function Get-ElevationMethod {
    # Check for native sudo with inline mode
    $sudoReg = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Sudo" -ErrorAction SilentlyContinue
    if ($sudoReg.Enabled -eq 3) {
        return "sudo"
    }
    
    # Check for gsudo
    if (Get-Command gsudo -ErrorAction SilentlyContinue) {
        return "gsudo"
    }
    
    # Fallback - no inline elevation available
    return $null
}

$method = Get-ElevationMethod
if ($method) {
    Write-Output "Elevation method available: $method"
} else {
    Write-Output "No inline elevation available. Enable sudo or install gsudo."
}
```

## Agent Integration

Before running elevated commands, check and use the appropriate method:

```powershell
$elevate = Get-ElevationMethod
if (-not $elevate) {
    Write-Error "No elevation method available. Enable Windows sudo (inline mode) or install gsudo."
    exit 1
}

# Run elevated command with output capture
& $elevate powershell -Command "your-admin-command"
```

## References

- [Enable Sudo on Windows 11](https://www.youtube.com/watch?v=eKjh5bvlA6E)
- [gsudo on GitHub](https://github.com/gerardog/gsudo)
