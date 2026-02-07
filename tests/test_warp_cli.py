"""Tests for warp_cli module."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.warp_cli import core, status, settings, account, tunnel


class TestCore:
    """Tests for core.py functions."""
    
    def test_run_command_success(self, mock_subprocess_run):
        """Test successful command execution."""
        mock_subprocess_run.return_value.stdout = "Success output"
        mock_subprocess_run.return_value.returncode = 0
        
        output, success = core.run_command(['status'])
        
        assert success is True
        assert output == "Success output"
        mock_subprocess_run.assert_called_once()
    
    def test_run_command_failure(self, mock_subprocess_run):
        """Test failed command execution."""
        mock_subprocess_run.return_value.stdout = "Error"
        mock_subprocess_run.return_value.returncode = 1
        
        output, success = core.run_command(['invalid'])
        
        assert success is False
    
    def test_run_command_timeout(self):
        """Test command timeout handling."""
        import subprocess
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd='test', timeout=10)
            
            output, success = core.run_command(['status'])
            
            assert success is False
            assert 'timed out' in output.lower()
    
    def test_run_command_not_found(self, mock_warp_unavailable):
        """Test warp-cli not installed handling."""
        output, success = core.run_command(['status'])
        
        assert success is False
        assert 'warp-cli not found' in output.lower()
    
    def test_is_warp_cli_available_true(self, mock_subprocess_run):
        """Test warp-cli availability check when installed."""
        mock_subprocess_run.return_value.returncode = 0
        
        result = core.is_warp_cli_available()
        
        assert result is True
    
    def test_is_warp_cli_available_false(self, mock_warp_unavailable):
        """Test warp-cli availability check when not installed."""
        result = core.is_warp_cli_available()
        
        assert result is False


class TestStatus:
    """Tests for status.py functions."""
    
    def test_get_status_connected(self, mock_connected_status):
        """Test connected status detection."""
        is_connected, network = status.get_status()
        
        assert is_connected is True
        assert network == "WARP"
    
    def test_get_status_disconnected(self, mock_disconnected_status):
        """Test disconnected status detection."""
        is_connected, network = status.get_status()
        
        assert is_connected is False
    
    def test_get_mode_warp(self, mock_settings_output):
        """Test mode detection."""
        mode = status.get_mode()
        
        assert mode == 'warp'
    
    def test_get_mode_doh(self, mock_subprocess_run):
        """Test DoH mode detection."""
        mock_subprocess_run.return_value.stdout = "Mode: doh"
        
        mode = status.get_mode()
        
        assert mode == 'doh'


class TestSettings:
    """Tests for settings.py functions."""
    
    def test_get_families_mode_off(self, mock_subprocess_run):
        """Test families mode off detection."""
        mock_subprocess_run.return_value.stdout = "Families mode: off"
        
        mode = settings.get_families_mode()
        
        assert mode == 'off'
    
    def test_get_families_mode_malware(self, mock_subprocess_run):
        """Test families mode malware detection."""
        mock_subprocess_run.return_value.stdout = "Families mode: malware"
        
        mode = settings.get_families_mode()
        
        assert mode == 'malware'
    
    def test_get_families_mode_full(self, mock_subprocess_run):
        """Test families mode full detection."""
        mock_subprocess_run.return_value.stdout = "Families mode: malware and adult content"
        
        mode = settings.get_families_mode()
        
        assert mode == 'full'
    
    def test_get_dns_logging_enabled(self, mock_subprocess_run):
        """Test DNS logging enabled detection."""
        mock_subprocess_run.return_value.stdout = "DNS logging: enabled"
        
        result = settings.get_dns_logging()
        
        assert result is True
    
    def test_get_dns_logging_disabled(self, mock_subprocess_run):
        """Test DNS logging disabled detection."""
        mock_subprocess_run.return_value.stdout = "DNS logging: disabled"
        
        result = settings.get_dns_logging()
        
        assert result is False


class TestAccount:
    """Tests for account.py functions."""
    
    def test_get_account_info_success(self, mock_subprocess_run):
        """Test account info parsing."""
        mock_subprocess_run.return_value.stdout = """
Account type: Free
Device ID: abc123
Account ID: def456
"""
        
        info = account.get_account_info()
        
        assert info['Type'] == 'Free'
        assert info['Device ID'] == 'abc123'
        assert info['Account ID'] == 'def456'
    
    def test_get_account_info_not_registered(self, mock_subprocess_run):
        """Test account info when not registered."""
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = "Not registered"
        
        info = account.get_account_info()
        
        assert info['Type'] == '-'
        assert info['Device ID'] == '-'


class TestTunnel:
    """Tests for tunnel.py functions."""
    
    def test_get_tunnel_protocol_wireguard(self, mock_subprocess_run):
        """Test WireGuard protocol detection."""
        mock_subprocess_run.return_value.stdout = "Protocol: WireGuard"
        
        protocol = tunnel.get_tunnel_protocol()
        
        assert protocol == 'wireguard'
    
    def test_get_tunnel_protocol_masque(self, mock_subprocess_run):
        """Test MASQUE protocol detection."""
        mock_subprocess_run.return_value.stdout = "Protocol: MASQUE"
        
        protocol = tunnel.get_tunnel_protocol()
        
        assert protocol == 'masque'
    
    def test_get_network_info(self, mock_subprocess_run):
        """Test network info parsing."""
        mock_subprocess_run.return_value.stdout = """
Interface: CloudflareWARP
IP: 100.96.0.1
Gateway: 100.96.0.1
DNS: 1.1.1.1
"""
        
        info = tunnel.get_network_info()
        
        assert info['Interface'] == 'CloudflareWARP'
        assert info['IP'] == '100.96.0.1'
        assert info['DNS'] == '1.1.1.1'
