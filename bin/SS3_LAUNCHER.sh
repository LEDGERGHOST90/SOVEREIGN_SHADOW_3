#!/bin/bash
# ============================================================================
#  SOVEREIGN SHADOW 3 - BLADE RUNNER DESKTOP LAUNCHER
#  "Wake up. Time to trade."
# ============================================================================

SS3_ROOT="/Volumes/LegacySafe/SS_III"
BRAIN_FILE="$SS3_ROOT/BRAIN.json"
LOG_DIR="$SS3_ROOT/logs"
BACKEND_DIR="$SS3_ROOT/neural_hub/backend"
FRONTEND_DIR="$SS3_ROOT/strategySynthai"

# Source the Blade Runner styling
source "$SS3_ROOT/core/styles/blade_runner.sh"

# Create logs directory if needed
mkdir -p "$LOG_DIR"

# ============================================================================
# BLADE RUNNER BOOT SEQUENCE
# ============================================================================

br_clear
br_rain 3
br_banner
br_scan_line
echo

# Log startup
echo "$(br_timestamp) - SS3 Launcher initiated" >> "$LOG_DIR/launcher.log"

br_section "NEXUS-7 NEURAL INTERFACE"
br_typewriter "Initializing replicant systems..." 0.012
br_typewriter "Loading memory banks..." 0.012

# Check BRAIN.json
if [[ -f "$BRAIN_FILE" ]]; then
    br_typewriter "BRAIN.json synchronized" 0.012
else
    br_alert_warning "BRAIN.json not found"
fi

br_typewriter "Council protocols engaging..." 0.012
br_scan_line
echo

# ============================================================================
# 1. Start Council Bridge (Backend API)
# ============================================================================
br_section "COUNCIL BRIDGE"
if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    br_status_service "Council Bridge API" "true" "8000"
else
    br_typewriter "Spinning up neural backend..." 0.010
    if [[ -d "$BACKEND_DIR" && -f "$BACKEND_DIR/main.py" ]]; then
        cd "$BACKEND_DIR"
        source "$SS3_ROOT/venv/bin/activate" 2>/dev/null || true
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/council_bridge.log" 2>&1 &
        sleep 2
        if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
            br_status_service "Council Bridge API" "true" "8000"
        else
            br_status_service "Council Bridge API" "false" "8000"
        fi
    else
        br_dim "Backend not configured - skipping"
    fi
fi
echo

# ============================================================================
# 2. Start GIO Frontend
# ============================================================================
br_section "GIO INTERFACE"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    br_status_service "GIO Frontend" "true" "3000"
else
    if [[ -d "$FRONTEND_DIR/node_modules" ]]; then
        br_typewriter "Booting holographic display..." 0.010
        cd "$FRONTEND_DIR"
        nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
        sleep 3
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            br_status_service "GIO Frontend" "true" "3000"
        else
            br_status_service "GIO Frontend" "false" "3000"
        fi
    else
        br_dim "Frontend not installed - run 'npm install' in strategySynthai/"
    fi
fi
echo

# ============================================================================
# 3. AI COUNCIL STATUS
# ============================================================================
br_scan_line
br_status_council
br_scan_line

# ============================================================================
# 4. Blade Runner Quote
# ============================================================================
br_quote

# ============================================================================
# 5. Open Claude Code Terminal with Custom Splash
# ============================================================================
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "cd '/Volumes/LegacySafe/SS_III' && clear && source core/styles/blade_runner.sh && printf '${BR_CYAN}' && echo '
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     ███████╗███████╗██████╗    ║  SOVEREIGN SHADOW 3         ║
    ║     ██╔════╝██╔════╝╚════██╗   ║  Neural Interface Active    ║
    ║     ███████╗███████╗ █████╔╝   ║  ─────────────────────────  ║
    ║     ╚════██║╚════██║ ╚═══██╗   ║  AURORA • GIO • ARCHITECT   ║
    ║     ███████║███████║██████╔╝   ║  Council Online             ║
    ║     ╚══════╝╚══════╝╚═════╝    ║                             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
' && printf '\\033[0m' && echo '' && printf '\\033[38;5;240m' && echo '    \"Wake up, time to trade.\"' && printf '\\033[0m' && echo '' && echo '' && claude --print 'Read BRAIN.json. Quick status: portfolio, debt, active missions. BRAIN BLAST ACTIVATED'"
end tell
APPLESCRIPT

# ============================================================================
# 6. Open GIO Dashboard in Browser
# ============================================================================
sleep 2
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    br_print "Opening GIO Dashboard in browser..."
    open "http://localhost:3000"
fi

# ============================================================================
# COMPLETE
# ============================================================================
echo "$(br_timestamp) - SS3 Launcher complete" >> "$LOG_DIR/launcher.log"

br_scan_line
br_alert_success "Launch sequence complete"
br_dim "All systems nominal"
echo

# macOS notification
osascript -e 'display notification "Neural systems online. Council assembled." with title "SOVEREIGN SHADOW 3" subtitle "「 REPLICANT SYSTEMS ACTIVE 」"'

br_brain_blast
