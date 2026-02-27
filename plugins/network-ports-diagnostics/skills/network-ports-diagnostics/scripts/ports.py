#!/usr/bin/env python3
"""
Open Network Ports — listening services and active local connections.
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
    lines = ["# Open Network Ports", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"]

    try:
        connections = psutil.net_connections(kind="inet")
    except Exception as exc:
        lines.append(f"- Unable to read connections: {exc}")
        lines.append("- Try running with elevated privileges for full visibility")
        print("\n".join(lines))
        return

    listening: dict[tuple[str, int], dict] = {}
    established: list[dict] = []

    for conn in connections:
        try:
            if conn.status == psutil.CONN_LISTEN and conn.laddr:
                key = (conn.laddr.ip, conn.laddr.port)
                if key not in listening:
                    proc_name, proc_pid = "Unknown", conn.pid
                    if conn.pid:
                        try:
                            proc_name = psutil.Process(conn.pid).name()
                        except Exception:
                            proc_name = "Access denied"
                    listening[key] = {
                        "port": conn.laddr.port,
                        "ip": conn.laddr.ip,
                        "protocol": "TCP" if conn.type == 1 else "UDP",
                        "process": proc_name,
                        "pid": proc_pid,
                    }
            elif conn.status == psutil.CONN_ESTABLISHED and conn.laddr and conn.raddr:
                established.append(
                    {
                        "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                        "pid": conn.pid,
                    }
                )
        except Exception:
            continue

    if listening:
        lines.append("## Listening Ports\n")
        lines.append("| Port | Proto | Bind Address | Process | PID |")
        lines.append("|------|-------|--------------|---------|-----|")
        for info in sorted(listening.values(), key=lambda item: item["port"]):
            ip = info["ip"]
            if ip in ("0.0.0.0", ""):
                bind = "All interfaces"
            elif ip == "127.0.0.1":
                bind = "Localhost"
            elif ip.startswith("::"):
                bind = "IPv6"
            else:
                bind = ip
            lines.append(
                f"| {info['port']} | {info['protocol']} | {bind} | {info['process'][:28]} | {info['pid'] or 'N/A'} |"
            )
    else:
        lines.append("## Listening Ports\n\n- *No listening ports found*")

    lines.append("\n## Active Connections")
    lines.append(f"- **Total established**: {len(established)}")

    if established:
        remote_counts: dict[str, int] = {}
        for conn in established:
            host = conn["remote"].split(":")[0]
            remote_counts[host] = remote_counts.get(host, 0) + 1
        lines.append("\n**Top peer hosts:**")
        for host, count in sorted(remote_counts.items(), key=lambda item: -item[1])[:10]:
            suffix = "s" if count > 1 else ""
            lines.append(f"- {host}: {count} connection{suffix}")

    lines.append(f"\n**Summary**: {len(listening)} listening, {len(established)} established")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
