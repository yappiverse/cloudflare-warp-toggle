"""Setup Tab - Check and install warp-cli and dependencies."""

from __future__ import annotations

import subprocess
import threading
from typing import Callable, Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from .. import warp_cli


# Installation commands for Debian/Ubuntu
WARP_INSTALL_COMMANDS = [
    # Add GPG key
    "curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg",
    # Add repository
    "echo 'deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ bookworm main' | sudo tee /etc/apt/sources.list.d/cloudflare-client.list",
    # Update and install
    "sudo apt-get update && sudo apt-get install -y cloudflare-warp",
]

WIREGUARD_INSTALL_COMMAND = "sudo apt-get install -y wireguard-tools"


class SetupTab(Gtk.Box):
    """Setup tab for checking and installing dependencies."""
    
    def __init__(self, on_setup_complete: Optional[Callable[[], None]] = None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_name("tab-content")
        
        self._on_setup_complete = on_setup_complete
        self._build_ui()
        GLib.idle_add(self._check_status)
    
    def _build_ui(self) -> None:
        """Build the setup tab UI."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        # Header
        header = Gtk.Label()
        header.set_name("section-title")
        header.set_text("SETUP & DEPENDENCIES")
        header.set_halign(Gtk.Align.START)
        content_box.pack_start(header, False, False, 0)
        
        # Description
        desc = Gtk.Label()
        desc.set_name("card-label")
        desc.set_text("Check and install required components for WARP")
        desc.set_halign(Gtk.Align.START)
        desc.set_line_wrap(True)
        content_box.pack_start(desc, False, False, 0)
        
        # === WARP CLI Section ===
        content_box.pack_start(self._create_section_title("CLOUDFLARE WARP CLI"), False, False, 8)
        warp_card = self._create_status_card(
            "warp-cli",
            "Required for WARP connection",
            self._install_warp
        )
        self.warp_status = warp_card["status"]
        self.warp_btn = warp_card["button"]
        content_box.pack_start(warp_card["box"], False, False, 0)
        
        # === WireGuard Section ===
        content_box.pack_start(self._create_section_title("WIREGUARD"), False, False, 8)
        wg_card = self._create_status_card(
            "wireguard-tools",
            "Optional: Alternative tunnel protocol",
            self._install_wireguard
        )
        self.wg_status = wg_card["status"]
        self.wg_btn = wg_card["button"]
        content_box.pack_start(wg_card["box"], False, False, 0)
        
        # === WARP Service Section ===
        content_box.pack_start(self._create_section_title("WARP SERVICE"), False, False, 8)
        service_card = self._create_status_card(
            "warp-svc",
            "WARP daemon service",
            self._enable_service
        )
        self.svc_status = service_card["status"]
        self.svc_btn = service_card["button"]
        content_box.pack_start(service_card["box"], False, False, 0)
        
        # === Registration Section ===
        content_box.pack_start(self._create_section_title("REGISTRATION"), False, False, 8)
        reg_card = self._create_status_card(
            "Registration",
            "WARP device registration",
            self._new_registration
        )
        self.reg_status = reg_card["status"]
        self.reg_btn = reg_card["button"]
        content_box.pack_start(reg_card["box"], False, False, 0)
        
        # === Log Output ===
        content_box.pack_start(self._create_section_title("LOG OUTPUT"), False, False, 8)
        
        log_frame = Gtk.Frame()
        log_frame.set_name("info-card")
        
        log_scroll = Gtk.ScrolledWindow()
        log_scroll.set_min_content_height(120)
        log_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_view.set_name("log-view")
        self.log_buffer = self.log_view.get_buffer()
        
        log_scroll.add(self.log_view)
        log_frame.add(log_scroll)
        content_box.pack_start(log_frame, True, True, 0)
        
        # Refresh button
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        refresh_box.set_halign(Gtk.Align.CENTER)
        refresh_box.set_margin_top(8)
        
        refresh_btn = Gtk.Button(label="↻ Refresh Status")
        refresh_btn.connect("clicked", lambda _: self._check_status())
        refresh_box.pack_start(refresh_btn, False, False, 0)
        content_box.pack_start(refresh_box, False, False, 0)
        
        scroll.add(content_box)
        self.pack_start(scroll, True, True, 0)
    
    def _create_section_title(self, text: str) -> Gtk.Label:
        """Create a section title label."""
        label = Gtk.Label()
        label.set_name("section-title")
        label.set_text(text)
        label.set_halign(Gtk.Align.START)
        return label
    
    def _create_status_card(
        self,
        name: str,
        description: str,
        install_callback: Callable
    ) -> dict:
        """Create a status card with install button."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_name("info-card")
        
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Name and description
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        name_label = Gtk.Label()
        name_label.set_name("card-value")
        name_label.set_text(name)
        name_label.set_halign(Gtk.Align.START)
        info_box.pack_start(name_label, False, False, 0)
        
        desc_label = Gtk.Label()
        desc_label.set_name("card-label")
        desc_label.set_text(description)
        desc_label.set_halign(Gtk.Align.START)
        info_box.pack_start(desc_label, False, False, 0)
        
        row.pack_start(info_box, True, True, 0)
        
        # Status indicator
        status_label = Gtk.Label()
        status_label.set_name("card-label")
        status_label.set_text("Checking...")
        row.pack_start(status_label, False, False, 0)
        
        # Install button
        install_btn = Gtk.Button(label="Install")
        install_btn.set_name("apply-button")
        install_btn.connect("clicked", lambda _: install_callback())
        install_btn.set_sensitive(False)
        row.pack_start(install_btn, False, False, 0)
        
        box.pack_start(row, False, False, 0)
        
        return {"box": box, "status": status_label, "button": install_btn}
    
    def _log(self, message: str) -> None:
        """Add message to log view."""
        def update_log():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, message + "\n")
            # Auto-scroll to bottom
            adj = self.log_view.get_parent().get_vadjustment()
            adj.set_value(adj.get_upper())
        GLib.idle_add(update_log)
    
    def _check_status(self) -> None:
        """Check all dependencies status."""
        def check():
            # Check warp-cli
            warp_installed = warp_cli.is_warp_cli_available()
            GLib.idle_add(self._update_warp_status, warp_installed)
            
            # Check WireGuard
            try:
                result = subprocess.run(
                    ["which", "wg"],
                    capture_output=True, timeout=5
                )
                wg_installed = result.returncode == 0
            except Exception:
                wg_installed = False
            GLib.idle_add(self._update_wg_status, wg_installed)
            
            # Check service
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", "warp-svc"],
                    capture_output=True, text=True, timeout=5
                )
                svc_active = "active" in result.stdout
            except Exception:
                svc_active = False
            GLib.idle_add(self._update_svc_status, svc_active)
            
            # Check registration
            if warp_installed and svc_active:
                info = warp_cli.get_account_info()
                registered = info.get("Device ID", "-") != "-"
            else:
                registered = False
            GLib.idle_add(self._update_reg_status, registered)
        
        threading.Thread(target=check, daemon=True).start()
    
    def _update_warp_status(self, installed: bool) -> None:
        """Update WARP status display."""
        if installed:
            self.warp_status.set_markup('<span foreground="#22c55e">✓ Installed</span>')
            self.warp_btn.set_label("Reinstall")
        else:
            self.warp_status.set_markup('<span foreground="#f44336">✗ Not installed</span>')
            self.warp_btn.set_label("Install")
        self.warp_btn.set_sensitive(True)
    
    def _update_wg_status(self, installed: bool) -> None:
        """Update WireGuard status display."""
        if installed:
            self.wg_status.set_markup('<span foreground="#22c55e">✓ Installed</span>')
            self.wg_btn.set_label("Reinstall")
        else:
            self.wg_status.set_markup('<span foreground="#f59e0b">○ Not installed</span>')
            self.wg_btn.set_label("Install")
        self.wg_btn.set_sensitive(True)
    
    def _update_svc_status(self, active: bool) -> None:
        """Update service status display."""
        if active:
            self.svc_status.set_markup('<span foreground="#22c55e">✓ Running</span>')
            self.svc_btn.set_label("Restart")
        else:
            self.svc_status.set_markup('<span foreground="#f44336">✗ Not running</span>')
            self.svc_btn.set_label("Enable")
        self.svc_btn.set_sensitive(True)
    
    def _update_reg_status(self, registered: bool) -> None:
        """Update registration status display."""
        if registered:
            self.reg_status.set_markup('<span foreground="#22c55e">✓ Registered</span>')
            self.reg_btn.set_label("Re-register")
        else:
            self.reg_status.set_markup('<span foreground="#f44336">✗ Not registered</span>')
            self.reg_btn.set_label("Register")
        self.reg_btn.set_sensitive(True)
    
    def _run_terminal_command(self, command: str, description: str) -> bool:
        """Run a command that needs terminal/sudo access."""
        self._log(f"Running: {description}")
        self._log(f"$ {command}")
        
        try:
            # Use pkexec for graphical sudo
            if command.startswith("sudo "):
                # Try pkexec first (graphical polkit auth)
                cmd_without_sudo = command.replace("sudo ", "", 1)
                result = subprocess.run(
                    ["pkexec", "bash", "-c", cmd_without_sudo],
                    capture_output=True, text=True, timeout=300
                )
            else:
                result = subprocess.run(
                    ["bash", "-c", command],
                    capture_output=True, text=True, timeout=300
                )
            
            if result.stdout:
                self._log(result.stdout.strip())
            if result.stderr:
                self._log(result.stderr.strip())
            
            if result.returncode == 0:
                self._log(f"✓ {description} completed successfully")
                return True
            else:
                self._log(f"✗ {description} failed (exit code: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            self._log(f"✗ {description} timed out")
            return False
        except Exception as e:
            self._log(f"✗ Error: {e}")
            return False
    
    def _install_warp(self) -> None:
        """Install Cloudflare WARP CLI."""
        self.warp_btn.set_sensitive(False)
        self._log("\n=== Installing Cloudflare WARP CLI ===")
        
        def install():
            # Combined command for installation
            combined_cmd = " && ".join([
                "curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg",
                "echo 'deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ bookworm main' > /etc/apt/sources.list.d/cloudflare-client.list",
                "apt-get update",
                "apt-get install -y cloudflare-warp"
            ])
            
            success = self._run_terminal_command(
                f"sudo bash -c \"{combined_cmd}\"",
                "WARP CLI installation"
            )
            
            GLib.idle_add(self._check_status)
            if success and self._on_setup_complete:
                GLib.idle_add(self._on_setup_complete)
        
        threading.Thread(target=install, daemon=True).start()
    
    def _install_wireguard(self) -> None:
        """Install WireGuard tools."""
        self.wg_btn.set_sensitive(False)
        self._log("\n=== Installing WireGuard ===")
        
        def install():
            success = self._run_terminal_command(
                "sudo apt-get install -y wireguard-tools",
                "WireGuard installation"
            )
            GLib.idle_add(self._check_status)
        
        threading.Thread(target=install, daemon=True).start()
    
    def _enable_service(self) -> None:
        """Enable and start WARP service."""
        self.svc_btn.set_sensitive(False)
        self._log("\n=== Enabling WARP Service ===")
        
        def enable():
            success = self._run_terminal_command(
                "sudo systemctl enable --now warp-svc",
                "WARP service activation"
            )
            GLib.idle_add(self._check_status)
        
        threading.Thread(target=enable, daemon=True).start()
    
    def _new_registration(self) -> None:
        """Create new WARP registration."""
        self.reg_btn.set_sensitive(False)
        self._log("\n=== Creating WARP Registration ===")
        
        def register():
            output, success = warp_cli.new_registration()
            self._log(output if output else "Registration command executed")
            
            if success:
                self._log("✓ Registration successful")
                # Accept ToS
                self._log("Accepting Terms of Service...")
                subprocess.run(
                    ["warp-cli", "registration", "organization", "--accept-tos"],
                    capture_output=True, timeout=30
                )
            else:
                self._log("✗ Registration failed")
            
            GLib.idle_add(self._check_status)
            if success and self._on_setup_complete:
                GLib.idle_add(self._on_setup_complete)
        
        threading.Thread(target=register, daemon=True).start()
