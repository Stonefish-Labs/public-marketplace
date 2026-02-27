#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Compact Docker Desktop VHDX using diskpart (fallback method).

.DESCRIPTION
    Uses Windows diskpart utility to compact the Docker WSL2 virtual disk.
    Works on Windows Home and systems without Hyper-V.
    
.PARAMETER VhdxPath
    Path to the VHDX file. Defaults to Docker Desktop's default location.

.EXAMPLE
    .\diskpart-compact.ps1
    
.EXAMPLE
    .\diskpart-compact.ps1 -VhdxPath "C:\Custom\Path\ext4.vhdx"
#>

param(
    [string]$VhdxPath = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
)

# Check if VHDX exists
if (-not (Test-Path $VhdxPath)) {
    Write-Host "ERROR: VHDX not found at: $VhdxPath" -ForegroundColor Red
    Write-Host "Check if Docker Desktop is installed and using WSL2 backend."
    exit 1
}

# Get size before
$sizeBefore = (Get-Item $VhdxPath).Length
$sizeBeforeGB = [math]::Round($sizeBefore / 1GB, 2)
Write-Host "VHDX size before: $sizeBeforeGB GB" -ForegroundColor Cyan

# Create diskpart script
$scriptPath = "$env:TEMP\docker-compact-vhdx.txt"
$diskpartScript = @"
select vdisk file="$VhdxPath"
attach vdisk readonly
compact vdisk
detach vdisk
"@

Write-Host "Creating diskpart script..." -ForegroundColor Yellow
$diskpartScript | Out-File -FilePath $scriptPath -Encoding ASCII

# Run diskpart
Write-Host "Running diskpart (this may take several minutes)..." -ForegroundColor Yellow
Write-Host "Script contents:"
Write-Host $diskpartScript -ForegroundColor DarkGray

try {
    $output = diskpart /s $scriptPath 2>&1
    Write-Host $output
    
    if ($LASTEXITCODE -ne 0) {
        throw "Diskpart returned exit code $LASTEXITCODE"
    }
    Write-Host "Compaction complete." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Diskpart failed." -ForegroundColor Red
    Write-Host $_.Exception.Message
    # Cleanup
    Remove-Item $scriptPath -ErrorAction SilentlyContinue
    exit 1
}

# Cleanup temp script
Remove-Item $scriptPath -ErrorAction SilentlyContinue

# Get size after
$sizeAfter = (Get-Item $VhdxPath).Length
$sizeAfterGB = [math]::Round($sizeAfter / 1GB, 2)
$savedGB = [math]::Round(($sizeBefore - $sizeAfter) / 1GB, 2)

Write-Host "`nResults:" -ForegroundColor Cyan
Write-Host "  Before: $sizeBeforeGB GB"
Write-Host "  After:  $sizeAfterGB GB"
Write-Host "  Saved:  $savedGB GB" -ForegroundColor Green
