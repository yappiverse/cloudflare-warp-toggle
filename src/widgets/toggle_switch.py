import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class ToggleSwitch(Gtk.EventBox):
    def __init__(self, on_toggle=None):
        super().__init__()
        self._active = False
        self._on_toggle = on_toggle
        self._animating = False
        self._loading = False  
        
        
        self.set_size_request(64, 36)
        
        
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(64, 36)
        self.drawing_area.connect('draw', self._on_draw)
        self.add(self.drawing_area)
        
        
        self.connect('button-press-event', self._on_click)
        self.set_events(self.get_events() | 1 << 9)  
        
        
        self._knob_position = 0.0
        self._pulse_phase = 0.0
    
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        if self._active != value:
            self._active = value
            self._animate_toggle()
    
    def set_active(self, active):
        """Set toggle state without triggering callback"""
        self._loading = False  
        if self._active != active:
            self._active = active
            self._knob_position = 1.0 if active else 0.0
            self.drawing_area.queue_draw()
    
    def set_loading(self, loading):
        """Set loading state (pulse animation while waiting)"""
        self._loading = loading
        if loading:
            self._start_pulse()
        self.drawing_area.queue_draw()
    
    def _start_pulse(self):
        """Start pulse animation for loading state"""
        import math
        
        def pulse():
            if not self._loading:
                return False
            self._pulse_phase += 0.15
            if self._pulse_phase > 2 * math.pi:
                self._pulse_phase = 0
            self.drawing_area.queue_draw()
            return True
        
        GLib.timeout_add(50, pulse)
    
    def _animate_toggle(self):
        """Animate the toggle transition"""
        if self._animating:
            return
        
        self._animating = True
        target = 1.0 if self._active else 0.0
        
        def step():
            diff = target - self._knob_position
            if abs(diff) < 0.05:
                self._knob_position = target
                self._animating = False
                self.drawing_area.queue_draw()
                return False
            
            self._knob_position += diff * 0.3
            self.drawing_area.queue_draw()
            return True
        
        GLib.timeout_add(16, step)  
    
    def _on_draw(self, widget, cr):
        """Draw the toggle switch"""
        import math
        
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        
        if self._loading:
            
            pulse = (math.sin(self._pulse_phase) + 1) / 2  
            gray = 0.35 + pulse * 0.15
            cr.set_source_rgb(gray, gray, gray)
        elif self._active:
            
            cr.set_source_rgb(0.957, 0.506, 0.125)  
        else:
            
            cr.set_source_rgb(0.42, 0.42, 0.42)  
        
        
        radius = height / 2
        cr.arc(radius, radius, radius, 0.5 * 3.14159, 1.5 * 3.14159)
        cr.arc(width - radius, radius, radius, -0.5 * 3.14159, 0.5 * 3.14159)
        cr.close_path()
        cr.fill()
        
        
        knob_radius = (height - 8) / 2
        knob_x = radius + (width - height) * self._knob_position
        knob_y = height / 2
        
        cr.set_source_rgb(1.0, 1.0, 1.0)  
        cr.arc(knob_x, knob_y, knob_radius, 0, 2 * 3.14159)
        cr.fill()
        
        return False
    
    def _on_click(self, widget, event):
        """Handle click to toggle - don't change state, just notify"""
        if self._animating or self._loading:
            return
        
        
        if self._on_toggle:
            
            self._on_toggle(not self._active)
