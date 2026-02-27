"""Compatibility shim for legacy authentication imports."""

from apple_auth.auth_flow import authenticate_client  # noqa: F401
from apple_auth.client_provider import credentials_store
from apple_auth.auth_flow import create_authenticated_client as _create_authenticated_client


async def create_authenticated_client(ctx):
    return await _create_authenticated_client(ctx, credentials_store)
