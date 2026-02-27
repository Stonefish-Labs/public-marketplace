"""System information collection functions"""

import os
import platform
import psutil
import requests
import subprocess
import getpass
import time
import locale
from datetime import datetime
from typing import List, Dict, Any


def safe_subprocess(cmd: List[str], timeout: int = 5) -> str:
    """Safely execute subprocess command with timeout"""
    try:
        return subprocess.check_output(cmd, text=True, timeout=timeout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def get_system_identity() -> List[str]:
    """Get basic system identity information"""
    info = []
    info.append("## 🖥️ System Identity")
    info.append(f"- **Hostname**: {platform.node()}")
    info.append(f"- **Platform**: {platform.system()} {platform.release()}")
    info.append(f"- **Architecture**: {platform.machine()}")
    info.append(f"- **Processor**: {platform.processor()}")
    
    # Serial number (macOS specific)
    if platform.system() == "Darwin":
        serial_output = safe_subprocess(["system_profiler", "SPHardwareDataType"])
        for line in serial_output.split('\n'):
            if 'Serial Number' in line:
                serial_num = line.split(':')[-1].strip()
                info.append(f"- **Serial Number**: {serial_num}")
                break
    
    return info


def get_hardware_info() -> List[str]:
    """Get hardware information (CPU, RAM, GPU)"""
    info = []
    info.append("\n## 🔧 Hardware")
    
    # CPU Information
    cpu_count = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    info.append(f"- **CPU Cores**: {cpu_count} physical, {cpu_logical} logical")
    if cpu_freq:
        info.append(f"- **CPU Frequency**: {cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)")
    info.append(f"- **CPU Usage**: {cpu_percent}%")
    
    # Memory Information
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    info.append(f"- **Total RAM**: {memory.total / (1024**3):.1f} GB")
    info.append(f"- **Available RAM**: {memory.available / (1024**3):.1f} GB ({memory.percent}% used)")
    if swap.total > 0:
        info.append(f"- **Swap**: {swap.total / (1024**3):.1f} GB ({swap.percent}% used)")
    
    # GPU Information
    gpu_info = _get_gpu_info()
    if gpu_info:
        info.extend(gpu_info)
    
    # Battery Information (if available)
    battery_info = _get_battery_info()
    if battery_info:
        info.extend(battery_info)
    
    # Boot time and uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    info.append(f"\n- **Boot Time**: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    info.append(f"- **Uptime**: {uptime.days} days, {uptime.seconds//3600} hours")
    
    return info


def _get_gpu_info() -> List[str]:
    """Get GPU information (platform-specific)"""
    info = []
    
    try:
        if platform.system() == "Darwin":
            gpu_output = safe_subprocess(["system_profiler", "SPDisplaysDataType"])
            if gpu_output:
                info.append("\n### Graphics Cards")
                for line in gpu_output.split('\n'):
                    line = line.strip()
                    if 'Chipset Model:' in line:
                        gpu_name = line.split(':')[-1].strip()
                        info.append(f"- **GPU**: {gpu_name}")
                    elif 'VRAM' in line:
                        vram = line.split(':')[-1].strip()
                        info.append(f"  - **VRAM**: {vram}")
                        
        elif platform.system() == "Linux":
            gpu_output = safe_subprocess(["lspci", "-mm"])
            if gpu_output:
                gpus = [line for line in gpu_output.split('\n') if 'VGA' in line or '3D' in line]
                if gpus:
                    info.append("\n### Graphics Cards")
                    for gpu in gpus[:3]:  # Limit to first 3
                        parts = gpu.split('"')
                        if len(parts) >= 6:
                            info.append(f"- **GPU**: {parts[5]}")
    except Exception:
        pass
    
    return info


def _get_battery_info() -> List[str]:
    """Get battery information (if available)"""
    info = []
    
    try:
        battery = psutil.sensors_battery()
        if battery:
            info.append("\n### Battery")
            info.append(f"- **Charge Level**: {battery.percent:.1f}%")
            
            # Battery status
            if battery.power_plugged:
                info.append("- **Status**: Charging (plugged in)")
            else:
                info.append("- **Status**: On battery")
            
            # Time remaining
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, _ = divmod(remainder, 60)
                if battery.power_plugged:
                    info.append(f"- **Time to Full**: {hours}h {minutes}m")
                else:
                    info.append(f"- **Time Remaining**: {hours}h {minutes}m")
            
            # macOS specific - get more detailed battery info
            if platform.system() == "Darwin":
                try:
                    battery_output = safe_subprocess(["system_profiler", "SPPowerDataType"])
                    if battery_output:
                        for line in battery_output.split('\n'):
                            line = line.strip()
                            if 'Wattage (W):' in line:
                                wattage = line.split(':')[-1].strip()
                                info.append(f"- **Charging Wattage**: {wattage}W")
                            elif 'Cycle Count:' in line:
                                cycles = line.split(':')[-1].strip()
                                info.append(f"- **Cycle Count**: {cycles}")
                            elif 'Condition:' in line:
                                condition = line.split(':')[-1].strip()
                                info.append(f"- **Condition**: {condition}")
                            elif 'Maximum Capacity:' in line:
                                max_capacity = line.split(':')[-1].strip()
                                info.append(f"- **Max Capacity**: {max_capacity}")
                except Exception:
                    pass
            
            # Linux specific - additional battery details
            elif platform.system() == "Linux":
                try:
                    # Try to get power consumption from /sys/class/power_supply/
                    with open('/sys/class/power_supply/BAT0/power_now', 'r') as f:
                        power_now = int(f.read().strip()) / 1000000  # Convert from µW to W
                        info.append(f"- **Power Draw**: {power_now:.1f}W")
                except Exception:
                    pass
                
                try:
                    # Battery health from /sys/class/power_supply/
                    with open('/sys/class/power_supply/BAT0/capacity', 'r') as f:
                        design_capacity = f.read().strip()
                    with open('/sys/class/power_supply/BAT0/charge_full_design', 'r') as f:
                        full_design = f.read().strip()
                    with open('/sys/class/power_supply/BAT0/charge_full', 'r') as f:
                        full_current = f.read().strip()
                        health = (int(full_current) / int(full_design)) * 100
                        info.append(f"- **Battery Health**: {health:.1f}%")
                except Exception:
                    pass
    
    except Exception:
        # No battery or battery detection failed
        pass
    
    return info


def get_display_info() -> List[str]:
    """Get display/monitor information - resolution, refresh rate, HDR status"""
    info = []
    info.append("## 🖥️ Display Information")
    
    try:
        if platform.system() == "Darwin":
            # macOS display detection
            displays = _get_macos_displays()
            if displays:
                for i, display in enumerate(displays, 1):
                    info.append(f"\n### Display {i}")
                    for key, value in display.items():
                        info.append(f"- **{key}**: {value}")
            else:
                info.append("- **Status**: No displays detected")
                
        elif platform.system() == "Linux":
            # Linux display detection
            displays = _get_linux_displays()
            if displays:
                for i, display in enumerate(displays, 1):
                    info.append(f"\n### Display {i}")
                    for key, value in display.items():
                        info.append(f"- **{key}**: {value}")
            else:
                info.append("- **Status**: No displays detected")
                
        elif platform.system() == "Windows":
            # Windows display detection
            displays = _get_windows_displays()
            if displays:
                for i, display in enumerate(displays, 1):
                    info.append(f"\n### Display {i}")
                    for key, value in display.items():
                        info.append(f"- **{key}**: {value}")
            else:
                info.append("- **Status**: No displays detected")
        else:
            info.append("- **Status**: Display detection not supported on this platform")
            
    except Exception as e:
        info.append(f"⚠️ **Display detection error**: {str(e)}")
    
    return info


def _get_macos_displays() -> List[Dict[str, str]]:
    """Get macOS display information using system_profiler"""
    displays = []
    
    try:
        # Get display data
        output = safe_subprocess(["system_profiler", "SPDisplaysDataType", "-json"], timeout=10)
        if not output:
            return displays
            
        import json
        data = json.loads(output)
        
        for gpu in data.get("SPDisplaysDataType", []):
            gpu_displays = gpu.get("spdisplays_ndrvs", [])
            for display in gpu_displays:
                display_info = {}
                
                # Display name/model
                if "_name" in display:
                    display_info["Name"] = display["_name"]
                
                # Resolution
                if "_spdisplays_resolution" in display:
                    display_info["Resolution"] = display["_spdisplays_resolution"]
                
                # Refresh rate
                if "_spdisplays_refresh_rate" in display:
                    display_info["Refresh Rate"] = f"{display['_spdisplays_refresh_rate']} Hz"
                
                # Color depth
                if "_spdisplays_depth" in display:
                    display_info["Color Depth"] = display["_spdisplays_depth"]
                
                # Connection type
                if "_spdisplays_connection_type" in display:
                    display_info["Connection"] = display["_spdisplays_connection_type"]
                
                # HDR support (check for relevant keys)
                hdr_keys = ["_spdisplays_hdr", "_spdisplays_hdr10", "_spdisplays_dolby_vision"]
                hdr_support = any(key in display for key in hdr_keys)
                display_info["HDR Support"] = "Yes" if hdr_support else "Unknown"
                
                if display_info:
                    displays.append(display_info)
                    
    except Exception:
        # Fallback to simpler method
        output = safe_subprocess(["system_profiler", "SPDisplaysDataType"])
        if output:
            display_info = {}
            for line in output.split('\n'):
                line = line.strip()
                if 'Resolution:' in line:
                    display_info["Resolution"] = line.split(':')[-1].strip()
                elif 'Refresh Rate:' in line:
                    display_info["Refresh Rate"] = line.split(':')[-1].strip()
                elif 'Connection Type:' in line:
                    display_info["Connection"] = line.split(':')[-1].strip()
            
            if display_info:
                displays.append(display_info)
    
    return displays


def _get_linux_displays() -> List[Dict[str, str]]:
    """Get Linux display information using xrandr and other tools"""
    displays = []
    
    try:
        # Try xrandr first (most common)
        output = safe_subprocess(["xrandr", "--verbose"])
        if output:
            current_display = {}
            for line in output.split('\n'):
                line = line.strip()
                
                # New display detected
                if ' connected' in line and not line.startswith(' '):
                    if current_display:
                        displays.append(current_display)
                    current_display = {}
                    
                    parts = line.split()
                    if parts:
                        current_display["Name"] = parts[0]
                        current_display["Status"] = "Connected"
                        
                        # Extract resolution from connection line
                        for part in parts:
                            if 'x' in part and part.replace('x', '').replace('+', '').replace('-', '').isdigit():
                                current_display["Resolution"] = part.split('+')[0]
                                break
                
                # Resolution and refresh rate details
                elif line and current_display and ('*' in line or '+' in line):
                    parts = line.split()
                    if parts and 'x' in parts[0]:
                        if '*' in line:  # Current mode
                            current_display["Current Resolution"] = parts[0]
                            # Extract refresh rate
                            for part in parts[1:]:
                                if part.endswith('*') or part.endswith('+'):
                                    rate = part.rstrip('*+')
                                    try:
                                        float(rate)
                                        current_display["Refresh Rate"] = f"{rate} Hz"
                                    except ValueError:
                                        pass
                
                # Brightness and other properties
                elif 'Brightness:' in line:
                    current_display["Brightness"] = line.split(':')[-1].strip()
                elif 'Colorspace:' in line:
                    current_display["Colorspace"] = line.split(':')[-1].strip()
            
            if current_display:
                displays.append(current_display)
        
        # Try alternative methods if xrandr failed
        if not displays:
            # Try using /sys/class/drm
            drm_output = safe_subprocess(["ls", "/sys/class/drm/"])
            if drm_output:
                for line in drm_output.split('\n'):
                    if 'card' in line and 'eDP' in line or 'HDMI' in line or 'DP' in line:
                        displays.append({"Name": line.strip(), "Status": "Detected via DRM"})
                        
    except Exception:
        pass
    
    return displays


def _get_windows_displays() -> List[Dict[str, str]]:
    """Get Windows display information using wmic and PowerShell"""
    displays = []
    
    try:
        # Try PowerShell method first (more detailed)
        ps_cmd = [
            "powershell", "-Command",
            "Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription, RefreshRate, AdapterRAM | Format-List"
        ]
        output = safe_subprocess(ps_cmd, timeout=10)
        
        if output:
            current_display = {}
            for line in output.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "Name" and value:
                        if current_display:
                            displays.append(current_display)
                        current_display = {"Name": value}
                    elif key == "VideoModeDescription" and value:
                        current_display["Resolution"] = value
                    elif key == "RefreshRate" and value and value != "0":
                        current_display["Refresh Rate"] = f"{value} Hz"
                    elif key == "AdapterRAM" and value and value != "0":
                        ram_gb = int(value) / (1024**3)
                        current_display["Video Memory"] = f"{ram_gb:.1f} GB"
            
            if current_display:
                displays.append(current_display)
        
        # Fallback to wmic
        if not displays:
            output = safe_subprocess(["wmic", "desktopmonitor", "get", "ScreenWidth,ScreenHeight,Name"])
            if output:
                lines = [line.strip() for line in output.split('\n') if line.strip()]
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                width, height = parts[1], parts[0]
                                if width.isdigit() and height.isdigit():
                                    displays.append({
                                        "Resolution": f"{width}x{height}",
                                        "Status": "Active"
                                    })
                            except (ValueError, IndexError):
                                pass
                                
    except Exception:
        pass
    
    return displays


def get_network_info() -> List[str]:
    """Get network interface and connectivity information"""
    info = []
    info.append("\n## 🌐 Network")
    
    # Network interfaces
    net_interfaces = psutil.net_if_addrs()
    net_stats = psutil.net_if_stats()
    
    for interface, addresses in net_interfaces.items():
        if interface.startswith('lo') or interface.startswith('utun'):
            continue  # Skip loopback and tunnels for main display
        
        stats = net_stats.get(interface)
        if stats and stats.isup:
            info.append(f"\n### {interface}")
            info.append(f"- **Status**: {'Up' if stats.isup else 'Down'}")
            
            for addr in addresses:
                if addr.family.name == 'AF_INET':  # IPv4
                    info.append(f"- **IPv4**: {addr.address}")
                    if addr.netmask:
                        info.append(f"  - **Netmask**: {addr.netmask}")
                elif addr.family.name == 'AF_INET6':  # IPv6
                    if not addr.address.startswith('fe80'):  # Skip link-local
                        info.append(f"- **IPv6**: {addr.address}")
    
    # Gateway and DNS
    gateway = _get_default_gateway()
    if gateway:
        info.append(f"\n- **Default Gateway**: {gateway}")
    
    dns_servers = _get_dns_servers()
    if dns_servers:
        info.append(f"- **DNS Servers**: {', '.join(dns_servers[:3])}")
    
    # External IP
    external_ip = _get_external_ip()
    info.append(f"- **External IP**: {external_ip}")
    
    # VPN Detection
    vpn_status = _detect_vpn(net_interfaces, net_stats)
    info.append(f"- **VPN Status**: {vpn_status}")
    
    return info


def _get_default_gateway() -> str:
    """Get default gateway address"""
    try:
        if platform.system() == "Darwin":
            output = safe_subprocess(["route", "-n", "get", "default"])
            for line in output.split('\n'):
                if 'gateway:' in line:
                    return line.split(':')[-1].strip()
        elif platform.system() == "Linux":
            output = safe_subprocess(["ip", "route", "show", "default"])
            if output:
                parts = output.split()
                if len(parts) >= 3:
                    return parts[2]
    except Exception:
        pass
    return ""


def _get_dns_servers() -> List[str]:
    """Get configured DNS servers"""
    dns_servers = []
    
    try:
        if platform.system() == "Darwin":
            output = safe_subprocess(["scutil", "--dns"])
            for line in output.split('\n'):
                if 'nameserver[0]' in line:
                    dns = line.split(':')[-1].strip()
                    if dns not in dns_servers:
                        dns_servers.append(dns)
        elif platform.system() == "Linux":
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            dns = line.split()[1]
                            dns_servers.append(dns)
            except Exception:
                pass
    except Exception:
        pass
    
    return dns_servers


def _get_external_ip() -> str:
    """Get external IP address"""
    try:
        response = requests.get('http://checkip.amazonaws.com', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return "Unable to determine"


def _detect_vpn(net_interfaces: Dict, net_stats: Dict) -> str:
    """Detect if VPN is active"""
    try:
        for interface in net_interfaces.keys():
            if any(vpn_name in interface.lower() for vpn_name in ['tun', 'tap', 'vpn', 'utun']):
                stats = net_stats.get(interface)
                if stats and stats.isup:
                    return "Active"
        return "Not detected"
    except Exception:
        return "Unknown"


def get_storage_info() -> List[str]:
    """Get disk and storage information"""
    info = []
    info.append("\n## 💾 Storage")
    
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        try:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Determine disk type
            disk_type = "Fixed"
            if partition.opts and 'removable' in partition.opts:
                disk_type = "Removable"
            elif partition.fstype in ['tmpfs', 'devtmpfs']:
                continue  # Skip temporary filesystems
                
            info.append(f"\n### {partition.device} ({partition.mountpoint})")
            info.append(f"- **Type**: {disk_type} ({partition.fstype})")
            info.append(f"- **Total**: {total_gb:.1f} GB")
            info.append(f"- **Free**: {free_gb:.1f} GB ({100-used_percent:.1f}% free)")
            info.append(f"- **Used**: {used_percent:.1f}%")
            
        except (PermissionError, OSError):
            continue  # Skip inaccessible drives
    
    return info


def get_user_session_info() -> List[str]:
    """Get current user and session information"""
    info = []
    info.append("\n## 👤 User & Session")
    
    # Current user
    current_user = getpass.getuser()
    info.append(f"- **Current User**: {current_user}")
    
    # Try to get full name
    full_name = _get_user_full_name(current_user)
    if full_name:
        info.append(f"- **Full Name**: {full_name}")
    
    # Session info
    try:
        current_process = psutil.Process()
        login_time = datetime.fromtimestamp(current_process.create_time())
        info.append(f"- **Session Start**: {login_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception:
        pass
    
    return info


def _get_user_full_name(username: str) -> str:
    """Get user's full name"""
    try:
        if platform.system() == "Darwin":
            output = safe_subprocess(["id", "-F", username])
            if output and output.strip() != username:
                return output.strip()
        elif platform.system() == "Linux":
            import pwd
            user_info = pwd.getpwnam(username)
            if user_info.pw_gecos:
                full_name = user_info.pw_gecos.split(',')[0]
                if full_name:
                    return full_name
    except Exception:
        pass
    return ""


def get_time_locale_info() -> List[str]:
    """Get time, timezone, and locale information"""
    info = []
    info.append("\n## 🕐 Time & Locale")
    
    now = datetime.now()
    info.append(f"- **Current Time**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Timezone
    try:
        timezone_name = time.tzname[0] if not time.daylight else time.tzname[1]
        info.append(f"- **Timezone**: {timezone_name}")
        
        # UTC offset
        utc_offset = time.timezone if not time.daylight else time.altzone
        offset_hours = -utc_offset // 3600
        offset_sign = '+' if offset_hours >= 0 else '-'
        info.append(f"- **UTC Offset**: UTC{offset_sign}{abs(offset_hours):02d}:00")
    except Exception:
        pass
    
    # System language/locale
    try:
        system_locale = locale.getdefaultlocale()
        if system_locale[0]:
            info.append(f"- **System Language**: {system_locale[0]}")
        if system_locale[1]:
            info.append(f"- **Encoding**: {system_locale[1]}")
    except Exception:
        pass
    
    return info


def get_usb_devices() -> List[str]:
    """Get list of connected USB devices"""
    info = []
    
    try:
        if platform.system() == "Darwin":
            output = safe_subprocess(["system_profiler", "SPUSBDataType"])
            if output:
                info.append("### USB Devices")
                lines = output.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # Look for actual device names (not system metadata)
                    if (line and ':' in line and not line.startswith(' ') and 
                        not any(skip in line.lower() for skip in [
                            'usb', 'bus', 'host controller', 'root hub', 'hub',
                            'product id', 'vendor id', 'version', 'speed', 'location id',
                            'current', 'manufacturer', 'extra operating', 'serial number',
                            'pci device', 'pci revision', 'pci vendor'
                        ])):
                        
                        device_name = line.split(':')[0].strip()
                        # Only include actual device names (longer than 5 chars, contains letters)
                        if (device_name and len(device_name) > 5 and 
                            any(c.isalpha() for c in device_name) and
                            not device_name.lower().startswith('usb')):
                            info.append(f"- **{device_name}**")
                    i += 1
                            
        elif platform.system() == "Linux":
            output = safe_subprocess(["lsusb"])
            if output:
                info.append("### USB Devices")
                for line in output.split('\n'):
                    if line.strip():
                        parts = line.split(' ', 6)
                        if len(parts) >= 7:
                            device_info = parts[6]
                            info.append(f"- **{device_info}**")
                            
        elif platform.system() == "Windows":
            # Windows PowerShell command for USB devices
            output = safe_subprocess(["powershell", "-Command", 
                                    "Get-WmiObject -Class Win32_USBControllerDevice | ForEach-Object { [wmi]($_.Dependent) } | Select-Object Name, DeviceID"])
            if output:
                info.append("### USB Devices")
                for line in output.split('\n')[2:]:  # Skip headers
                    if line.strip():
                        info.append(f"- **{line.strip()}**")
                        
    except Exception:
        info.append("### USB Devices")
        info.append("- *USB device detection not available*")
    
    return info


def get_bluetooth_devices() -> List[str]:
    """Get list of connected Bluetooth devices"""
    info = []
    
    try:
        if platform.system() == "Darwin":
            output = safe_subprocess(["system_profiler", "SPBluetoothDataType"])
            if output:
                info.append("### Bluetooth Devices")
                lines = output.split('\n')
                
                current_section = ""
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Track connection status sections
                    if stripped in ["Connected:", "Not Connected:"]:
                        current_section = stripped
                        continue
                    
                    # Look for device names (indented with colon, under a section)
                    if (stripped and ':' in stripped and 
                        line.startswith('          ') and  # Proper indentation for device names
                        current_section and
                        not any(skip in stripped.lower() for skip in [
                            'address:', 'state:', 'chipset:', 'firmware', 'product id:',
                            'vendor id:', 'transport:', 'supported services', 'discoverable:',
                            'rssi:', 'serial number', 'case version', 'minor type'
                        ])):
                        
                        device_name = stripped.split(':')[0].strip()
                        
                        # Skip controller info and system stuff
                        if (device_name and len(device_name) > 2 and 
                            'Controller' not in device_name):
                            
                            # Add connection status based on current section
                            if current_section == "Connected:":
                                info.append(f"- **{device_name}** (Connected)")
                            elif current_section == "Not Connected:":
                                info.append(f"- **{device_name}** (Paired, not connected)")
                            
        elif platform.system() == "Linux":
            # Try bluetoothctl
            output = safe_subprocess(["bluetoothctl", "devices"])
            if output:
                info.append("### Bluetooth Devices")
                for line in output.split('\n'):
                    if line.startswith('Device'):
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            device_name = parts[2]
                            info.append(f"- **{device_name}**")
                            
        elif platform.system() == "Windows":
            # Windows PowerShell for Bluetooth
            output = safe_subprocess(["powershell", "-Command",
                                    "Get-WmiObject -Class Win32_PnPEntity | Where-Object { $_.Name -like '*Bluetooth*' } | Select-Object Name"])
            if output:
                info.append("### Bluetooth Devices") 
                for line in output.split('\n')[2:]:  # Skip headers
                    if line.strip():
                        info.append(f"- **{line.strip()}**")
                        
    except Exception:
        info.append("### Bluetooth Devices")
        info.append("- *Bluetooth device detection not available*")
    
    return info


def get_connectivity_devices() -> List[str]:
    """Get USB and Bluetooth device information"""
    info = []
    info.append("## 🔌 Connected Devices")
    
    # USB devices
    usb_info = get_usb_devices()
    if len(usb_info) > 1:  # More than just the header
        info.extend(usb_info)
    
    # Bluetooth devices  
    bt_info = get_bluetooth_devices()
    if len(bt_info) > 1:  # More than just the header
        info.append("")  # Add spacing
        info.extend(bt_info)
    
    return info


def get_running_processes() -> List[str]:
    """Get list of running processes with resource usage"""
    info = []
    info.append("## ⚙️ Running Processes")
    
    try:
        # Get all processes and sort by CPU usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'exe', 'cmdline']):
            try:
                pinfo = proc.info
                if pinfo['name'] and pinfo['name'] != '':
                    # Get CPU percent (this call triggers measurement)
                    cpu_percent = proc.cpu_percent()
                    pinfo['cpu_percent'] = cpu_percent
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage, then memory usage
        processes.sort(key=lambda x: (x.get('cpu_percent', 0), x.get('memory_percent', 0)), reverse=True)
        
        # Display top 20 processes
        info.append(f"\n### Top Processes (by CPU/Memory usage)")
        info.append("| PID | Name | CPU% | Memory% | Path |")
        info.append("|-----|------|------|---------|------|")
        
        count = 0
        for proc in processes:
            if count >= 20:
                break
                
            pid = proc.get('pid', 'N/A')
            name = proc.get('name', 'Unknown')[:20]  # Truncate long names
            cpu = proc.get('cpu_percent', 0)
            memory = proc.get('memory_percent', 0)
            
            # Get executable path
            exe_path = proc.get('exe', '')
            if not exe_path and proc.get('cmdline'):
                # Fallback to first command line argument
                cmdline = proc.get('cmdline', [])
                if cmdline:
                    exe_path = cmdline[0]
            
            # Truncate path for display
            if exe_path:
                if len(exe_path) > 40:
                    exe_path = "..." + exe_path[-37:]
            else:
                exe_path = "N/A"
            
            # Only show processes with some activity or important system processes
            if cpu > 0.1 or memory > 0.5 or name.lower() in ['kernel_task', 'systemd', 'init', 'launchd']:
                info.append(f"| {pid} | {name} | {cpu:.1f}% | {memory:.1f}% | {exe_path} |")
                count += 1
        
        # Add process summary
        total_processes = len(processes)
        active_processes = len([p for p in processes if p.get('cpu_percent', 0) > 0])
        info.append(f"\n**Summary**: {total_processes} total processes, {active_processes} active")
        
    except Exception as e:
        info.append(f"⚠️ **Error collecting process information**: {str(e)}")
    
    return info


def get_network_ports() -> List[str]:
    """Get list of open network ports and listening services"""
    info = []
    info.append("## 🌐 Network Ports")
    
    try:
        # Get network connections - try with different approaches for permissions
        try:
            connections = psutil.net_connections(kind='inet')
        except psutil.AccessDenied:
            # Fallback to connections without process info
            try:
                connections = psutil.net_connections(kind='inet', pid=None)
            except Exception:
                # Last resort - get connections for current process only
                connections = psutil.Process().connections(kind='inet')
        
        # Group by listening ports
        listening_ports = {}
        established_connections = []
        
        for conn in connections:
            try:
                if conn.status == psutil.CONN_LISTEN and conn.laddr:
                    # This is a listening port
                    port_key = f"{conn.laddr.ip}:{conn.laddr.port}"
                    if port_key not in listening_ports:
                        # Get process info
                        proc_name = "Unknown"
                        proc_exe = "N/A"
                        if conn.pid:
                            try:
                                proc = psutil.Process(conn.pid)
                                proc_name = proc.name()
                                try:
                                    proc_exe = proc.exe() or "N/A"
                                except (psutil.AccessDenied, OSError):
                                    proc_exe = "Access denied"
                            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                                proc_name = "Access denied"
                        
                        listening_ports[port_key] = {
                            'port': conn.laddr.port,
                            'ip': conn.laddr.ip,
                            'protocol': 'TCP' if conn.type == 1 else 'UDP',
                            'process': proc_name,
                            'executable': proc_exe,
                            'pid': conn.pid
                        }
                
                elif conn.status == psutil.CONN_ESTABLISHED and conn.laddr and conn.raddr:
                    # This is an established connection
                    established_connections.append({
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}",
                        'pid': conn.pid
                    })
                    
            except Exception:
                continue
        
        # Display listening ports
        if listening_ports:
            info.append("\n### Listening Ports")
            info.append("| Port | Protocol | Bind Address | Process | PID |")
            info.append("|------|----------|--------------|---------|-----|")
            
            # Sort by port number
            sorted_ports = sorted(listening_ports.values(), key=lambda x: x['port'])
            
            for port_info in sorted_ports:
                port = port_info['port']
                protocol = port_info['protocol']
                ip = port_info['ip']
                process = port_info['process'][:25]  # Truncate long process names
                pid = port_info['pid'] or 'N/A'
                
                # Show bind address (0.0.0.0 means all interfaces)
                bind_addr = "All interfaces" if ip == "0.0.0.0" else ip
                if ip == "127.0.0.1":
                    bind_addr = "Localhost only"
                elif ip.startswith("::"):
                    bind_addr = "IPv6"
                
                info.append(f"| {port} | {protocol} | {bind_addr} | {process} | {pid} |")
        
        # Display established connections summary (top 10)
        if established_connections:
            info.append(f"\n### Active Connections")
            info.append(f"**Total established connections**: {len(established_connections)}")
            
            # Group by remote host
            remote_hosts = {}
            for conn in established_connections:
                remote_ip = conn['remote'].split(':')[0]
                if remote_ip not in remote_hosts:
                    remote_hosts[remote_ip] = 0
                remote_hosts[remote_ip] += 1
            
            # Show top remote hosts
            if remote_hosts:
                info.append("\n**Top remote hosts by connection count**:")
                sorted_hosts = sorted(remote_hosts.items(), key=lambda x: x[1], reverse=True)
                for host, count in sorted_hosts[:10]:
                    info.append(f"- {host}: {count} connection{'s' if count > 1 else ''}")
        
        # Add summary
        total_listening = len(listening_ports)
        total_established = len(established_connections)
        info.append(f"\n**Summary**: {total_listening} listening ports, {total_established} active connections")
        
    except Exception as e:
        info.append(f"⚠️ **Error collecting network port information**: {str(e)}")
    
    return info
