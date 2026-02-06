import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from .. import warp_cli


class StatsTab(Gtk.Box):    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self._stat_labels = {}
        self._network_labels = {}
        self._build_ui()
    
    def _build_ui(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        title = Gtk.Label()
        title.set_name("section-title")
        title.set_text("TUNNEL")
        title.set_halign(Gtk.Align.START)
        content_box.pack_start(title, False, False, 0)
        
        stats_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        stats_card.set_name("info-card")
        
        stats = ['Protocol', 'Endpoint', 'Latency', 'Loss', 'Sent', 'Received']
        
        for stat in stats:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            label = Gtk.Label()
            label.set_name("card-label")
            label.set_text(stat)
            label.set_halign(Gtk.Align.START)
            label.set_size_request(80, -1)
            row.pack_start(label, False, False, 0)
            
            value = Gtk.Label()
            value.set_name("card-value")
            value.set_text("-")
            value.set_halign(Gtk.Align.START)
            value.set_selectable(True)
            value.set_line_wrap(True)
            self._stat_labels[stat] = value
            row.pack_start(value, True, True, 0)
            
            stats_card.pack_start(row, False, False, 0)
        
        content_box.pack_start(stats_card, False, False, 0)
        
        net_title = Gtk.Label()
        net_title.set_name("section-title")
        net_title.set_text("NETWORK")
        net_title.set_halign(Gtk.Align.START)
        net_title.set_margin_top(8)
        content_box.pack_start(net_title, False, False, 0)
        
        net_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        net_card.set_name("info-card")
        
        net_fields = ['Interface', 'IP', 'Gateway', 'DNS']
        
        for field in net_fields:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            label = Gtk.Label()
            label.set_name("card-label")
            label.set_text(field)
            label.set_halign(Gtk.Align.START)
            label.set_size_request(80, -1)
            row.pack_start(label, False, False, 0)
            
            value = Gtk.Label()
            value.set_name("card-value")
            value.set_text("-")
            value.set_halign(Gtk.Align.START)
            value.set_selectable(True)
            value.set_line_wrap(True)
            self._network_labels[field] = value
            row.pack_start(value, True, True, 0)
            
            net_card.pack_start(row, False, False, 0)
        
        content_box.pack_start(net_card, False, False, 0)
        
        diag_title = Gtk.Label()
        diag_title.set_name("section-title")
        diag_title.set_text("DIAGNOSTICS")
        diag_title.set_halign(Gtk.Align.START)
        diag_title.set_margin_top(8)
        content_box.pack_start(diag_title, False, False, 0)
        
        diag_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        diag_card.set_name("info-card")
        
        check_btn = Gtk.Button(label="Run Connectivity Check")
        check_btn.set_name("apply-button")
        check_btn.connect('clicked', self._on_connectivity_check)
        diag_card.pack_start(check_btn, False, False, 0)
        
        self.check_result = Gtk.Label()
        self.check_result.set_name("card-label")
        self.check_result.set_halign(Gtk.Align.START)
        self.check_result.set_line_wrap(True)
        self.check_result.set_max_width_chars(40)
        diag_card.pack_start(self.check_result, False, False, 0)
        
        content_box.pack_start(diag_card, False, False, 0)
        
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        refresh_box.set_halign(Gtk.Align.CENTER)
        refresh_box.set_margin_top(16)
        
        refresh_btn = Gtk.Button(label="↻ Refresh All")
        refresh_btn.set_name("link-button")
        refresh_btn.set_relief(Gtk.ReliefStyle.NONE)
        refresh_btn.connect('clicked', lambda b: self.update_all())
        refresh_box.pack_start(refresh_btn, False, False, 0)
        
        content_box.pack_start(refresh_box, False, False, 0)
        
        scroll.add(content_box)
        self.pack_start(scroll, True, True, 0)
    
    def _on_connectivity_check(self, button):
        """Run connectivity check"""
        self.check_result.set_text("Checking...")
        button.set_sensitive(False)
        
        import threading
        
        def do_check():
            output, success = warp_cli.run_connectivity_check()
            GLib.idle_add(self._on_check_complete, output, success, button)
        
        threading.Thread(target=do_check, daemon=True).start()
    
    def _on_check_complete(self, output, success, button):
        """Handle check completion"""
        button.set_sensitive(True)
        if success:
            self.check_result.set_markup('<span foreground="#22c55e">✓ Connectivity OK</span>')
        else:
            short = output[:100] if len(output) > 100 else output
            self.check_result.set_markup(f'<span foreground="#f44336">{short}</span>')
    
    def update_stats(self):
        """Update tunnel statistics"""
        stats = warp_cli.get_tunnel_stats()
        for key, value in stats.items():
            if key in self._stat_labels:
                self._stat_labels[key].set_text(value)
    
    def update_network(self):
        """Update network info"""
        info = warp_cli.get_network_info()
        for key, value in info.items():
            if key in self._network_labels:
                self._network_labels[key].set_text(value)
    
    def update_all(self):
        """Update all stats"""
        import threading
        
        if getattr(self, '_is_updating', False):
            return
            
        self._is_updating = True
        
        def fetch_stats():
            try:
                stats = warp_cli.get_tunnel_stats()
                network = warp_cli.get_network_info()
                GLib.idle_add(self._apply_stats, stats, network)
            finally:
                self._is_updating = False
                
        threading.Thread(target=fetch_stats, daemon=True).start()

    def _apply_stats(self, stats, network):
        """Apply stats to UI"""
        for key, value in stats.items():
            if key in self._stat_labels:
                self._stat_labels[key].set_text(value)
                
        for key, value in network.items():
            if key in self._network_labels:
                self._network_labels[key].set_text(value)
