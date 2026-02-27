# FastMCP 2.x → 3.x Breaking Changes Checklist

Work through each item. Every one of these will cause runtime errors if not fixed.

## 1. Import Path

```python
# OLD
from mcp.server.fastmcp import FastMCP
# NEW
from fastmcp import FastMCP
```

## 2. WSTransport Removed

```python
# OLD
from fastmcp.client.transports import WSTransport
# NEW
from fastmcp.client.transports import StreamableHttpTransport
```

## 3. Auth Providers — No Auto Env Loading

```python
# OLD (2.x auto-loaded from env)
auth = GitHubProvider()

# NEW (3.x — explicit)
import os
auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
)
```

## 4. Component Control → Server Level

```python
# OLD
my_tool.enable()
my_tool.disable()

# NEW
mcp.disable(names={"my_tool"}, components=["tool"])
mcp.enable(names={"my_tool"}, components=["tool"])
mcp.enable(tags={"public"}, only=True)  # Allowlist mode
```

## 5. Listing Returns Lists

```python
# OLD (returned dicts)
tools = await server.get_tools()
tool = tools["my_tool"]

# NEW (returns lists)
tools = await server.list_tools()
tool = next((t for t in tools if t.name == "my_tool"), None)
```

## 6. PromptMessage → Message

```python
# OLD
from mcp.types import PromptMessage

# NEW
from fastmcp.prompts import Message

@mcp.prompt
def my_prompt() -> Message:
    return Message("Hello")
```

## 7. Async State Management

```python
# OLD (sync)
ctx.set_state("key", "value")
value = ctx.get_state("key")

# NEW (async)
await ctx.set_state("key", "value")
value = await ctx.get_state("key")
```

## 8. State Serialization

Values must be JSON-serializable by default:

```python
await ctx.set_state("count", 42)  # OK

# For non-serializable objects:
await ctx.set_state("client", http_client, serializable=False)
```

## 9. Mount Prefix → Namespace

```python
# OLD
mcp.mount(sub_server, prefix="api")
# NEW
mcp.mount(sub_server, namespace="api")
```

## 10. Tag Filtering → Enable/Disable

```python
# OLD
mcp = FastMCP(include_tags={"public"}, exclude_tags={"admin"})

# NEW
mcp = FastMCP()
mcp.enable(tags={"public"}, only=True)
mcp.disable(tags={"admin"})
```

## 11. Tool Serializer → ToolResult

```python
# OLD
@mcp.tool(tool_serializer=my_serializer)
def my_tool(): ...

# NEW
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

@mcp.tool
def my_tool() -> ToolResult:
    return ToolResult(content=[TextContent(type="text", text="result")])
```

## 12. Tool Transformations → Transforms

```python
# OLD
mcp.add_tool_transformation(my_transform)

# NEW
from fastmcp.server.transforms import ToolTransform
mcp.add_transform(ToolTransform(...))
```

## 13. Proxy Creation

```python
# OLD
proxy = FastMCP.as_proxy("http://remote/mcp")

# NEW
from fastmcp.server import create_proxy
proxy = create_proxy("http://remote/mcp", name="MyProxy")
```

## 14. Metadata Namespace

```python
# OLD
{"_meta": {"_fastmcp": {"version": "1.0"}}}

# NEW
{"_meta": {"fastmcp": {"version": "1.0"}}}
```

## 15. Environment Variable Rename

```bash
# OLD
FASTMCP_SHOW_CLI_BANNER=false

# NEW
FASTMCP_SHOW_SERVER_BANNER=false
```

## 16. Decorators Return Original Function

`@mcp.tool` now returns your function unchanged. This is a behavior improvement —
direct calls work now, which is great for testing:

```python
@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

assert greet("World") == "Hello, World!"  # Works in 3.x
```

## 17. Constructor Changes

```python
# OLD
mcp = FastMCP(ui=UIConfig(...))

# NEW
from fastmcp import AppConfig
mcp = FastMCP(app=AppConfig(...))
```

Many constructor kwargs were removed. If you were passing kwargs not listed in the
3.x docs, check the upgrade guide at https://gofastmcp.com/development/upgrade-guide

## Deprecation Warnings (Still Work, Will Break Later)

| Deprecated | Replacement |
|---|---|
| `mount(prefix=)` | `mount(namespace=)` |
| `include_tags` / `exclude_tags` | `enable()` / `disable()` |
| `tool_serializer` | Return `ToolResult` |
| `add_tool_transformation()` | `add_transform(ToolTransform())` |
| `FastMCP.as_proxy()` | `create_proxy()` |
| `enabled` param on decorators | `mcp.enable()` / `mcp.disable()` |
| `on_duplicate_tools=` / `on_duplicate_resources=` / `on_duplicate_prompts=` | `on_duplicate=` |

## New 3.x Features to Adopt

After fixing breaks, consider:

- `@mcp.tool(timeout=30.0)` — tool execution timeouts
- `@mcp.tool(version="2.0")` — backward-compatible versioning
- `fastmcp.json` — canonical deployment config
- `CurrentContext()` — preferred context access pattern
- `on_duplicate="error"` — catch registration bugs (`on_duplicate_tools` was renamed to `on_duplicate`)
- `FileSystemProvider` — modular tool organization with hot-reload
- Transforms — namespace, filter, reshape components
