#!/usr/bin/env python3
"""Bootstrap the PM system directory structure."""

from pathlib import Path


LIFECYCLE_FOLDERS = [
    "Proposed",
    "On-Deck",
    "Active",
    "Paused",
    "Archive",
    "Groups",
]


def main():
    root = Path(__file__).resolve().parents[4]

    created, skipped = [], []

    for name in LIFECYCLE_FOLDERS:
        p = root / name
        if p.exists():
            skipped.append(name)
        else:
            p.mkdir(parents=True)
            (p / ".gitkeep").touch()
            created.append(name)

    if created:
        print(f"Created: {', '.join(created)}")
    if skipped:
        print(f"Skipped (already exist): {', '.join(skipped)}")
    print("Bootstrap complete.")


if __name__ == "__main__":
    main()
