"""Secret reference URI resolution helpers."""

from __future__ import annotations

import os


class SecretResolutionError(Exception):
    """Raised when a secret reference cannot be resolved."""


def resolve_secret_uri(uri: str) -> str:
    """
    Resolve a v1 secret URI.

    Supported in v1:
    - secret://env/ENV_VAR_NAME

    Placeholder-only backends in v1 (fail closed):
    - bitwarden
    - 1password
    - keychain
    """
    if not isinstance(uri, str) or not uri.startswith("secret://"):
        raise SecretResolutionError("Invalid secret URI format.")

    remainder = uri[len("secret://") :]
    backend, sep, key_path = remainder.partition("/")
    if not sep or not backend or not key_path:
        raise SecretResolutionError("Secret URI must be secret://<backend>/<path-or-key>.")

    if backend == "env":
        value = os.getenv(key_path)
        if value is None or value == "":
            raise SecretResolutionError("Secret backend configured but env var is not set.")
        return value

    if backend in {"bitwarden", "1password", "keychain"}:
        raise SecretResolutionError(
            f"Secret backend '{backend}' is not configured for this server instance."
        )

    raise SecretResolutionError(f"Unsupported secret backend '{backend}'.")
