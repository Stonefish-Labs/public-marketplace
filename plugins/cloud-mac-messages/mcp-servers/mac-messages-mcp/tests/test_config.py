from pathlib import Path

import pytest

from mac_messages_mcp.config import ConfigError, get_runtime_config, resolve_profile_name


def _write_profile(base: Path, name: str, content: str) -> Path:
    profile_path = base / ".config" / "mac-messages-mcp" / "profiles" / f"{name}.toml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(content)
    return profile_path


def test_default_profile_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MAC_MESSAGES_MCP_PROFILE", raising=False)
    assert resolve_profile_name() == "default"


def test_invalid_profile_name_raises() -> None:
    with pytest.raises(ConfigError):
        resolve_profile_name("../bad")


def test_loads_project_profile_by_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write_profile(
        tmp_path,
        "default",
        'confirmation_policy = "group-only"\nallow_group_messages = true\n',
    )

    cfg = get_runtime_config()
    assert cfg.confirmation_policy == "group-only"
    assert cfg.source_path is not None
    assert str(cfg.source_path).endswith("default.toml")


def test_resolves_allowed_recipients_secret_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALLOWED_RECIPIENTS", "+15551234567,alice@example.com")
    _write_profile(
        tmp_path,
        "default",
        'allowed_recipients_secret = "secret://env/ALLOWED_RECIPIENTS"\n',
    )

    cfg = get_runtime_config()
    assert "+15551234567" in cfg.allowed_recipients
    assert "alice@example.com" in cfg.allowed_recipients


def test_unsupported_secret_backend_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_profile(
        tmp_path,
        "default",
        'allowed_recipients_secret = "secret://keychain/messages/allowlist"\n',
    )

    with pytest.raises(ConfigError, match="Unable to resolve profile secrets"):
        get_runtime_config()
