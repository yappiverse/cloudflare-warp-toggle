"""
Account Tab - Account information and registration management
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from .. import warp_cli


class AccountTab(Gtk.Box):
    """Account information and registration management tab"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self._info_labels = {}
        self._build_ui()
    
    def _build_ui(self):
        """Build the account tab UI"""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        # === Account Info ===
        title = Gtk.Label()
        title.set_name("section-title")
        title.set_text("ACCOUNT")
        title.set_halign(Gtk.Align.START)
        content_box.pack_start(title, False, False, 0)
        
        info_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_card.set_name("info-card")
        
        fields = ['Type', 'Device ID', 'Account ID', 'Organization']
        
        for field in fields:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            label = Gtk.Label()
            label.set_name("card-label")
            label.set_text(field)
            label.set_halign(Gtk.Align.START)
            label.set_size_request(90, -1)
            row.pack_start(label, False, False, 0)
            
            value = Gtk.Label()
            value.set_name("card-value")
            value.set_text("-")
            value.set_halign(Gtk.Align.START)
            value.set_selectable(True)
            value.set_line_wrap(True)
            value.set_max_width_chars(25)
            self._info_labels[field] = value
            row.pack_start(value, True, True, 0)
            
            info_card.pack_start(row, False, False, 0)
        
        content_box.pack_start(info_card, False, False, 0)
        
        # === Registration Actions ===
        reg_title = Gtk.Label()
        reg_title.set_name("section-title")
        reg_title.set_text("REGISTRATION")
        reg_title.set_halign(Gtk.Align.START)
        reg_title.set_margin_top(8)
        content_box.pack_start(reg_title, False, False, 0)
        
        reg_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        reg_card.set_name("info-card")
        
        hint = Gtk.Label()
        hint.set_name("card-label")
        hint.set_text("Manage your WARP registration")
        hint.set_halign(Gtk.Align.START)
        reg_card.pack_start(hint, False, False, 0)
        
        # Buttons row
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        new_btn = Gtk.Button(label="New Registration")
        new_btn.set_name("apply-button")
        new_btn.connect('clicked', self._on_new_registration)
        btn_box.pack_start(new_btn, True, True, 0)
        
        delete_btn = Gtk.Button(label="Delete")
        delete_btn.set_name("delete-button")  # Use custom style instead of destructive-action
        delete_btn.connect('clicked', self._on_delete_registration)
        btn_box.pack_start(delete_btn, False, False, 0)
        
        reg_card.pack_start(btn_box, False, False, 0)
        
        # Status label
        self.reg_status = Gtk.Label()
        self.reg_status.set_name("card-label")
        self.reg_status.set_halign(Gtk.Align.START)
        reg_card.pack_start(self.reg_status, False, False, 0)
        
        content_box.pack_start(reg_card, False, False, 0)
        
        scroll.add(content_box)
        self.pack_start(scroll, True, True, 0)
    
    def _on_new_registration(self, button):
        """Create new registration"""
        self.reg_status.set_text("Creating registration...")
        
        import threading
        
        def do_register():
            output, success = warp_cli.new_registration()
            GLib.idle_add(self._on_reg_complete, success, "Registration created!" if success else output)
        
        threading.Thread(target=do_register, daemon=True).start()
    
    def _on_delete_registration(self, button):
        """Delete registration with confirmation"""
        # Use standard GTK dialog - respects system theme
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.CANCEL,
            text="Delete Registration?"
        )
        dialog.format_secondary_text("This will remove your WARP registration. You'll need to register again to use WARP.")
        
        # Add delete button
        dialog.add_button("Delete", Gtk.ResponseType.OK)
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.reg_status.set_text("Deleting...")
            
            import threading
            
            def do_delete():
                output, success = warp_cli.delete_registration()
                GLib.idle_add(self._on_reg_complete, success, "Registration deleted" if success else output)
            
            threading.Thread(target=do_delete, daemon=True).start()
    
    def _on_reg_complete(self, success, message):
        """Handle registration action completion"""
        if success:
            self.reg_status.set_markup(f'<span foreground="#22c55e">{message}</span>')
            self.update_account()
        else:
            short = message[:50] if len(message) > 50 else message
            self.reg_status.set_markup(f'<span foreground="#f44336">{short}</span>')
    
    def update_account(self):
        """Update account information"""
        import threading
        
        if getattr(self, '_is_updating', False):
            return
            
        self._is_updating = True
        
        def fetch_account():
            try:
                info = warp_cli.get_account_info()
                org = warp_cli.get_organization()
                GLib.idle_add(self._apply_account, info, org)
            finally:
                self._is_updating = False
                
        threading.Thread(target=fetch_account, daemon=True).start()

    def _apply_account(self, info, org):
        """Apply account info to UI"""
        for key, value in info.items():
            if key in self._info_labels:
                self._info_labels[key].set_text(value)
        
        self._info_labels['Organization'].set_text(org if org else '-')
