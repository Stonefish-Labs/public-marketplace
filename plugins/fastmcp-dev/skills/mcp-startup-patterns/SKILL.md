---
name: mcp-startup-patterns
description: >
  Prevent MCP server startup timeouts caused by blocking initialization code. Use this
  skill when an MCP server needs OAuth, token refresh, API connections, or any async
  setup that could block the MCP handshake. Triggered by: "server times out on startup",
  "Cursor can't connect to MCP server", "OAuth blocks server start", "lifespan blocking",
  "lazy load credentials", "deferred initialization", or "server startup too slow".
  Covers three patterns: lazy singleton (OAuth/first-time auth), background warmup task
  (token refresh), and lifespan-safe resource initialization.
---

# MCP Server Startup Patterns

## Why This Matters

MCP clients (Cursor, Claude Desktop, VS Code) launch the server process and immediately
send an `initialize` RPC. They expect a response within ~5 seconds. **Any blocking code
before `mcp.run()` can service that handshake causes a timeout.**

The lifespan function is the most common trap: its startup phase (everything before
`yield`) runs **before the server can respond to `initialize`**. Putting OAuth,
user-interactive prompts, or slow network calls there silently starves the handshake.

## The Anti-Pattern

```python
# ❌ NEVER DO THIS — blocks initialize response until OAuth completes
@asynccontextmanager
async def lifespan(server):
    token = await do_oauth_browser_flow()   # user opens browser, clicks… minutes pass
    yield {"token": token}                  # server can't handshake until this line

mcp = FastMCP("MyServer", lifespan=lifespan)
```

```python
# ❌ ALSO WRONG — blocks at module load, before mcp.run() is even called
token = asyncio.run(fetch_token_from_network())   # never do this at module level
mcp = FastMCP("MyServer")
```

## Decision: Which Pattern to Use?

| Situation | Pattern |
|---|---|
| First-time OAuth / user hasn't authenticated yet | **A — Lazy Singleton** |
| Token refresh using a stored refresh_token | **B — Background Warmup Task** |
| HTTP client pool, DB connection, config file | **C — Lifespan (safe)** |

---

## Pattern A — Lazy Singleton (OAuth / First-Time Auth)

The server starts instantly. On the **first tool call** that needs auth, the credential
check and elicitation happen there, where `ctx.elicit()` is available.

See `assets/lazy_auth.py` for the full implementation.

**Key rules:**
- Module-level state is `None` — no I/O
- An `asyncio.Lock` prevents race conditions when two tools call simultaneously
- Uses double-checked locking (`if _client is None` before AND inside the lock)
- Pairs with `secretstore` so the flow only triggers once across restarts

```python
_client: MyClient | None = None
_init_lock: asyncio.Lock | None = None

def _lock() -> asyncio.Lock:
    global _init_lock
    if _init_lock is None:
        _init_lock = asyncio.Lock()
    return _init_lock

async def get_client(ctx: Context) -> MyClient:
    global _client
    if _client is not None:
        return _client                       # fast path — already initialized
    async with _lock():
        if _client is None:                  # double-check after acquiring lock
            creds = secrets.get("oauth_token")
            if not creds:
                # ✅ elicitation is fine here — we're inside a tool call, not lifespan
                result = await ctx.elicit("Connect to MyService?", response_type=None)
                if result.action != "accept":
                    raise ToolError("Authorization required")
                creds = await _run_oauth_flow()
                secrets.save("oauth_token", creds)
            _client = MyClient(creds["token"])
    return _client
```

---

## Pattern B — Background Warmup Task (Token Refresh)

For operations that are **fast and reliable** (refreshing a stored token via HTTP), use
`asyncio.create_task()` in lifespan. The task fires after `yield` — the server is
already up and serving `initialize` before the refresh runs.

See `assets/background_warmup.py` for the full implementation.

**Key rules:**
- `asyncio.create_task()` returns immediately — does not block the lifespan yield
- Tools `await` the task only if they actually need the result
- If the task failed (network error), tools fall back to the stored credential
- Always `cancel()` the task in the lifespan teardown

```python
@asynccontextmanager
async def lifespan(server: FastMCP):
    # ✅ create_task returns immediately — server can respond to initialize
    warmup = asyncio.create_task(_refresh_token_if_needed())
    yield {"warmup": warmup}
    warmup.cancel()                          # cancel on shutdown

async def _refresh_token_if_needed():
    creds = secrets.get("oauth_token")
    if creds and _token_is_expiring(creds):
        refreshed = await do_token_refresh(creds["refresh_token"])
        secrets.save("oauth_token", refreshed)
    return secrets.get("oauth_token")

@mcp.tool
async def my_tool(ctx: Context = CurrentContext()):
    warmup: asyncio.Task = ctx.lifespan_context["warmup"]
    try:
        creds = await asyncio.wait_for(asyncio.shield(warmup), timeout=5.0)
    except (asyncio.TimeoutError, asyncio.CancelledError):
        creds = secrets.get("oauth_token")   # fall back to whatever is stored
    ...
```

---

## Pattern C — Lifespan (Safe Resources Only)

Use lifespan only for fast, non-interactive initialization: HTTP client pools, DB
connection pools, config parsing. These complete in milliseconds and don't require
user input.

```python
@asynccontextmanager
async def lifespan(server: FastMCP):
    # ✅ httpx.AsyncClient() is synchronous and fast
    async with httpx.AsyncClient(timeout=30.0) as http:
        db = await create_db_pool(os.getenv("DATABASE_URL"))
        yield {"http": http, "db": db}
        await db.close()

mcp = FastMCP("MyServer", lifespan=lifespan)

@mcp.tool
async def query(sql: str, ctx: Context = CurrentContext()) -> list[dict]:
    db = ctx.lifespan_context["db"]
    return await db.fetch_all(sql)
```

**What belongs in lifespan:**
- `httpx.AsyncClient` / `aiohttp.ClientSession`
- DB / Redis connection pools (if the URL is already known from env vars)
- Loaded config files or parsed schemas

**What does NOT belong in lifespan:**
- OAuth flows (require user interaction)
- Any `ctx.elicit()` call (not available in lifespan)
- Network calls that could be slow or fail intermittently
- First-time credential setup

---

## Checklist

Before shipping a server with any async initialization:

- [ ] No `asyncio.run()` at module level
- [ ] No blocking network/OAuth calls before `mcp.run()`
- [ ] Lifespan (if used) only contains fast, non-interactive setup
- [ ] First-time OAuth uses Pattern A (lazy singleton)
- [ ] Token refresh uses Pattern B (background task) or Pattern A
- [ ] Tools that need auth call a `get_client(ctx)` helper — not the credential directly
- [ ] `asyncio.Lock` guards the lazy-init critical section
