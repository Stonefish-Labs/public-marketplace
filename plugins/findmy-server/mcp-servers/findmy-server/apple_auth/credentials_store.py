"""Credential storage layer for Apple account authentication."""

from __future__ import annotations

from typing import Protocol


APPLE_ID_SECRET = "APPLE_ID"
APPLE_PASSWORD_SECRET = "APPLE_PASSWORD"


class SecretsBackend(Protocol):
    def store_secret(self, secret_name: str, content: str) -> None: ...
    def retrieve_secret(self, secret_name: str) -> str | None: ...
    def delete_secret(self, secret_name: str) -> None: ...


class AppleCredentialsStore:
    """Stores and retrieves Apple account credentials via a backend."""

    def __init__(self, backend: SecretsBackend):
        self._backend = backend

    def get_apple_id(self) -> str:
        return self._backend.retrieve_secret(APPLE_ID_SECRET) or ""

    def get_apple_password(self) -> str:
        return self._backend.retrieve_secret(APPLE_PASSWORD_SECRET) or ""

    def store_credentials(self, apple_id: str, password: str) -> None:
        self._backend.store_secret(APPLE_ID_SECRET, apple_id)
        self._backend.store_secret(APPLE_PASSWORD_SECRET, password)

    def clear_credentials(self) -> None:
        for secret_name in (APPLE_ID_SECRET, APPLE_PASSWORD_SECRET):
            try:
                self._backend.delete_secret(secret_name)
            except Exception:
                pass
