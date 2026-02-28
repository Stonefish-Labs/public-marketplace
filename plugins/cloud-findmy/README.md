# Apple Find My MCP Server

An MCP (Model Context Protocol) server that provides access to Apple's Find My network for device tracking and management.

## Overview

This server allows you to interact with your Apple devices through the Find My network, providing location tracking, battery status, and device information via MCP-compatible tools.

## Features

### Device Management
- **List Devices**: Retrieve all devices associated with your Apple account
- **Device Info**: Get detailed information including location, battery level, and status for specific devices
- **Caching**: 5-minute cache for improved performance and reduced API calls

### Administration
- **Cache Management**: Clear caches, refresh data, or reset authentication
- **Credential Management**: Securely store and manage Apple ID credentials
- **Authentication**: Interactive Apple ID authentication with secure credential storage

## Tools

### Device Tools
- `list_devices()` - List all Find My devices with basic information
- `get_device_info(discovery_id)` - Get comprehensive details for a specific device

### Admin Tools
- `clear_stored_credentials()` - Remove stored Apple ID and password from secure storage
- `refresh_cache()` - Clear data cache and force fresh data retrieval

## Installation

### Prerequisites
- Python 3.11+
- Apple ID with Find My enabled

### Install Dependencies
```bash
cd mcp-servers/findmy-server
uv sync
```

### Build
```bash
cd mcp-servers/findmy-server
uv build
```

## Usage

### Running the Server
```bash
cd mcp-servers/findmy-server

# FastMCP stdio mode (default)
uv run server

# Or directly
python server.py

# FastMCP HTTP mode
PORT=8000 uv run server
```

### Configuration
- **HOST**: Server host (default: 127.0.0.1)
- **PORT**: If set, server runs using `streamable-http` on this port
- **FINDMY_CACHE_TIMEOUT**: Cache timeout in minutes (default: 5)

### MCP Configuration Example

```json

"findmy-server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "${CLAUDE_PLUGIN_ROOT}/mcp-servers/findmy-server",
        "run",
        "server"
      ]
    },
```

## Authentication

The server uses interactive authentication for your Apple ID. On first use:

1. Provide your Apple ID email when prompted
2. Enter your password (stored securely using keyring)
3. Complete 2FA if required

Credentials are stored securely and reused for subsequent requests.

## Apple Auth Component

Apple-specific authentication is isolated in `mcp-servers/findmy-server/apple_auth/` for reuse across future Apple MCP servers:

- `mcp-servers/findmy-server/apple_auth/credentials_store.py` - Apple credential storage abstraction
- `mcp-servers/findmy-server/apple_auth/prompts.py` - FastMCP elicitation prompts for credential and verification collection
- `mcp-servers/findmy-server/apple_auth/auth_flow.py` - iCloud 2FA/2SA authentication flow orchestration
- `mcp-servers/findmy-server/apple_auth/client_provider.py` - Lazy authenticated client provider and reset hooks

## Dependencies

- `fastmcp>=3.0.0` - MCP server framework
- `pyicloud>=2.0.2` - Apple iCloud/Find My API client
- `keyring>=25.6.0` - Secure credential storage

## Security

- Credentials are stored securely using system keyring
- Authentication state is cached per session
- Data is cached for 5 minutes to minimize API calls
- No sensitive data is logged or stored permanently

## License

This project is provided as-is for personal use with Apple's Find My service.
