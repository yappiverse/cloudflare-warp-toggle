"""WARP settings management functions."""

from __future__ import annotations

from .core import run_command


def get_families_mode() -> str:
    """Get current Families mode setting.
    
    Returns:
        Mode string: 'off', 'malware', or 'full'
    """
    output, success = run_command(['dns', 'families'])
    if success:
        output_lower = output.lower()
        if 'malware' in output_lower and 'adult' in output_lower:
            return 'full'
        elif 'malware' in output_lower:
            return 'malware'
        elif 'off' in output_lower or 'disabled' in output_lower:
            return 'off'
    return 'off'


def set_families_mode(mode: str) -> tuple[str, bool]:
    """Set Families mode.
    
    Args:
        mode: 'off', 'malware', or 'full'
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['dns', 'families', mode], timeout=10)


def get_dns_logging() -> bool:
    """Check if DNS logging is enabled.
    
    Returns:
        True if DNS logging is enabled
    """
    output, success = run_command(['dns', 'log'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_dns_logging(enabled: bool) -> tuple[str, bool]:
    """Enable/disable DNS logging.
    
    Args:
        enabled: True to enable, False to disable
        
    Returns:
        Tuple of (output, success)
    """
    state = 'enable' if enabled else 'disable'
    return run_command(['dns', 'log', state], timeout=10)


def get_trusted_wifi() -> bool:
    """Get trusted WiFi auto-disconnect status.
    
    Returns:
        True if auto-disconnect on WiFi is enabled
    """
    output, success = run_command(['trusted', 'wifi'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_trusted_wifi(enabled: bool) -> tuple[str, bool]:
    """Enable/disable auto-disconnect on all WiFi.
    
    Args:
        enabled: True to enable, False to disable
        
    Returns:
        Tuple of (output, success)
    """
    state = 'enable' if enabled else 'disable'
    return run_command(['trusted', 'wifi', state], timeout=10)


def get_trusted_ethernet() -> bool:
    """Get trusted ethernet auto-disconnect status.
    
    Returns:
        True if auto-disconnect on ethernet is enabled
    """
    output, success = run_command(['trusted', 'ethernet'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_trusted_ethernet(enabled: bool) -> tuple[str, bool]:
    """Enable/disable auto-disconnect on ethernet.
    
    Args:
        enabled: True to enable, False to disable
        
    Returns:
        Tuple of (output, success)
    """
    state = 'enable' if enabled else 'disable'
    return run_command(['trusted', 'ethernet', state], timeout=10)


def get_trusted_ssids() -> list[str]:
    """Get list of trusted WiFi SSIDs.
    
    Returns:
        List of SSID strings
    """
    output, success = run_command(['trusted', 'ssid'])
    ssids: list[str] = []
    if success:
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('Trusted'):
                ssids.append(line)
    return ssids


def add_trusted_ssid(ssid: str) -> tuple[str, bool]:
    """Add SSID to trusted networks.
    
    Args:
        ssid: WiFi network name to trust
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['trusted', 'ssid', 'add', ssid], timeout=10)


def remove_trusted_ssid(ssid: str) -> tuple[str, bool]:
    """Remove SSID from trusted networks.
    
    Args:
        ssid: WiFi network name to remove
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['trusted', 'ssid', 'remove', ssid], timeout=10)
