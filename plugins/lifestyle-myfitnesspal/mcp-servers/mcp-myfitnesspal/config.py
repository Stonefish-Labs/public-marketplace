"""Profile-based configuration and secret resolution for the MyFitnessPal MCP server."""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

APP_NAME = "mfp-mcp"
PROFILE_ENV_VAR = "MFP_MCP_PROFILE"
LEGACY_COOKIES_ENV_VAR = "MFP_COOKIES"
_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class ConfigError(RuntimeError):
    """Raised when profile or secret setup is invalid."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Resolved runtime configuration."""

    profile_name: str
    profile_path: Path | None
    mfp_cookies: str | None


def resolve_profile_name(explicit_profile: str | None = None) -> str:
    """Resolve profile name using explicit arg, env var, then default."""
    name = explicit_profile or os.getenv(PROFILE_ENV_VAR) or "default"
    if not _PROFILE_NAME_RE.fullmatch(name):
        raise ConfigError("Invalid profile name. Use letters, numbers, '_' or '-'.")
    return name


def _profile_candidates(profile_name: str) -> list[Path]:
    """Return profile candidates in precedence order."""
    candidates: list[Path] = []

    project_path = Path.cwd() / ".config" / APP_NAME / "profiles" / f"{profile_name}.toml"
    candidates.append(project_path)

    xdg_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_home:
        candidates.append(Path(xdg_home) / APP_NAME / "profiles" / f"{profile_name}.toml")

    candidates.append(Path.home() / ".config" / APP_NAME / "profiles" / f"{profile_name}.toml")
    return candidates


def _load_profile(profile_name: str) -> tuple[dict[str, Any], Path] | tuple[None, None]:
    """Load first profile file found by precedence."""
    for candidate in _profile_candidates(profile_name):
        if candidate.exists() and candidate.is_file():
            raw = tomllib.loads(candidate.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ConfigError("Profile file is invalid.")
            return raw, candidate
    return None, None


def _resolve_secret_uri(value: str) -> str:
    """Resolve a secret URI, currently supporting env backend only."""
    parsed = urlparse(value)
    if parsed.scheme != "secret":
        raise ConfigError("Secret references must use secret:// URI format.")

    backend = parsed.netloc
    secret_key = parsed.path.lstrip("/")
    if not backend or not secret_key:
        raise ConfigError("Secret reference is invalid.")

    if backend == "env":
        secret = os.getenv(secret_key)
        if not secret:
            raise ConfigError("Configuration required: referenced env secret is not set.")
        return secret

    if backend in {"bitwarden", "1password", "keychain"}:
        raise ConfigError(f"Configuration required: secret backend '{backend}' is not configured.")

    raise ConfigError(f"Configuration required: unknown secret backend '{backend}'.")


def load_runtime_config(explicit_profile: str | None = None) -> RuntimeConfig:
    """Resolve runtime config from profile + secret references."""
    profile_name = resolve_profile_name(explicit_profile)
    profile_data, profile_path = _load_profile(profile_name)

    cookies_value: str | None = None
    if profile_data:
        cookies_ref = profile_data.get("mfp_cookies")
        if cookies_ref is not None:
            if not isinstance(cookies_ref, str) or not cookies_ref.startswith("secret://"):
                raise ConfigError("Profile field 'mfp_cookies' must be a secret:// reference.")
            cookies_value = _resolve_secret_uri(cookies_ref)

    # Backward-compatible fallback for existing deployments.
    if cookies_value is None:
        cookies_value = os.getenv(LEGACY_COOKIES_ENV_VAR)

    return RuntimeConfig(
        profile_name=profile_name,
        profile_path=profile_path,
        mfp_cookies=cookies_value,
    )
