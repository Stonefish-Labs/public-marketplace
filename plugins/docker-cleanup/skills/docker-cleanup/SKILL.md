---
name: docker-cleanup
description: Clean up Docker environments - compact WSL2 VHDX on Windows, controlled pruning of images/containers/volumes, export and document containers before removal. Use when the user mentions Docker cleanup, disk space, VHDX, dangling images, or wants to archive containers.
---

# Docker Cleanup

Maintain a tidy Docker environment across Windows, macOS, and Linux.

## Platform Detection

Detect OS first:
- **Windows**: Prune Docker first, then compact WSL2 VHDX to reclaim space
- **macOS/Linux**: Prune Docker, then restart Docker Desktop (macOS) to reclaim disk

## Controlled Prune

Always show what will be removed and ask for confirmation. **Do this BEFORE compacting VHDX.**

### Step 1: Survey the Damage

```bash
docker system df
```

### Step 2: List Candidates

**Dangling images** (untagged, unused):
```bash
docker images -f "dangling=true" --format "{{.ID}}\t{{.Size}}\t{{.CreatedSince}}"
```

**Stopped containers**:
```bash
docker ps -a -f "status=exited" --format "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"
```

**Unused volumes**:
```bash
docker volume ls -f "dangling=true" --format "{{.Name}}\t{{.Driver}}"
```

**Build cache**:
```bash
docker builder prune --dry-run
```

### Step 3: Ask User Per Category

Present each category with sizes. Ask:
1. Remove dangling images? (y/n)
2. Remove stopped containers? (y/n/select specific)
3. Remove unused volumes? (y/n) - **warn about data loss**
4. Clear build cache? (y/n)

### Step 4: Execute Selected Cleanup

```bash
# Dangling images only
docker image prune -f

# Stopped containers
docker container prune -f

# Unused volumes (careful!)
docker volume prune -f

# Build cache
docker builder prune -f

# Or nuclear option (with confirmation):
docker system prune -a --volumes
```

## Windows VHDX Compaction

Docker Desktop on Windows uses WSL2 with a virtual disk (`ext4.vhdx`) that grows but doesn't shrink automatically. **Run this AFTER pruning** to reclaim the freed space.

### Step 0: Elevate to Admin

Compaction requires administrator privileges. Use inline sudo for agent-visible output.

**If Windows 11 sudo (inline mode) is enabled:**
```powershell
sudo powershell -Command "wsl.exe --shutdown; Start-Sleep 5; Optimize-VHD -Path '$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx' -Mode Full"
```

**If using gsudo:**
```powershell
gsudo powershell -Command "wsl.exe --shutdown; Start-Sleep 5; Optimize-VHD -Path '$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx' -Mode Full"
```

**Fallback (opens new window, agent loses output):**
```powershell
Start-Process powershell -Verb RunAs -ArgumentList "-Command `"wsl.exe --shutdown; Start-Sleep 5; Optimize-VHD -Path '$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx' -Mode Full`"" -Wait
```

See the `windows-elevation` skill for setup.

### Step 1: Check Current Size

```powershell
$vhdxPaths = @(
    "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx",
    "$env:LOCALAPPDATA\Docker\wsl\main\ext4.vhdx"
)
foreach ($path in $vhdxPaths) {
    if (Test-Path $path) {
        $file = Get-Item $path -Force
        $sizeGB = [math]::Round($file.Length / 1GB, 2)
        Write-Output "$path : $sizeGB GB (Modified: $($file.LastWriteTime))"
    } else {
        Write-Output "$path : NOT FOUND"
    }
}
```

### Step 2: Shutdown WSL

Run in admin PowerShell:
```powershell
wsl.exe --shutdown
```

Wait 5 seconds for clean shutdown.

### Step 3: Compact (Try Optimize-VHD First)

Requires Hyper-V feature enabled:
```powershell
Optimize-VHD -Path "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx" -Mode Full
```

If Optimize-VHD fails (Hyper-V not available), use diskpart fallback:
```powershell
# Create diskpart script
$vhdxPath = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
@"
select vdisk file="$vhdxPath"
compact vdisk
detach vdisk
"@ | diskpart
```

### Step 4: Verify Size Reduction

```powershell
$vhdxPaths = @(
    "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx",
    "$env:LOCALAPPDATA\Docker\wsl\main\ext4.vhdx"
)
foreach ($path in $vhdxPaths) {
    if (Test-Path $path) {
        $sizeGB = [math]::Round((Get-Item $path -Force).Length / 1GB, 2)
        Write-Output "$path : $sizeGB GB"
    }
}
```

## macOS Disk Reclaim

Docker Desktop on macOS uses `Docker.raw` instead of VHDX. To reclaim space:
1. Run the prune commands above
2. Open Docker Desktop > Settings > Resources > Apply & Restart

The VM disk doesn't auto-shrink, so restart is required after pruning.

## Export and Document

Before removing a container or image, offer to export and document it.

### Export Container

```bash
# Export container filesystem
docker export <container_id> | gzip > container_backup.tar.gz

# Or commit to image first (preserves layers)
docker commit <container_id> backup_image:latest
docker save backup_image:latest | gzip > image_backup.tar.gz
```

### Export Image

```bash
docker save <image_name> | gzip > image_backup.tar.gz
```

### Generate Documentation

Extract configuration with `docker inspect` and generate either:

1. **Markdown notes** with run command
2. **docker-compose.yml** snippet

See [reference.md](references/reference.md) for templates.

## Additional Resources

- For detailed command reference, see [reference.md](references/reference.md)
- Platform scripts in `scripts/` directory
