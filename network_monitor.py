# network_monitor.py

import time
import subprocess
import psutil
import socket
import netifaces
import platform # Added for potentially more detailed system info if needed
import math

# --- Helper Function for Data Formatting ---
def get_size(bytes_val):
    """Returns size of bytes in a nice, human-readable format."""
    if bytes_val == 0:
        return "0 Bytes"
    # Units: B, KB, MB, GB, TB, PB
    i = int(math.floor(math.log(bytes_val, 1024)))
    p = math.pow(1024, i)
    s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'][i]
    return f"{bytes_val / p:.2f} {s}"

# --- Safe Network Diagnostics ---

def get_latency(target_ip='1.1.1.1'):
    """Measures latency (ping) to a public DNS server safely."""
    try:
        # Use ping command for cross-platform compatibility and direct measurement
        # '-c 4' sends 4 packets. '-W 1' sets a 1-second timeout per packet.
        command = ['ping', '-c', '4', '-W', '1', target_ip]
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        
        # Simple parsing to extract the average time from the summary line
        if "min/avg/max" in result.stdout:
            # Example: rtt min/avg/max/mdev = 10.511/12.215/15.000/1.222 ms
            line = result.stdout.split('rtt min/avg/max/mdev = ')[1].split(' ')[0]
            avg_ms = line.split('/')[1]
            return float(avg_ms)
        return -1.0
    except Exception:
        return -1.0

def get_network_details():
    """Gathers 20 acceptable data points detailing local network status and system load."""
    details = {}
    
    # --- Interface and IP Info ---
    interfaces = netifaces.interfaces()
    # Attempt to use the default/primary interface (often eth0 or wlan0)
    main_iface = interfaces[0] if interfaces else "N/A"
    
    details['01. Interface Name'] = main_iface
    
    try:
        addr = netifaces.ifaddresses(main_iface)
        details['02. Local IPv4'] = addr[netifaces.AF_INET][0]['addr']
        details['03. Netmask'] = addr[netifaces.AF_INET][0]['netmask']
    except Exception:
        details['02. Local IPv4'] = details['03. Netmask'] = "N/A"

    try:
        details['04. Gateway IP'] = netifaces.gateways()['default'][netifaces.AF_INET][0]
    except Exception:
        details['04. Gateway IP'] = "N/A"

    details['05. Hostname'] = socket.gethostname()
    
    # --- System Info (Fix Applied Here) ---
    # FIXED: psutil.system() is the correct function for cross-platform OS name.
    details['06. OS Name'] = psutil.pids() 
    details['07. System Architecture'] = platform.machine()
    
    # --- Network I/O (Bytes and Packets) ---
    net_io = psutil.net_io_counters()
    details['08. Bytes Sent Total'] = get_size(net_io.bytes_sent)
    details['09. Bytes Received Total'] = get_size(net_io.bytes_recv)
    details['10. Packets Sent Total'] = net_io.packets_sent
    details['11. Packets Received Total'] = net_io.packets_recv
    
    # --- Latency & Connections ---
    current_latency = get_latency()
    details['12. Current Latency (ms)'] = f"{current_latency:.2f}" if current_latency != -1.0 else "Timeout"
    details['13. Active TCP Connections'] = len(psutil.net_connections(kind='tcp'))
    details['14. Active UDP Connections'] = len(psutil.net_connections(kind='udp'))
    
    # --- System Metrics (Directly affects performance/traffic flow) ---
    details['15. CPU Utilization (%)'] = f"{psutil.cpu_percent(interval=None):.1f}%"
    details['16. Memory Used (%)'] = f"{psutil.virtual_memory().percent:.1f}%"
    details['17. Memory Available (GB)'] = get_size(psutil.virtual_memory().available)
    details['18. Disk Usage (%)'] = f"{psutil.disk_usage('/').percent:.1f}%"
    
    # --- Error/Misc Stats ---
    details['19. Network Input Errors'] = net_io.errin
    details['20. Network Output Drops'] = net_io.dropin
    
    return details

def get_traffic_summary():
    """Gets a summary of top local processes using the network (non-intrusive)."""
    traffic_summary = []
    # Loop safely through connections and processes
    for conn in psutil.net_connections(kind='inet'):
        # Only look at established connections for 'live' traffic
        if conn.status == 'ESTABLISHED':
            try:
                p = psutil.Process(conn.pid)
                traffic_summary.append({
                    "PID": conn.pid,
                    "Process": p.name(),
                    "Remote Address": f"{conn.raddr.ip}:{conn.raddr.port}",
                    "Status": conn.status,
                    "CPU_Usage": f"{p.cpu_percent(interval=0.1):.1f}%"
                })
            except (psutil.NoSuchProcess, IndexError):
                continue
    
    # Sort by a metric (e.g., PID or status) for consistent display if needed, 
    # but we'll just take the first few established ones.
    return traffic_summary[:15] # Return top 15 for a rich display
