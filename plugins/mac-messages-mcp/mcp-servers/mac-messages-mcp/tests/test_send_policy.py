from pathlib import Path

import pytest

from mac_messages_mcp import server


class _FakeResult:
    def __init__(self, action: str) -> None:
        self.action = action


class _FakeContext:
    def __init__(self, action: str) -> None:
        self._action = action
        self.elicit_calls = 0

    async def elicit(self, message: str, response_type=None):
        self.elicit_calls += 1
        return _FakeResult(self._action)


def _write_profile(base: Path, content: str) -> None:
    profile_path = base / ".config" / "mac-messages-mcp" / "profiles" / "default.toml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(content)


@pytest.mark.asyncio
async def test_policy_always_decline_blocks_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_profile(tmp_path, 'confirmation_policy = "always"\n')

    called = {"value": False}

    def _fake_send(*args, **kwargs) -> str:
        called["value"] = True
        return "sent"

    monkeypatch.setattr(server, "core_send_message", _fake_send)
    ctx = _FakeContext(action="decline")

    result = await server.send_message_tool(
        recipient="+15551234567",
        message="hello",
        group_chat=False,
        ctx=ctx,
    )

    assert "declined" in result.lower()
    assert ctx.elicit_calls == 1
    assert called["value"] is False


@pytest.mark.asyncio
async def test_policy_never_sends_without_elicitation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_profile(tmp_path, 'confirmation_policy = "never"\n')

    monkeypatch.setattr(server, "core_send_message", lambda **_: "sent")
    ctx = _FakeContext(action="accept")

    result = await server.send_message_tool(
        recipient="+15551234567",
        message="hello",
        group_chat=False,
        ctx=ctx,
    )

    assert result == "sent"
    assert ctx.elicit_calls == 0


@pytest.mark.asyncio
async def test_external_only_skips_confirmation_for_allowlisted_recipient(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_profile(
        tmp_path,
        'confirmation_policy = "external-only"\nallowed_recipients = ["+15551234567"]\n',
    )

    monkeypatch.setattr(server, "core_send_message", lambda **_: "sent")
    ctx = _FakeContext(action="accept")

    result = await server.send_message_tool(
        recipient="+15551234567",
        message="hello",
        group_chat=False,
        ctx=ctx,
    )

    assert result == "sent"
    assert ctx.elicit_calls == 0
