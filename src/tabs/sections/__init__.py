"""Settings tab UI sections.

This package contains modular UI sections for the settings tab.
"""

from .mode_section import ModeSection
from .license_section import LicenseSection
from .dns_section import DNSSection
from .network_section import NetworkSection
from .tunnel_section import TunnelSection

__all__ = [
    'ModeSection',
    'LicenseSection',
    'DNSSection',
    'NetworkSection',
    'TunnelSection',
]
