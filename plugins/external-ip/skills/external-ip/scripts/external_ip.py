#!/usr/bin/env python3
"""
Resolve public IP address using multiple HTTPS reflector services.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.32",
# ]
# ///

import argparse
import ipaddress
from datetime import datetime

import requests


PROVIDERS = [
    ("checkip-amazonaws", "https://checkip.amazonaws.com"),
    ("api-ipify", "https://api.ipify.org"),
    ("ifconfig-me", "https://ifconfig.me/ip"),
]


def parse_ip(text: str) -> str | None:
    candidate = text.strip()
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Get external/public IP address")
    parser.add_argument("--timeout", type=float, default=4.0, help="Per-provider timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Emit JSON-like output lines")
    args = parser.parse_args()

    errors: list[str] = []
    for provider, url in PROVIDERS:
        try:
            response = requests.get(url, timeout=args.timeout)
            if response.status_code != 200:
                errors.append(f"{provider}: HTTP {response.status_code}")
                continue
            parsed = parse_ip(response.text)
            if not parsed:
                errors.append(f"{provider}: invalid response")
                continue

            if args.json:
                print(
                    "{"
                    f'"timestamp":"{datetime.now().isoformat()}",' 
                    f'"provider":"{provider}",' 
                    f'"external_ip":"{parsed}"'
                    "}"
                )
            else:
                lines = [
                    "# External IP",
                    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
                    f"- **External IP**: {parsed}",
                    f"- **Provider**: {provider}",
                ]
                print("\n".join(lines))
            return
        except Exception as exc:
            errors.append(f"{provider}: {exc}")

    if args.json:
        print("{\"error\":\"unable to determine external IP\"}")
    else:
        lines = [
            "# External IP",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            "- Unable to determine external IP from configured providers.",
            "- Attempts:",
        ]
        for err in errors:
            lines.append(f"  - {err}")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
