"""FastMCP elicitation helpers for Apple authentication."""

from __future__ import annotations

from dataclasses import dataclass

from fastmcp import Context

from apple_auth.credentials_store import AppleCredentialsStore


@dataclass
class AppleCredentials:
    apple_id: str
    password: str


async def elicit_credentials(ctx: Context, store: AppleCredentialsStore) -> tuple[str, str]:
    """Request Apple ID credentials and persist them securely."""
    credentials = await ctx.elicit(
        "Please provide your Apple ID credentials:",
        response_type=AppleCredentials,
    )

    if credentials.action == "cancel":
        raise ValueError("Authentication cancelled")
    if credentials.action == "decline":
        raise ValueError("Apple ID credentials required")

    apple_id = credentials.data.apple_id.strip()
    password = credentials.data.password.strip()

    if not apple_id:
        raise ValueError("Apple ID cannot be empty")
    if not password:
        raise ValueError("Password cannot be empty")

    store.store_credentials(apple_id, password)
    await ctx.info("Apple ID and password stored securely")
    return apple_id, password


async def get_2fa_code(ctx: Context) -> str:
    """Request a valid 6-digit Apple 2FA code."""
    while True:
        code_result = await ctx.elicit(
            "Enter 6-digit verification code from your Apple device:",
            response_type=str,
        )
        if code_result.action == "cancel":
            raise ValueError("Authentication cancelled")
        if code_result.action == "decline":
            raise ValueError("Verification code required")

        code = code_result.data.strip()
        if len(code) == 6 and code.isdigit():
            return code

        await ctx.info("Invalid code format. Enter 6 digits.")


async def select_device(ctx: Context, devices: list[dict]) -> int:
    """Request trusted device selection for legacy Apple 2SA flow."""
    device_list: list[str] = []
    for index, device in enumerate(devices):
        label = device.get("deviceName") or f"SMS to {device.get('phoneNumber', 'Unknown')}"
        device_list.append(f"{index}: {label}")
    await ctx.info("Available devices:\n" + "\n".join(device_list))

    device_result = await ctx.elicit(
        f"Select device (0-{len(devices) - 1}):",
        response_type=[str(index) for index in range(len(devices))],
    )
    if device_result.action == "cancel":
        raise ValueError("Authentication cancelled")
    if device_result.action == "decline":
        raise ValueError("Device selection required")

    return int(device_result.data)


async def get_2sa_code(ctx: Context) -> str:
    """Request Apple 2SA code."""
    code_result = await ctx.elicit("Enter verification code:", response_type=str)
    if code_result.action == "cancel":
        raise ValueError("Authentication cancelled")
    if code_result.action == "decline":
        raise ValueError("Verification code required")

    code = code_result.data.strip()
    if not code:
        raise ValueError("Code cannot be empty")
    return code
