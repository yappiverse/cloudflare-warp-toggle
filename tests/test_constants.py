"""Tests for constants module."""

from __future__ import annotations

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.constants import MODES, MODE_MAP


class TestModes:
    """Tests for mode constants."""
    
    def test_modes_has_expected_keys(self):
        """Test that MODES contains expected mode keys."""
        expected_modes = ['warp', 'doh', 'warp+doh', 'dot', 'warp+dot', 'proxy', 'tunnel_only']
        
        for mode in expected_modes:
            assert mode in MODES, f"Mode '{mode}' not found in MODES"
    
    def test_modes_values_are_tuples(self):
        """Test that MODES values are (name, description) tuples."""
        for mode_key, value in MODES.items():
            assert isinstance(value, tuple), f"Mode '{mode_key}' value is not a tuple"
            assert len(value) == 2, f"Mode '{mode_key}' tuple should have 2 elements"
            assert isinstance(value[0], str), f"Mode '{mode_key}' name should be string"
            assert isinstance(value[1], str), f"Mode '{mode_key}' description should be string"
    
    def test_mode_map_normalizes_modes(self):
        """Test that MODE_MAP normalizes various mode strings."""
        # Test normalized lowercase keys
        assert MODE_MAP['warp'] == 'warp'
        assert MODE_MAP['doh'] == 'doh'
        
        # Test alternative forms
        assert MODE_MAP['warpwithdnsoverhttps'] == 'warp+doh'
        assert MODE_MAP['warpwithdnsovertls'] == 'warp+dot'
        assert MODE_MAP['tunnelonly'] == 'tunnel_only'
    
    def test_mode_map_values_exist_in_modes(self):
        """Test that all MODE_MAP values are valid MODES keys."""
        for normalized_mode in MODE_MAP.values():
            assert normalized_mode in MODES, f"Normalized mode '{normalized_mode}' not in MODES"
