---
name: system-elevation
description: Execute commands as NT AUTHORITY\SYSTEM (highest Windows privilege) using Task Scheduler. Use when admin elevation is insufficient, or when true SYSTEM-level access is needed for registry, services, or protected operations.
---

# SYSTEM Elevation

Run commands as `NT AUTHORITY\SYSTEM` - the highest privilege level on Windows. This is above Administrator.

## When to Use

- Admin elevation (`sudo`/`gsudo`) isn't enough
- Need to modify protected registry keys
- Need to access SYSTEM-only resources
- Working with Windows services at the deepest level

## The Catch: Session 0 Isolation

SYSTEM runs in Session 0, which has no connection to your desktop. You **cannot** see output directly - it must be written to files that you then read.

## Prerequisites

- Must run from an **Administrator** terminal
- Output directory must exist before running

## Usage

### Step 1: Load the function

```powershell
. scripts/Invoke-AsSystem.ps1
```

### Step 2: Run command as SYSTEM

```powershell
$result = Invoke-AsSystem -Command "whoami" -OutputDir "C:\temp"
```

Parameters:
- `-Command` - What to run (required)
- `-OutputDir` - Where to write stdout/stderr files (required)
- `-WaitSeconds` - How long to wait for completion (default: 10)

### Step 3: Read output and clean up

```powershell
$output = Read-SystemOutput -Result $result
$output.Stdout   # The command's stdout
$output.Stderr   # The command's stderr (if any)
```

`Read-SystemOutput` auto-deletes the files after reading by default.

## Complete Example

```powershell
# Load functions
. scripts/Invoke-AsSystem.ps1

# Run whoami as SYSTEM
$result = Invoke-AsSystem -Command "whoami" -OutputDir $env:TEMP

# Read and display output
$output = Read-SystemOutput -Result $result
Write-Output "SYSTEM identity: $($output.Stdout)"
# Expected: nt authority\system
```

## Running Scripts

For multi-line operations, write a script file first:

```powershell
# Create script
$script = @'
whoami
hostname
ipconfig /all
'@
$script | Out-File "C:\temp\sysscript.cmd" -Encoding ASCII

# Run it as SYSTEM
$result = Invoke-AsSystem -Command "C:\temp\sysscript.cmd" -OutputDir "C:\temp" -WaitSeconds 15

# Get results
$output = Read-SystemOutput -Result $result
$output.Stdout
```

## Limitations

1. **No interactive commands** - Can't run anything requiring user input
2. **No GUI** - Session 0 cannot display windows on your desktop
3. **Async execution** - Task runs in background; increase `-WaitSeconds` for slow commands
4. **No direct exit code** - Check `$result.HasErrors` (true if stderr has content)
5. **Network paths may fail** - SYSTEM may not have access to mapped drives or network shares

## Error Handling

```powershell
$result = Invoke-AsSystem -Command "some-command" -OutputDir "C:\temp"
$output = Read-SystemOutput -Result $result

if ($result.HasErrors) {
    Write-Warning "Command produced errors:"
    Write-Warning $output.Stderr
}
```

## Comparison with Admin Elevation

| Feature | sudo/gsudo (Admin) | Invoke-AsSystem |
|---------|-------------------|-----------------|
| Privilege level | Administrator | NT AUTHORITY\SYSTEM |
| Output visibility | Direct (inline) | File-based |
| Interactive | Yes | No |
| GUI possible | Yes | No |
| Use case | Most admin tasks | Deep system access |

**Use admin elevation first.** Only use SYSTEM when admin isn't enough.
