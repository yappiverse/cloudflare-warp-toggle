"""Network settings section for settings tab."""

from __future__ import annotations

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ... import warp_cli


class NetworkSection(Gtk.Box):
    """Network trust settings section."""
    
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the network section UI."""
        hint = Gtk.Label()
        hint.set_name("card-label")
        hint.set_text("Auto-disconnect WARP on:")
        hint.set_halign(Gtk.Align.START)
        self.pack_start(hint, False, False, 0)
        
        # WiFi toggle row
        wifi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        wifi_label = Gtk.Label(label="All WiFi Networks")
        wifi_label.set_name("card-value")
        wifi_label.set_halign(Gtk.Align.START)
        wifi_row.pack_start(wifi_label, False, False, 0)
        
        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.set_halign(Gtk.Align.END)
        self.wifi_switch.connect('state-set', self._on_wifi_trusted_changed)
        wifi_row.pack_end(self.wifi_switch, False, False, 0)
        
        self.pack_start(wifi_row, False, False, 0)
        
        # Ethernet toggle row
        eth_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        eth_label = Gtk.Label(label="All Ethernet")
        eth_label.set_name("card-value")
        eth_label.set_halign(Gtk.Align.START)
        eth_row.pack_start(eth_label, False, False, 0)
        
        self.eth_switch = Gtk.Switch()
        self.eth_switch.set_halign(Gtk.Align.END)
        self.eth_switch.connect('state-set', self._on_eth_trusted_changed)
        eth_row.pack_end(self.eth_switch, False, False, 0)
        
        self.pack_start(eth_row, False, False, 0)
    
    def _on_wifi_trusted_changed(self, switch: Gtk.Switch, state: bool) -> bool:
        """Handle WiFi trusted toggle."""
        threading.Thread(
            target=lambda: warp_cli.set_trusted_wifi(state),
            daemon=True
        ).start()
        return False
    
    def _on_eth_trusted_changed(self, switch: Gtk.Switch, state: bool) -> bool:
        """Handle ethernet trusted toggle."""
        threading.Thread(
            target=lambda: warp_cli.set_trusted_ethernet(state),
            daemon=True
        ).start()
        return False
    
    def update(self, wifi_trusted: bool, eth_trusted: bool) -> None:
        """Update network settings display.
        
        Args:
            wifi_trusted: WiFi auto-disconnect enabled
            eth_trusted: Ethernet auto-disconnect enabled
        """
        # Block signals to avoid triggering handlers
        self.wifi_switch.handler_block_by_func(self._on_wifi_trusted_changed)
        self.wifi_switch.set_active(wifi_trusted)
        self.wifi_switch.handler_unblock_by_func(self._on_wifi_trusted_changed)
        
        self.eth_switch.handler_block_by_func(self._on_eth_trusted_changed)
        self.eth_switch.set_active(eth_trusted)
        self.eth_switch.handler_unblock_by_func(self._on_eth_trusted_changed)
