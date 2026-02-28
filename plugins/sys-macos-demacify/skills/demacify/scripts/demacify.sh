#!/bin/bash
# demacify - Strip Mac garbage from directories before archiving

set -euo pipefail

TARGET="${1:-.}"

if [[ ! -d "$TARGET" ]]; then
    echo "Error: '$TARGET' is not a directory" >&2
    exit 1
fi

echo "Cleaning Mac cruft from: $TARGET"

# The usual suspects
PATTERNS=(
    ".DS_Store"
    "._*"
    "__MACOSX"
    ".Spotlight-V100"
    ".Trashes"
    ".fseventsd"
    ".TemporaryItems"
    ".DocumentRevisions-V100"
    ".VolumeIcon.icns"
    ".AppleDouble"
    ".LSOverride"
    ".AppleDB"
    ".AppleDesktop"
    "Network Trash Folder"
    "Temporary Items"
    ".apdisk"
)

COUNT=0
for pattern in "${PATTERNS[@]}"; do
    while IFS= read -r -d '' file; do
        rm -rf "$file"
        echo "Removed: $file"
        ((COUNT++)) || true
    done < <(find "$TARGET" -name "$pattern" -print0 2>/dev/null)
done

# Icon files with carriage return (yes, really)
while IFS= read -r -d '' file; do
    rm -rf "$file"
    echo "Removed: $file"
    ((COUNT++)) || true
done < <(find "$TARGET" -name $'Icon\r' -print0 2>/dev/null)

echo "Done. Removed $COUNT items."
