#!/bin/bash
#
# Export Docker Container with Documentation
# Exports a container to .tar.gz and generates markdown documentation
# with the original configuration and restore instructions.
#
# Usage: ./export-container.sh <container_id_or_name> [output_directory]
#

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <container_id_or_name> [output_directory]"
    echo ""
    echo "Examples:"
    echo "  $0 my_container"
    echo "  $0 abc123def ./backups"
    exit 1
fi

CONTAINER="$1"
OUTPUT_DIR="${2:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Verify container exists
if ! docker inspect "$CONTAINER" &>/dev/null; then
    echo "ERROR: Container '$CONTAINER' not found"
    exit 1
fi

# Get container info
CONTAINER_NAME=$(docker inspect --format '{{.Name}}' "$CONTAINER" | sed 's/^\///')
IMAGE_NAME=$(docker inspect --format '{{.Config.Image}}' "$CONTAINER")
CONTAINER_ID=$(docker inspect --format '{{.Id}}' "$CONTAINER" | cut -c1-12)

echo "Exporting container: $CONTAINER_NAME ($CONTAINER_ID)"
echo "Image: $IMAGE_NAME"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Export filenames
EXPORT_FILE="$OUTPUT_DIR/${CONTAINER_NAME}_${TIMESTAMP}.tar.gz"
DOC_FILE="$OUTPUT_DIR/${CONTAINER_NAME}_${TIMESTAMP}.md"
COMPOSE_FILE="$OUTPUT_DIR/${CONTAINER_NAME}_${TIMESTAMP}_compose.yml"

# Export container filesystem
echo "Exporting container filesystem..."
docker export "$CONTAINER" | gzip > "$EXPORT_FILE"
EXPORT_SIZE=$(ls -lh "$EXPORT_FILE" | awk '{print $5}')
echo "Created: $EXPORT_FILE ($EXPORT_SIZE)"

# Extract configuration
echo "Extracting configuration..."

# Get ports
PORTS=$(docker inspect --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{(index $conf 0).HostPort}}:{{$p}}{{"\n"}}{{end}}{{end}}' "$CONTAINER" 2>/dev/null || echo "")

# Get volumes/mounts
MOUNTS=$(docker inspect --format '{{range .Mounts}}{{.Source}}:{{.Destination}}:{{.Mode}}{{"\n"}}{{end}}' "$CONTAINER" 2>/dev/null || echo "")

# Get environment variables (filter out common defaults)
ENV_VARS=$(docker inspect --format '{{range .Config.Env}}{{.}}{{"\n"}}{{end}}' "$CONTAINER" 2>/dev/null | grep -v "^PATH=" | grep -v "^HOME=" || echo "")

