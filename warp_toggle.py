#!/usr/bin/env python3

"""
Cloudflare WARP Toggle - GTK GUI for controlling WARP CLI on Linux
Refactored modular version with minimalist UI
"""

import os
import sys

# Ensure script directory is in python path
RESULT_DIR = os.path.dirname(os.path.abspath(__file__))
if RESULT_DIR not in sys.path:
    sys.path.insert(0, RESULT_DIR)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

from src.styles import get_css_bytes
from src.constants import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, REFRESH_INTERVAL_SECONDS
from src.tabs import ConnectionTab, SettingsTab, StatsTab, AccountTab


class WarpToggleWindow(Gtk.Window):
    """Main application window"""
    
    def __init__(self):
        super().__init__(title=APP_NAME)
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self._apply_styles()
        self._build_ui()
        
        
        GLib.idle_add(self._update_all)
        
        
        GLib.timeout_add_seconds(REFRESH_INTERVAL_SECONDS, self._auto_refresh)
    
    def _apply_styles(self):
        """Apply CSS styling and respect system theme"""
        self._gtk_settings = Gtk.Settings.get_default()
        
        
        self._update_theme_preference()
        
        
        try:
            from gi.repository import Gio
            self._gio_settings = Gio.Settings.new('org.gnome.desktop.interface')
            self._gio_settings.connect('changed::color-scheme', self._on_theme_changed)
        except Exception as e:
            print(f"Could not monitor theme changes: {e}")
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(get_css_bytes())
        
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _update_theme_preference(self):
        """Update GTK theme preference based on system setting"""
        try:
            from gi.repository import Gio
            settings = Gio.Settings.new('org.gnome.desktop.interface')
            color_scheme = settings.get_string('color-scheme')
            prefer_dark = 'dark' in color_scheme.lower()
            self._gtk_settings.set_property("gtk-application-prefer-dark-theme", prefer_dark)
        except:
            pass
    
    def _on_theme_changed(self, settings, key):
        """Handle system theme change"""
        self._update_theme_preference()
    
    def _build_ui(self):
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
        
        self.notebook.append_page(self.connection_tab, Gtk.Label(label="Connection"))
        self.notebook.append_page(self.settings_tab, Gtk.Label(label="Settings"))
        self.notebook.append_page(self.stats_tab, Gtk.Label(label="Stats"))
        self.notebook.append_page(self.account_tab, Gtk.Label(label="Account"))
        
        
        for i in range(4):
            self.notebook.child_set_property(self.notebook.get_nth_page(i), "tab-expand", True)
    
    def _update_all(self):
        """Update all tabs"""
        self.connection_tab.update_status()
        self.settings_tab.update_all()
        self.stats_tab.update_all()
        self.account_tab.update_account()
        return False
    
    def _auto_refresh(self):
        """Auto-refresh connection status"""
        self.connection_tab.update_status()
        return True
    
    def _on_status_change(self):
        """Handle connection status change"""
        self.stats_tab.update_all()
    
    def _on_mode_change(self):
        """Handle mode change"""
        self.connection_tab.update_status()


def main():
    win = WarpToggleWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
