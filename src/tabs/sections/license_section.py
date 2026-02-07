"""License input section for settings tab."""

from __future__ import annotations

import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from ... import warp_cli


class LicenseSection(Gtk.Box):
    """License key input section."""
    
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the license section UI."""
        hint = Gtk.Label()
        hint.set_name("card-label")
        hint.set_text("Enter WARP+ license key to upgrade")
        hint.set_halign(Gtk.Align.START)
        self.pack_start(hint, False, False, 0)
        
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.license_entry = Gtk.Entry()
        self.license_entry.set_placeholder_text("xxxx-xxxx-xxxx-xxxx")
        self.license_entry.set_hexpand(True)
        input_row.pack_start(self.license_entry, True, True, 0)
        
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.set_name("apply-button")
        apply_btn.connect('clicked', self._on_apply_license)
        input_row.pack_start(apply_btn, False, False, 0)
        
        self.pack_start(input_row, False, False, 0)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_name("card-label")
        self.status_label.set_halign(Gtk.Align.START)
        self.pack_start(self.status_label, False, False, 0)
    
    def _on_apply_license(self, button: Gtk.Button) -> None:
        """Apply license key."""
        license_key = self.license_entry.get_text().strip()
        if not license_key:
            self.status_label.set_markup('<span foreground="#f44336">Enter a license key</span>')
            return
        
        self.status_label.set_text("Applying...")
        
        def do_apply() -> None:
            output, success = warp_cli.register_license(license_key)
            GLib.idle_add(self._on_license_applied, success, output)
        
        threading.Thread(target=do_apply, daemon=True).start()
    
    def _on_license_applied(self, success: bool, output: str) -> None:
        """Handle license apply completion."""
        if success:
            self.status_label.set_markup('<span foreground="#22c55e">License applied!</span>')
            self.license_entry.set_text("")
        else:
            short = output[:50] if len(output) > 50 else output
            self.status_label.set_markup(f'<span foreground="#f44336">Failed: {short}</span>')
