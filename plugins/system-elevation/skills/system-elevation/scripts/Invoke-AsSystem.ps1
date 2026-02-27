function Invoke-AsSystem {
    <#
    .SYNOPSIS
        Execute a command as NT AUTHORITY\SYSTEM using Task Scheduler.
    
    .DESCRIPTION
        Runs a command with SYSTEM privileges by creating a scheduled task,
        executing it immediately, then deleting it. Output is captured to files
        due to Session 0 Isolation (SYSTEM runs in a non-interactive session).
    
    .PARAMETER Command
        The command to execute as SYSTEM.
    
    .PARAMETER OutputDir
        Directory where stdout.txt and stderr.txt will be written.
        Must exist and be writable by SYSTEM (most local paths work).
    
    .PARAMETER WaitSeconds
        Seconds to wait for task completion. Default: 10.
        Increase for long-running commands.
    
    .EXAMPLE
        $result = Invoke-AsSystem -Command "whoami" -OutputDir "C:\temp"
        Get-Content $result.StdoutPath
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        
        [Parameter(Mandatory = $true)]
        [string]$OutputDir,
        
        [Parameter(Mandatory = $false)]
        [int]$WaitSeconds = 10
    )
    
    # Verify running as admin (required to create SYSTEM tasks)
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "Must run from an elevated (Administrator) terminal to create SYSTEM tasks."
    }
    
    # Verify output directory exists
    if (-not (Test-Path $OutputDir -PathType Container)) {
        throw "Output directory does not exist: $OutputDir"
    }
    
    # Generate unique task name
    $taskName = "CursorSystem_$([guid]::NewGuid().ToString('N').Substring(0, 8))"
    
    # Define output file paths
    $stdoutPath = Join-Path $OutputDir "stdout_$taskName.txt"
    $stderrPath = Join-Path $OutputDir "stderr_$taskName.txt"
    $batchPath = Join-Path $OutputDir "cmd_$taskName.cmd"
    
    # Write batch file (schtasks cannot handle > redirection in /tr argument)
    [System.IO.File]::WriteAllText($batchPath, "@echo off`r`n$Command > `"$stdoutPath`" 2> `"$stderrPath`"")
    
    try {
        # Create the scheduled task to run the batch file
        $createResult = & schtasks /create /sc once /st 00:00 /tn $taskName /tr "`"$batchPath`"" /ru SYSTEM /rl HIGHEST /f 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create task: $createResult"
        }
        
        # Run the task immediately
        $runResult = & schtasks /run /tn $taskName 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to run task: $runResult"
        }
        
        # Wait for execution (Session 0 tasks are async)
        Start-Sleep -Seconds $WaitSeconds
        
    }
    finally {
        # Always clean up the task and batch file
        & schtasks /delete /tn $taskName /f 2>&1 | Out-Null
        Remove-Item $batchPath -Force -ErrorAction SilentlyContinue
    }
    
    # Check if output files were created
    $stdoutExists = Test-Path $stdoutPath
    $stderrExists = Test-Path $stderrPath
    
    # Read stderr to check for errors (heuristic since we can't get exit code)
    $hasErrors = $false
    if ($stderrExists) {
        $stderrContent = Get-Content $stderrPath -Raw -ErrorAction SilentlyContinue
        $hasErrors = -not [string]::IsNullOrWhiteSpace($stderrContent)
    }
    
    # Return result object
    return [PSCustomObject]@{
        TaskName    = $taskName
        StdoutPath  = if ($stdoutExists) { $stdoutPath } else { $null }
        StderrPath  = if ($stderrExists) { $stderrPath } else { $null }
        HasErrors   = $hasErrors
        WaitSeconds = $WaitSeconds
    }
}

function Read-SystemOutput {
    <#
    .SYNOPSIS
        Read and optionally delete output files from Invoke-AsSystem.
    
    .PARAMETER Result
        The result object from Invoke-AsSystem.
    
    .PARAMETER DeleteAfterRead
        Remove output files after reading. Default: $true.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [PSCustomObject]$Result,
        
        [Parameter(Mandatory = $false)]
        [bool]$DeleteAfterRead = $true
    )
    
    $output = [PSCustomObject]@{
        Stdout = $null
        Stderr = $null
    }
    
    if ($Result.StdoutPath -and (Test-Path $Result.StdoutPath)) {
        $output.Stdout = Get-Content $Result.StdoutPath -Raw
        if ($DeleteAfterRead) {
            Remove-Item $Result.StdoutPath -Force -ErrorAction SilentlyContinue
        }
    }
    
    if ($Result.StderrPath -and (Test-Path $Result.StderrPath)) {
        $output.Stderr = Get-Content $Result.StderrPath -Raw
        if ($DeleteAfterRead) {
            Remove-Item $Result.StderrPath -Force -ErrorAction SilentlyContinue
        }
    }
    
    return $output
}