#!/usr/bin/env python3
"""
Connected Devices — USB and Bluetooth peripherals.
"""

import platform
import subprocess
from datetime import datetime


def safe_run(cmd: list[str], timeout: int = 8) -> str:
    try:
        return subprocess.check_output(cmd, text=True, timeout=timeout, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


SKIP_USB = {
    "usb",
    "bus",
    "host controller",
    "root hub",
    "hub",
    "product id",
    "vendor id",
    "version",
    "speed",
    "location id",
    "current",
    "manufacturer",
}

SKIP_BT = {"address:", "state:", "chipset:", "firmware", "product id:", "vendor id:"}


def usb_devices() -> list[str]:
    sys_name = platform.system()
    devices: list[str] = []

    if sys_name == "Darwin":
        out = safe_run(["system_profiler", "SPUSBDataType"])
        for line in out.splitlines():
            stripped = line.strip()
            if stripped and ":" in stripped and not line.startswith("    "):
                if any(skip in stripped.lower() for skip in SKIP_USB):
                    continue
                name = stripped.split(":")[0].strip()
                if len(name) > 3 and not name.lower().startswith("usb"):
                    devices.append(name)
    elif sys_name == "Linux":
        out = safe_run(["lsusb"])
        for line in out.splitlines():
            parts = line.split(None, 6)
            if len(parts) >= 7:
                devices.append(parts[6].strip())

    return devices


def bluetooth_devices() -> list[tuple[str, bool | None]]:
    sys_name = platform.system()
    devices: list[tuple[str, bool | None]] = []

    if sys_name == "Darwin":
        out = safe_run(["system_profiler", "SPBluetoothDataType"])
        section = ""
        for line in out.splitlines():
            stripped = line.strip()
            if stripped in ("Connected:", "Not Connected:"):
                section = stripped
            elif stripped and ":" in stripped and line.startswith("          ") and section:
                if any(skip in stripped.lower() for skip in SKIP_BT):
                    continue
                name = stripped.split(":")[0].strip()
                if name and len(name) > 2 and "Controller" not in name:
                    devices.append((name, section == "Connected:"))
    elif sys_name == "Linux":
        out = safe_run(["bluetoothctl", "devices"])
        for line in out.splitlines():
            if line.startswith("Device"):
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    devices.append((parts[2], None))

    return devices


def main() -> None:
    lines = ["# Connected Devices", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    lines.append("## USB Devices")
    usb = usb_devices()
    if usb:
        for device in usb:
            lines.append(f"- {device}")
    else:
        lines.append("- *None detected (or not supported on this platform)*")

    lines.append("\n## Bluetooth Devices")
    bt = bluetooth_devices()
    if bt:
        for name, connected in bt:
            if connected is True:
                status = " *(connected)*"
            elif connected is False:
                status = " *(paired, not connected)*"
            else:
                status = ""
            lines.append(f"- {name}{status}")
    else:
        lines.append("- *None detected (or not supported on this platform)*")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
