#!/bin/bash
set -e

echo "Uninstalling WARP Toggle..."

# Remove desktop entry
if [ -f ~/.local/share/applications/warp-toggle.desktop ]; then
    rm ~/.local/share/applications/warp-toggle.desktop
    echo "Removed desktop entry"
fi

# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "Uninstallation complete!"
echo ""
echo "Note: This does not remove the application files or system dependencies."
echo "To fully remove, delete the cloudflare-warp-toggle directory."
