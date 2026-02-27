---
name: discord-notifier
description: Send alerts and notifications to Discord channels via webhook. Use when an agent needs to post a status update, completion notice, error report, or urgent alert to Discord. Triggers on requests like "notify Discord", "send Discord alert", "post to Discord", or "Discord notification".
---

# Discord Notifier

Send formatted messages to a Discord channel via webhook.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package runner
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- A notifier profile must already be configured by the operator.

## Usage

Basic alert:

```bash
uv run scripts/send_alert.py "Deployment completed successfully" --profile default
```

With title:

```bash
uv run scripts/send_alert.py "All tests passed" --title "CI Results" --profile default
```

Urgent alert:

```bash
uv run scripts/send_alert.py "Database connection lost" --urgent --profile default
```

Urgent alert with title:

```bash
uv run scripts/send_alert.py "CPU usage above threshold" --title "Server Alert" --urgent --profile default
```

## Script Reference

**scripts/send_alert.py** - Send a Discord embed message using a webhook.

| Argument | Required | Description |
|---|---|---|
| `message` | Yes | Main alert message text |
| `--title` | No | Embed title |
| `--urgent` | No | Marks alert as urgent with red formatting |
| `--profile` | No | Profile name (defaults to `DISCORD_NOTIFIER_PROFILE` or `default`) |

Exit code is 0 on success and 1 on failure.

## Limitations

- Sends embed messages only (no attachments)
- Discord embed title limit: 256 characters
- Discord embed description limit: 4096 characters

## Security Notes

- `--profile` accepts profile names only, not file paths.
