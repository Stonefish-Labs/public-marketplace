#!/bin/bash
#
# Docker Prune Report - macOS
# Generates a comprehensive report of Docker resources that can be cleaned up.
# Includes macOS-specific Docker Desktop information.
#

set -e

echo "=========================================="
echo "Docker Cleanup Report - macOS - $(date)"
echo "=========================================="
echo ""

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# macOS-specific: Docker Desktop VM disk
echo "=== DOCKER DESKTOP VM DISK ==="
DOCKER_RAW="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
if [ -f "$DOCKER_RAW" ]; then
    size=$(ls -lh "$DOCKER_RAW" | awk '{print $5}')
    echo "Docker.raw size: $size"
    echo "Location: $DOCKER_RAW"
    echo ""
    echo "Note: To reclaim VM disk space on macOS:"
    echo "  1. Run 'docker system prune -a --volumes'"
    echo "  2. Open Docker Desktop > Settings > Resources"
    echo "  3. Reduce 'Disk image size' or click 'Apply & Restart'"
else
    echo "Docker.raw not found at expected location."
    echo "Docker Desktop may be using a different storage backend."
fi
echo ""

# Overall disk usage
echo "=== DISK USAGE SUMMARY ==="
docker system df
echo ""

# Dangling images
echo "=== DANGLING IMAGES (untagged, safe to remove) ==="
dangling=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$dangling" -gt 0 ]; then
    docker images -f "dangling=true" --format "table {{.ID}}\t{{.Size}}\t{{.CreatedSince}}"
    echo ""
    echo "Remove with: docker image prune -f"
else
    echo "None found."
fi
echo ""

# Unused images
echo "=== UNUSED IMAGES (not used by any container) ==="
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}" | head -20
echo "(showing first 20)"
echo ""
echo "Remove all unused with: docker image prune -a -f"
echo ""

# Stopped containers
echo "=== STOPPED CONTAINERS ==="
stopped=$(docker ps -a -f "status=exited" -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$stopped" -gt 0 ]; then
    docker ps -a -f "status=exited" --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}"
    echo ""
    echo "Remove with: docker container prune -f"
else
    echo "None found."
fi
echo ""

# Dead containers
echo "=== DEAD CONTAINERS ==="
dead=$(docker ps -a -f "status=dead" -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$dead" -gt 0 ]; then
    docker ps -a -f "status=dead" --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"
else
    echo "None found."
fi
echo ""

# Dangling volumes
echo "=== DANGLING VOLUMES (not used by any container) ==="
volumes=$(docker volume ls -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$volumes" -gt 0 ]; then
    docker volume ls -f "dangling=true" --format "table {{.Name}}\t{{.Driver}}"
    echo ""
    echo "WARNING: Removing volumes will DELETE DATA!"
    echo "Remove with: docker volume prune -f"
else
    echo "None found."
fi
echo ""

# Build cache
echo "=== BUILD CACHE ==="
docker builder du 2>/dev/null || echo "Build cache info not available"
echo ""
echo "Clear with: docker builder prune -f"
echo ""

# Networks
echo "=== UNUSED NETWORKS ==="
networks=$(docker network ls -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
if [ "$networks" -gt 0 ]; then
    docker network ls -f "dangling=true"
else
    echo "None found (excluding default networks)."
fi
echo ""

echo "=========================================="
echo "CLEANUP COMMANDS"
echo "=========================================="
echo "Safe cleanup (dangling only):"
echo "  docker system prune -f"
echo ""
echo "Aggressive cleanup (all unused):"
echo "  docker system prune -a -f"
echo ""
echo "Nuclear option (includes volumes - DATA LOSS):"
echo "  docker system prune -a --volumes -f"
echo ""
echo "macOS: After cleanup, restart Docker Desktop to reclaim VM disk space."
echo ""
