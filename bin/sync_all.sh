#!/bin/bash
#
# MASTER SYNC SCRIPT
# Syncs BRAIN.json across all platforms
#
# Usage: ./bin/sync_all.sh
#

set -e
cd /Volumes/LegacySafe/SS_III

echo "═══════════════════════════════════════════════"
echo "  SOVEREIGN SHADOW III - MASTER SYNC"
echo "═══════════════════════════════════════════════"
echo ""

# 1. Update timestamp in BRAIN.json
echo "📝 Updating BRAIN.json timestamp..."
python3 -c "
import json
from datetime import datetime
with open('BRAIN.json', 'r') as f:
    brain = json.load(f)
brain['last_updated'] = datetime.now().isoformat()
with open('BRAIN.json', 'w') as f:
    json.dump(brain, f, indent=2)
print('   ✓ Timestamp updated')
"

# 2. Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
if git diff --quiet && git diff --staged --quiet; then
    echo "   ✓ No changes to commit"
else
    git add BRAIN.json memory/SESSIONS/*.md 2>/dev/null || true
    git commit -m "SYNC: Auto-sync $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || true
    git push origin main 2>/dev/null && echo "   ✓ Pushed to GitHub" || echo "   ⚠ Push failed (check connection)"
fi

# 3. Push to Replit (if webhook configured)
echo ""
echo "📡 Syncing to Replit..."
REPLIT_URL="https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
BRAIN_DATA=$(cat BRAIN.json)

curl -s -X POST "$REPLIT_URL/api/manus-webhook" \
    -H "Content-Type: application/json" \
    -d "{\"event\": \"sync\", \"brain\": $BRAIN_DATA}" \
    > /dev/null 2>&1 && echo "   ✓ Synced to Replit" || echo "   ⚠ Replit sync failed (check URL)"

# 4. Send notification
echo ""
echo "📱 Sending notification..."
curl -s -d "🔄 System synced at $(date '+%H:%M')" \
    "https://ntfy.sh/sovereignshadow_dc4d2fa1" \
    > /dev/null 2>&1 && echo "   ✓ Notification sent" || echo "   ⚠ Notification failed"

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ SYNC COMPLETE"
echo "═══════════════════════════════════════════════"
