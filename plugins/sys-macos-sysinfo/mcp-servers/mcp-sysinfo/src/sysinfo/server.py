#!/usr/bin/env python3
"""
System Information MCP Server - Modular Tool Design
Provides focused system information tools for efficient diagnostics.
"""

import os
from datetime import datetime
from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from .collectors import (
    get_system_identity,
    get_hardware_info,
    get_network_info,
    get_storage_info,
    get_user_session_info,
    get_time_locale_info,
    get_connectivity_devices,
    get_running_processes,
    get_network_ports,
    get_display_info
)


def text_response(text: str) -> ToolResult:
    """Return raw text as a ToolResult without JSON wrapping overhead."""
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=None
    )


# Initialize FastMCP server
mcp = FastMCP(
    name="SystemInfoServer",
    instructions="""
    Provides modular system information tools for efficient diagnostics.
    Use individual tools for specific info, or get_full_system_report for everything.
    Perfect for system debugging, environment analysis, and troubleshooting.
    """
)


@mcp.tool
def get_system_summary() -> ToolResult:
    """Get essential system overview - hostname, OS, CPU, RAM, uptime.
    
    Quick system identity check without heavy data collection.
    Perfect for basic system verification and health checks.
    """
    info_sections = []
    info_sections.append("# System Summary")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        # Just the essentials from system identity and hardware
        identity_info = get_system_identity()
        hardware_info = get_hardware_info()
        
        # Extract key lines only
        info_sections.extend(identity_info)
        
        # Add just CPU, RAM, and uptime from hardware
        for line in hardware_info:
            if any(keyword in line for keyword in ['CPU Cores:', 'CPU Usage:', 'Total RAM:', 'Available RAM:', 'Boot Time:', 'Uptime:']):
                info_sections.append(line)
                
    except Exception as e:
        info_sections.append(f"⚠️ **Error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_hardware_details() -> ToolResult:
    """Get comprehensive hardware information - CPU, RAM, GPU, storage overview.
    
    Detailed hardware specs including performance metrics and device detection.
    Use for hardware diagnostics and system capability assessment.
    """
    info_sections = []
    info_sections.append("# Hardware Details")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_hardware_info())
    except Exception as e:
        info_sections.append(f"⚠️ **Hardware detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_network_status() -> ToolResult:
    """Get network configuration and connectivity - interfaces, IPs, DNS, VPN status.
    
    Complete network diagnostics including external connectivity and VPN detection.
    Essential for troubleshooting network issues and security analysis.
    """
    info_sections = []
    info_sections.append("# Network Status")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_network_info())
    except Exception as e:
        info_sections.append(f"⚠️ **Network detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_storage_analysis() -> ToolResult:
    """Get disk and storage analysis - all partitions, capacity, usage.
    
    Comprehensive storage overview including all mounted volumes and usage stats.
    Critical for disk space management and storage troubleshooting.
    """
    info_sections = []
    info_sections.append("# Storage Analysis")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_storage_info())
    except Exception as e:
        info_sections.append(f"⚠️ **Storage detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_connected_devices() -> ToolResult:
    """Get USB and Bluetooth device information.
    
    Lists all connected USB devices and paired/active Bluetooth devices.
    Useful for peripheral troubleshooting and device inventory.
    """
    info_sections = []
    info_sections.append("# Connected Devices")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_connectivity_devices())
    except Exception as e:
        info_sections.append(f"⚠️ **Device detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_user_environment() -> ToolResult:
    """Get user session and locale information - current user, timezone, language.
    
    User context including session details, timezone, and system language settings.
    Important for environment-specific troubleshooting and localization issues.
    """
    info_sections = []
    info_sections.append("# User Environment")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_user_session_info())
        info_sections.extend(get_time_locale_info())
    except Exception as e:
        info_sections.append(f"⚠️ **Environment detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_running_processes() -> ToolResult:
    """Get list of running processes with resource usage and executable paths.
    
    Shows top processes by CPU/memory usage with PIDs, names, and executable paths.
    Essential for performance analysis, troubleshooting resource issues, and security auditing.
    """
    info_sections = []
    info_sections.append("# Running Processes")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        from .collectors import get_running_processes as get_processes_data
        info_sections.extend(get_processes_data())
    except Exception as e:
        info_sections.append(f"⚠️ **Process detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_open_ports() -> ToolResult:
    """Get list of open network ports and listening services.
    
    Shows listening ports with associated processes and active network connections.
    Critical for security analysis, service monitoring, and network troubleshooting.
    """
    info_sections = []
    info_sections.append("# Open Network Ports")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        info_sections.extend(get_network_ports())
    except Exception as e:
        info_sections.append(f"⚠️ **Port detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_display_info() -> ToolResult:
    """Get connected display information - resolution, refresh rate, HDR status.
    
    Shows details for all connected monitors including resolution, refresh rates,
    connection types, and HDR capabilities. Essential for display troubleshooting
    and multi-monitor setup verification.
    """
    info_sections = []
    info_sections.append("# Display Information")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        from .collectors import get_display_info as get_display_data
        info_sections.extend(get_display_data())
    except Exception as e:
        info_sections.append(f"⚠️ **Display detection error**: {str(e)}")
    
    return text_response("\n".join(info_sections))


@mcp.tool
def get_full_system_report() -> ToolResult:
    """Get complete system analysis - runs all diagnostic tools.
    
    Comprehensive system report including hardware, network, storage, 
    devices, and user environment. Use for complete system analysis
    and thorough troubleshooting sessions.
    """
    info_sections = []
    info_sections.append("# Complete System Report")
    info_sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    try:
        # Collect all information sections
        info_sections.extend(get_system_identity())
        info_sections.extend(get_hardware_info())
        info_sections.extend(get_display_info())
        info_sections.extend(get_network_info())
        info_sections.extend(get_storage_info())
        info_sections.extend(get_connectivity_devices())
        from .collectors import get_running_processes as get_processes_data
        info_sections.extend(get_processes_data())
        info_sections.extend(get_network_ports())
        info_sections.extend(get_user_session_info())
        info_sections.extend(get_time_locale_info())
        
    except Exception as e:
        info_sections.append(f"\n⚠️ **Error collecting system info**: {str(e)}")
    
    # Footer
    info_sections.append("\n---")
    info_sections.append("*Complete system analysis finished*")
    
    return text_response("\n".join(info_sections))


def run_server():
    """Run the MCP server with proper configuration"""
    mcp_host = os.getenv("HOST", "127.0.0.1")
    mcp_port = os.getenv("PORT", None)
    
    if mcp_port:
        mcp.run(port=int(mcp_port), host=mcp_host, transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    run_server()