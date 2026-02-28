#!/usr/bin/env python3
"""Load Discord notifier profiles and resolve secret references."""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse


DEFAULT_ALLOWED_HOSTS = ["discord.com"]
DEFAULT_PROFILE = "default"
DEFAULT_TIMEOUT_SECONDS = 30
PROFILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class ConfigError(Exception):
    """Configuration loading or validation error."""


class RuntimeConfig(TypedDict):
    profile_name: str
    profile_path: str
    bot_name: str
    timeout_seconds: int
    allowed_hosts: list[str]
    webhook_url: str


def _resolve_profile_name(profile_name: str | None) -> str:
    name = profile_name or os.getenv("DISCORD_NOTIFIER_PROFILE") or DEFAULT_PROFILE
    if not PROFILE_RE.match(name):
        raise ConfigError(
            "Invalid profile name. Use letters, numbers, underscore, or hyphen only."
        )
    return name


def _candidate_profile_paths(profile_name: str) -> list[Path]:
    paths: list[Path] = [
        Path.cwd() / ".config" / "discord-notifier" / "profiles" / f"{profile_name}.toml"
    ]

    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        paths.append(
            Path(xdg_config_home)
            / "discord-notifier"
            / "profiles"
            / f"{profile_name}.toml"
        )

    paths.append(
        Path.home() / ".config" / "discord-notifier" / "profiles" / f"{profile_name}.toml"
    )
    return paths


def _load_profile_file(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Profile at {path} must parse to a TOML table")
    return data


def _resolve_secret_ref(value: str) -> str:
    parsed = urlparse(value)
    backend = parsed.netloc
    secret_key = parsed.path.lstrip("/")

    if backend == "env":
        if not secret_key:
            raise ConfigError("secret://env/<VAR_NAME> must include an environment variable name")
        secret_value = os.getenv(secret_key)
        if not secret_value:
            raise ConfigError(f"Environment variable {secret_key} is not set")
        return secret_value

    if backend in {"bitwarden", "1password", "keychain"}:
        raise ConfigError(
            f"Secret backend '{backend}' is referenced but no adapter is configured yet"
        )

    raise ConfigError(f"Unsupported secret backend '{backend}'")


def _resolve_webhook_url(raw_webhook: str) -> str:
    if not raw_webhook.startswith("secret://"):
        raise ConfigError(
            "webhook_url must be a secret reference (for example secret://env/DISCORD_WEBHOOK_URL)"
        )
    return _resolve_secret_ref(raw_webhook)


def _validate_webhook_url(webhook_url: str, allowed_hosts: list[str]) -> None:
    parsed = urlparse(webhook_url)
    if parsed.scheme != "https":
        raise ConfigError("Webhook URL must use https")
    if not parsed.netloc:
        raise ConfigError("Webhook URL is missing host")

    host = parsed.hostname or ""
    if not any(host == allowed or host.endswith(f".{allowed}") for allowed in allowed_hosts):
        raise ConfigError(f"Webhook host '{host}' is not in allowed_hosts")

    if not parsed.path.startswith("/api/webhooks/"):
        raise ConfigError("Webhook URL path must start with /api/webhooks/")


def load_runtime_config(profile_name: str | None = None) -> RuntimeConfig:
    """Load, resolve, and validate runtime config for the notifier."""
    resolved_profile = _resolve_profile_name(profile_name)
    candidate_paths = _candidate_profile_paths(resolved_profile)

    profile_path = next((path for path in candidate_paths if path.is_file()), None)
    if profile_path is None:
        looked = ", ".join(str(path) for path in candidate_paths)
        raise ConfigError(
            f"Profile '{resolved_profile}' not found. Looked in: {looked}"
        )

    data = _load_profile_file(profile_path)
    raw_webhook = data.get("webhook_url")
    if not isinstance(raw_webhook, str) or not raw_webhook.strip():
        raise ConfigError("Profile must define non-empty string 'webhook_url'")

    raw_allowed_hosts = data.get("allowed_hosts", DEFAULT_ALLOWED_HOSTS)
    if not isinstance(raw_allowed_hosts, list) or not raw_allowed_hosts:
        raise ConfigError("'allowed_hosts' must be a non-empty list")
    allowed_hosts = [str(host).strip() for host in raw_allowed_hosts if str(host).strip()]
    if not allowed_hosts:
        raise ConfigError("'allowed_hosts' must contain at least one non-empty host")

    timeout_value = data.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout_seconds = int(timeout_value)
    except (TypeError, ValueError) as exc:
        raise ConfigError("'timeout_seconds' must be an integer") from exc
    if timeout_seconds <= 0:
        raise ConfigError("'timeout_seconds' must be greater than 0")

    bot_name = str(data.get("bot_name", "MCP Agent")).strip() or "MCP Agent"
    webhook_url = _resolve_webhook_url(raw_webhook.strip())
    _validate_webhook_url(webhook_url, allowed_hosts=allowed_hosts)

    return {
        "profile_name": resolved_profile,
        "profile_path": str(profile_path),
        "bot_name": bot_name,
        "timeout_seconds": timeout_seconds,
        "allowed_hosts": allowed_hosts,
        "webhook_url": webhook_url,
    }
