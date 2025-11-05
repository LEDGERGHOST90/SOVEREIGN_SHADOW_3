#!/bin/bash
#
# PERSISTENT STATE HOURLY UPDATER
# Wrapper script for cron/launchd to update persistent state
#

# Navigate to project directory
cd /Volumes/LegacySafe/SovereignShadow_II || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the update script
python3 scripts/update_persistent_state.py

# Exit with the script's exit code
exit $?
