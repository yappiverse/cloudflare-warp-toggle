import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from ..widgets import ToggleSwitch, StatusIndicator
from .. import warp_cli
from ..constants import MODES


class ConnectionTab(Gtk.Box):    
    def __init__(self, on_status_change=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self._on_status_change = on_status_change
        self._is_toggling = False
        
        self._build_ui()
    
    def _build_ui(self):        
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_valign(Gtk.Align.CENTER)
        center_box.set_margin_top(40)
        center_box.set_margin_bottom(40)
        
        
        self.status_indicator = StatusIndicator(size=100)
        self.status_indicator.set_halign(Gtk.Align.CENTER)
        center_box.pack_start(self.status_indicator, False, False, 0)
        
        
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.set_margin_top(16)
        center_box.pack_start(self.status_label, False, False, 0)
        
        
        self.mode_label = Gtk.Label()
        self.mode_label.set_name("card-label")
        self.mode_label.set_halign(Gtk.Align.CENTER)
        center_box.pack_start(self.mode_label, False, False, 4)
        
        
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        switch_box.set_halign(Gtk.Align.CENTER)
        switch_box.set_margin_top(24)
        
        self.toggle_switch = ToggleSwitch(on_toggle=self._on_toggle)
        switch_box.pack_start(self.toggle_switch, False, False, 0)
        
        center_box.pack_start(switch_box, False, False, 0)
        
        
        self.toggle_label = Gtk.Label()
        self.toggle_label.set_name("card-label")
        self.toggle_label.set_halign(Gtk.Align.CENTER)
        self.toggle_label.set_margin_top(8)
        center_box.pack_start(self.toggle_label, False, False, 0)
        
        self.pack_start(center_box, True, True, 0)
    
    def _on_toggle(self, active):
        if self._is_toggling:
            return
        
        self._is_toggling = True
        
        
        self.toggle_switch.set_loading(True)
        self.toggle_label.set_text("Connecting..." if active else "Disconnecting...")
        
        import threading
        import time
        from gi.repository import GLib
        
        def do_toggle():
            try:
                if active:
                    warp_cli.connect()
                else:
                    warp_cli.disconnect()
                
                
                time.sleep(1.5)
                
                GLib.idle_add(self._refresh_after_toggle)
            except Exception as e:
                print(f"Toggle error: {e}")
                GLib.idle_add(self._refresh_after_toggle)
            finally:
                self._is_toggling = False
        
        thread = threading.Thread(target=do_toggle)
        thread.daemon = True
        thread.start()
    
    def _refresh_after_toggle(self):
        """Refresh UI after toggle"""
        self.toggle_switch.set_loading(False)
        self.update_status()
        if self._on_status_change:
            self._on_status_change()
    
    
    def update_status(self):
        """Update connection status display"""
        import threading
        
        # Avoid concurrent updates
        if getattr(self, '_is_updating', False):
            return
            
        self._is_updating = True
        
        def fetch_status():
            try:
                if self._is_toggling:
                    return
                
                is_connected, network = warp_cli.get_status()
                current_mode = warp_cli.get_mode()
                
                GLib.idle_add(self._apply_status_update, is_connected, current_mode)
            finally:
                self._is_updating = False
        
        threading.Thread(target=fetch_status, daemon=True).start()
        return True # Return True to keep GLib timeout active if used there
        
    def _apply_status_update(self, is_connected, current_mode):
        """Apply status update to UI (runs on main thread)"""
        if self._is_toggling:
            return

        self.status_indicator.set_connected(is_connected)
        self.toggle_switch.set_active(is_connected)
        
        if is_connected:
            self.status_label.set_name("status-connected")
            self.status_label.set_markup('<span font_weight="600" size="large">Connected</span>')
            self.toggle_label.set_text("Click to disconnect")
        else:
            self.status_label.set_name("status-disconnected")
            self.status_label.set_markup('<span font_weight="600" size="large">Disconnected</span>')
            self.toggle_label.set_text("Click to connect")
        
        mode_name = MODES.get(current_mode, ('Unknown', ''))[0]
        self.mode_label.set_text(f"Mode: {mode_name}")

