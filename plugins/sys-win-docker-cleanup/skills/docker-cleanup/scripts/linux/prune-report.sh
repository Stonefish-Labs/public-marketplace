#!/bin/bash
#
# Docker Prune Report - Linux
# Generates a comprehensive report of Docker resources that can be cleaned up.
#

set -e

echo "=========================================="
echo "Docker Cleanup Report - $(date)"
echo "=========================================="
echo ""

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# Overall disk usage
echo "=== DISK USAGE SUMMARY ==="
docker system df
echo ""

# Docker storage location size
if [ -d "/var/lib/docker" ]; then
    echo "=== DOCKER STORAGE ==="
    sudo du -sh /var/lib/docker 2>/dev/null || du -sh /var/lib/docker 2>/dev/null || echo "Cannot read /var/lib/docker size"
    echo ""
fi

# Dangling images
echo "=== DANGLING IMAGES (untagged, safe to remove) ==="
dangling=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l)
if [ "$dangling" -gt 0 ]; then
    docker images -f "dangling=true" --format "table {{.ID}}\t{{.Size}}\t{{.CreatedSince}}"
    echo ""
    echo "Remove with: docker image prune -f"
else
    echo "None found."
fi
echo ""

# Unused images (no container reference)
echo "=== UNUSED IMAGES (not used by any container) ==="
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}" | head -20
echo "(showing first 20)"
echo ""
echo "Remove all unused with: docker image prune -a -f"
echo ""

# Stopped containers
echo "=== STOPPED CONTAINERS ==="
stopped=$(docker ps -a -f "status=exited" -q 2>/dev/null | wc -l)
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
dead=$(docker ps -a -f "status=dead" -q 2>/dev/null | wc -l)
if [ "$dead" -gt 0 ]; then
    docker ps -a -f "status=dead" --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"
else
    echo "None found."
fi
echo ""

# Dangling volumes
echo "=== DANGLING VOLUMES (not used by any container) ==="
volumes=$(docker volume ls -f "dangling=true" -q 2>/dev/null | wc -l)
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
networks=$(docker network ls -f "dangling=true" -q 2>/dev/null | wc -l)
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
