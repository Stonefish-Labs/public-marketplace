#!/bin/bash
#
# Export Docker Image with Documentation
# Exports an image to .tar.gz and generates markdown documentation.
#
# Usage: ./export-image.sh <image_name> [output_directory]
#

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <image_name> [output_directory]"
    echo ""
    echo "Examples:"
    echo "  $0 nginx:latest"
    echo "  $0 myapp:v1.2.3 ./backups"
    exit 1
fi

IMAGE="$1"
OUTPUT_DIR="${2:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Verify image exists
if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "ERROR: Image '$IMAGE' not found"
    exit 1
fi

# Get image info
IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$IMAGE" | cut -d: -f2 | cut -c1-12)
IMAGE_SIZE=$(docker image inspect --format '{{.Size}}' "$IMAGE")
IMAGE_SIZE_HR=$(echo "$IMAGE_SIZE" | awk '{printf "%.2f MB", $1/1024/1024}')
CREATED=$(docker image inspect --format '{{.Created}}' "$IMAGE")

# Sanitize image name for filename
SAFE_NAME=$(echo "$IMAGE" | tr ':/' '_')

echo "Exporting image: $IMAGE"
echo "Image ID: $IMAGE_ID"
echo "Size: $IMAGE_SIZE_HR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Export filenames
EXPORT_FILE="$OUTPUT_DIR/${SAFE_NAME}_${TIMESTAMP}.tar.gz"
DOC_FILE="$OUTPUT_DIR/${SAFE_NAME}_${TIMESTAMP}.md"

# Export image
echo "Exporting image (this may take a while for large images)..."
docker save "$IMAGE" | gzip > "$EXPORT_FILE"
EXPORT_SIZE=$(ls -lh "$EXPORT_FILE" | awk '{print $5}')
echo "Created: $EXPORT_FILE ($EXPORT_SIZE)"

# Get image labels
LABELS=$(docker image inspect --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}' "$IMAGE" 2>/dev/null || echo "")

# Get exposed ports
EXPOSED_PORTS=$(docker image inspect --format '{{range $p, $conf := .Config.ExposedPorts}}{{$p}}{{"\n"}}{{end}}' "$IMAGE" 2>/dev/null || echo "")

# Get default environment
DEFAULT_ENV=$(docker image inspect --format '{{range .Config.Env}}{{.}}{{"\n"}}{{end}}' "$IMAGE" 2>/dev/null | grep -v "^PATH=" || echo "")

# Get default command
DEFAULT_CMD=$(docker image inspect --format '{{.Config.Cmd}}' "$IMAGE" 2>/dev/null || echo "")
ENTRYPOINT=$(docker image inspect --format '{{.Config.Entrypoint}}' "$IMAGE" 2>/dev/null || echo "")

# Get history/layers
LAYERS=$(docker image history --no-trunc --format "{{.CreatedBy}}" "$IMAGE" 2>/dev/null | head -10 || echo "")

# Generate markdown documentation
echo "Generating documentation..."
cat > "$DOC_FILE" << EOF
# Image Export: $IMAGE

**Exported**: $(date)
**Image ID**: $IMAGE_ID
**Original Size**: $IMAGE_SIZE_HR
**Created**: $CREATED
**Export File**: $(basename "$EXPORT_FILE") ($EXPORT_SIZE)

## Image Configuration

### Exposed Ports
EOF

if [ -n "$EXPOSED_PORTS" ]; then
    echo "$EXPOSED_PORTS" | while read -r port; do
        [ -n "$port" ] && echo "- $port" >> "$DOC_FILE"
    done
else
    echo "- None" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

### Default Environment
EOF

if [ -n "$DEFAULT_ENV" ]; then
    echo '```' >> "$DOC_FILE"
    echo "$DEFAULT_ENV" >> "$DOC_FILE"
    echo '```' >> "$DOC_FILE"
else
    echo "- None (beyond PATH)" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

### Command / Entrypoint
- **Entrypoint**: \`$ENTRYPOINT\`
- **Cmd**: \`$DEFAULT_CMD\`

### Labels
EOF

if [ -n "$LABELS" ]; then
    echo '```' >> "$DOC_FILE"
    echo "$LABELS" >> "$DOC_FILE"
    echo '```' >> "$DOC_FILE"
else
    echo "- None" >> "$DOC_FILE"
fi

cat >> "$DOC_FILE" << EOF

## Restore Instructions

### Load the Image

\`\`\`bash
# Load from exported file
gunzip -c $(basename "$EXPORT_FILE") | docker load

# Verify it loaded
docker images | grep "$IMAGE"
\`\`\`

### Run a Container

\`\`\`bash
docker run -d --name my_container \\
EOF

if [ -n "$EXPOSED_PORTS" ]; then
    echo "$EXPOSED_PORTS" | while read -r port; do
        # Extract port number for mapping
        port_num=$(echo "$port" | cut -d/ -f1)
        [ -n "$port_num" ] && echo "  -p $port_num:$port_num \\" >> "$DOC_FILE"
    done
fi

cat >> "$DOC_FILE" << EOF
  $IMAGE
\`\`\`

## Layer History (first 10)

\`\`\`
EOF

echo "$LAYERS" >> "$DOC_FILE"

cat >> "$DOC_FILE" << EOF
\`\`\`

## Notes

- This export preserves all image layers and metadata
- Use \`docker load\` (not \`docker import\`) to restore
- The restored image will have the same ID and tags
EOF

echo "Created: $DOC_FILE"

echo ""
echo "=========================================="
echo "Export complete!"
echo "=========================================="
echo "Files created:"
echo "  - $EXPORT_FILE ($EXPORT_SIZE)"
echo "  - $DOC_FILE"
echo ""
echo "To restore:"
echo "  gunzip -c $(basename "$EXPORT_FILE") | docker load"
echo ""
