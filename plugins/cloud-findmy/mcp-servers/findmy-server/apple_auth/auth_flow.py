"""Apple iCloud authentication flow orchestration."""

from __future__ import annotations

from fastmcp import Context
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException, PyiCloudFailedLoginException

from apple_auth.credentials_store import AppleCredentialsStore
from apple_auth.prompts import elicit_credentials, get_2fa_code, get_2sa_code, select_device


async def authenticate_client(ctx: Context, client: PyiCloudService) -> PyiCloudService:
    """Ensure an iCloud client is fully authenticated."""
    await ctx.info("Checking authentication status...")

    if not client.requires_2fa and not client.requires_2sa and client.is_trusted_session:
        await ctx.info("Already authenticated")
        return client

    if client.requires_2fa:
        await ctx.info("2FA required")
        await ctx.info("Check your Apple devices for a verification code")

        code = await get_2fa_code(ctx)
        if not client.validate_2fa_code(code):
            raise ValueError("2FA verification failed")

        if not client.is_trusted_session:
            await ctx.info("Establishing trusted session...")
            if not client.trust_session():
                await ctx.info("Trusted session failed - you may need to verify again")

    elif client.requires_2sa:
        await ctx.info("2SA required")
        devices = client.trusted_devices
        device_index = await select_device(ctx, devices)
        selected_device = devices[device_index]

        if not client.send_verification_code(selected_device):
            raise ValueError("Failed to send verification code")

        await ctx.info(f"Code sent to {selected_device.get('deviceName', 'device')}")
        code = await get_2sa_code(ctx)
        if not client.validate_verification_code(selected_device, code):
            raise ValueError("2SA verification failed")

        await ctx.info("2SA successful")

    await ctx.info("Authentication complete")
    return client


async def create_authenticated_client(ctx: Context, store: AppleCredentialsStore) -> PyiCloudService:
    """Create and authenticate an iCloud client from stored or elicited credentials."""
    try:
        apple_id = store.get_apple_id()
        password = store.get_apple_password()

        if apple_id and password:
            await ctx.info(f"Found stored credentials for: {apple_id}")
            return await authenticate_client(ctx, PyiCloudService(apple_id, password))

        if apple_id and not password:
            await ctx.info(f"Found Apple ID: {apple_id} (using pyicloud keyring for password)")
            return await authenticate_client(ctx, PyiCloudService(apple_id))

    except PyiCloudFailedLoginException:
        await ctx.info("Stored credentials failed, requesting new credentials")

    await ctx.info("Credentials required")
    apple_id, password = await elicit_credentials(ctx, store)

    try:
        return await authenticate_client(ctx, PyiCloudService(apple_id, password))
    except PyiCloudFailedLoginException as exc:
        raise ValueError(f"Authentication failed: {exc}") from exc
    except PyiCloudAPIResponseException as exc:
        raise ValueError(f"iCloud API error: {exc}") from exc
