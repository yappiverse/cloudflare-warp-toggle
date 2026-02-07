"""Core warp-cli command execution."""

from __future__ import annotations

import subprocess
from ..constants import COMMAND_TIMEOUT


def run_command(args: list[str], timeout: int = COMMAND_TIMEOUT) -> tuple[str, bool]:
    """Run a warp-cli command and return (output, success).
    
    Args:
        args: Command arguments to pass to warp-cli
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (stdout output, success boolean)
    """
    try:
        result = subprocess.run(
            ['warp-cli'] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip(), result.returncode == 0
    except subprocess.TimeoutExpired:
        return "Command timed out", False
    except FileNotFoundError:
        return "warp-cli not found. Please install Cloudflare WARP.", False
    except Exception as e:
        return str(e), False


def is_warp_cli_available() -> bool:
    """Check if warp-cli is installed and accessible.
    
    Returns:
        True if warp-cli is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['warp-cli', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False
