#!/usr/bin/env python3
"""
Generic MCP Client Test Script

This script serves as a template for testing MCP (Model Context Protocol) servers.
It demonstrates:
- Creating an MCP client with stdio transport
- Implementing an input()-based elicitation handler for authentication
- Connecting to any MCP server and exploring its capabilities
- Calling tools dynamically
- Proper error handling and connection lifecycle management

CUSTOMIZATION GUIDE:
1. Update the MCP_CONFIG below with your server's details
2. Modify tool_calls list to test specific tools
3. Adjust elicitation_handler if your server needs different input handling
4. Add server-specific logic in the test_server() function

Based on MCP_CLIENT_INFO.md documentation.
"""

import asyncio
import os
import sys
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

# ==========================================
# MCP SERVER CONFIGURATION
# ==========================================
# Modify this configuration to test different MCP servers
MCP_CONFIG = {
    "mcpServers": {
        "test-server": {  # Change this name for your server
            "command": "uv",  # Could be "python", "node", etc.
            "args": [
                "--directory",
                os.path.expanduser("~/Downloads/where/findmy-server"),  # Update path to your server
                "run",
                "python",
                "server.py"  # Update to your server's entry point
            ],
            "env": {
                # Add any environment variables your server needs
                # "APPLE_ID": "example@outlook.com",
                # "API_KEY": "your-api-key-here",
                # "ENVFILE_PATH": "/path/to/.env",
            }
        }
    }
}

# ==========================================
# TEST CONFIGURATION
# ==========================================
# Tools to test - modify this list for your server's tools
TOOL_CALLS_TO_TEST = [
    {
        "name": "list_devices",
        "args": {},
        "description": "Test device listing functionality"
    },
    # Add more tools to test here:
    # {
    #     "name": "get_device_info",
    #     "args": {"device_id": "example-id"},
    #     "description": "Test device info retrieval"
    # },
    # {
    #     "name": "list_items",
    #     "args": {},
    #     "description": "Test items listing"
    # }
]

# ==========================================
# ELICITATION HANDLER
# ==========================================

async def elicitation_handler(message: str, response_type: type, params, context):
    """
    Interactive elicitation handler that prompts user for input via terminal.

    This handler will be called when the server needs user authentication
    or other interactive input (like API keys, passwords, etc.).

    Customize this function based on your server's authentication requirements.
    """
    print(f"\n🔐 Server Request: {message}")

    # Handle case where no response schema is provided
    if response_type is None:
        user_response = input("Press Enter to continue (or 'cancel' to abort): ").strip()
        if user_response.lower() == 'cancel':
            return ElicitResult(action="cancel")
        return ElicitResult(action="accept")

    # Inspect the response type to understand what fields are expected
    if hasattr(response_type, '__dataclass_fields__'):
        fields = response_type.__dataclass_fields__
        print(f"📝 Expected fields: {list(fields.keys())}")

        # Collect input for each field
        field_values = {}
        for field_name, field_info in fields.items():
            while True:
                user_input = input(f"Enter {field_name}: ").strip()

                # Allow user to cancel
                if user_input.lower() == 'cancel':
                    return ElicitResult(action="cancel")

                # Allow user to decline
                if user_input.lower() == 'decline':
                    return ElicitResult(action="decline")

                # Basic validation - require non-empty input
                if user_input:
                    field_values[field_name] = user_input
                    break
                else:
                    print(f"❌ {field_name} cannot be empty. Please try again.")

        # Create response using the dataclass constructor
        try:
            response_data = response_type(**field_values)
            print(f"✅ Collected data: {field_values}")
            return response_data  # Return directly - FastMCP will implicitly accept
        except Exception as e:
            print(f"❌ Error creating response: {e}")
            return ElicitResult(action="decline")

    else:
        # Fallback for simple responses
        user_response = input("Your response: ").strip()

        if user_response.lower() == 'cancel':
            return ElicitResult(action="cancel")
        elif user_response.lower() == 'decline' or not user_response:
            return ElicitResult(action="decline")

        # Try to create response with 'value' field (common pattern)
        try:
            response_data = response_type(value=user_response)
            return response_data
        except Exception as e:
            print(f"❌ Error creating response: {e}")
            return ElicitResult(action="decline")

# ==========================================
# TEST FUNCTIONS
# ==========================================

