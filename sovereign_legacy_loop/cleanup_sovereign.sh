#!/bin/bash

ARCHIVE="/Volumes/LegacySafe/SovereignShadow_Archive"
PRODUCTION="/Volumes/LegacySafe/SovereignShadow"

echo "🧹 Starting SovereignShadow Cleanup..."

# 1. DELETE - Safe removals
echo -e "\n=== DELETING SAFE FILES ==="
find "$PRODUCTION" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PRODUCTION" -name "*.pyc" -delete
find "$PRODUCTION" -name ".DS_Store" -delete
find "$PRODUCTION" -name "*.tmp" -delete
find "$PRODUCTION" -name "*~" -delete
echo "✅ Deleted cache and temp files"

# 2. ARCHIVE - Documentation
echo -e "\n=== ARCHIVING DOCUMENTATION ==="
find "$PRODUCTION" -name "*.md" -type f -exec mv {} "$ARCHIVE/docs/" \; 2>/dev/null
echo "✅ Moved markdown files to archive"

# 3. ARCHIVE - Test files
echo -e "\n=== ARCHIVING TEST FILES ==="
find "$PRODUCTION" -name "test_*.py" -exec mv {} "$ARCHIVE/tests/" \; 2>/dev/null
find "$PRODUCTION" -name "*_test.py" -exec mv {} "$ARCHIVE/tests/" \; 2>/dev/null
find "$PRODUCTION" -name "advanced_troubleshoot.py" -exec mv {} "$ARCHIVE/tests/" \; 2>/dev/null
echo "✅ Moved test files to archive"

# 4. ARCHIVE - Old versions
echo -e "\n=== ARCHIVING OLD VERSIONS ==="
find "$PRODUCTION" -name "*_old.py" -exec mv {} "$ARCHIVE/old_code/" \; 2>/dev/null
find "$PRODUCTION" -name "*_backup.py" -exec mv {} "$ARCHIVE/old_code/" \; 2>/dev/null
find "$PRODUCTION" -name "*copy*.py" -exec mv {} "$ARCHIVE/old_code/" \; 2>/dev/null
echo "✅ Moved old code to archive"

# 5. ARCHIVE - Large logs (>1MB or >7 days old)
echo -e "\n=== ARCHIVING OLD LOGS ==="
find "$PRODUCTION" -name "*.log" -size +1M -exec mv {} "$ARCHIVE/logs/" \; 2>/dev/null
find "$PRODUCTION" -name "*.log" -mtime +7 -exec mv {} "$ARCHIVE/logs/" \; 2>/dev/null
echo "✅ Moved large/old logs to archive"

# 6. ARCHIVE - Handoff documents
echo -e "\n=== ARCHIVING HANDOFF DOCS ==="
find "$PRODUCTION" -name "*HANDOFF*.md" -exec mv {} "$ARCHIVE/handoffs/" \; 2>/dev/null
find "$PRODUCTION" -name "*SOLUTION*.md" -exec mv {} "$ARCHIVE/handoffs/" \; 2>/dev/null
echo "✅ Moved handoff docs to archive"

# 7. Show results
echo -e "\n📊 CLEANUP RESULTS:"
echo "Production folder size: $(du -sh "$PRODUCTION" | cut -f1)"
echo "Archive folder size: $(du -sh "$ARCHIVE" | cut -f1)"

echo -e "\n✨ Cleanup complete!"
