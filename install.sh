#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing WARP Toggle..."

chmod +x "$SCRIPT_DIR/warp_toggle.py"

install_dependencies() {
    if command -v apt-get &> /dev/null; then
        echo "Detected apt (Debian/Ubuntu)"
        if ! python3 -c "import gi" 2>/dev/null; then
            echo "Installing PyGObject (GTK3 Python bindings)..."
            sudo apt-get update
            sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
        fi
        if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3" 2>/dev/null; then
            echo "Installing AppIndicator3 for system tray support (optional)..."
            if apt-cache show gir1.2-ayatanaappindicator3-0.1 &>/dev/null; then
                sudo apt-get install -y gir1.2-ayatanaappindicator3-0.1 || echo "Note: System tray not available, app will work without it"
            elif apt-cache show gir1.2-appindicator3-0.1 &>/dev/null; then
                sudo apt-get install -y gir1.2-appindicator3-0.1 || echo "Note: System tray not available, app will work without it"
            else
                echo "Note: AppIndicator3 package not found. System tray will not be available."
                echo "      The app will work fine without it."
            fi
        fi
    elif command -v dnf &> /dev/null; then
        echo "Detected dnf (Fedora/RHEL)"
        if ! python3 -c "import gi" 2>/dev/null; then
            echo "Installing PyGObject (GTK3 Python bindings)..."
            sudo dnf install -y python3-gobject gtk3
        fi
        if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1')" 2>/dev/null; then
            echo "Installing AppIndicator3 for system tray support (optional)..."
            sudo dnf install -y libappindicator-gtk3 || echo "Note: System tray not available"
        fi
    elif command -v pacman &> /dev/null; then
        echo "Detected pacman (Arch Linux)"
        if ! python3 -c "import gi" 2>/dev/null; then
            echo "Installing PyGObject (GTK3 Python bindings)..."
            sudo pacman -S --noconfirm python-gobject gtk3
        fi
        if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1')" 2>/dev/null; then
            echo "Installing AppIndicator3 for system tray support (optional)..."
            sudo pacman -S --noconfirm libappindicator-gtk3 || echo "Note: System tray not available"
        fi
    else
        echo "Warning: Unknown package manager. Please install manually:"
        echo "  - python3-gi (PyGObject)"
        echo "  - gir1.2-gtk-3.0"
        echo "  - gir1.2-appindicator3-0.1 (optional, for system tray)"
    fi
}

install_dependencies

echo "Installing desktop entry..."
sed "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$SCRIPT_DIR/warp-toggle.desktop.template" > ~/.local/share/applications/warp-toggle.desktop

update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "Installation complete!"
echo ""
echo "You can now:"
echo "  1. Run directly: $SCRIPT_DIR/warp_toggle.py"
echo "  2. Search 'WARP Wrapper' in your application menu"
echo ""
echo "To uninstall, run: $SCRIPT_DIR/uninstall.sh"
