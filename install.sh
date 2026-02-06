set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing WARP Toggle..."

chmod +x "$SCRIPT_DIR/warp_toggle.py"

if ! python3 -c "import gi" 2>/dev/null; then
    echo "Installing PyGObject (GTK3 Python bindings)..."
    sudo apt-get update
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
fi

echo "Installing desktop entry..."
sed "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$SCRIPT_DIR/warp-toggle.desktop.template" > ~/.local/share/applications/warp-toggle.desktop

update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "Installation complete!"
echo ""
echo "You can now:"
echo "  1. Run directly: $SCRIPT_DIR/warp_toggle.py"
echo "  2. Search 'WARP Wrapper' in your application menu"
