#!/usr/bin/env python3
"""
System Summary — hostname, OS, CPU, RAM, uptime.
Quick system identity check without high-sensitivity fields.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psutil>=7.0",
# ]
# ///

import platform
from datetime import datetime

import psutil


def main() -> None:
    lines = ["# System Summary", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    lines.append("## System Identity")
    lines.append(f"- **Hostname**: {platform.node()}")
    lines.append(f"- **Platform**: {platform.system()} {platform.release()}")
    lines.append(f"- **Architecture**: {platform.machine()}")
    lines.append(f"- **Processor**: {platform.processor() or 'Unknown'}")

    lines.append("\n## Resources")
    cpu_count = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    cpu_pct = psutil.cpu_percent(interval=0.5)
    lines.append(f"- **CPU Cores**: {cpu_count} physical, {cpu_logical} logical")
    lines.append(f"- **CPU Usage**: {cpu_pct}%")

    mem = psutil.virtual_memory()
    lines.append(f"- **Total RAM**: {mem.total / 1024**3:.1f} GB")
    lines.append(f"- **Available RAM**: {mem.available / 1024**3:.1f} GB ({mem.percent}% used)")

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    lines.append(f"\n- **Boot Time**: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        f"- **Uptime**: {uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
    )

    print("\n".join(lines))


if __name__ == "__main__":
    main()
