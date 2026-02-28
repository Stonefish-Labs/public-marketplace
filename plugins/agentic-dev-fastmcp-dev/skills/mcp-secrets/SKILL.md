---
name: mcp-secrets
description: >
  Manage secrets and credentials in MCP servers using the secretstore package.
  Use this skill when an MCP server needs API keys, tokens, or credentials,
  when integrating keychain-based storage, when choosing a secrets backend,
  or when someone asks "how to store secrets in MCP", "credential management
  for MCP server", "keychain integration", or "secure API key storage". Covers
  secretstore backends (Keyring, Ephemeral, EnvVar, 1Password), integration
  patterns, and security guidelines.
---

# MCP Secrets Management

MCP servers frequently need API keys and credentials. Environment variables work
for simple cases but are fragile. The `secretstore` package provides a consistent
interface across backends so your server works on desktop (keychain), in containers
(env vars), and in teams (1Password) without code changes.

## Quick Start

```bash
uv add "secretstore[keyring]"  # For desktop/local dev
```

```python
from secretstore import KeyringStorage

secrets = KeyringStorage("my-mcp-server")

# Store
secrets.save("api", {"key": "sk-abc123", "endpoint": "https://api.example.com"})

# Retrieve
creds = secrets.get("api")  # Returns dict or None

# Delete
secrets.delete("api")
```

## Backend Selection

| Backend | Install | Best For |
|---|---|---|
| `EphemeralStorage` | (included) | Testing — in-memory, lost on exit |
| `KeyringStorage` | `secretstore[keyring]` | Desktop apps — OS keychain encryption |
| `EnvVarStorage` | (included) | Containers/CI — reads from env vars |
| `OnePasswordStorage` | `secretstore[onepassword]` | Teams — shared vault access |

## MCP Integration Pattern

> **Startup Safety:** `secrets.get()` is a fast, synchronous local-cache read — safe
> to call anywhere. However, **never trigger `ctx.elicit()` or an OAuth flow inside a
> `lifespan` function** — that blocks the MCP `initialize` handshake and causes clients
> like Cursor to time out. Always elicit credentials inside a tool call. See the
> `mcp-startup-patterns` skill for lazy-singleton and background-warmup patterns.

```python
from fastmcp import FastMCP, Context
from fastmcp.dependencies import CurrentContext
from secretstore import KeyringStorage

mcp = FastMCP(name="MyAPI", instructions="...")
secrets = KeyringStorage("my-api-server")

# ✅ Credentials checked lazily on first tool call — server starts instantly
@mcp.tool
async def call_api(endpoint: str, ctx: Context = CurrentContext()) -> dict:
    creds = secrets.get("api_credentials")
    if not creds:
        # ctx.elicit() is safe here — we're inside a tool call, not lifespan
        result = await ctx.elicit("API key not found. Enter your API key:", response_type=str)
        if result.action != "accept":
            raise ToolError("API key required")
        secrets.save("api_credentials", {"api_key": result.data})
        creds = {"api_key": result.data}
    # Use credentials...
    return {"status": "ok"}
```

Read `references/patterns.md` for credential management tools, the
MCPSecretsManager alternative, and security guidelines.

## Security Rules

1. **Never return secret values** in tool responses — return `"api_key_set": True` instead
2. **Never log secrets** — log `"Credentials loaded"` not the actual values
3. **Use `serializable=False`** when storing sensitive objects in context state
4. **Use elicitation** to request missing credentials — don't silently fail
