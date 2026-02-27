---
name: demacify
description: Strip Mac cruft from directories before archiving or sharing. Use when cleaning .DS_Store, ._*, __MACOSX, Spotlight, Trashes, and other macOS metadata from a target directory—e.g. before zipping, uploading, or moving to non-Mac systems.
---

# Demacify

## Overview

Removes macOS metadata and junk files from a directory so it can be archived or shared cleanly. Targets the usual suspects: `.DS_Store`, `._*`, `__MACOSX`, `.Spotlight-V100`, `.Trashes`, `.fseventsd`, `.TemporaryItems`, `.DocumentRevisions-V100`, `.VolumeIcon.icns`, `.AppleDouble`, `.LSOverride`, `.AppleDB`, `.AppleDesktop`, `Network Trash Folder`, `Temporary Items`, `.apdisk`, and `Icon\r` files.

## Instructions

1. Run the bundled script on the target directory:
   ```bash
   ./scripts/demacify.sh [TARGET]
   ```
   If `TARGET` is omitted, uses current directory (`.`).

2. The script uses `find` and `rm -rf`; it will report each removed item and a final count.

3. Verify the directory is clean before archiving or transferring.

## Usage

```bash
# Clean current directory
./scripts/demacify.sh

# Clean a specific folder
./scripts/demacify.sh /path/to/project

# Clean before zipping
./scripts/demacify.sh ./my-project && zip -r my-project.zip my-project
```

## Checklist

- [ ] Target is a directory (script errors if not)
- [ ] No critical files match the removal patterns
- [ ] Run from a safe location; deletions are permanent
