"""WARP account management functions."""

from __future__ import annotations

from typing import Optional
from .core import run_command


def get_account_info() -> dict[str, str]:
    """Get account information.
    
    Returns:
        Dictionary with 'Type', 'Device ID', and 'Account ID' keys
    """
    output, success = run_command(['registration', 'show'])
    
    info: dict[str, str] = {
        'Type': '-',
        'Device ID': '-',
        'Account ID': '-',
    }
    
    if not success:
        return info
    
    for line in output.split('\n'):
        if 'Account type:' in line:
            info['Type'] = line.split(':', 1)[1].strip()
        elif 'Device ID:' in line:
            info['Device ID'] = line.split(':', 1)[1].strip()
        elif 'Account ID:' in line:
            info['Account ID'] = line.split(':', 1)[1].strip()
    
    return info


def register_license(license_key: str) -> tuple[str, bool]:
    """Attach registration to account using license key.
    
    Args:
        license_key: WARP+ license key (format: xxxx-xxxx-xxxx-xxxx)
        
    Returns:
        Tuple of (output, success)
    """
    return run_command(['registration', 'license', license_key], timeout=30)


def new_registration() -> tuple[str, bool]:
    """Create new registration.
    
    Returns:
        Tuple of (output, success)
    """
    return run_command(['registration', 'new'], timeout=30)


def delete_registration() -> tuple[str, bool]:
    """Delete current registration.
    
    Returns:
        Tuple of (output, success)
    """
    return run_command(['registration', 'delete'], timeout=30)


def get_organization() -> Optional[str]:
    """Get Teams organization name.
    
    Returns:
        Organization name or None if not enrolled in Teams
    """
    output, success = run_command(['registration', 'organization'])
    if success and output:
        return output
    return None
