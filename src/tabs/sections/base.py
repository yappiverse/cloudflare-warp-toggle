"""Base section class for settings tab sections."""

from __future__ import annotations

from typing import Callable, Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class BaseSection(Gtk.Box):
    """Base class for settings tab sections."""
    
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_name("info-card")
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the section UI. Override in subclasses."""
        pass
    
    def update(self) -> None:
        """Update section state from warp-cli. Override in subclasses."""
        pass
