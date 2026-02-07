"""DNS settings section for settings tab."""

from __future__ import annotations

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ... import warp_cli


# Families mode options
FAMILIES_MODES = {
    'off': 'Off',
    'malware': 'Malware Only',
    'full': 'Malware + Adult Content',
}


class DNSSection(Gtk.Box):
    """DNS settings section with families filter and logging toggle."""
    
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the DNS section UI."""
        # Families mode row
        families_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        families_label = Gtk.Label(label="Families Filter")
        families_label.set_name("card-value")
        families_label.set_halign(Gtk.Align.START)
        families_row.pack_start(families_label, False, False, 0)
        
        self.families_combo = Gtk.ComboBoxText()
        for key, name in FAMILIES_MODES.items():
            self.families_combo.append(key, name)
        self.families_combo.set_active_id('off')
        self.families_combo.connect('changed', self._on_families_changed)
        families_row.pack_end(self.families_combo, False, False, 0)
        
        self.pack_start(families_row, False, False, 0)
        
        # DNS Logging toggle row
        logging_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        logging_label = Gtk.Label(label="DNS Logging")
        logging_label.set_name("card-value")
        logging_label.set_halign(Gtk.Align.START)
        logging_row.pack_start(logging_label, False, False, 0)
        
        self.dns_logging_switch = Gtk.Switch()
        self.dns_logging_switch.set_halign(Gtk.Align.END)
        self.dns_logging_switch.connect('state-set', self._on_dns_logging_changed)
        logging_row.pack_end(self.dns_logging_switch, False, False, 0)
        
        self.pack_start(logging_row, False, False, 0)
    
    def _on_families_changed(self, combo: Gtk.ComboBoxText) -> None:
        """Handle families mode change."""
        mode = combo.get_active_id()
        if mode:
            threading.Thread(
                target=lambda: warp_cli.set_families_mode(mode),
                daemon=True
            ).start()
    
    def _on_dns_logging_changed(self, switch: Gtk.Switch, state: bool) -> bool:
        """Handle DNS logging toggle."""
        threading.Thread(
            target=lambda: warp_cli.set_dns_logging(state),
            daemon=True
        ).start()
        return False
    
    def update(self, families: str, dns_log: bool) -> None:
        """Update DNS settings display.
        
        Args:
            families: Current families mode
            dns_log: DNS logging enabled state
        """
        self.families_combo.set_active_id(families)
        
        # Block signal to avoid triggering handler
        self.dns_logging_switch.handler_block_by_func(self._on_dns_logging_changed)
        self.dns_logging_switch.set_active(dns_log)
        self.dns_logging_switch.handler_unblock_by_func(self._on_dns_logging_changed)
