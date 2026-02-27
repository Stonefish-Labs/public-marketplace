#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Gracefully shutdown WSL before VHDX operations.

.DESCRIPTION
    Stops all running WSL distributions and waits for clean shutdown.
    Must be run before any VHDX compaction operations.

.EXAMPLE
    .\shutdown-wsl.ps1
#>

Write-Host "Shutting down WSL..." -ForegroundColor Yellow

# Check if any WSL distros are running
$running = wsl.exe --list --running 2>$null
if ($LASTEXITCODE -eq 0 -and $running -match '\S') {
    Write-Host "Running distros detected, initiating shutdown..."
    wsl.exe --shutdown
    
    # Wait for shutdown to complete
    $timeout = 30
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        Start-Sleep -Seconds 1
        $elapsed++
        $stillRunning = wsl.exe --list --running 2>$null
        if ($stillRunning -notmatch '\S' -or $stillRunning -match 'no running') {
            Write-Host "WSL shutdown complete." -ForegroundColor Green
            break
        }
        Write-Host "Waiting for shutdown... ($elapsed s)"
    }
    
    if ($elapsed -ge $timeout) {
        Write-Host "Warning: WSL shutdown timed out. Proceeding anyway." -ForegroundColor Red
    }
} else {
    Write-Host "No WSL distros running." -ForegroundColor Green
}

# Additional wait for filesystem sync
Write-Host "Waiting for filesystem sync..."
Start-Sleep -Seconds 5
Write-Host "Ready for VHDX operations." -ForegroundColor Green
