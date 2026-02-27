"""Lazy iCloud client provider with reset and credential management hooks."""

from __future__ import annotations

import asyncio

from fastmcp import Context
from pyicloud import PyiCloudService

from apple_auth.auth_flow import create_authenticated_client
from apple_auth.credentials_store import AppleCredentialsStore
from secrets_manager import secrets_manager


class AppleClientProvider:
    """Provides a lazily initialized authenticated Apple iCloud client."""

    def __init__(self, store: AppleCredentialsStore):
        self._store = store
        self._client: PyiCloudService | None = None
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get_client(self, ctx: Context) -> PyiCloudService:
        if self._client is not None:
            return self._client

        async with self._get_lock():
            if self._client is None:
                self._client = await create_authenticated_client(ctx, self._store)
            return self._client

    def reset_auth_state(self) -> None:
        self._client = None

    def clear_stored_credentials(self) -> None:
        self._store.clear_credentials()


credentials_store = AppleCredentialsStore(secrets_manager)
apple_client_provider = AppleClientProvider(credentials_store)


async def get_authenticated_client(ctx: Context) -> PyiCloudService:
    return await apple_client_provider.get_client(ctx)


def clear_stored_credentials() -> None:
    apple_client_provider.clear_stored_credentials()


def reset_auth_state_only() -> None:
    apple_client_provider.reset_auth_state()


def reset_auth_state() -> None:
    reset_auth_state_only()
    clear_stored_credentials()
