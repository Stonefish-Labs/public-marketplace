# System Information MCP Server

A modular FastMCP server providing focused system diagnostic tools for efficient troubleshooting and environment analysis. Each tool targets specific system aspects for optimal performance and clarity.

## 🚀 Features

### 📊 Modular Tool Design
- **10 specialized tools** for targeted diagnostics
- **Efficient data collection** with minimal overhead
- **Raw text output** for optimal performance
- **Cross-platform compatibility** (macOS, Linux, Windows)

### 🔧 Available Tools

| Tool | Purpose | Key Information |
|------|---------|----------------|
| `get_system_summary` | Quick system overview | Hostname, OS, CPU, RAM, uptime |
| `get_hardware_details` | Comprehensive hardware specs | CPU cores, memory, GPU detection |
| `get_display_info` | Display/monitor analysis | Resolution, refresh rate, HDR status |
| `get_network_status` | Network diagnostics | Interfaces, IPs, DNS, VPN detection |
| `get_storage_analysis` | Storage overview | Disk usage, partitions, filesystem types |
| `get_connected_devices` | Peripheral inventory | USB and Bluetooth devices |
| `get_user_environment` | Session context | User info, timezone, locale settings |
| `get_running_processes` | Process analysis | Top processes by CPU/memory usage |
| `get_open_ports` | Network security | Listening ports and services |
| `get_full_system_report` | Complete analysis | All diagnostics in one comprehensive report |

## Installation

```bash
# Clone and setup
git clone <repository>
cd mcp-sysinfo

# Install dependencies
uv add fastmcp psutil requests

# Test the server
uv run python main.py
```

## Usage

### MCP Configuration

Add to your MCP client configuration:

#### Local/stdio Configuration
```json
{
  "mcpServers": {
    "sysinfo": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-sysinfo", "python", "main.py"]
    }
  }
}
```

#### Remote/HTTP Configuration
```json
{
  "mcpServers": {
    "sysinfo": {
      "type": "http",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

For HTTP mode, set the `PORT` environment variable:
```bash
PORT=8000 uv run python main.py
```

### Tool Usage Examples

#### Quick System Check
```python
# Get essential system overview
result = await client.call_tool("get_system_summary", {})
```

#### Targeted Diagnostics
```python
# Network troubleshooting
network_info = await client.call_tool("get_network_status", {})

# Storage analysis
storage_info = await client.call_tool("get_storage_analysis", {})

# Security audit
ports_info = await client.call_tool("get_open_ports", {})
```

#### Complete System Analysis
```python
# Full diagnostic report
full_report = await client.call_tool("get_full_system_report", {})
```

## Platform Support

- **macOS** 10.15+ (tested on Apple Silicon)
- **Linux** Ubuntu/Debian-based distributions
- **Windows** 10/11 (basic support)

## Architecture

```
src/sysinfo/
├── __init__.py          # Package exports
├── collectors.py        # Modular info collection functions
└── server.py           # FastMCP server implementation
main.py                 # Entry point
```

### Key Design Principles

- **Modular Tools**: Each diagnostic function is a separate MCP tool for targeted usage
- **Performance Optimized**: Raw text output without JSON wrapping overhead
- **Error-resilient**: Graceful handling of missing/inaccessible data
- **Cross-platform**: Platform-specific detection with intelligent fallbacks
- **Agent-friendly**: Clean markdown output optimized for LLM consumption
- **Minimal Dependencies**: Uses only `fastmcp`, `psutil`, and `requests`

## Development

### Testing
```bash
# Test with in-memory client
uv run python test_refactored.py

# Test individual collectors
uv run python -c "from src.sysinfo.collectors import get_hardware_info; print(get_hardware_info())"
```

### Adding New Collectors

1. Add function to `collectors.py`
2. Export in `__init__.py`
3. Call from `server.py` tool
4. Test cross-platform compatibility

## License

MIT License - see LICENSE file for details.
