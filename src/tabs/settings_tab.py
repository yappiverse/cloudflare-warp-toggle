"""
Settings Tab - Mode selection, License, DNS, Network settings
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from .. import warp_cli
from ..constants import MODES


# Families mode options
FAMILIES_MODES = {
    'off': 'Off',
    'malware': 'Malware Only',
    'full': 'Malware + Adult Content',
}

# Tunnel protocols
TUNNEL_PROTOCOLS = {
    'auto': 'Auto',
    'wireguard': 'WireGuard',
    'masque': 'MASQUE',
}


class SettingsTab(Gtk.Box):
    """Settings tab with mode, license, DNS, and network options"""
    
    def __init__(self, on_mode_change=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self.connect("destroy", self._on_destroy)
        self.destroyed = False
        
        self._on_mode_change = on_mode_change
        self._current_mode = 'warp'
        self._is_applying = False
        
        self._build_ui()
    
    def _on_destroy(self, widget):
        """Handle destruction"""
        self.destroyed = True


    def _apply_settings(self, mode, families, dns_log, wifi_trusted, eth_trusted, protocol):
        """Apply fetched settings to UI (runs on main thread)"""
        if self.destroyed or not self.mode_combo.get_visible():
            return

        # Mode
        self._current_mode = mode
        self.mode_combo.set_active_id(mode)
        
        # Families
        self.families_combo.set_active_id(families)
        
        # DNS Logging
        # Block signals to avoid triggering setters
        self.dns_logging_switch.handler_block_by_func(self._on_dns_logging_changed)
        self.dns_logging_switch.set_active(dns_log)
        self.dns_logging_switch.handler_unblock_by_func(self._on_dns_logging_changed)
        
        # WiFi
        self.wifi_switch.handler_block_by_func(self._on_wifi_trusted_changed)
        self.wifi_switch.set_active(wifi_trusted)
        self.wifi_switch.handler_unblock_by_func(self._on_wifi_trusted_changed)
        
        # Ethernet
        self.eth_switch.handler_block_by_func(self._on_eth_trusted_changed)
        self.eth_switch.set_active(eth_trusted)
        self.eth_switch.handler_unblock_by_func(self._on_eth_trusted_changed)
        
        # Protocol
        self.protocol_combo.set_active_id(protocol)
    
    def update_mode(self):
        """Update only mode (async)"""
        import threading
        
        if getattr(self, '_is_updating_mode', False) or self.destroyed:
            return
            
        self._is_updating_mode = True
        
        def fetch_mode():
            try:
                mode = warp_cli.get_mode()
                if not self.destroyed:
                    GLib.idle_add(self._safe_update_mode, mode)
            finally:
                self._is_updating_mode = False
            
        threading.Thread(target=fetch_mode, daemon=True).start()

    def _safe_update_mode(self, mode):
        """Safely update mode combo"""
        if not self.destroyed and self.mode_combo.get_visible():
            self.mode_combo.set_active_id(mode)

    
    def _build_ui(self):
        """Build the settings tab UI"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        # === Connection Mode ===
        content_box.pack_start(self._create_section_title("CONNECTION MODE"), False, False, 0)
        content_box.pack_start(self._create_mode_section(), False, False, 0)
        
        # === License ===
        content_box.pack_start(self._create_section_title("LICENSE"), False, False, 8)
        content_box.pack_start(self._create_license_section(), False, False, 0)
        
        # === DNS ===
        content_box.pack_start(self._create_section_title("DNS"), False, False, 8)
        content_box.pack_start(self._create_dns_section(), False, False, 0)
        
        # === Network ===
        content_box.pack_start(self._create_section_title("NETWORK"), False, False, 8)
        content_box.pack_start(self._create_network_section(), False, False, 0)
        
        # === Tunnel ===
        content_box.pack_start(self._create_section_title("TUNNEL"), False, False, 8)
        content_box.pack_start(self._create_tunnel_section(), False, False, 0)
        
        scroll.add(content_box)
        self.pack_start(scroll, True, True, 0)
    
    def _create_section_title(self, text):
        """Create a section title label"""
        label = Gtk.Label()
        label.set_name("section-title")
        label.set_text(text)
        label.set_halign(Gtk.Align.START)
        return label
    
    def _create_mode_section(self):
        """Create mode selection section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        # Mode dropdown
        mode_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        mode_label = Gtk.Label(label="Mode")
        mode_label.set_name("card-value")
        mode_label.set_halign(Gtk.Align.START)
        mode_row.pack_start(mode_label, False, False, 0)
        
        self.mode_combo = Gtk.ComboBoxText()
        for mode_key, (mode_name, _) in MODES.items():
            self.mode_combo.append(mode_key, mode_name)
        self.mode_combo.set_active_id('warp')
        mode_row.pack_end(self.mode_combo, False, False, 0)
        
        box.pack_start(mode_row, False, False, 0)
        
        # Mode description
        self.mode_desc = Gtk.Label()
        self.mode_desc.set_name("card-label")
        self.mode_desc.set_halign(Gtk.Align.START)
        self.mode_desc.set_line_wrap(True)
        self.mode_desc.set_text(MODES['warp'][1])
        box.pack_start(self.mode_desc, False, False, 0)
        
        self.mode_combo.connect('changed', self._on_mode_selected)
        
        # Apply button
        apply_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        apply_box.set_halign(Gtk.Align.END)
        apply_box.set_margin_top(8)
        
        self.mode_apply_btn = Gtk.Button(label="Apply")
        self.mode_apply_btn.set_name("apply-button")
        self.mode_apply_btn.connect('clicked', self._on_apply_mode)
        apply_box.pack_start(self.mode_apply_btn, False, False, 0)
        
        box.pack_start(apply_box, False, False, 0)
        
        return box
    
    def _create_license_section(self):
        """Create license input section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        hint = Gtk.Label()
        hint.set_name("card-label")
        hint.set_text("Enter WARP+ license key to upgrade")
        hint.set_halign(Gtk.Align.START)
        box.pack_start(hint, False, False, 0)
        
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.license_entry = Gtk.Entry()
        self.license_entry.set_placeholder_text("xxxx-xxxx-xxxx-xxxx")
        self.license_entry.set_hexpand(True)
        input_row.pack_start(self.license_entry, True, True, 0)
        
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.set_name("apply-button")
        apply_btn.connect('clicked', self._on_apply_license)
        input_row.pack_start(apply_btn, False, False, 0)
        
        box.pack_start(input_row, False, False, 0)
        
        # Status label
        self.license_status = Gtk.Label()
        self.license_status.set_name("card-label")
        self.license_status.set_halign(Gtk.Align.START)
        box.pack_start(self.license_status, False, False, 0)
        
        return box
    
    def _create_dns_section(self):
        """Create DNS settings section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        # Families mode
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
        
        box.pack_start(families_row, False, False, 0)
        
        # DNS Logging toggle
        logging_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        logging_label = Gtk.Label(label="DNS Logging")
        logging_label.set_name("card-value")
        logging_label.set_halign(Gtk.Align.START)
        logging_row.pack_start(logging_label, False, False, 0)
        
        self.dns_logging_switch = Gtk.Switch()
        self.dns_logging_switch.set_halign(Gtk.Align.END)
        self.dns_logging_switch.connect('state-set', self._on_dns_logging_changed)
        logging_row.pack_end(self.dns_logging_switch, False, False, 0)
        
        box.pack_start(logging_row, False, False, 0)
        
        return box
    
    def _create_network_section(self):
        """Create network settings section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        hint = Gtk.Label()
        hint.set_name("card-label")
        hint.set_text("Auto-disconnect WARP on:")
        hint.set_halign(Gtk.Align.START)
        box.pack_start(hint, False, False, 0)
        
        # WiFi toggle
        wifi_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        wifi_label = Gtk.Label(label="All WiFi Networks")
        wifi_label.set_name("card-value")
        wifi_label.set_halign(Gtk.Align.START)
        wifi_row.pack_start(wifi_label, False, False, 0)
        
        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.set_halign(Gtk.Align.END)
        self.wifi_switch.connect('state-set', self._on_wifi_trusted_changed)
        wifi_row.pack_end(self.wifi_switch, False, False, 0)
        
        box.pack_start(wifi_row, False, False, 0)
        
        # Ethernet toggle
        eth_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        eth_label = Gtk.Label(label="All Ethernet")
        eth_label.set_name("card-value")
        eth_label.set_halign(Gtk.Align.START)
        eth_row.pack_start(eth_label, False, False, 0)
        
        self.eth_switch = Gtk.Switch()
        self.eth_switch.set_halign(Gtk.Align.END)
        self.eth_switch.connect('state-set', self._on_eth_trusted_changed)
        eth_row.pack_end(self.eth_switch, False, False, 0)
        
        box.pack_start(eth_row, False, False, 0)
        
        return box
    
    def _create_tunnel_section(self):
        """Create tunnel settings section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        # Protocol dropdown
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
        
        box.pack_start(proto_row, False, False, 0)
        
        return box
    
    # ===== Event Handlers =====
    
    def _on_mode_selected(self, combo):
        """Update description when mode changes"""
        mode_key = combo.get_active_id()
        if mode_key and mode_key in MODES:
            self.mode_desc.set_text(MODES[mode_key][1])
    
    def _on_apply_mode(self, button):
        """Apply selected mode"""
        if self._is_applying:
            return
        
        selected_mode = self.mode_combo.get_active_id()
        if selected_mode is None or selected_mode == self._current_mode:
            return
        
        self._is_applying = True
        self.mode_apply_btn.set_sensitive(False)
        
        import threading
        import time
        
        def do_apply():
            try:
                _, success = warp_cli.set_mode(selected_mode)
                time.sleep(0.5)
                GLib.idle_add(self._on_mode_applied, selected_mode, success)
            except Exception as e:
                print(f"Mode error: {e}")
                GLib.idle_add(self._on_mode_applied, selected_mode, False)
            finally:
                self._is_applying = False
        
        threading.Thread(target=do_apply, daemon=True).start()
    
    def _on_mode_applied(self, mode, success):
        """Handle mode change completion"""
        self.mode_apply_btn.set_sensitive(True)
        if success:
            self._current_mode = mode
            if self._on_mode_change:
                self._on_mode_change()
    
    def _on_apply_license(self, button):
        """Apply license key"""
        license_key = self.license_entry.get_text().strip()
        if not license_key:
            self.license_status.set_markup('<span foreground="#f44336">Enter a license key</span>')
            return
        
        self.license_status.set_text("Applying...")
        
        import threading
        
        def do_apply():
            output, success = warp_cli.register_license(license_key)
            GLib.idle_add(self._on_license_applied, success, output)
        
        threading.Thread(target=do_apply, daemon=True).start()
    
    def _on_license_applied(self, success, output):
        """Handle license apply completion"""
        if success:
            self.license_status.set_markup('<span foreground="#22c55e">License applied!</span>')
            self.license_entry.set_text("")
        else:
            self.license_status.set_markup(f'<span foreground="#f44336">Failed: {output[:50]}</span>')
    
    def _on_families_changed(self, combo):
        """Handle families mode change"""
        mode = combo.get_active_id()
        if mode:
            import threading
            threading.Thread(target=lambda: warp_cli.set_families_mode(mode), daemon=True).start()
    
    def _on_dns_logging_changed(self, switch, state):
        """Handle DNS logging toggle"""
        import threading
        threading.Thread(target=lambda: warp_cli.set_dns_logging(state), daemon=True).start()
        return False
    
    def _on_wifi_trusted_changed(self, switch, state):
        """Handle WiFi trusted toggle"""
        import threading
        threading.Thread(target=lambda: warp_cli.set_trusted_wifi(state), daemon=True).start()
        return False
    
    def _on_eth_trusted_changed(self, switch, state):
        """Handle ethernet trusted toggle"""
        import threading
        threading.Thread(target=lambda: warp_cli.set_trusted_ethernet(state), daemon=True).start()
        return False
    
    def _on_protocol_changed(self, combo):
        """Handle protocol change"""
        protocol = combo.get_active_id()
        if protocol:
            import threading
            threading.Thread(target=lambda: warp_cli.set_tunnel_protocol(protocol), daemon=True).start()

    def update_mode(self):
        """Update only mode (async)"""
        import threading
        
        if getattr(self, '_is_updating_mode', False) or self.destroyed:
            return
            
        self._is_updating_mode = True
        
        def fetch_mode():
            try:
                mode = warp_cli.get_mode()
                if not self.destroyed:
                    GLib.idle_add(self._safe_update_mode, mode)
            finally:
                self._is_updating_mode = False
            
        threading.Thread(target=fetch_mode, daemon=True).start()

    def _safe_update_mode(self, mode):
        """Safely update mode combo"""
        if not self.destroyed and self.mode_combo.get_visible():
            self.mode_combo.set_active_id(mode)

    def update_all(self):
        """Update all settings from current state"""
        import threading
        
        if getattr(self, '_is_updating', False) or self.destroyed:
            return
            
        self._is_updating = True
            
        def fetch_settings():
            try:
                # Fetch all data in background
                mode = warp_cli.get_mode()
                families = warp_cli.get_families_mode()
                dns_log = warp_cli.get_dns_logging()
                wifi_trusted = warp_cli.get_trusted_wifi()
                eth_trusted = warp_cli.get_trusted_ethernet()
                protocol = warp_cli.get_tunnel_protocol()
                
                if not self.destroyed:
                    GLib.idle_add(self._apply_settings, mode, families, dns_log, wifi_trusted, eth_trusted, protocol)
            finally:
                self._is_updating = False
                
        threading.Thread(target=fetch_settings, daemon=True).start()

    def _apply_settings(self, mode, families, dns_log, wifi_trusted, eth_trusted, protocol):
        """Apply fetched settings to UI (runs on main thread)"""
        if self.destroyed or not self.mode_combo.get_visible():
            return

        # Mode
        self._current_mode = mode
        self.mode_combo.set_active_id(mode)
        
        # Families
        self.families_combo.set_active_id(families)
        
        # DNS Logging
        # Block signals to avoid triggering setters
        self.dns_logging_switch.handler_block_by_func(self._on_dns_logging_changed)
        self.dns_logging_switch.set_active(dns_log)
        self.dns_logging_switch.handler_unblock_by_func(self._on_dns_logging_changed)
        
        # WiFi
        self.wifi_switch.handler_block_by_func(self._on_wifi_trusted_changed)
        self.wifi_switch.set_active(wifi_trusted)
        self.wifi_switch.handler_unblock_by_func(self._on_wifi_trusted_changed)
        
        # Ethernet
        self.eth_switch.handler_block_by_func(self._on_eth_trusted_changed)
        self.eth_switch.set_active(eth_trusted)
        self.eth_switch.handler_unblock_by_func(self._on_eth_trusted_changed)
        
        # Protocol
        self.protocol_combo.set_active_id(protocol)
