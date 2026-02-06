# Cloudflare WARP Toggle

A graphical user interface for controlling Cloudflare WARP CLI on Linux. This application provides a convenient way to manage WARP connections, configure settings, monitor statistics, and handle account management through a native GTK3 interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Application Tabs](#application-tabs)
- [Supported Modes](#supported-modes)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

Cloudflare WARP Toggle is a Python GTK3 application that wraps the `warp-cli` command-line tool, providing a user-friendly graphical interface for managing WARP connections on Linux systems. The application automatically detects and respects the system theme (light/dark mode) and provides real-time status updates.

## Features

- **Connection Management**: Connect and disconnect from WARP with a single click
- **Multiple Operating Modes**: Support for WARP, DoH, DoT, and proxy configurations
- **Real-time Status**: Live connection status updates with visual indicators
- **Statistics Monitoring**: View tunnel statistics and network information
- **Account Management**: Manage WARP licenses and registrations
- **Trusted Networks**: Configure WiFi SSIDs and network trust settings
- **Families Mode**: Enable content filtering (malware, adult content)
- **DNS Logging**: Toggle DNS query logging
- **Protocol Selection**: Choose between WireGuard and MASQUE tunnel protocols
- **System Theme Integration**: Automatically adapts to GNOME light/dark theme settings

## Requirements

### System Requirements

- Linux operating system (tested on Debian/Ubuntu with GNOME)
- Python 3.6 or later
- GTK 3.0

### Dependencies

- `warp-cli` - Cloudflare WARP command-line client must be installed and configured
- `python3-gi` - Python GObject introspection bindings
- `python3-gi-cairo` - Cairo bindings for GTK
- `gir1.2-gtk-3.0` - GTK 3 introspection data

### Installing Cloudflare WARP CLI

Before using this application, you must install the Cloudflare WARP client:

```bash
# Add Cloudflare GPG key
curl -fsSL https://pkg.cloudflarewarp.com/cloudflare-warp-ascii.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflarewarp.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list

# Install WARP client
sudo apt update && sudo apt install cloudflare-warp

# Register the client
warp-cli registration new
```

## Installation

1. Clone or download this repository:

```bash
git clone https://github.com/yourusername/cloudflare-warp-toggle.git
cd cloudflare-warp-toggle
```

2. Run the installation script:

```bash
./install.sh
```

The installation script will:

- Make the main script executable
- Install required Python GTK dependencies if not present
- Create a desktop entry for easy application launching

3. After installation, you can:
   - Run directly: `./warp_toggle.py`
   - Search for "WARP Wrapper" in your GNOME activities menu

## Usage

### Running the Application

```bash
# Direct execution
./warp_toggle.py

# Or via Python
python3 warp_toggle.py
```

### Desktop Integration

After running the installation script, the application will appear in your application menu under "WARP Wrapper". You can search for it in GNOME Activities or add it to your favorites.

## Application Tabs

### Connection Tab

The main tab provides:

- Current connection status with visual indicator
- Toggle switch to connect/disconnect
- Connection mode display
- Real-time status updates every 3 seconds

### Settings Tab

Configure WARP behavior:

- **Operating Mode**: Select from WARP, DoH, DoT, and proxy modes
- **Tunnel Protocol**: Choose between WireGuard and MASQUE
- **Families Mode**: Off, Malware-only, or Full (malware + adult content)
- **DNS Logging**: Enable or disable DNS query logging
- **Trusted Networks**: Configure auto-disconnect behavior for WiFi and Ethernet
- **Trusted SSIDs**: Manage specific WiFi networks as trusted

### Stats Tab

View connection statistics:

- Tunnel protocol in use
- Data transfer statistics
- Network information
- Connectivity check results

### Account Tab

Manage your WARP account:

- View account status and device ID
- Register with a license key
- Create new registration
- Delete current registration
- View organization information (if enrolled in Teams)

## Supported Modes

| Mode           | CLI Value     | Description                     |
| -------------- | ------------- | ------------------------------- |
| WARP           | `warp`        | Full tunnel with encrypted DNS  |
| DNS over HTTPS | `doh`         | DNS encryption only using HTTPS |
| WARP + DoH     | `warp+doh`    | Full tunnel with DNS over HTTPS |
| DNS over TLS   | `dot`         | DNS encryption only using TLS   |
| WARP + DoT     | `warp+dot`    | Full tunnel with DNS over TLS   |
| Proxy          | `proxy`       | SOCKS5 proxy tunnel             |
| Tunnel Only    | `tunnel_only` | Tunnel without DNS proxy        |

## Project Structure

```
cloudflare-warp-toggle/
├── warp_toggle.py              # Main application entry point
├── install.sh                  # Installation script
├── warp-toggle.desktop.template # Desktop entry template
├── Cloudflare-WARP.webp        # Application icon
├── .gitignore                  # Git ignore rules
└── src/
    ├── __init__.py
    ├── constants.py            # Application constants and mode definitions
    ├── styles.py               # CSS styling for the application
    ├── warp_cli/               # WARP CLI wrapper module
    │   ├── __init__.py
    │   ├── core.py             # Core command execution
    │   ├── status.py           # Connection status functions
    │   ├── account.py          # Account management functions
    │   ├── settings.py         # Settings management functions
    │   └── tunnel.py           # Tunnel and network functions
    ├── tabs/                   # UI tab components
    │   ├── __init__.py
    │   ├── connection_tab.py   # Main connection UI
    │   ├── settings_tab.py     # Settings configuration UI
    │   ├── stats_tab.py        # Statistics display UI
    │   └── account_tab.py      # Account management UI
    └── widgets/                # Custom GTK widgets
        ├── __init__.py
        ├── status_indicator.py # Connection status indicator
        └── toggle_switch.py    # Custom toggle switch
```

## Configuration

### Application Constants

The application behavior can be modified by editing `src/constants.py`:

- `WINDOW_WIDTH`: Application window width (default: 380)
- `WINDOW_HEIGHT`: Application window height (default: 580)
- `REFRESH_INTERVAL_SECONDS`: Auto-refresh interval for connection status (default: 3)
- `COMMAND_TIMEOUT`: Timeout for warp-cli commands in seconds (default: 10)

### Desktop Entry

The desktop entry is installed to `~/.local/share/applications/warp-toggle.desktop`. The template file `warp-toggle.desktop.template` is used during installation to generate the final desktop entry with correct paths.

## Troubleshooting

### Application Does Not Start

1. Verify Python GTK dependencies are installed:

   ```bash
   python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk"
   ```

2. If the above fails, install dependencies:
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```

### WARP CLI Not Found

Ensure `warp-cli` is installed and accessible in your PATH:

```bash
which warp-cli
warp-cli status
```

### Connection Fails

1. Check WARP service status:

   ```bash
   systemctl status warp-svc
   ```

2. Ensure the client is registered:

   ```bash
   warp-cli registration show
   ```

3. If not registered, create a new registration:
   ```bash
   warp-cli registration new
   ```

### Theme Not Applied

The application reads the GNOME color scheme setting. Ensure your desktop environment properly sets the `org.gnome.desktop.interface color-scheme` gsetting. You can check with:

```bash
gsettings get org.gnome.desktop.interface color-scheme
```

### Desktop Entry Not Appearing

1. Update the desktop database:

   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

2. Log out and log back in, or restart GNOME Shell (Alt+F2, type `r`, press Enter)

## License

This project is provided as-is for personal use. See the source code for details.

---

For more information about Cloudflare WARP, visit the official documentation at https://developers.cloudflare.com/warp-client/
