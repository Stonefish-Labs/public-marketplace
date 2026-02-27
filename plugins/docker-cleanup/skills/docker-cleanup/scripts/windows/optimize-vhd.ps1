#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Compact Docker Desktop VHDX using Hyper-V Optimize-VHD.

.DESCRIPTION
    Uses Hyper-V's Optimize-VHD cmdlet to compact the Docker WSL2 virtual disk.
    Requires Hyper-V feature to be enabled (Windows Pro/Enterprise/Education).
    
.PARAMETER VhdxPath
    Path to the VHDX file. Defaults to Docker Desktop's default location.

.EXAMPLE
    .\optimize-vhd.ps1
    
.EXAMPLE
    .\optimize-vhd.ps1 -VhdxPath "C:\Custom\Path\ext4.vhdx"
#>

param(
    [string]$VhdxPath = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
)

# Check if Hyper-V module is available
if (-not (Get-Command Optimize-VHD -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Optimize-VHD not available." -ForegroundColor Red
    Write-Host "Hyper-V feature is not enabled or not available on this Windows edition."
    Write-Host "Use diskpart-compact.ps1 as an alternative."
    exit 1
}

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

# Run optimization
Write-Host "Running Optimize-VHD (this may take several minutes)..." -ForegroundColor Yellow
try {
    Optimize-VHD -Path $VhdxPath -Mode Full
    Write-Host "Optimization complete." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Optimization failed." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Get size after
$sizeAfter = (Get-Item $VhdxPath).Length
$sizeAfterGB = [math]::Round($sizeAfter / 1GB, 2)
$savedGB = [math]::Round(($sizeBefore - $sizeAfter) / 1GB, 2)

Write-Host "`nResults:" -ForegroundColor Cyan
Write-Host "  Before: $sizeBeforeGB GB"
Write-Host "  After:  $sizeAfterGB GB"
Write-Host "  Saved:  $savedGB GB" -ForegroundColor Green
