#!/usr/bin/env python3
"""
Storage Analysis — disk partitions, capacity, usage, and filesystem types.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psutil>=7.0",
# ]
# ///

from datetime import datetime

import psutil


def main() -> None:
    lines = ["# Storage Analysis", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    partitions = psutil.disk_partitions(all=False)
    total_shown = 0

    for part in partitions:
        if part.fstype in (
            "tmpfs",
            "devtmpfs",
            "squashfs",
            "overlay",
            "proc",
            "sysfs",
            "devpts",
            "cgroup",
            "cgroup2",
            "pstore",
        ):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue

        total_gb = usage.total / 1024**3
        free_gb = usage.free / 1024**3
        used_pct = usage.percent

        filled = round(used_pct / 10)
        bar = "#" * filled + "." * (10 - filled)

        disk_type = "Removable" if part.opts and "removable" in part.opts else "Fixed"

        lines.append(f"### {part.device}  ->  `{part.mountpoint}`")
        lines.append(f"- **Type**: {disk_type}  |  **FS**: {part.fstype}")
        lines.append(f"- **Capacity**: {total_gb:.1f} GB")
        lines.append(f"- **Used**: {used_pct:.1f}%  [{bar}]  ({free_gb:.1f} GB free)\n")
        total_shown += 1

    if total_shown == 0:
        lines.append("- *No accessible partitions found*")

    try:
        io = psutil.disk_io_counters()
        if io:
            lines.append("\n## Disk I/O (since boot)")
            lines.append(f"- **Read**: {io.read_bytes / 1024**3:.2f} GB ({io.read_count:,} ops)")
            lines.append(f"- **Write**: {io.write_bytes / 1024**3:.2f} GB ({io.write_count:,} ops)")
    except Exception:
        pass

    print("\n".join(lines))


if __name__ == "__main__":
    main()
