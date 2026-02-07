"""WARP CLI wrapper module.

Provides functions for interacting with the warp-cli command-line tool.
"""

from .core import run_command, is_warp_cli_available
from .status import get_status, get_mode, set_mode, connect, disconnect
from .account import (
    get_account_info,
    register_license,
    new_registration,
    delete_registration,
    get_organization,
)
from .tunnel import (
    get_tunnel_stats,
    get_tunnel_protocol,
    set_tunnel_protocol,
    get_network_info,
    run_connectivity_check,
)
from .settings import (
    get_families_mode,
    set_families_mode,
    get_dns_logging,
    set_dns_logging,
    get_trusted_wifi,
    set_trusted_wifi,
    get_trusted_ethernet,
    set_trusted_ethernet,
    get_trusted_ssids,
    add_trusted_ssid,
    remove_trusted_ssid,
)

__all__ = [
    # Core
    'run_command',
    'is_warp_cli_available',
    # Status
    'get_status',
    'get_mode',
    'set_mode',
    'connect',
    'disconnect',
    # Account
    'get_account_info',
    'register_license',
    'new_registration',
    'delete_registration',
    'get_organization',
    # Tunnel
    'get_tunnel_stats',
    'get_tunnel_protocol',
    'set_tunnel_protocol',
    'get_network_info',
    'run_connectivity_check',
    # Settings
    'get_families_mode',
    'set_families_mode',
    'get_dns_logging',
    'set_dns_logging',
    'get_trusted_wifi',
    'set_trusted_wifi',
    'get_trusted_ethernet',
    'set_trusted_ethernet',
    'get_trusted_ssids',
    'add_trusted_ssid',
    'remove_trusted_ssid',
]
