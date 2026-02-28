"""Compatibility shim for legacy credential imports."""

from apple_auth.client_provider import credentials_store
from apple_auth.prompts import (  # noqa: F401
    AppleCredentials,
    elicit_credentials as _elicit_credentials,
    get_2fa_code,
    get_2sa_code,
    select_device,
)


async def elicit_credentials(ctx):
    return await _elicit_credentials(ctx, credentials_store)


async def get_apple_id_from_secrets() -> str:
    return credentials_store.get_apple_id()


async def get_apple_password_from_secrets() -> str:
    return credentials_store.get_apple_password()
