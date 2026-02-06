import re
from ..constants import MODE_MAP, MODES
from .core import run_command


def get_status():
    """Get connection status. Returns (is_connected, network_status)"""
    output, success = run_command(['status'])
    
    is_connected = 'Connected' in output
    network_status = "Unknown"
    
    for line in output.split('\n'):
        if 'Network:' in line:
            network_status = line.split(':')[1].strip()
            break
    
    return is_connected, network_status


def get_mode():
    """Get current WARP mode"""
    output, success = run_command(['settings', 'list'])
    
    for line in output.split('\n'):
        if 'Mode:' in line:
            mode_match = re.search(r'Mode:\s*(\S+)', line)
            if mode_match:
                raw_mode = mode_match.group(1).lower()
                if raw_mode in MODE_MAP:
                    return MODE_MAP[raw_mode]
                if raw_mode in MODES:
                    return raw_mode
    return 'warp'


def connect():
    """Connect to WARP"""
    return run_command(['connect'], timeout=30)


def disconnect():
    """Disconnect from WARP"""
    return run_command(['disconnect'], timeout=30)


def set_mode(mode):
    """Set WARP mode"""
    return run_command(['mode', mode], timeout=30)
