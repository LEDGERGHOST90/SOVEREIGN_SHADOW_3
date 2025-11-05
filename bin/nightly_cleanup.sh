#!/bin/bash
# 🏴 SOVEREIGN SHADOW II - Nightly Cleanup Script
# Runs at shutdown to keep directory clean and organized

set -e

PROJECT_ROOT="/Volumes/LegacySafe/SovereignShadow_II"
LOG_FILE="$PROJECT_ROOT/logs/maintenance/nightly_cleanup.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs/maintenance"

echo "[$DATE] Starting nightly cleanup..." >> "$LOG_FILE"

cd "$PROJECT_ROOT"

# 1. Remove Python cache files
echo "[$DATE] Cleaning __pycache__ directories..." >> "$LOG_FILE"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# 2. Remove .DS_Store files
echo "[$DATE] Removing .DS_Store files..." >> "$LOG_FILE"
find . -name ".DS_Store" -delete 2>/dev/null || true

# 3. Clean temporary files
echo "[$DATE] Removing temporary files..." >> "$LOG_FILE"
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

# 4. Archive old log files (older than 30 days)
echo "[$DATE] Archiving old logs..." >> "$LOG_FILE"
find logs/ -type f -name "*.log" -mtime +30 -exec gzip {} \; 2>/dev/null || true

# 5. Check for duplicate modules (safety check)
DUPLICATES=$(find agents/ modules/ -name "*.py" -type f | sort | uniq -d | wc -l)
if [ "$DUPLICATES" -gt 0 ]; then
    echo "[$DATE] WARNING: Found $DUPLICATES duplicate modules!" >> "$LOG_FILE"
fi

# 6. Verify critical files exist
CRITICAL_FILES=(
    "PERSISTENT_STATE.json"
    "agents/master_trading_system.py"
    "core/trading/strategy_knowledge_base.py"
    "app/app/page.tsx"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "[$DATE] ERROR: Critical file missing: $file" >> "$LOG_FILE"
    fi
done

# 7. Check git status (don't auto-commit)
CHANGED_FILES=$(git status --porcelain | wc -l)
if [ "$CHANGED_FILES" -gt 0 ]; then
    echo "[$DATE] INFO: $CHANGED_FILES uncommitted changes detected" >> "$LOG_FILE"
fi

echo "[$DATE] Nightly cleanup complete!" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
