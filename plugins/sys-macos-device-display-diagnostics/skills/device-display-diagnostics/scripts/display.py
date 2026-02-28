#!/usr/bin/env python3
"""
Display Information — monitors, resolution, refresh rate, and connection info.
"""

import json
import platform
import subprocess
from datetime import datetime


def safe_run(cmd: list[str], timeout: int = 10) -> str:
    try:
        return subprocess.check_output(cmd, text=True, timeout=timeout, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def macos_displays() -> list[dict[str, str]]:
    displays: list[dict[str, str]] = []
    out = safe_run(["system_profiler", "SPDisplaysDataType", "-json"])
    if out:
        try:
            data = json.loads(out)
            for gpu in data.get("SPDisplaysDataType", []):
                for display in gpu.get("spdisplays_ndrvs", []):
                    info: dict[str, str] = {}
                    if "_name" in display:
                        info["Name"] = display["_name"]
                    if "_spdisplays_resolution" in display:
                        info["Resolution"] = display["_spdisplays_resolution"]
                    if "_spdisplays_refresh_rate" in display:
                        info["Refresh Rate"] = f"{display['_spdisplays_refresh_rate']} Hz"
                    if "_spdisplays_connection_type" in display:
                        info["Connection"] = display["_spdisplays_connection_type"]
                    if info:
                        displays.append(info)
        except Exception:
            return []
    return displays


def linux_displays() -> list[dict[str, str]]:
    displays: list[dict[str, str]] = []
    out = safe_run(["xrandr", "--verbose"])
    if not out:
        return displays

    current: dict[str, str] = {}
    for line in out.splitlines():
        if " connected" in line and not line.startswith(" "):
            if current:
                displays.append(current)
            current = {"Name": line.split()[0], "Status": "Connected"}
        elif current and "*" in line:
            parts = line.split()
            if parts and "x" in parts[0]:
                current["Resolution"] = parts[0]
    if current:
        displays.append(current)
    return displays


def main() -> None:
    lines = ["# Display Information", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    sys_name = platform.system()
    if sys_name == "Darwin":
        displays = macos_displays()
    elif sys_name == "Linux":
        displays = linux_displays()
    else:
        lines.append(f"- *Display detection has limited support on {sys_name}*")
        print("\n".join(lines))
        return

    if not displays:
        lines.append("- *No displays detected (GUI session may be required)*")
    else:
        for idx, display in enumerate(displays, 1):
            lines.append(f"\n### Display {idx}")
            for key, value in display.items():
                lines.append(f"- **{key}**: {value}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
