#!/bin/bash
# Send notification to macOS (syncs to Apple Watch if enabled)
# Usage: ./notify.sh "Title" "Message"

TITLE="${1:-Sovereign Shadow}"
MESSAGE="${2:-Alert}"

osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"Glass\""
