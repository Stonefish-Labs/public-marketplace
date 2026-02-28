"""Portable runtime config loading with optional secret references."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from mac_messages_mcp.secrets import SecretResolutionError, resolve_secret_uri

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


APP_NAME = "mac-messages-mcp"
PROFILE_ENV_VAR = "MAC_MESSAGES_MCP_PROFILE"
_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")

ConfirmationPolicy = Literal["always", "never", "external-only", "group-only"]


class ConfigError(Exception):
    """Raised when runtime config resolution or validation fails."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Effective runtime config for policy-sensitive tools."""

    profile_name: str
    source_path: Path | None
    confirmation_policy: ConfirmationPolicy = "external-only"
    allowed_recipients: tuple[str, ...] = ()
    allow_group_messages: bool = True
    default_hours: int = 24


def _validate_profile_name(profile_name: str) -> None:
    if not _PROFILE_NAME_RE.match(profile_name):
        raise ConfigError("Invalid profile name. Use letters, numbers, underscore, or dash.")


def resolve_profile_name(profile_override: str | None = None) -> str:
    """Resolve the active profile name with CLI/env/default precedence."""
    profile_name = profile_override or os.getenv(PROFILE_ENV_VAR) or "default"
    _validate_profile_name(profile_name)
    return profile_name


def candidate_profile_paths(profile_name: str) -> list[Path]:
    """Return profile lookup paths by precedence order."""
    project_root = Path.cwd()
    xdg_root = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
    user_root = Path("~/.config").expanduser()

    rel = Path(APP_NAME) / "profiles" / f"{profile_name}.toml"
    return [project_root / ".config" / rel, xdg_root / rel, user_root / rel]


def _load_profile_data(path: Path) -> dict:
    try:
        with path.open("rb") as fp:
            loaded = tomllib.load(fp)
    except OSError as exc:
        raise ConfigError(f"Could not read profile file: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Profile is not valid TOML: {path}") from exc

    if not isinstance(loaded, dict):
        raise ConfigError("Profile must contain a TOML table at the top level.")
    return loaded


def _parse_confirmation_policy(raw: object) -> ConfirmationPolicy:
    if raw is None:
        return "external-only"
    if raw not in {"always", "never", "external-only", "group-only"}:
        raise ConfigError("confirmation_policy must be one of: always, never, external-only, group-only.")
    return raw


def _parse_allowed_recipients(raw: object) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list) or not all(isinstance(v, str) and v.strip() for v in raw):
        raise ConfigError("allowed_recipients must be a list of non-empty strings.")
    return [v.strip() for v in raw]


def _parse_allow_group_messages(raw: object) -> bool:
    if raw is None:
        return True
    if not isinstance(raw, bool):
        raise ConfigError("allow_group_messages must be a boolean.")
    return raw


def _parse_default_hours(raw: object) -> int:
    if raw is None:
        return 24
    if not isinstance(raw, int) or raw <= 0:
        raise ConfigError("default_hours must be a positive integer.")
    return raw


def _split_patterns(secret_value: str) -> list[str]:
    return [part.strip() for part in secret_value.split(",") if part.strip()]


def get_runtime_config(profile_override: str | None = None) -> RuntimeConfig:
    """Load runtime config from first matching profile path or defaults."""
    profile_name = resolve_profile_name(profile_override)
    source_path = next((p for p in candidate_profile_paths(profile_name) if p.exists()), None)

    if source_path is None:
        return RuntimeConfig(profile_name=profile_name, source_path=None)

    data = _load_profile_data(source_path)

    confirmation_policy = _parse_confirmation_policy(data.get("confirmation_policy"))
    allowed_recipients = _parse_allowed_recipients(data.get("allowed_recipients"))
    allow_group_messages = _parse_allow_group_messages(data.get("allow_group_messages"))
    default_hours = _parse_default_hours(data.get("default_hours"))

    secret_ref = data.get("allowed_recipients_secret")
    if secret_ref is not None:
        if not isinstance(secret_ref, str) or not secret_ref.startswith("secret://"):
            raise ConfigError("allowed_recipients_secret must be a secret:// URI.")
        try:
            secret_value = resolve_secret_uri(secret_ref)
        except SecretResolutionError as exc:
            raise ConfigError("Unable to resolve profile secrets; backend not configured.") from exc
        allowed_recipients.extend(_split_patterns(secret_value))

    deduped = tuple(dict.fromkeys(allowed_recipients))
    return RuntimeConfig(
        profile_name=profile_name,
        source_path=source_path,
        confirmation_policy=confirmation_policy,
        allowed_recipients=deduped,
        allow_group_messages=allow_group_messages,
        default_hours=default_hours,
    )


def _normalize_phone(raw: str) -> str:
    return "".join(ch for ch in raw if ch.isdigit())


def _match_pattern(recipient: str, pattern: str) -> bool:
    pattern_norm = pattern.strip().lower()
    recipient_norm = recipient.strip().lower()

    if "*" in pattern_norm:
        import fnmatch

        return fnmatch.fnmatch(recipient_norm, pattern_norm)

    if "@" in recipient_norm or "@" in pattern_norm:
        return recipient_norm == pattern_norm

    return _normalize_phone(recipient_norm) == _normalize_phone(pattern_norm)


def recipient_is_allowed(recipient: str, allowed_recipients: tuple[str, ...]) -> bool:
    """Return True if recipient matches any configured allowlist pattern."""
    if not allowed_recipients:
        return False
    return any(_match_pattern(recipient, pattern) for pattern in allowed_recipients)


def requires_confirmation(
    policy: ConfirmationPolicy,
    recipient: str,
    group_chat: bool,
    allowed_recipients: tuple[str, ...],
) -> bool:
    """Compute whether a send action needs explicit user confirmation."""
    if policy == "always":
        return True
    if policy == "never":
        return False
    if policy == "group-only":
        return group_chat
    if policy == "external-only":
        if recipient_is_allowed(recipient, allowed_recipients):
            return False
        return True
    raise ConfigError("Invalid confirmation policy.")
