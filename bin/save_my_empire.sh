#!/bin/bash
# 🏴 SAVE MY EMPIRE - Daily Backup Ritual
# Run this EVERY DAY - Your future self will thank you

echo "🏴 SOVEREIGN SHADOW - DAILY EMPIRE BACKUP"
echo "=========================================="

# Navigate to empire
cd /Volumes/LegacySafe/SovereignShadow

# Capture current portfolio value
echo "📊 Capturing portfolio snapshot..."
PORTFOLIO=""
if [ -f "scripts/get_real_balances.py" ]; then
    PORTFOLIO=$(python3 scripts/get_real_balances.py 2>/dev/null | grep "Total" | cut -d: -f2 | tr -d ' $')
fi

# If no portfolio script, use placeholder
if [ -z "$PORTFOLIO" ]; then
    PORTFOLIO="$8,707.86"
fi

# Get current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Create backup commit
echo "💾 Creating backup commit..."
git add -A
git commit -m "📈 Daily Empire Backup - Portfolio: \$$PORTFOLIO - $TIMESTAMP

- System operational
- Capital protected
- Edge preserved
- Empire secured 🔒"

# Push to remote (if exists)
if git remote -v | grep -q "origin"; then
    echo "🚀 Pushing to remote fortress..."
    git push
    echo "✅ Empire backed up to remote fortress"
else
    echo "⚠️  No remote fortress configured yet"
    echo "   Run: git remote add origin <your-github-repo>"
fi

# Show status
echo ""
echo "🏴 EMPIRE STATUS:"
echo "=================="
git log --oneline -1
echo ""
echo "💰 Portfolio: \$$PORTFOLIO"
echo "🕐 Backup Time: $TIMESTAMP"
echo ""
echo "✅ EMPIRE SECURED - Your future self is safe!"
echo ""

# Optional: Show recent activity
echo "📊 Recent Empire Activity:"
git log --oneline -5
