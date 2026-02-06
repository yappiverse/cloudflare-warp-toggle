import subprocess
from ..constants import COMMAND_TIMEOUT


def run_command(args, timeout=COMMAND_TIMEOUT):
    """Run a warp-cli command and return (output, success)"""
    try:
        result = subprocess.run(
            ['warp-cli'] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip(), result.returncode == 0
    except subprocess.TimeoutExpired:
        return "Timeout", False
    except Exception as e:
        return str(e), False
