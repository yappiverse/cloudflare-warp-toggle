"""Pytest configuration and fixtures for testing."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing warp_cli commands."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_connected_status(mock_subprocess_run):
    """Mock connected WARP status."""
    mock_subprocess_run.return_value.stdout = "Status: Connected\nNetwork: WARP"
    return mock_subprocess_run


@pytest.fixture
def mock_disconnected_status(mock_subprocess_run):
    """Mock disconnected WARP status."""
    mock_subprocess_run.return_value.stdout = "Status: Disconnected"
    return mock_subprocess_run


@pytest.fixture
def mock_warp_unavailable():
    """Mock warp-cli not being installed."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError("warp-cli not found")
        yield mock_run


@pytest.fixture
def mock_settings_output(mock_subprocess_run):
    """Mock warp-cli settings list output."""
    mock_subprocess_run.return_value.stdout = """
Mode: warp
Always On: true
Switch Lock: false
"""
    return mock_subprocess_run