# Get restart policy
RESTART=$(docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' "$CONTAINER" 2>/dev/null || echo "no")

# Get network mode
NETWORK=$(docker inspect --format '{{.HostConfig.NetworkMode}}' "$CONTAINER" 2>/dev/null || echo "default")

# Generate markdown documentation
echo "Generating documentation..."
cat > "$DOC_FILE" << EOF
# Container Export: $CONTAINER_NAME

**Exported**: $(date)
**Container ID**: $CONTAINER_ID
**Original Image**: $IMAGE_NAME
**Export File**: $(basename "$EXPORT_FILE")

## Original Configuration

### Ports
EOF

if [ -n "$PORTS" ]; then
    echo "$PORTS" | while read -r port; do
        [ -n "$port" ] && echo "- $port" >> "$DOC_FILE"
    done
else
    echo "- None configured" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

### Volumes/Mounts
EOF

if [ -n "$MOUNTS" ]; then
    echo "$MOUNTS" | while read -r mount; do
        [ -n "$mount" ] && echo "- \`$mount\`" >> "$DOC_FILE"
    done
else
    echo "- None configured" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

### Environment Variables
EOF

if [ -n "$ENV_VARS" ]; then
    echo '```' >> "$DOC_FILE"
    echo "$ENV_VARS" >> "$DOC_FILE"
    echo '```' >> "$DOC_FILE"
else
    echo "- None (beyond defaults)" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

### Other Settings
- **Restart Policy**: $RESTART
- **Network Mode**: $NETWORK

## Restore Instructions

### Option 1: Import as New Image

This imports the container filesystem as a new image (loses original image layers):

\`\`\`bash
# Import the exported filesystem
gunzip -c $(basename "$EXPORT_FILE") | docker import - ${CONTAINER_NAME}_restored:latest

# Run the restored image
docker run -d --name ${CONTAINER_NAME}_restored \\
EOF

# Add port mappings to restore command
if [ -n "$PORTS" ]; then
    echo "$PORTS" | while read -r port; do
        [ -n "$port" ] && echo "  -p $port \\" >> "$DOC_FILE"
    done
fi

# Add volume mappings
if [ -n "$MOUNTS" ]; then
    echo "$MOUNTS" | while read -r mount; do
        [ -n "$mount" ] && echo "  -v $mount \\" >> "$DOC_FILE"
    done
fi

cat >> "$DOC_FILE" << EOF
  ${CONTAINER_NAME}_restored:latest
\`\`\`

### Option 2: Use Original Image

If the original image is still available:

\`\`\`bash
docker run -d --name ${CONTAINER_NAME}_new \\
  --restart=$RESTART \\
EOF

if [ -n "$PORTS" ]; then
    echo "$PORTS" | while read -r port; do
        [ -n "$port" ] && echo "  -p $port \\" >> "$DOC_FILE"
    done
fi

if [ -n "$MOUNTS" ]; then
    echo "$MOUNTS" | while read -r mount; do
        [ -n "$mount" ] && echo "  -v $mount \\" >> "$DOC_FILE"
    done
fi

if [ -n "$ENV_VARS" ]; then
    echo "$ENV_VARS" | while read -r env; do
        [ -n "$env" ] && echo "  -e \"$env\" \\" >> "$DOC_FILE"
    done
fi

cat >> "$DOC_FILE" << EOF
  $IMAGE_NAME
\`\`\`

## Docker Compose

See: $(basename "$COMPOSE_FILE")
EOF

echo "Created: $DOC_FILE"

# Generate docker-compose.yml
echo "Generating docker-compose.yml..."
cat > "$COMPOSE_FILE" << EOF
version: "3.8"

services:
  $CONTAINER_NAME:
    image: $IMAGE_NAME
    container_name: $CONTAINER_NAME
    restart: $RESTART
EOF

if [ -n "$PORTS" ]; then
    echo "    ports:" >> "$COMPOSE_FILE"
    echo "$PORTS" | while read -r port; do
        [ -n "$port" ] && echo "      - \"$port\"" >> "$COMPOSE_FILE"
    done
fi

if [ -n "$MOUNTS" ]; then
    echo "    volumes:" >> "$COMPOSE_FILE"
    echo "$MOUNTS" | while read -r mount; do
        [ -n "$mount" ] && echo "      - $mount" >> "$COMPOSE_FILE"
    done
fi

if [ -n "$ENV_VARS" ]; then
    echo "    environment:" >> "$COMPOSE_FILE"
    echo "$ENV_VARS" | while read -r env; do
        [ -n "$env" ] && echo "      - $env" >> "$COMPOSE_FILE"
    done
fi

if [ "$NETWORK" != "default" ] && [ "$NETWORK" != "bridge" ]; then
    echo "    network_mode: $NETWORK" >> "$COMPOSE_FILE"
fi

echo "Created: $COMPOSE_FILE"

echo ""
echo "=========================================="
echo "Export complete!"
echo "=========================================="
echo "Files created:"
echo "  - $EXPORT_FILE ($EXPORT_SIZE)"
echo "  - $DOC_FILE"
echo "  - $COMPOSE_FILE"
echo ""
