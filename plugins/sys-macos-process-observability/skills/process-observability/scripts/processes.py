#!/usr/bin/env python3
"""
Running Processes — top processes by CPU and memory usage.
Default output excludes executable paths unless explicitly requested.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psutil>=7.0",
# ]
# ///

import argparse
import time
from datetime import datetime

import psutil


def main() -> None:
    parser = argparse.ArgumentParser(description="Show top processes by CPU and memory usage")
    parser.add_argument("--limit", type=int, default=25, help="Max rows to show")
    parser.add_argument(
        "--include-paths",
        action="store_true",
        help="Include executable/cmdline path column (higher sensitivity)",
    )
    args = parser.parse_args()

    lines = ["# Running Processes", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    fields = ["pid", "name", "cpu_percent", "memory_percent"]
    if args.include_paths:
        fields.extend(["exe", "cmdline"])

    procs: list[dict] = []
    for proc in psutil.process_iter(fields):
        try:
            procs.append(proc.info.copy())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(0.5)
    for proc in procs:
        try:
            proc["cpu_percent"] = psutil.Process(proc["pid"]).cpu_percent()
        except Exception:
            proc["cpu_percent"] = 0.0

    procs.sort(
        key=lambda item: (item.get("cpu_percent", 0), item.get("memory_percent", 0) or 0),
        reverse=True,
    )

    total = len(procs)
    active = sum(1 for proc in procs if (proc.get("cpu_percent", 0) or 0) > 0)
    lines.append(f"**{total} total processes, {active} active**\n")

    if args.include_paths:
        lines.append("## Top Processes by CPU / Memory\n")
        lines.append("| PID | Name | CPU% | Mem% | Path |")
        lines.append("|-----|------|------|------|------|")
    else:
        lines.append("## Top Processes by CPU / Memory\n")
        lines.append("| PID | Name | CPU% | Mem% |")
        lines.append("|-----|------|------|------|")

    shown = 0
    key_procs = {"kernel_task", "systemd", "init", "launchd", "WindowServer", "loginwindow"}

    for proc in procs:
        if shown >= args.limit:
            break
        cpu = proc.get("cpu_percent", 0) or 0
        mem = proc.get("memory_percent", 0) or 0
        name = proc.get("name", "?") or "?"

        if cpu < 0.1 and mem < 0.3 and name.lower() not in key_procs:
            continue

        if args.include_paths:
            exe = proc.get("exe") or ""
            if not exe and proc.get("cmdline"):
                exe = (proc["cmdline"] or [""])[0]
            if len(exe) > 45:
                exe = "..." + exe[-42:]
            lines.append(f"| {proc['pid']} | {name[:22]} | {cpu:.1f}% | {mem:.1f}% | {exe or 'N/A'} |")
        else:
            lines.append(f"| {proc['pid']} | {name[:22]} | {cpu:.1f}% | {mem:.1f}% |")

        shown += 1

    if shown == 0:
        if args.include_paths:
            lines.append("| - | *No active processes detected* | - | - | - |")
        else:
            lines.append("| - | *No active processes detected* | - | - |")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
