#!/usr/bin/env python3
"""
Local Network Status — interfaces, gateway, DNS, VPN heuristic, and traffic.
No external network requests are made.
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


def default_gateway() -> str:
    sys_name = platform.system()
    if sys_name == "Darwin":
        out = safe_run(["route", "-n", "get", "default"])
        for line in out.splitlines():
            if "gateway:" in line:
                return line.split(":", 1)[-1].strip()
    elif sys_name == "Linux":
        out = safe_run(["ip", "route", "show", "default"])
        parts = out.split()
        if len(parts) >= 3:
            return parts[2]
    return ""


def dns_servers() -> list[str]:
    servers: list[str] = []
    sys_name = platform.system()
    if sys_name == "Darwin":
        out = safe_run(["scutil", "--dns"])
        for line in out.splitlines():
            if "nameserver[0]" in line:
                dns = line.split(":", 1)[-1].strip()
                if dns not in servers:
                    servers.append(dns)
    elif sys_name == "Linux":
        try:
            with open("/etc/resolv.conf", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("nameserver"):
                        servers.append(line.split()[1])
        except OSError:
            pass
    return servers


def detect_vpn(interfaces: dict, stats: dict) -> str:
    vpn_names = ("tun", "tap", "vpn", "utun", "wg", "proton", "nordlynx")
    for iface in interfaces:
        if any(tag in iface.lower() for tag in vpn_names):
            if stats.get(iface) and stats[iface].isup:
                return f"Active ({iface})"
    return "Not detected"


def main() -> None:
    lines = ["# Local Network Status", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    lines.append("## Interfaces")
    active_count = 0
    for iface, addr_list in addrs.items():
        if iface.startswith("lo") or iface.startswith("utun"):
            continue
        stat = stats.get(iface)
        if not (stat and stat.isup):
            continue
        active_count += 1
        lines.append(f"\n### {iface}")
        lines.append(f"- **Status**: Up  |  **Speed**: {stat.speed} Mbps")
        for addr in addr_list:
            family_name = addr.family.name
            if family_name == "AF_INET":
                lines.append(f"- **IPv4**: {addr.address}")
                if addr.netmask:
                    lines.append(f"  - Netmask: {addr.netmask}")
            elif family_name == "AF_INET6" and not addr.address.startswith("fe80"):
                lines.append(f"- **IPv6**: {addr.address}")
            elif family_name == "AF_PACKET" and addr.address:
                lines.append(f"- **MAC**: {addr.address}")

    if active_count == 0:
        lines.append("- *No active interfaces detected*")

    lines.append("\n## Connectivity")
    gateway = default_gateway()
    if gateway:
        lines.append(f"- **Default Gateway**: {gateway}")

    dns = dns_servers()
    if dns:
        lines.append(f"- **DNS Servers**: {', '.join(dns[:4])}")

    lines.append(f"- **VPN Status**: {detect_vpn(addrs, stats)}")

    try:
        io = psutil.net_io_counters()
        lines.append("\n## Traffic (since boot)")
        lines.append(f"- **Sent**: {io.bytes_sent / 1024**3:.2f} GB ({io.packets_sent:,} packets)")
        lines.append(f"- **Received**: {io.bytes_recv / 1024**3:.2f} GB ({io.packets_recv:,} packets)")
    except Exception:
        pass

    print("\n".join(lines))


if __name__ == "__main__":
    main()
