#!/bin/bash
#
# PERSISTENT STATE HOURLY UPDATER
# Wrapper script for cron/launchd to update persistent state
#

# Navigate to project directory
cd /Volumes/LegacySafe/SS_III || exit 1

# Set Python path
export PYTHONPATH=/Volumes/LegacySafe/SS_III

# Run the portfolio sync
python3 bin/sync_portfolio.py

# Exit with the script's exit code
exit $?
