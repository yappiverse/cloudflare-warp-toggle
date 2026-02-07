"""Settings Tab - Mode selection, License, DNS, Network settings.

This tab uses modular sections for a cleaner, maintainable structure.
"""

from __future__ import annotations

from typing import Callable, Optional
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from .. import warp_cli
from .sections import ModeSection, LicenseSection, DNSSection, NetworkSection, TunnelSection


class SettingsTab(Gtk.Box):
    """Settings tab with mode, license, DNS, and network options."""
    
    def __init__(self, on_mode_change: Optional[Callable[[], None]] = None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self.connect("destroy", self._on_destroy)
        self.destroyed = False
        
        self._on_mode_change = on_mode_change
        self._is_updating = False
        self._is_updating_mode = False
        
        self._build_ui()
    
    def _on_destroy(self, widget: Gtk.Widget) -> None:
        """Handle destruction."""
        self.destroyed = True
    
    def _build_ui(self) -> None:
        """Build the settings tab UI."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        # === Connection Mode ===
        content_box.pack_start(self._create_section_title("CONNECTION MODE"), False, False, 0)
        self.mode_section = ModeSection(on_mode_change=self._on_mode_change)
        content_box.pack_start(self.mode_section, False, False, 0)
        
        # === License ===
        content_box.pack_start(self._create_section_title("LICENSE"), False, False, 8)
        self.license_section = LicenseSection()
        content_box.pack_start(self.license_section, False, False, 0)
        
        # === DNS ===
        content_box.pack_start(self._create_section_title("DNS"), False, False, 8)
        self.dns_section = DNSSection()
        content_box.pack_start(self.dns_section, False, False, 0)
        
        # === Network ===
        content_box.pack_start(self._create_section_title("NETWORK"), False, False, 8)
        self.network_section = NetworkSection()
        content_box.pack_start(self.network_section, False, False, 0)
        
        # === Tunnel ===
        content_box.pack_start(self._create_section_title("TUNNEL"), False, False, 8)
        self.tunnel_section = TunnelSection()
        content_box.pack_start(self.tunnel_section, False, False, 0)
        
        scroll.add(content_box)
        self.pack_start(scroll, True, True, 0)
        
        # Expose mode_combo for backward compatibility
        self.mode_combo = self.mode_section.get_mode_combo()
    
    def _create_section_title(self, text: str) -> Gtk.Label:
        """Create a section title label."""
        label = Gtk.Label()
        label.set_name("section-title")
        label.set_text(text)
        label.set_halign(Gtk.Align.START)
        return label
    
    def update_mode(self) -> None:
        """Update only mode (async)."""
        if self._is_updating_mode or self.destroyed:
            return
            
        self._is_updating_mode = True
        
        def fetch_mode() -> None:
            try:
                mode = warp_cli.get_mode()
                if not self.destroyed:
                    GLib.idle_add(self._safe_update_mode, mode)
            finally:
                self._is_updating_mode = False
            
        threading.Thread(target=fetch_mode, daemon=True).start()

    def _safe_update_mode(self, mode: str) -> None:
        """Safely update mode combo."""
        if not self.destroyed and self.mode_combo.get_visible():
            self.mode_section.update(mode)
    
    def update_all(self) -> None:
        """Update all settings from current state."""
        if self._is_updating or self.destroyed:
            return
            
        self._is_updating = True
            
        def fetch_settings() -> None:
            try:
                # Fetch all data in background
                mode = warp_cli.get_mode()
                families = warp_cli.get_families_mode()
                dns_log = warp_cli.get_dns_logging()
                wifi_trusted = warp_cli.get_trusted_wifi()
                eth_trusted = warp_cli.get_trusted_ethernet()
                protocol = warp_cli.get_tunnel_protocol()
                
                if not self.destroyed:
                    GLib.idle_add(
                        self._apply_settings,
                        mode, families, dns_log, wifi_trusted, eth_trusted, protocol
                    )
            finally:
                self._is_updating = False
                
        threading.Thread(target=fetch_settings, daemon=True).start()
    
    def _apply_settings(
        self,
        mode: str,
        families: str,
        dns_log: bool,
        wifi_trusted: bool,
        eth_trusted: bool,
        protocol: str
    ) -> None:
        """Apply fetched settings to UI (runs on main thread)."""
        if self.destroyed or not self.mode_combo.get_visible():
            return
        
        # Update each section
        self.mode_section.update(mode)
        self.dns_section.update(families, dns_log)
        self.network_section.update(wifi_trusted, eth_trusted)
        self.tunnel_section.update(protocol)
