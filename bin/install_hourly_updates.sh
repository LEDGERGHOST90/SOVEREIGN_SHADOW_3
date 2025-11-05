#!/bin/bash
#
# PERSISTENT STATE HOURLY UPDATER - INSTALLER
# Installs LaunchAgent for automated hourly system snapshots
#

set -e

echo "🏴 SovereignShadow_II - Hourly Update Installer"
echo "================================================"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script needs sudo to install the LaunchAgent"
    echo ""
    echo "Please run:"
    echo "  sudo /Volumes/LegacySafe/SovereignShadow_II/bin/install_hourly_updates.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "👤 Installing for user: $ACTUAL_USER"
echo "🏠 Home directory: $USER_HOME"
echo ""

# Source and destination paths
SOURCE_PLIST="/Volumes/LegacySafe/SovereignShadow_II/config/com.sovereignshadow.state-updater.plist"
DEST_DIR="$USER_HOME/Library/LaunchAgents"
DEST_PLIST="$DEST_DIR/com.sovereignshadow.state-updater.plist"

# Ensure LaunchAgents directory exists
if [ ! -d "$DEST_DIR" ]; then
    echo "📁 Creating LaunchAgents directory..."
    mkdir -p "$DEST_DIR"
fi

# Fix ownership of LaunchAgents directory
echo "🔧 Fixing LaunchAgents directory ownership..."
chown $ACTUAL_USER:staff "$DEST_DIR"
chmod 755 "$DEST_DIR"

# Copy the plist file
echo "📋 Copying plist file..."
cp "$SOURCE_PLIST" "$DEST_PLIST"

# Fix ownership of plist file
echo "🔑 Setting correct permissions..."
chown $ACTUAL_USER:staff "$DEST_PLIST"
chmod 644 "$DEST_PLIST"

echo "✅ File installed: $DEST_PLIST"
echo ""

# Unload if already loaded (ignore errors)
echo "🔄 Unloading any existing instance..."
sudo -u $ACTUAL_USER launchctl unload "$DEST_PLIST" 2>/dev/null || true

# Load the LaunchAgent as the actual user
echo "🚀 Loading LaunchAgent..."
sudo -u $ACTUAL_USER launchctl load "$DEST_PLIST"

# Verify it's running
echo ""
echo "🔍 Verifying installation..."
sleep 2

if sudo -u $ACTUAL_USER launchctl list | grep -q "sovereignshadow"; then
    echo "✅ LaunchAgent successfully installed and running!"
    echo ""
    echo "📊 Your system will now be scanned every hour:"
    echo "   - Git state"
    echo "   - Code inventory (228 Python files, 52,644 LOC)"
    echo "   - Config file changes"
    echo "   - Python packages"
    echo "   - Trading system state"
    echo "   - Disk space"
    echo ""
    echo "📝 Logs will be written to:"
    echo "   /Volumes/LegacySafe/SovereignShadow_II/logs/persistent_state_updates.log"
    echo ""
    echo "🎯 To check status:"
    echo "   launchctl list | grep sovereignshadow"
    echo ""
    echo "🛑 To stop:"
    echo "   launchctl unload ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist"
    echo ""
    echo "🏴 Installation complete!"
else
    echo "⚠️ LaunchAgent installed but not running yet"
    echo "   It will start on next login or you can load it manually:"
    echo "   launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist"
fi

exit 0
