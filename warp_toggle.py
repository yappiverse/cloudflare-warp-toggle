#!/usr/bin/env python3

"""
Cloudflare WARP Toggle - GTK GUI for controlling WARP CLI on Linux
Refactored modular version with minimalist UI
"""

from __future__ import annotations

import os
import sys

# Ensure script directory is in python path
RESULT_DIR = os.path.dirname(os.path.abspath(__file__))
if RESULT_DIR not in sys.path:
    sys.path.insert(0, RESULT_DIR)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Gio

from src.styles import get_css_bytes
from src.constants import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, REFRESH_INTERVAL_SECONDS
from src.tabs import ConnectionTab, SettingsTab, StatsTab, AccountTab, SetupTab
from src import warp_cli
from src.tray import TrayIcon


def show_warp_not_found_dialog() -> None:
    """Show error dialog when warp-cli is not found."""
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.CLOSE,
        text="WARP CLI Not Found"
    )
    dialog.format_secondary_text(
        "The warp-cli command was not found. Please install Cloudflare WARP first.\n\n"
        "Installation instructions:\n"
        "1. Add Cloudflare GPG key and repository\n"
        "2. sudo apt install cloudflare-warp\n"
        "3. warp-cli registration new\n\n"
        "See README.md for detailed instructions."
    )
    dialog.run()
    dialog.destroy()


class WarpToggleWindow(Gtk.Window):
    """Main application window"""
    
    def __init__(self) -> None:
        super().__init__(title=APP_NAME)
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_resizable(False)
        self.connect("destroy", self._on_destroy)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self._apply_styles()
        self._build_ui()
        
        self.destroyed = False
        GLib.idle_add(self._update_all)
        
        GLib.timeout_add_seconds(REFRESH_INTERVAL_SECONDS, self._auto_refresh)
    
    def _on_destroy(self, widget: Gtk.Widget) -> None:
        """Handle window destruction"""
        self.destroyed = True
    
    def _apply_styles(self) -> None:
        """Apply CSS styling and respect system theme"""
        self._gtk_settings = Gtk.Settings.get_default()
        self._gio_settings = None
        
        # Update theme preference
        self._update_theme_preference()
        
        # Try to monitor theme changes (GNOME-based DEs)
        try:
            self._gio_settings = Gio.Settings.new('org.gnome.desktop.interface')
            self._gio_settings.connect('changed::color-scheme', self._on_theme_changed)
        except Exception:
            pass  # Not on GNOME, theme monitoring not available
        
        # Monitor GTK theme changes (works on all DEs)
        self._gtk_settings.connect('notify::gtk-theme-name', self._on_gtk_theme_changed)
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(get_css_bytes())
        
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _detect_dark_theme(self) -> bool:
        """Detect if the system is using a dark theme (cross-DE compatible)"""
        # Method 1: Check GTK theme name for "dark" indicator (works on all DEs)
        theme_name = self._gtk_settings.get_property('gtk-theme-name')
        if theme_name and 'dark' in theme_name.lower():
            return True
        
        # Method 2: Check GNOME color-scheme setting (GNOME-based DEs)
        try:
            settings = Gio.Settings.new('org.gnome.desktop.interface')
            color_scheme = settings.get_string('color-scheme')
            if 'dark' in color_scheme.lower():
                return True
        except Exception:
            pass  # Not on GNOME or setting not available
        
        return False
    
    def _update_theme_preference(self) -> None:
        """Update GTK theme preference based on system setting"""
        prefer_dark = self._detect_dark_theme()
        self._gtk_settings.set_property("gtk-application-prefer-dark-theme", prefer_dark)
    
    def _on_theme_changed(self, settings: Gio.Settings, key: str) -> None:
        """Handle GNOME color-scheme change"""
        self._update_theme_preference()
    
    def _on_gtk_theme_changed(self, settings: Gtk.Settings, pspec: object) -> None:
        """Handle GTK theme change (works on all DEs)"""
        self._update_theme_preference()
    
    def _build_ui(self) -> None:
        """Build the main UI"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.set_name("header-box")
        
        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_row.set_halign(Gtk.Align.CENTER)
        
        logo = Gtk.Label()
        logo.set_markup('<span size="x-large">☁️</span>')
        title_row.pack_start(logo, False, False, 0)
        
        title = Gtk.Label()
        title.set_name("app-title")
        title.set_text("Cloudflare WARP")
        title_row.pack_start(title, False, False, 0)
        
        header.pack_start(title_row, False, False, 0)
        
        subtitle = Gtk.Label()
        subtitle.set_name("app-subtitle")
        subtitle.set_text("Your Internet, Secured")
        subtitle.set_halign(Gtk.Align.CENTER)
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        self.notebook = Gtk.Notebook()
        main_box.pack_start(self.notebook, True, True, 0)
        
        self.connection_tab = ConnectionTab(on_status_change=self._on_status_change)
        self.settings_tab = SettingsTab(on_mode_change=self._on_mode_change)
        self.stats_tab = StatsTab()
        self.account_tab = AccountTab()
        self.setup_tab = SetupTab(on_setup_complete=self._update_all)
        
        self.notebook.append_page(self.connection_tab, Gtk.Label(label="Connection"))
        self.notebook.append_page(self.settings_tab, Gtk.Label(label="Settings"))
        self.notebook.append_page(self.stats_tab, Gtk.Label(label="Stats"))
        self.notebook.append_page(self.account_tab, Gtk.Label(label="Account"))
        self.notebook.append_page(self.setup_tab, Gtk.Label(label="Setup"))
        
        for i in range(5):
            self.notebook.child_set_property(self.notebook.get_nth_page(i), "tab-expand", True)
    
    def _update_all(self) -> bool:
        """Update all tabs"""
        self.connection_tab.update_status()
        self.settings_tab.update_all()
        self.stats_tab.update_all()
        self.account_tab.update_account()
        return False
    
    def _auto_refresh(self) -> bool:
        """Auto-refresh connection status"""
        if getattr(self, 'destroyed', False):
            return False
            
        self.connection_tab.update_status()
        self.settings_tab.update_mode()
        return True
    
    def _on_status_change(self) -> None:
        """Handle connection status change"""
        self.stats_tab.update_all()
    
    def _on_mode_change(self) -> None:
        """Handle mode change"""
        self.connection_tab.update_status()


class WarpToggleApplication(Gtk.Application):
    """Main GTK application with optional system tray."""
    
    def __init__(self) -> None:
        super().__init__(
            application_id="com.cloudflare.warp.toggle",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window: WarpToggleWindow | None = None
        self.tray: TrayIcon | None = None

    def do_activate(self) -> None:
        """Handle application activation."""
        if not self.window:
            self.window = WarpToggleWindow()
            self.window.set_application(self)
            
            # System tray disabled - GNOME doesn't support AppIndicator natively
            # To enable, install: gnome-shell-extension-appindicator
            # Then uncomment the block below:
            #
            # if TrayIcon.is_available():
            #     self.tray = TrayIcon(
            #         on_show_window=self._show_window,
            #         on_quit=self.quit
            #     )
            #     self.tray.update_status()
            
            self.window.show_all()
        
        self.window.present()
    
    def _show_window(self) -> None:
        """Show the main window."""
        if self.window:
            self.window.present()


def main() -> None:
    """Application entry point."""
    # Check if warp-cli is available
    if not warp_cli.is_warp_cli_available():
        # Initialize GTK just for the error dialog
        Gtk.init([])
        show_warp_not_found_dialog()
        sys.exit(1)
    
    app = WarpToggleApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
