# Docker Cleanup Skill

Clean up Docker environments with precision — controlled pruning, VHDX compaction on Windows, and container archiving before removal.

## Features

- **Survey before destroy** — Shows what will be removed, asks before nuking
- **WSL2 VHDX compaction** — Reclaim disk space on Windows after pruning
- **Cross-platform** — Works on Windows, macOS, and Linux
- **Export & document** — Archive containers/images before removal

## Installation

```bash
# Cursor
cp -r skills/docker-cleanup ~/.cursor/skills/

# Claude Code
cp -r skills/docker-cleanup ~/.claude/skills/

# Codex
cp -r skills/docker-cleanup ~/.codex/skills/

# Roo
cp -r skills/docker-cleanup ~/.roo/skills/
```

## Usage

Trigger phrases:
- "Clean up Docker"
- "Reclaim Docker disk space"
- "Compact VHDX"
- "Prune dangling images"
- "Export this container before removing"

## License

MIT
