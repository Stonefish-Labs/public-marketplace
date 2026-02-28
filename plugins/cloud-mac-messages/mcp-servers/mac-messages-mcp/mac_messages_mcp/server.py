#!/usr/bin/env python3
"""Mac Messages MCP server entrypoint."""

import logging
import os
import sys

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.exceptions import ToolError

from mac_messages_mcp.config import ConfigError, get_runtime_config, requires_confirmation
from mac_messages_mcp.messages import (
    check_addressbook_access,
    check_contacts,
    check_imessage_availability,
    check_messages_db_access,
    format_find_contact,
    fuzzy_search_messages,
    get_chats,
    get_recent_messages,
    send_message as core_send_message,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mac_messages_mcp")


mcp = FastMCP(
    "MessageBridge",
    instructions=(
        "Bridge for interacting with the macOS Messages app. "
        "Use this to search messages, inspect contacts, and send iMessage/SMS. "
        "Requires Full Disk Access for the host terminal application."
    ),
    on_duplicate="error",
)


READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
    "openWorldHint": False,
}


mcp.tool(name="find_contact", annotations=READ_ONLY_ANNOTATIONS)(format_find_contact)
mcp.tool(name="check_addressbook", annotations=READ_ONLY_ANNOTATIONS)(check_addressbook_access)
mcp.tool(name="check_db_access", annotations=READ_ONLY_ANNOTATIONS)(check_messages_db_access)
mcp.tool(name="get_chats", annotations=READ_ONLY_ANNOTATIONS)(get_chats)
mcp.tool(name="check_contacts", annotations=READ_ONLY_ANNOTATIONS)(check_contacts)
mcp.tool(name="check_imessage_availability", annotations=READ_ONLY_ANNOTATIONS)(
    check_imessage_availability
)


@mcp.tool(name="get_recent_messages", annotations=READ_ONLY_ANNOTATIONS)
def get_recent_messages_tool(hours: int = 24, contact: str | None = None) -> str:
    """Get recent messages, optionally filtered by contact."""
    return get_recent_messages(hours=hours, contact=contact)


@mcp.tool(name="fuzzy_search_messages", annotations=READ_ONLY_ANNOTATIONS)
def fuzzy_search_messages_tool(
    search_term: str,
    hours: int = 24,
    threshold: float = 0.6,
) -> str:
    """Fuzzy search recent messages for text similarity matches."""
    return fuzzy_search_messages(search_term=search_term, hours=hours, threshold=threshold)


@mcp.tool(
    name="send_message",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def send_message_tool(
    recipient: str,
    message: str,
    group_chat: bool = False,
    profile: str | None = None,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Send a message with configurable confirmation policy.

    Confirmation policy comes from profile config:
    - always
    - never
    - external-only
    - group-only
    """
    try:
        config = get_runtime_config(profile)
    except ConfigError as exc:
        raise ToolError(str(exc)) from exc

    if group_chat and not config.allow_group_messages:
        return "Group messages are disabled by runtime policy for the selected profile."

    should_confirm = requires_confirmation(
        policy=config.confirmation_policy,
        recipient=recipient,
        group_chat=group_chat,
        allowed_recipients=config.allowed_recipients,
    )
    if should_confirm:
        result = await ctx.elicit(
            (
                f"Send message to '{recipient}'?\n\n"
                f"Policy: {config.confirmation_policy}\n"
                f"Group chat: {group_chat}\n"
                f"Message preview: {message[:240]}"
            ),
            response_type=None,
        )
        if result.action == "decline":
            return "Message send declined by user."
        if result.action == "cancel":
            return "Message send cancelled by user."
        if result.action != "accept":
            return "Message send not confirmed; no action taken."

    return core_send_message(recipient=recipient, message=message, group_chat=group_chat)


@mcp.tool(name="get_runtime_policy", annotations=READ_ONLY_ANNOTATIONS)
def get_runtime_policy(profile: str | None = None) -> str:
    """Return effective runtime policy details for the selected profile."""
    try:
        cfg = get_runtime_config(profile)
    except ConfigError as exc:
        return f"Configuration error: {exc}"

    source = str(cfg.source_path) if cfg.source_path else "defaults (no profile file found)"
    allowlist = ", ".join(cfg.allowed_recipients) if cfg.allowed_recipients else "none"
    return (
        "Runtime policy\n"
        f"- profile: {cfg.profile_name}\n"
        f"- source: {source}\n"
        f"- confirmation_policy: {cfg.confirmation_policy}\n"
        f"- allow_group_messages: {cfg.allow_group_messages}\n"
        f"- allowed_recipients: {allowlist}"
    )


@mcp.resource("messages://recent/{hours}")
def get_recent_messages_resource(hours: int = 24) -> str:
    """Resource that provides recent messages."""
    return get_recent_messages(hours=hours)


@mcp.resource("messages://contact/{contact}/{hours}")
def get_contact_messages_resource(contact: str, hours: int = 24) -> str:
    """Resource that provides messages from a specific contact."""
    return get_recent_messages(hours=hours, contact=contact)


def run_server() -> None:
    """Run the MCP server with transport selection and error handling."""
    try:
        logger.info("Starting Mac Messages MCP server...")
        port = os.getenv("PORT")
        if port:
            mcp.run(
                port=int(port),
                host=os.getenv("HOST", "127.0.0.1"),
                transport="streamable-http",
            )
        else:
            mcp.run()
    except Exception as exc:
        logger.error("Failed to start server: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
