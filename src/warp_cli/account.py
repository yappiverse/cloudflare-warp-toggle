from .core import run_command


def get_account_info():
    """Get account information"""
    output, success = run_command(['registration', 'show'])
    
    info = {
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


def register_license(license_key):
    """Attach registration to account using license key"""
    return run_command(['registration', 'license', license_key], timeout=30)


def new_registration():
    """Create new registration"""
    return run_command(['registration', 'new'], timeout=30)


def delete_registration():
    """Delete current registration"""
    return run_command(['registration', 'delete'], timeout=30)


def get_organization():
    """Get Teams organization name"""
    output, success = run_command(['registration', 'organization'])
    if success and output:
        return output
    return None
