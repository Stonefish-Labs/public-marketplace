# Demacify

Strip Mac cruft from directories before archiving or sharing.

## Overview

Demacify removes macOS metadata and junk files (`.DS_Store`, `._*`, `__MACOSX`, Spotlight, Trashes, etc.) from a target directory so it can be zipped, uploaded, or moved to non-Mac systems without carrying platform-specific garbage.

## Usage

Run the script on a directory:

```bash
./skills/demacify/scripts/demacify.sh [TARGET]
```

- **TARGET** — Directory to clean (default: current directory)
- Output: Lists each removed file and a final count

### Examples

```bash
# Clean current directory
./skills/demacify/scripts/demacify.sh

# Clean before zipping
./skills/demacify/scripts/demacify.sh ./my-project && zip -r my-project.zip my-project
```

## License

MIT
