"""WARP tunnel and network functions."""

from __future__ import annotations

from .core import run_command


def get_tunnel_stats() -> dict[str, str]:
    """Get tunnel statistics.
    
    Returns:
        Dictionary with Protocol, Endpoint, Latency, Loss, Sent, Received keys
    """
    output, success = run_command(['tunnel', 'stats'])
    
    stats: dict[str, str] = {
        'Protocol': '-',
        'Endpoint': '-',
        'Latency': '-',
        'Loss': '-',
        'Sent': '-',
        'Received': '-',
    }
    
    if not success:
        return stats
    
    for line in output.split('\n'):
        line = line.strip()
        if 'Tunnel Protocol:' in line:
            stats['Protocol'] = line.split(':', 1)[1].strip()
        elif 'Endpoints:' in line:
            stats['Endpoint'] = line.split(':', 1)[1].strip()
        elif 'Estimated latency:' in line:
            stats['Latency'] = line.split(':', 1)[1].strip()
        elif 'Estimated loss:' in line:
            stats['Loss'] = line.split(':', 1)[1].strip()
        elif 'Sent:' in line and 'Received:' in line:
            parts = line.split(';')
            stats['Sent'] = parts[0].split(':')[1].strip()
            stats['Received'] = parts[1].split(':')[1].strip()
    
    return stats


def get_tunnel_protocol() -> str:
    """Get current tunnel protocol.
    
    Returns:
        Protocol string: 'auto', 'wireguard', or 'masque'
    """
    output, success = run_command(['tunnel', 'protocol'])
    if success:
        output_lower = output.lower()
        if 'wireguard' in output_lower:
            return 'wireguard'
        elif 'masque' in output_lower:
            return 'masque'
    return 'auto'


def set_tunnel_protocol(protocol: str) -> tuple[str, bool]:
    """Set tunnel protocol.
    
    Args:
        protocol: 'auto', 'wireguard', or 'masque'
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['tunnel', 'protocol', protocol], timeout=10)


def get_network_info() -> dict[str, str]:
    """Get current network information.
    
    Returns:
        Dictionary with Interface, IP, Gateway, DNS keys
    """
    output, success = run_command(['debug', 'network'])
    
    info: dict[str, str] = {
        'Interface': '-',
        'IP': '-',
        'Gateway': '-',
        'DNS': '-',
    }
    
    if not success:
        return info
    
    for line in output.split('\n'):
        line = line.strip()
        if 'Interface:' in line:
            info['Interface'] = line.split(':', 1)[1].strip()
        elif 'IP:' in line or 'Address:' in line:
            info['IP'] = line.split(':', 1)[1].strip()
        elif 'Gateway:' in line:
            info['Gateway'] = line.split(':', 1)[1].strip()
        elif 'DNS:' in line:
            info['DNS'] = line.split(':', 1)[1].strip()
    
    return info


def run_connectivity_check() -> tuple[str, bool]:
    """Run connectivity check.
    
    Returns:
        Tuple of (output, success)
    """
    output, success = run_command(['debug', 'connectivity-check'], timeout=30)
    return output, success
