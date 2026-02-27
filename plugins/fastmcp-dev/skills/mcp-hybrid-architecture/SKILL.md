---
name: mcp-hybrid-architecture
description: >
  Implement a Library-First Hybrid Architecture for MCP servers. Use this skill when
  designing an MCP server that needs its core logic to be reusable by other Python 
  applications, scripts, or CLIs, rather than being tightly coupled to FastMCP decorators.
  Also use when a user asks about "separating concerns", "hybrid MCP architecture",
  "reusable MCP tools", or "library-first MCP". Covers the separation of business 
  logic from the server envelope, context injection, and testing strategies.
---

# MCP Hybrid Architecture (Library-First approach)

When building an MCP server, tying your business logic directly into `@mcp.tool` decorators makes that code inaccessible to other non-MCP tools, CLIs, or downstream applications.

The **Hybrid Architecture** (or Library-First Architecture) solves this by distilling core functionality into standard Python modules, using the MCP server strictly as a lightweight wrapper or envelope.

## 1. Distilling the Core Logic
Your core library files (e.g., `core.py`, `logic.py`, `messages.py`) should **not** import `fastmcp` or rely on the `Context` object directly. They should be written as standard, robust Python functions.

```python
# core.py
def process_data(input_text: str, limit: int = 10) -> list[dict]:
    """Process data strictly as a Python library function."""
    results = [{"item": input_text, "processed": True}] * min(limit, 5)
    return results

def complex_operation(config_path: str, verbose: bool = False) -> str:
    """A complex operation that might be called from a CLI or MCP."""
    if not verbose:
        return "Success"
    return "Operation completed with 5 items processed at 12:00PM."
```

## 2. Setting up the MCP Envelope (server.py)
In your `server.py` file, you import your core logic and either use the `mcp.tool()` hook directly on the function, or wrap it in a lightweight decorator to handle FastMCP specific concerns like `Context` injection or error mapping.

### Approach A: Direct Wrapping (Cleanest)
If your core function doesn't need to report progress or use FastMCP logs, you can register it directly without decorators:

```python
# server.py
from fastmcp import FastMCP
from .core import process_data, complex_operation

mcp = FastMCP("MyHybridServer")

# Register the library functions directly! Type hints and docstrings are auto-mapped.
mcp.tool()(process_data)
mcp.tool(name="run_operation")(complex_operation)
```

### Approach B: Envelope Wrapper (For Context Injection)
If your tool needs MCP-specific capabilities (like `ctx.info()` or `ctx.report_progress()`), you wrap the core library call in an MCP-specific function. **Default to `text_response()`** for the MCP output — agents read text more efficiently than JSON. Only return structured data if a programmatic consumer needs it.

```python
# server.py
from fastmcp import FastMCP, Context
from fastmcp.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult
from utils import text_response
from .core import process_data

mcp = FastMCP("MyHybridServer")

@mcp.tool()
async def process_data_tool(input_text: str, ctx: Context = CurrentContext()) -> ToolResult:
    """Process data and report progress to the MCP client."""
    await ctx.info(f"Starting data processing for {input_text}")

    # Call the clean library function
    results = process_data(input_text)

    await ctx.report_progress(50, 100)
    # Default to text for agent consumption
    return text_response(f"Processed {len(results)} items for '{input_text}'")
```

## 3. Benefits of Hybrid Architecture
- **Reusability**: Your `core.py` can easily be imported into a CLI tool (e.g., using `click` or `typer`) or by other internal company scripts.
- **Testability**: You can write standard `pytest` unit tests against `core.py` without needing to mock or initialize the FastMCP framework.
- **Separation of Concerns**: The MCP file is solely responsible for transport, authorization, context injection, and schema mapping.

## When to Use This Pattern
- 🟢 High complexity logic, heavy data processing, or large codebases.
- 🟢 Projects that also have a CLI component or are deployed as internal Python packages.
- 🔴 Simple 1-2 tool scripts tailored explicitly for an AI agent. (Use the standard monolith pattern for these).
