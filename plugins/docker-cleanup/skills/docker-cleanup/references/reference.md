# Docker Cleanup Reference

Detailed command reference and templates for each platform.

## Windows Commands

### VHDX Locations

Default Docker Desktop path:
```
%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx
```

Alternative WSL distro paths:
```
%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu*\LocalState\ext4.vhdx
```

### Check VHDX Size

```powershell
$vhdx = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
$size = (Get-Item $vhdx).Length
Write-Host "VHDX Size: $([math]::Round($size / 1GB, 2)) GB"
```

### WSL Shutdown

Must run before any VHDX operations:
```powershell
wsl.exe --shutdown
# Verify all distros stopped
wsl.exe --list --running
```

### Optimize-VHD (Hyper-V Method)

Requires:
- Windows Pro/Enterprise/Education
- Hyper-V feature enabled
- Admin privileges

```powershell
# Check if Hyper-V is available
Get-Command Optimize-VHD -ErrorAction SilentlyContinue

# Run optimization
$vhdx = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"
Optimize-VHD -Path $vhdx -Mode Full
```

### Diskpart Method (Fallback)

Works on Windows Home, no Hyper-V needed:
```powershell
$vhdx = "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx"

# Create temp script
$scriptPath = "$env:TEMP\compact-vhdx.txt"
@"
select vdisk file="$vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
"@ | Out-File -FilePath $scriptPath -Encoding ASCII

# Run diskpart (requires admin)
diskpart /s $scriptPath

# Cleanup
Remove-Item $scriptPath
```

## macOS Commands

### Docker Desktop VM

macOS uses a different virtualization. Disk reclaim options:

1. **Docker Desktop Settings** > Resources > Disk image size
2. **Factory Reset** (nuclear option)

Check disk usage:
```bash
ls -lh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw
```

### Reclaim Space

```bash
# Prune everything first
docker system prune -a --volumes

# Then in Docker Desktop: Settings > Resources > "Apply & Restart"
```

## Linux Commands

### Check Docker Disk Usage

```bash
# Overlay storage location
du -sh /var/lib/docker/

# Detailed breakdown
docker system df -v
```

### Direct Cleanup

```bash
# Remove all stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes (DATA LOSS WARNING)
docker volume prune -f

# Remove build cache
docker builder prune -f

# Everything at once
docker system prune -a --volumes -f
```

## Export Templates

### Generate docker run Command

Extract from inspect and format:

```bash
docker inspect <container> --format '
docker run -d \
  --name {{.Name}} \
  {{range $k, $v := .Config.Env}}-e "{{$v}}" \
  {{end}}{{range $k, $v := .HostConfig.PortBindings}}{{range $v}}-p {{.HostPort}}:{{$k}} \
  {{end}}{{end}}{{range .HostConfig.Binds}}-v {{.}} \
  {{end}}{{.Config.Image}}'
```

### Generate docker-compose.yml

Template for extracted container config:

```yaml
version: "3.8"
services:
  <service_name>:
    image: <image_name>
    container_name: <container_name>
    restart: unless-stopped
    ports:
      - "<host_port>:<container_port>"
    volumes:
      - "<host_path>:<container_path>"
    environment:
      - KEY=value
    networks:
      - default
```

### Export Documentation Template

When exporting a container, create a markdown file:

```markdown
# Container Export: <container_name>

**Exported**: <date>
**Original Image**: <image_name>
**Export File**: <filename>.tar.gz

## Original Configuration

### Ports
- 8080:80 (HTTP)
- 443:443 (HTTPS)

### Volumes
- /data:/app/data
- config:/app/config

### Environment Variables
- DATABASE_URL=...
- API_KEY=...

## Restore Instructions

### From Image Export
\`\`\`bash
gunzip -c image_backup.tar.gz | docker load
docker run -d --name <name> <restored_image>
\`\`\`

### From Container Export
\`\`\`bash
gunzip -c container_backup.tar.gz | docker import - restored_image:latest
docker run -d --name <name> restored_image:latest
\`\`\`

## Docker Compose

\`\`\`yaml
version: "3.8"
services:
  <service>:
    image: <image>
    # ... full config ...
\`\`\`
```

## Prune Filters

### By Age

Remove images older than 24 hours:
```bash
docker image prune -a --filter "until=24h"
```

### By Label

Keep labeled containers:
```bash
docker container prune --filter "label!=keep"
```

### Dry Run

Preview what would be removed:
```bash
docker system prune --dry-run
docker builder prune --dry-run
```
