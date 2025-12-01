#!/bin/bash
# Install nightly cleanup LaunchD job

PLIST_SOURCE="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/config/com.sovereignshadow.nightly-cleanup.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.sovereignshadow.nightly-cleanup.plist"

echo "Installing nightly cleanup job..."

# Unload existing job if present
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Copy plist to LaunchAgents
cp "$PLIST_SOURCE" "$PLIST_DEST"

# Load the job
launchctl load "$PLIST_DEST"

echo "✅ Nightly cleanup job installed!"
echo "   Runs daily at 11:55 PM"
echo ""
echo "To check status:"
echo "   launchctl list | grep nightly-cleanup"
echo ""
echo "To run manually:"
echo "   /Volumes/LegacySafe/SOVEREIGN_SHADOW_3/bin/nightly_cleanup.sh"
echo ""
echo "To view logs:"
echo "   tail -f /Volumes/LegacySafe/SOVEREIGN_SHADOW_3/logs/maintenance/nightly_cleanup.log"
