"""Tunnel settings section for settings tab."""

from __future__ import annotations

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ... import warp_cli


# Tunnel protocols
TUNNEL_PROTOCOLS = {
    'auto': 'Auto',
    'wireguard': 'WireGuard',
    'masque': 'MASQUE',
}


class TunnelSection(Gtk.Box):
    """Tunnel protocol settings section."""
    
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the tunnel section UI."""
        proto_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        proto_label = Gtk.Label(label="Protocol")
        proto_label.set_name("card-value")
        proto_label.set_halign(Gtk.Align.START)
        proto_row.pack_start(proto_label, False, False, 0)
        
        self.protocol_combo = Gtk.ComboBoxText()
        for key, name in TUNNEL_PROTOCOLS.items():
            self.protocol_combo.append(key, name)
        self.protocol_combo.set_active_id('auto')
        self.protocol_combo.connect('changed', self._on_protocol_changed)
        proto_row.pack_end(self.protocol_combo, False, False, 0)
        
        self.pack_start(proto_row, False, False, 0)
    
    def _on_protocol_changed(self, combo: Gtk.ComboBoxText) -> None:
        """Handle protocol change."""
        protocol = combo.get_active_id()
        if protocol:
            threading.Thread(
                target=lambda: warp_cli.set_tunnel_protocol(protocol),
                daemon=True
            ).start()
    
    def update(self, protocol: str) -> None:
        """Update tunnel protocol display.
        
        Args:
            protocol: Current tunnel protocol
        """
        self.protocol_combo.set_active_id(protocol)
