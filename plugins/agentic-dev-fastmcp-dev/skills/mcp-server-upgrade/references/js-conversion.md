# JavaScript/TypeScript → Python FastMCP 3.x Conversion

## Conversion Workflow

1. Inventory the JS server — identify all tools, resources, prompts, dependencies
2. Map each JS tool to a Python function with type annotations
3. Replace JS dependencies with Python equivalents
4. Test with in-memory client for tool parity

## Pattern Mapping

### Server Creation

```javascript
// JS
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
const server = new Server({ name: "my-server", version: "1.0.0" }, {
  capabilities: { tools: {} }
});
```

```python
# Python
from fastmcp import FastMCP
mcp = FastMCP(name="my-server", instructions="...", on_duplicate="error")
```

### Tool Registration

JS uses monolithic handlers with manual schema definitions. Python uses one
function per tool with type annotations generating the schema automatically.

```javascript
// JS — manual schema + switch statement
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "search",
    description: "Search items",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string" },
        limit: { type: "number", default: 10 }
      },
      required: ["query"]
    }
  }]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "search") {
    const { query, limit } = request.params.arguments;
    const results = await doSearch(query, limit || 10);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
});
```

```python
# Python — schema from type annotations, one function per tool
@mcp.tool
def search(query: str, limit: int = 10) -> dict:
    """Search items."""
    return do_search(query, limit)
```

### Zod → Python Types

| Zod | Python |
|---|---|
| `z.string()` | `str` |
| `z.number()` | `int` or `float` |
| `z.boolean()` | `bool` |
| `z.enum(["a", "b"])` | `Literal["a", "b"]` |
| `z.string().optional()` | `str \| None = None` |
| `z.number().min(1).max(100)` | `Annotated[int, Field(ge=1, le=100)]` |
| `z.string().describe("...")` | Docstring or `Field(description="...")` |
| `z.object({...})` | Pydantic `BaseModel` or `dict` |
| `z.array(z.string())` | `list[str]` |

### Error Handling

```javascript
// JS
return { content: [{ type: "text", text: "Error: bad input" }], isError: true };
```

```python
# Python
from fastmcp.exceptions import ToolError
raise ToolError("Bad input")
```

### Transport Startup

```javascript
// JS
const transport = new StdioServerTransport();
await server.connect(transport);
```

```python
# Python
if __name__ == "__main__":
    mcp.run()  # stdio by default
```

### Async Patterns

```javascript
// JS — Promise
async function fetchData(url) {
  const response = await fetch(url);
  return await response.json();
}
```

```python
# Python — httpx
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()
```

## Dependency Mapping

| JS Package | Python Equivalent |
|---|---|
| `node-fetch` / `axios` | `httpx` |
| `zod` | Type annotations + `pydantic` |
| `fs` / `fs/promises` | `pathlib` / `aiofiles` |
| `path` | `pathlib.Path` |
| `child_process` | `subprocess` / `asyncio.create_subprocess_exec` |
| `crypto` | `hashlib` / `secrets` (stdlib) |
| `dotenv` | `python-dotenv` or `os.getenv` |
| `winston` / `pino` | `logging` (stdlib) |
| `better-sqlite3` | `sqlite3` (stdlib) |
| `pg` / `mysql2` | `asyncpg` / `aiomysql` |
| `@napi-rs/keyring` | `keyring` / `secretstore` |
| `cheerio` | `beautifulsoup4` |
| `puppeteer` | `playwright` |
| `dayjs` / `moment` | `datetime` (stdlib) |
| `uuid` | `uuid` (stdlib) |
| `lodash` | Usually unnecessary — Python builtins suffice |

## Verification

After conversion, verify tool parity:

```python
from server import mcp
from fastmcp import Client

async def verify():
    async with Client(transport=mcp) as client:
        tools = await client.list_tools()
        for t in tools:
            print(f"{t.name}: {t.inputSchema}")
        # Compare against original JS server's tool list
```