async def test_server_tools(client: Client, tools_to_test: list) -> bool:
    """
    Test specific tools on the MCP server.

    Args:
        client: Connected MCP client
        tools_to_test: List of tool configurations to test

    Returns:
        bool: True if all tests passed
    """
    all_passed = True

    for tool_config in tools_to_test:
        tool_name = tool_config["name"]
        tool_args = tool_config["args"]
        description = tool_config["description"]

        print(f"\n🔍 Testing: {description}")
        print(f"🛠️  Tool: {tool_name}")
        print(f"📝 Args: {tool_args}")

        try:
            result = await client.call_tool(tool_name, tool_args)
            print("✅ Tool call successful!")

            # Display result in various formats
            if hasattr(result, 'data'):
                print(f"📄 Result data: {result.data}")
            if hasattr(result, 'content'):
                print(f"📄 Result content: {result.content}")
                if isinstance(result.content, list) and len(result.content) > 0:
                    for i, content_item in enumerate(result.content):
                        print(f"📄 Content item {i}: {content_item}")
                        if hasattr(content_item, 'text'):
                            print(f"📄 Content text: {content_item.text}")

            # Pretty print if it's text
            if hasattr(result, 'data') and isinstance(result.data, str):
                print(f"\n📊 {tool_name.upper()} RESULT:")
                print(result.data)

        except Exception as e:
            print(f"❌ Error calling {tool_name}: {e}")
            print(f"🔍 Error type: {type(e)}")
            all_passed = False

    return all_passed

async def test_mcp_server():
    """Generic test function for MCP servers."""

    print(f"🚀 Connecting to MCP server via stdio transport")

    # Extract server name from config
    server_name = list(MCP_CONFIG["mcpServers"].keys())[0]
    server_config = MCP_CONFIG["mcpServers"][server_name]

    print(f"📍 Server: {server_name}")
    print(f"🏃 Command: {' '.join(server_config['args'])}")

    client = Client(
        MCP_CONFIG,
        elicitation_handler=elicitation_handler,
        timeout=60.0  # Give plenty of time for user input
    )

    try:
        async with client:
            print("✅ Connected to MCP server")
            print(f"🔗 Connection status: {client.is_connected()}")

            # Test server connectivity
            print("\n📡 Testing server connectivity...")
            await client.ping()
            print("✅ Server ping successful")

            # List available tools
            print("\n🛠️  Discovering available tools...")
            tools = await client.list_tools()
            print(f"📋 Found {len(tools)} tools:")

            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")

                # Check if tool input schema is available
                if hasattr(tool, 'inputSchema'):
                    print(f"    📝 Input schema: {tool.inputSchema}")

            # Test configured tools
            if TOOL_CALLS_TO_TEST:
                print(f"\n🧪 Testing {len(TOOL_CALLS_TO_TEST)} configured tools...")
                tools_test_passed = await test_server_tools(client, TOOL_CALLS_TO_TEST)

                if tools_test_passed:
                    print("\n✅ All tool tests passed!")
                else:
                    print("\n⚠️  Some tool tests failed")
                    return False
            else:
                print("\nℹ️  No tools configured for testing")
                print("   Add tools to TOOL_CALLS_TO_TEST list above")

            return True

    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"🔍 Error type: {type(e)}")
        return False

# ==========================================
# MAIN FUNCTION
# ==========================================

async def main():
    """Main function to run the MCP server test."""
    print("🧪 Generic MCP Client Test Script")
    print("=" * 60)
    print("This script will:")
    print("1. Connect to your configured MCP server via stdio transport")
    print("2. Handle authentication prompts interactively")
    print("3. Discover and list available tools")
    print("4. Test configured tools")
    print("=" * 60)
    print()

    # Display current configuration
    server_name = list(MCP_CONFIG["mcpServers"].keys())[0]
    server_config = MCP_CONFIG["mcpServers"][server_name]
    print(f"🎯 Testing Server: {server_name}")
    print(f"📂 Directory: {server_config['args'][1]}")
    print(f"🏃 Entry Point: {server_config['args'][4]}")
    print(f"🔧 Tools to Test: {len(TOOL_CALLS_TO_TEST)}")
    print()

    success = await test_mcp_server()

    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)

# ==========================================
# SCRIPT ENTRY POINT
# ==========================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)