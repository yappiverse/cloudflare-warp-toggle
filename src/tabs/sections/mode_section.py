"""Mode selection section for settings tab."""

from __future__ import annotations

from typing import Callable, Optional
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from ... import warp_cli
from ...constants import MODES


class ModeSection(Gtk.Box):
    """Mode selection section with dropdown and apply button."""
    
    def __init__(self, on_mode_change: Optional[Callable[[], None]] = None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        
        self._on_mode_change = on_mode_change
        self._current_mode = 'warp'
        self._is_applying = False
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the mode section UI."""
        # Mode dropdown row
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
        
        self.pack_start(mode_row, False, False, 0)
        
        # Mode description
        self.mode_desc = Gtk.Label()
        self.mode_desc.set_name("card-label")
        self.mode_desc.set_halign(Gtk.Align.START)
        self.mode_desc.set_line_wrap(True)
        self.mode_desc.set_text(MODES['warp'][1])
        self.pack_start(self.mode_desc, False, False, 0)
        
        self.mode_combo.connect('changed', self._on_mode_selected)
        
        # Apply button
        apply_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        apply_box.set_halign(Gtk.Align.END)
        apply_box.set_margin_top(8)
        
        self.apply_btn = Gtk.Button(label="Apply")
        self.apply_btn.set_name("apply-button")
        self.apply_btn.connect('clicked', self._on_apply_mode)
        apply_box.pack_start(self.apply_btn, False, False, 0)
        
        self.pack_start(apply_box, False, False, 0)
    
    def _on_mode_selected(self, combo: Gtk.ComboBoxText) -> None:
        """Update description when mode changes."""
        mode_key = combo.get_active_id()
        if mode_key and mode_key in MODES:
            self.mode_desc.set_text(MODES[mode_key][1])
    
    def _on_apply_mode(self, button: Gtk.Button) -> None:
        """Apply selected mode."""
        if self._is_applying:
            return
        
        selected_mode = self.mode_combo.get_active_id()
        if selected_mode is None or selected_mode == self._current_mode:
            return
        
        self._is_applying = True
        self.apply_btn.set_sensitive(False)
        
        def do_apply() -> None:
            try:
                import time
                _, success = warp_cli.set_mode(selected_mode)
                time.sleep(0.5)
                GLib.idle_add(self._on_mode_applied, selected_mode, success)
            except Exception as e:
                print(f"Mode error: {e}")
                GLib.idle_add(self._on_mode_applied, selected_mode, False)
            finally:
                self._is_applying = False
        
        threading.Thread(target=do_apply, daemon=True).start()
    
    def _on_mode_applied(self, mode: str, success: bool) -> None:
        """Handle mode change completion."""
        self.apply_btn.set_sensitive(True)
        if success:
            self._current_mode = mode
            if self._on_mode_change:
                self._on_mode_change()
    
    def update(self, mode: str) -> None:
        """Update mode display.
        
        Args:
            mode: Current mode from warp-cli
        """
        self._current_mode = mode
        self.mode_combo.set_active_id(mode)
    
    def get_mode_combo(self) -> Gtk.ComboBoxText:
        """Get the mode combo widget for external access."""
        return self.mode_combo
