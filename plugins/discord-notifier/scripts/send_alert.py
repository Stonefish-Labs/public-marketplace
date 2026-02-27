#!/usr/bin/env python3
"""Send a formatted alert to Discord via webhook."""

import argparse
import json
import sys
import urllib.error
import urllib.request

from config_loader import ConfigError, load_runtime_config


def send_alert(
    message: str,
    *,
    webhook_url: str,
    bot_name: str,
    timeout_seconds: int,
    title: str = "",
    urgent: bool = False,
) -> str:
    """Format and send an embed alert to a Discord webhook."""
    if len(message) > 4096:
        return "ERROR: Message exceeds Discord embed limit (4096 chars)"

    if title and len(title) > 256:
        return "ERROR: Title exceeds Discord embed limit (256 chars)"

    if urgent:
        if not title:
            title = "URGENT ALERT"
        message = f"[URGENT]\n\n{message}"
        color = 16711680  # Red
    else:
        color = 10181046  # Purple

    embed = {
        "description": message,
        "color": color,
    }

    if title:
        embed["title"] = title

    payload = {
        "username": bot_name,
        "embeds": [embed],
    }

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "discord-notifier"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            if response.status == 204:
                kind = "Urgent alert" if urgent else "Alert"
                return f"OK: {kind} sent to Discord"
            return f"ERROR: Discord returned HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        return f"ERROR: Discord returned HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return f"ERROR: {exc.reason}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a Discord webhook alert")
    parser.add_argument("message", help="Message content")
    parser.add_argument("--title", default="", help="Embed title")
    parser.add_argument("--urgent", action="store_true", help="Format as urgent alert")
    parser.add_argument(
        "--profile",
        default=None,
        help="Profile name (defaults to DISCORD_NOTIFIER_PROFILE or 'default')",
    )
    args = parser.parse_args()

    try:
        config = load_runtime_config(args.profile)
    except ConfigError:
        print(
            "ERROR: Discord notifier is not configured yet. "
            "Set up a notifier profile and required secrets, then retry."
        )
        sys.exit(1)

    result = send_alert(
        args.message,
        webhook_url=str(config["webhook_url"]),
        bot_name=str(config["bot_name"]),
        timeout_seconds=int(config["timeout_seconds"]),
        title=args.title,
        urgent=args.urgent,
    )
    print(result)
    sys.exit(0 if result.startswith("OK:") else 1)


if __name__ == "__main__":
    main()
