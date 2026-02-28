#!/usr/bin/env python3
"""
Hardware Details — CPU, RAM, swap, GPU, battery, uptime.
Comprehensive hardware specs for diagnostics and capability assessment.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psutil>=7.0",
# ]
# ///

import platform
import subprocess
from datetime import datetime

import psutil


def safe_run(cmd: list[str], timeout: int = 5) -> str:
    try:
        return subprocess.check_output(cmd, text=True, timeout=timeout, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def cpu_section() -> list[str]:
    lines = ["## CPU"]
    count_phys = psutil.cpu_count(logical=False)
    count_log = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    pct = psutil.cpu_percent(interval=0.5)

    lines.append(f"- **Cores**: {count_phys} physical, {count_log} logical")
    if freq:
        lines.append(f"- **Frequency**: {freq.current:.0f} MHz (max: {freq.max:.0f} MHz)")
    lines.append(f"- **Usage**: {pct}%")

    per_cpu = psutil.cpu_percent(interval=0.3, percpu=True)
    if per_cpu and len(per_cpu) <= 16:
        core_str = "  ".join(f"C{i}:{p}%" for i, p in enumerate(per_cpu))
        lines.append(f"- **Per-core**: {core_str}")
    return lines


def ram_section() -> list[str]:
    lines = ["\n## Memory"]
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    lines.append(f"- **Total RAM**: {mem.total / 1024**3:.1f} GB")
    lines.append(f"- **Available**: {mem.available / 1024**3:.1f} GB ({mem.percent}% used)")
    lines.append(f"- **Used**: {mem.used / 1024**3:.1f} GB")
    if swap.total > 0:
        lines.append(f"- **Swap Total**: {swap.total / 1024**3:.1f} GB ({swap.percent}% used)")
    return lines


def gpu_section() -> list[str]:
    lines: list[str] = []
    sys_name = platform.system()

    if sys_name == "Darwin":
        out = safe_run(["system_profiler", "SPDisplaysDataType"])
        if out:
            lines.append("\n## GPU")
            for line in out.splitlines():
                stripped = line.strip()
                if "Chipset Model:" in stripped:
                    lines.append(f"- **GPU**: {stripped.split(':', 1)[-1].strip()}")
                elif "VRAM" in stripped:
                    lines.append(f"  - **VRAM**: {stripped.split(':', 1)[-1].strip()}")
    elif sys_name == "Linux":
        out = safe_run(["lspci", "-mm"])
        if out:
            gpus = [line for line in out.splitlines() if "VGA" in line or "3D" in line]
            if gpus:
                lines.append("\n## GPU")
                for gpu_line in gpus[:4]:
                    parts = gpu_line.split('"')
                    if len(parts) >= 6:
                        lines.append(f"- **GPU**: {parts[5]}")

    return lines


def battery_section() -> list[str]:
    lines: list[str] = []
    try:
        bat = psutil.sensors_battery()
        if not bat:
            return lines

        lines.append("\n## Battery")
        lines.append(f"- **Charge**: {bat.percent:.1f}%")
        lines.append(f"- **Status**: {'Charging' if bat.power_plugged else 'On battery'}")
        if bat.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
            hours, rem = divmod(bat.secsleft, 3600)
            minutes = rem // 60
            label = "Time to full" if bat.power_plugged else "Time remaining"
            lines.append(f"- **{label}**: {hours}h {minutes}m")
    except Exception:
        return lines
    return lines


def uptime_section() -> list[str]:
    boot = datetime.fromtimestamp(psutil.boot_time())
    up = datetime.now() - boot
    return [
        "\n## Uptime",
        f"- **Boot Time**: {boot.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Uptime**: {up.days}d {up.seconds // 3600}h {(up.seconds % 3600) // 60}m",
    ]


def main() -> None:
    lines = ["# Hardware Details", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]
    lines.extend(cpu_section())
    lines.extend(ram_section())
    lines.extend(gpu_section())
    lines.extend(battery_section())
    lines.extend(uptime_section())
    print("\n".join(lines))


if __name__ == "__main__":
    main()
