#!/bin/bash
# =============================================================================
# SCRNGRAB DAEMON - Auto-collect Screenshots & AirDrops
# =============================================================================

SCRNGRAB_DIR="$HOME/Desktop/SCRNGRAB"
DESKTOP="$HOME/Desktop"
DOWNLOADS="$HOME/Downloads"
LOG="$SCRNGRAB_DIR/.grab.log"

mkdir -p "$SCRNGRAB_DIR"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG"
}

# Move screenshots from Desktop
for f in "$DESKTOP"/Screenshot*.png "$DESKTOP"/Screen\ Recording*.mov; do
    if [[ -f "$f" ]]; then
        filename=$(basename "$f")
        mv "$f" "$SCRNGRAB_DIR/"
        log "GRABBED: $filename (Desktop)"
    fi
done

# Move recent AirDrops from Downloads (files modified in last 2 minutes)
find "$DOWNLOADS" -maxdepth 1 -type f -mmin -2 ! -name ".*" ! -name "*.crdownload" ! -name "*.part" 2>/dev/null | while read f; do
    filename=$(basename "$f")
    # Skip if already in SCRNGRAB
    if [[ ! -f "$SCRNGRAB_DIR/$filename" ]]; then
        mv "$f" "$SCRNGRAB_DIR/"
        log "GRABBED: $filename (AirDrop/Download)"
    fi
done

# Cleanup log if too big (>1MB)
if [[ -f "$LOG" ]] && [[ $(stat -f%z "$LOG" 2>/dev/null || echo 0) -gt 1048576 ]]; then
    tail -100 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
