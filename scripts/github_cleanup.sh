#!/bin/bash
# =============================================================================
# GITHUB DEPLOYMENT CLEANUP SCRIPT
# =============================================================================
# Removes all sensitive data before pushing to GitHub
# Run this BEFORE your first git push
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "========================================================================"
echo "🔐 GITHUB DEPLOYMENT CLEANUP - SOVEREIGN SHADOW II"
echo "========================================================================"
echo ""
echo "This script will remove all sensitive data before GitHub push."
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will DELETE files permanently!${NC}"
echo ""
echo "What will be deleted:"
echo "  • Archive directories (config/Abicus&ENV/, abicusHO2CC*/)"
echo "  • AbacusAI files (.abacus.donotdelete)"
echo "  • Build artifacts (*.tsbuildinfo, __pycache__)"
echo "  • Transaction CSV files (ledgerlive-*.csv, etc.)"
echo "  • Sensitive logs (*_report.json)"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}❌ Cleanup cancelled${NC}"
    exit 1
fi

echo ""
echo "========================================================================"
echo "🗑️  STARTING CLEANUP..."
echo "========================================================================"
echo ""

# Track what was deleted
deleted_count=0
deleted_size=0

# Function to delete files/directories
delete_item() {
    local pattern="$1"
    local description="$2"

    echo "🔍 Searching for: $description"

    # Find and delete
    if [ -d "$pattern" ] || [ -f "$pattern" ]; then
        size=$(du -sh "$pattern" 2>/dev/null | cut -f1 || echo "0")
        rm -rf "$pattern"
        echo -e "   ${GREEN}✓${NC} Deleted: $pattern ($size)"
        ((deleted_count++))
    else
        # Pattern search
        found=$(find . -path "$pattern" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$found" -gt 0 ]; then
            find . -path "$pattern" -print -exec rm -rf {} + 2>/dev/null || true
            echo -e "   ${GREEN}✓${NC} Deleted $found items matching: $pattern"
            ((deleted_count+=$found))
        else
            echo -e "   ${YELLOW}⊘${NC} None found: $pattern"
        fi
    fi
}

# 1. Archive directories
echo ""
echo "📦 Step 1/7: Archive directories"
delete_item "config/Abicus&ENV" "Abicus&ENV archive"
delete_item "config/AbicusENV" "AbicusENV archive"
delete_item "./abicusHO2CC*" "abicusHO2CC archives"
delete_item "./*backup*" "Backup directories"
delete_item "./*_backup" "Backup directories (underscore)"

# 2. AbacusAI files
echo ""
echo "🤖 Step 2/7: AbacusAI files"
delete_item "./.abacus.donotdelete" "AbacusAI root file"
delete_item "*/.abacus.donotdelete" "AbacusAI files in subdirs"

# 3. Build artifacts
echo ""
echo "🏗️  Step 3/7: Build artifacts"
delete_item "./*/tsconfig.tsbuildinfo" "TypeScript build info"
delete_item "./*/__pycache__" "Python cache dirs"
delete_item "./node_modules" "Node modules (will be in .gitignore)"
delete_item "./app/.next" "Next.js build (will be in .gitignore)"

# 4. Transaction CSV files
echo ""
echo "💳 Step 4/7: Transaction CSV files"
delete_item "./*/ledgerlive-*.csv" "Ledger Live CSVs"
delete_item "./*/*/ledgerlive-*.csv" "Ledger Live CSVs (nested)"
delete_item "./*/data/*transaction*.csv" "Transaction CSVs"
delete_item "./*/data/*operations*.csv" "Operations CSVs"

# 5. Sensitive logs
echo ""
echo "📋 Step 5/7: Sensitive logs"
delete_item "logs/security_audit_detailed.json" "Detailed security audit"
delete_item "logs/security_audit_summary.json" "Summary security audit"
delete_item "logs/aave_monitor_report.json" "AAVE monitor report"
delete_item "logs/*_report.json" "All report JSONs"

# 6. Verify .env is not tracked
echo ""
echo "🔒 Step 6/7: Verify .env protection"
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo -e "   ${RED}⚠️  .env is tracked by Git!${NC}"
    echo "   Removing from Git (file will remain on disk)..."
    git rm --cached .env
    echo -e "   ${GREEN}✓${NC} .env removed from Git tracking"
else
    echo -e "   ${GREEN}✓${NC} .env is NOT tracked (good)"
fi

# 7. Verify .env.example exists
echo ""
echo "📝 Step 7/7: Verify .env.example exists"
if [ -f ".env.example" ]; then
    echo -e "   ${GREEN}✓${NC} .env.example exists"
else
    echo -e "   ${RED}❌ .env.example missing!${NC}"
    echo "   Please create .env.example before pushing"
fi

echo ""
echo "========================================================================"
echo "✅ CLEANUP COMPLETE"
echo "========================================================================"
echo ""
echo "📊 Summary:"
echo "   • Items deleted: $deleted_count"
echo ""

# Run security audit
echo "========================================================================"
echo "🔍 RUNNING SECURITY AUDIT..."
echo "========================================================================"
echo ""

if [ -f "scripts/github_security_audit.py" ]; then
    python3 scripts/github_security_audit.py || true

    echo ""
    echo "========================================================================"
    echo "📄 REVIEW AUDIT RESULTS ABOVE"
    echo "========================================================================"
    echo ""
    echo "✅ If audit shows '0 findings' → SAFE TO PUSH TO GITHUB"
    echo "❌ If audit shows findings → REVIEW AND FIX BEFORE PUSHING"
    echo ""

    # Check audit results
    if [ -f "logs/security_audit_summary.json" ]; then
        findings=$(python3 -c "import json; data=json.load(open('logs/security_audit_summary.json')); print(data.get('total_findings', -1))")

        if [ "$findings" = "0" ]; then
            echo -e "${GREEN}🎉 SUCCESS: No sensitive data found - ready for GitHub!${NC}"
            echo ""
            echo "Next steps:"
            echo "  1. git status  # Verify no sensitive files shown"
            echo "  2. git add ."
            echo "  3. git commit -m 'Initial commit - Sovereign Shadow II'"
            echo "  4. git push origin main"
        else
            echo -e "${RED}⚠️  WARNING: $findings sensitive findings remain${NC}"
            echo ""
            echo "Review logs/security_audit_detailed.json for details"
            echo ""
            echo -e "${RED}DO NOT PUSH TO GITHUB YET!${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Security audit script not found${NC}"
    echo "   Skipping audit - please verify manually"
fi

echo ""
echo "========================================================================"
echo ""
