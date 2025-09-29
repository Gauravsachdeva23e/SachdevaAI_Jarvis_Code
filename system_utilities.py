"""
Enhanced System Utilities for Jarvis AI Assistant
Provides additional system control and monitoring features
"""

import psutil
import platform
import socket
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
async def get_system_info() -> str:
    """
    Get comprehensive system information including CPU, memory, disk usage, etc.
    
    Use this when the user asks about system performance, computer specs, or hardware info.
    Example prompts:
    - "System की जानकारी बताओ"
    - "RAM कितनी है?"
    - "CPU usage क्या है?"
    """
    try:
        # Basic system info
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()
        
        # CPU info
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024**3), 2)  # GB
        memory_used = round(memory.used / (1024**3), 2)
        memory_percent = memory.percent
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 2)  # GB
        disk_used = round(disk.used / (1024**3), 2)
        disk_percent = round((disk.used / disk.total) * 100, 1)
        
        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        result = f"""System Information:
━━━━━━━━━━━━━━━━━━━━
🖥️  OS: {system} {release}
⚙️  Architecture: {machine}
🔧  Processor: {processor[:50]}...
💾  CPU Cores: {cpu_count}
📊  CPU Usage: {cpu_usage}%

💽  Memory: {memory_used}GB / {memory_total}GB ({memory_percent}% used)
💿  Disk: {disk_used}GB / {disk_total}GB ({disk_percent}% used)

⏰  Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return "System information retrieve करने में error आया।"

@tool
async def get_running_processes(limit: int = 10) -> str:
    """
    Get list of top running processes by CPU or memory usage.
    
    Args:
        limit: Number of processes to show (default 10)
    
    Use this when user asks about running programs or what's using system resources.
    Example prompts:
    - "कौन से processes चल रहे हैं?"
    - "Top programs बताओ"
    - "Memory ज्यादा कौन use कर रहा है?"
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        result = f"Top {limit} Running Processes:\n━━━━━━━━━━━━━━━━━━━━\n"
        
        for i, proc in enumerate(processes[:limit], 1):
            name = proc['name'][:20] if proc['name'] else 'Unknown'
            cpu = proc['cpu_percent'] or 0
            memory = proc['memory_percent'] or 0
            pid = proc['pid']
            
            result += f"{i:2d}. {name:<20} | CPU: {cpu:5.1f}% | RAM: {memory:5.1f}% | PID: {pid}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting processes: {e}")
        return "Process information retrieve करने में error आया।"

@tool  
async def get_network_info() -> str:
    """
    Get network information including IP addresses, network usage, etc.
    
    Use this when user asks about internet connection, IP address, or network stats.
    Example prompts:
    - "मेरा IP address क्या है?"
    - "Network की speed कितनी है?"
    - "Internet connection ठीक है?"
    """
    try:
        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        
        # Get network statistics
        net_io = psutil.net_io_counters()
        
        result = f"""Network Information:
━━━━━━━━━━━━━━━━━━━━
🌐  Hostname: {hostname}
🏠  Local IP: {local_ip}

📊  Network Usage:
   📤 Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB
   📥 Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB
   📦 Packets Sent: {net_io.packets_sent:,}
   📦 Packets Received: {net_io.packets_recv:,}

🔌  Network Interfaces:"""
        
        for interface, addrs in list(interfaces.items())[:3]:  # Show first 3 interfaces
            result += f"\n   • {interface}:"
            for addr in addrs:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    result += f" {addr.address}"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting network info: {e}")
        return "Network information retrieve करने में error आया।"

@tool
async def cleanup_system() -> str:
    """
    Perform basic system cleanup - clear temp files, empty recycle bin, etc.
    
    Use this when user asks to clean system, free up space, or optimize performance.
    Example prompts:
    - "System clean करो"
    - "Temp files delete करो"  
    - "Space free करो"
    """
    try:
        cleanup_commands = [
            "del /q /f /s %TEMP%\\*",
            "del /q /f /s C:\\Windows\\Temp\\*",
            "cleanmgr /sagerun:1"
        ]
        
        results = []
        for cmd in cleanup_commands[:1]:  # Only run temp cleanup for safety
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    results.append("✅ Temporary files cleaned")
                else:
                    results.append("⚠️ Some cleanup operations failed")
            except subprocess.TimeoutExpired:
                results.append("⏰ Cleanup operation timed out")
            except Exception as e:
                results.append(f"❌ Cleanup failed: {str(e)[:50]}")
        
        return f"System Cleanup Results:\n━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(results)
        
    except Exception as e:
        logger.error(f"Error in system cleanup: {e}")
        return "System cleanup करने में error आया।"

@tool
async def get_installed_programs(limit: int = 15) -> str:
    """
    Get list of installed programs on Windows.
    
    Args:
        limit: Number of programs to show (default 15)
    
    Use this when user asks what software is installed.
    Example prompts:
    - "कौन से programs install हैं?"
    - "Software list बताओ"
    """
    try:
        # Use PowerShell to get installed programs
        ps_command = """
        Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
        Select-Object DisplayName, DisplayVersion, Publisher | 
        Where-Object {$_.DisplayName} | 
        Sort-Object DisplayName
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            programs = []
            
            for line in lines[3:]:  # Skip headers
                if line.strip():
                    parts = line.split(None, 2)
                    if len(parts) >= 1:
                        programs.append(parts[0])
            
            programs = programs[:limit]
            program_list = "\n".join([f"{i+1:2d}. {prog}" for i, prog in enumerate(programs)])
            
            return f"Installed Programs ({len(programs)} shown):\n━━━━━━━━━━━━━━━━━━━━\n{program_list}"
        else:
            return "Could not retrieve installed programs list."
            
    except Exception as e:
        logger.error(f"Error getting installed programs: {e}")
        return "Installed programs की list retrieve करने में error आया।"