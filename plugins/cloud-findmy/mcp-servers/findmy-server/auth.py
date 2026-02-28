"""Compatibility shim for legacy auth imports."""

from apple_auth.client_provider import (  # noqa: F401
    clear_stored_credentials,
    get_authenticated_client,
    reset_auth_state,
    reset_auth_state_only,
)

