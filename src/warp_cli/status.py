"""WARP connection status functions."""

from __future__ import annotations

import re
from ..constants import MODE_MAP, MODES
from .core import run_command


def get_status() -> tuple[bool, str]:
    """Get connection status.
    
    Returns:
        Tuple of (is_connected, network_status)
    """
    output, success = run_command(['status'])
    
    is_connected = 'Connected' in output
    network_status = "Unknown"
    
    for line in output.split('\n'):
        if 'Network:' in line:
            network_status = line.split(':')[1].strip()
            break
    
    return is_connected, network_status


def get_mode() -> str:
    """Get current WARP mode.
    
    Returns:
        Mode string (e.g., 'warp', 'doh', 'warp+doh')
    """
    output, _ = run_command(['settings', 'list'])
    
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


def connect() -> tuple[str, bool]:
    """Connect to WARP.
    
    Returns:
        Tuple of (output, success)
    """
    return run_command(['connect'], timeout=30)


def disconnect() -> tuple[str, bool]:
    """Disconnect from WARP.
    
    Returns:
        Tuple of (output, success)
    """
    return run_command(['disconnect'], timeout=30)


def set_mode(mode: str) -> tuple[str, bool]:
    """Set WARP mode.
    
    Args:
        mode: Mode to set (e.g., 'warp', 'doh', 'warp+doh')
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['mode', mode], timeout=30)
