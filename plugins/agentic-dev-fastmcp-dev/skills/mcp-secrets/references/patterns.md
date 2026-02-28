# Secrets Management Patterns

## Credential Management Tools

Give users tools to manage their stored credentials:

```python
@mcp.tool(annotations={"readOnlyHint": True})
def list_stored_credentials() -> dict:
    """List which credentials are stored (names only, never values)."""
    known_keys = ["api_credentials", "oauth_token", "webhook_secret"]
    return {key: secrets.get(key) is not None for key in known_keys}


@mcp.tool(annotations={"destructiveHint": True})
async def clear_credentials(name: str, ctx: Context = CurrentContext()) -> str:
    """Remove stored credentials. Requires confirmation."""
    result = await ctx.elicit(
        f"Delete credential '{name}'?",
        response_type=["yes", "no"]
    )
    if result.action == "accept" and result.data == "yes":
        secrets.delete(name)
        return f"Credential '{name}' deleted."
    return "Deletion cancelled."
```

## MCPSecretsManager Alternative

For simpler use cases, `secrets_manager.py` provides a self-contained keyring
manager with automatic indexing:

```python
from secrets_manager import MCPSecretsManager

sm = MCPSecretsManager("my-server")

# Stores dict, list, or string values (JSON-serialized automatically)
sm.store_secret("api_key", "sk-abc123")
sm.store_secret("config", {"endpoint": "https://api.example.com"})

# Retrieve
key = sm.retrieve_secret("api_key")
config = sm.retrieve_secret("config")  # Returns dict

# Manage
names = sm.list_secrets()              # ["api_key", "config"]
sm.delete_secret("api_key")
sm.clear_server_secrets()              # Remove all for this server
```

This uses the `com.mcp.{server_name}` service namespace and maintains a
`__secret_index__` in the keychain for discoverability.

## Backend Details

### KeyringStorage

Uses macOS Keychain, Windows Credential Manager, or Linux Secret Service:

```python
from secretstore import KeyringStorage
secrets = KeyringStorage("my-mcp-server")
secrets.save("oauth", {"access_token": "abc", "refresh_token": "xyz"})
```

### EphemeralStorage

In-memory only — for tests:

```python
from secretstore import EphemeralStorage
secrets = EphemeralStorage()
```

### EnvVarStorage

Reads from environment variables with a prefix:

```python
from secretstore import EnvVarStorage
secrets = EnvVarStorage(prefix="MYAPP")
# MYAPP_API_KEY=abc → secrets.get("api") returns {"key": "abc"}
```

Features: auto JSON-encodes complex types, read-only by default (`auto_save=True`
to enable writes), UTF-8 byte length validation for Windows.

### OnePasswordStorage

```python
from secretstore import OnePasswordStorage
secrets = OnePasswordStorage("my-server", vault="Development")
```

Requires 1Password CLI (`op`) installed and configured.

## Security Guidelines

1. **Never return secrets in tool responses** — expose metadata only
2. **Never log secrets** — use generic messages like "Credentials loaded"
3. **Use `serializable=False`** for sensitive context state:
   ```python
   await ctx.set_state("http_client", auth_client, serializable=False)
   ```
4. **Validate before storing** — check credentials work before persisting
5. **Use elicitation** for missing credentials — prompt the user explicitly
6. **Consider `SECRETS_MANAGER_CLEAR`** env var for wiping on server start

## Reference Files

- `secretstore/` — Full backend-agnostic package (4 implementations)
- `secrets_manager.py` — Self-contained keyring manager with indexing
