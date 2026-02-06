from .core import run_command


def get_families_mode():
    """Get current Families mode setting"""
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


def set_families_mode(mode):
    """Set Families mode (off, malware, full)"""
    return run_command(['dns', 'families', mode], timeout=10)


def get_dns_logging():
    """Check if DNS logging is enabled"""
    output, success = run_command(['dns', 'log'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_dns_logging(enabled):
    """Enable/disable DNS logging"""
    state = 'enable' if enabled else 'disable'
    return run_command(['dns', 'log', state], timeout=10)


def get_trusted_wifi():
    """Get trusted WiFi auto-disconnect status"""
    output, success = run_command(['trusted', 'wifi'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_trusted_wifi(enabled):
    """Enable/disable auto-disconnect on all WiFi"""
    state = 'enable' if enabled else 'disable'
    return run_command(['trusted', 'wifi', state], timeout=10)


def get_trusted_ethernet():
    """Get trusted ethernet auto-disconnect status"""
    output, success = run_command(['trusted', 'ethernet'])
    if success:
        return 'enabled' in output.lower() or 'on' in output.lower()
    return False


def set_trusted_ethernet(enabled):
    """Enable/disable auto-disconnect on ethernet"""
    state = 'enable' if enabled else 'disable'
    return run_command(['trusted', 'ethernet', state], timeout=10)


def get_trusted_ssids():
    """Get list of trusted WiFi SSIDs"""
    output, success = run_command(['trusted', 'ssid'])
    ssids = []
    if success:
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('Trusted'):
                ssids.append(line)
    return ssids


def add_trusted_ssid(ssid):
    """Add SSID to trusted networks"""
    return run_command(['trusted', 'ssid', 'add', ssid], timeout=10)


def remove_trusted_ssid(ssid):
    """Remove SSID from trusted networks"""
    return run_command(['trusted', 'ssid', 'remove', ssid], timeout=10)
