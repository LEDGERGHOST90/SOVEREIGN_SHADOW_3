#!/bin/bash
#
# MEMEMACHINE SCHEDULED SCANNER
# Runs 3x daily: 8AM, 12PM, 6PM PST
# Scans for breakout candidates and smart money activity
#

set -e

PROJECT_ROOT="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3"
LOGS_DIR="${PROJECT_ROOT}/logs/meme_machine"
TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
HOUR=$(date +"%H")

cd "$PROJECT_ROOT"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Log file for this run
LOG_FILE="${LOGS_DIR}/scan_${TIMESTAMP}.log"

echo "========================================" >> "$LOG_FILE"
echo "MEMEMACHINE SCAN - $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Activate venv if exists
if [ -f "${PROJECT_ROOT}/venv/bin/activate" ]; then
    source "${PROJECT_ROOT}/venv/bin/activate"
fi

# MORNING SCAN (6AM-11AM): Focus on overnight movers
if [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 12 ]; then
    echo "" >> "$LOG_FILE"
    echo "[MORNING SCAN] Finding overnight movers..." >> "$LOG_FILE"

    echo "--- BREAKOUT CANDIDATES (score > 70) ---" >> "$LOG_FILE"
    python -m meme_machine --breakout --min-score 70 >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- SMART MONEY BUYS ---" >> "$LOG_FILE"
    python -m meme_machine --smart-buys >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- GRADUATING TO RAYDIUM ---" >> "$LOG_FILE"
    python -m meme_machine --graduating >> "$LOG_FILE" 2>&1 || true

# MIDDAY SCAN (12PM-5PM): Momentum plays
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 18 ]; then
    echo "" >> "$LOG_FILE"
    echo "[MIDDAY SCAN] Catching momentum..." >> "$LOG_FILE"

    echo "--- KING OF THE HILL ---" >> "$LOG_FILE"
    python -m meme_machine --kings >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- TRENDING TOKENS ---" >> "$LOG_FILE"
    python -m meme_machine --trending >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- BREAKOUT UPDATE ---" >> "$LOG_FILE"
    python -m meme_machine --breakout --min-score 70 >> "$LOG_FILE" 2>&1 || true

# EVENING SCAN (6PM-11PM): Asian market prep + new launches
else
    echo "" >> "$LOG_FILE"
    echo "[EVENING SCAN] New launches + whale activity..." >> "$LOG_FILE"

    echo "--- PUMP.FUN NEW LAUNCHES ---" >> "$LOG_FILE"
    python -m meme_machine --pumpfun >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- WHALE ACTIVITY ---" >> "$LOG_FILE"
    python -m meme_machine --whales >> "$LOG_FILE" 2>&1 || true

    echo "" >> "$LOG_FILE"
    echo "--- BREAKOUT UPDATE ---" >> "$LOG_FILE"
    python -m meme_machine --breakout --min-score 70 >> "$LOG_FILE" 2>&1 || true
fi

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "SCAN COMPLETE - $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Copy to latest for easy access
cp "$LOG_FILE" "${LOGS_DIR}/LATEST_SCAN.log"

# CHECK FOR HIGH SCORE ALERTS AND NOTIFY
SNIPE_COUNT=$(grep -c "SNIPE" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$SNIPE_COUNT" -gt 0 ]; then
    # Get the token names
    SNIPE_TOKENS=$(grep "SNIPE" "$LOG_FILE" | head -3)

    # Play Vegas 808 trap → Jessica voice alert
    VEGAS="${PROJECT_ROOT}/sounds/vegas_trap.mp3"
    VOICE="${PROJECT_ROOT}/sounds/shadow_alert.mp3"

    [ -f "$VEGAS" ] && afplay "$VEGAS"
    [ -f "$VOICE" ] && afplay "$VOICE"

    # macOS notification (syncs to Apple Watch)
    osascript -e "display notification \"$SNIPE_COUNT tokens scored 70+! Check logs.\" with title \"SOVEREIGN SHADOW ALERT\" subtitle \"Signal locked. Execute now.\"" 2>/dev/null || true

    # Ntfy.sh notification with Jessica's voice attached
    NTFY_TOPIC="sovereignshadow_dc4d2fa1"
    JESSICA_VOICE="${PROJECT_ROOT}/sounds/shadow_alert.mp3"

    curl -s \
        -H "Title: SOVEREIGN SHADOW ALERT" \
        -H "Priority: high" \
        -H "Tags: moneybag" \
        -H "Filename: jessica_alert.mp3" \
        -T "$JESSICA_VOICE" \
        "ntfy.sh/$NTFY_TOPIC" >/dev/null 2>&1 || true

    # Pushover notification (if configured)
    if [ -n "$PUSHOVER_USER" ] && [ -n "$PUSHOVER_TOKEN" ]; then
        curl -s --form-string "token=$PUSHOVER_TOKEN" \
             --form-string "user=$PUSHOVER_USER" \
             --form-string "title=🎯 Sovereign Shadow Alert" \
             --form-string "message=$SNIPE_COUNT tokens scored 70+!" \
             https://api.pushover.net/1/messages.json >/dev/null 2>&1 || true
    fi
fi

# Cleanup old logs (keep last 7 days)
find "$LOGS_DIR" -name "scan_*.log" -mtime +7 -delete 2>/dev/null || true

echo "Scan complete. Log: $LOG_FILE"
