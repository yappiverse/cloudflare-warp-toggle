"""System tray integration using AppIndicator3.

Provides a system tray icon with connection status and quick actions.
"""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING
import threading

import gi
gi.require_version('Gtk', '3.0')

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
    HAS_APPINDICATOR = True
except (ValueError, ImportError):
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        HAS_APPINDICATOR = True
    except (ValueError, ImportError):
        HAS_APPINDICATOR = False
        AppIndicator3 = None

from gi.repository import Gtk, GLib

from . import warp_cli


class TrayIcon:
    """System tray icon with connection status indicator."""
    
    def __init__(
        self,
        on_show_window: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None
    ) -> None:

        self._on_show_window = on_show_window
        self._on_quit = on_quit
        self._is_connected = False
        self._indicator: Optional[AppIndicator3.Indicator] = None
        
        if HAS_APPINDICATOR:
            self._create_indicator()
    
    def _create_indicator(self) -> None:
        self._indicator = AppIndicator3.Indicator.new(
            "warp-toggle",
            "network-vpn-symbolic",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self._indicator.set_menu(self._create_menu())
        self._update_icon()
    
    def _create_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()
        
        self._status_item = Gtk.MenuItem(label="WARP: Checking...")
        self._status_item.set_sensitive(False)
        menu.append(self._status_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        self._toggle_item = Gtk.MenuItem(label="Connect")
        self._toggle_item.connect("activate", self._on_toggle)
        menu.append(self._toggle_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        show_item = Gtk.MenuItem(label="Open WARP Toggle")
        show_item.connect("activate", lambda _: self._on_show_window() if self._on_show_window else None)
        menu.append(show_item)
        
        menu.append(Gtk.SeparatorMenuItem())
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: self._on_quit() if self._on_quit else None)
        menu.append(quit_item)
        
        menu.show_all()
        return menu
    
    def _update_icon(self) -> None:
        if not self._indicator:
            return
        
        if self._is_connected:
            self._indicator.set_icon_full("network-vpn-symbolic", "WARP Connected")
        else:
            self._indicator.set_icon_full("network-vpn-disconnected-symbolic", "WARP Disconnected")
    
    def _on_toggle(self, _: Gtk.MenuItem) -> None:
        def do_toggle() -> None:
            if self._is_connected:
                warp_cli.disconnect()
            else:
                warp_cli.connect()
            GLib.timeout_add(1500, self.update_status)
        
        threading.Thread(target=do_toggle, daemon=True).start()
    
    def update_status(self) -> bool:
        def fetch_status() -> None:
            is_connected, _ = warp_cli.get_status()
            GLib.idle_add(self._apply_status, is_connected)
        
        threading.Thread(target=fetch_status, daemon=True).start()
        return False
    
    def _apply_status(self, is_connected: bool) -> None:
        self._is_connected = is_connected
        
        if self._status_item:
            status_text = "WARP: Connected" if is_connected else "WARP: Disconnected"
            self._status_item.set_label(status_text)
        
        if self._toggle_item:
            toggle_text = "Disconnect" if is_connected else "Connect"
            self._toggle_item.set_label(toggle_text)
        
        self._update_icon()
    
    @staticmethod
    def is_available() -> bool:
        return HAS_APPINDICATOR
