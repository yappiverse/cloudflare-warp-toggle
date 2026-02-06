"""
Status Indicator Widget
Circle indicator with subtle pulse animation when connected
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import math


class StatusIndicator(Gtk.DrawingArea):
    """Animated status indicator circle"""
    
    def __init__(self, size=80):
        super().__init__()
        self._connected = False
        self._pulse_phase = 0.0
        self._pulse_active = False
        self._size = size
        
        self.set_size_request(size, size)
        self.connect('draw', self._on_draw)
    
    @property
    def connected(self):
        return self._connected
    
    @connected.setter
    def connected(self, value):
        if self._connected != value:
            self._connected = value
            if value and not self._pulse_active:
                self._start_pulse()
            elif not value:
                self._pulse_active = False
            self.queue_draw()
    
    def set_connected(self, connected):
        """Set connection state"""
        self.connected = connected
    
    def _start_pulse(self):
        """Start subtle pulse animation"""
        self._pulse_active = True
        
        def pulse():
            if not self._pulse_active or not self._connected:
                self._pulse_active = False
                return False
            
            self._pulse_phase += 0.08
            if self._pulse_phase > 2 * math.pi:
                self._pulse_phase = 0
            
            self.queue_draw()
            return True
        
        GLib.timeout_add(50, pulse)
    
    def _on_draw(self, widget, cr):
        """Draw the status indicator"""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 4
        
        if self._connected:
            # Subtle pulse effect
            pulse_offset = math.sin(self._pulse_phase) * 0.1
            alpha = 0.8 + pulse_offset
            
            # Outer glow
            cr.set_source_rgba(0.133, 0.773, 0.369, 0.2)  # Green glow
            cr.arc(center_x, center_y, radius + 4, 0, 2 * math.pi)
            cr.fill()
            
            # Main circle - green
            cr.set_source_rgba(0.133, 0.773, 0.369, alpha)  # #22c55e
        else:
            # Gray circle
            cr.set_source_rgb(0.42, 0.45, 0.50)  # #6b7280
        
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.fill()
        
        # Inner icon
        cr.set_source_rgb(1.0, 1.0, 1.0)
        
        if self._connected:
            # Checkmark
            cr.set_line_width(3)
            cr.set_line_cap(1)  # Round caps
            
            # Start checkmark path
            check_size = radius * 0.4
            cr.move_to(center_x - check_size * 0.6, center_y)
            cr.line_to(center_x - check_size * 0.1, center_y + check_size * 0.5)
            cr.line_to(center_x + check_size * 0.6, center_y - check_size * 0.4)
            cr.stroke()
        else:
            # Power icon
            cr.set_line_width(2.5)
            icon_radius = radius * 0.35
            
            # Circle part (open at top)
            cr.arc(center_x, center_y + 2, icon_radius, 0.4 * math.pi, 2.6 * math.pi)
            cr.stroke()
            
            # Vertical line
            cr.move_to(center_x, center_y - icon_radius - 2)
            cr.line_to(center_x, center_y + 2)
            cr.stroke()
        
        return False
