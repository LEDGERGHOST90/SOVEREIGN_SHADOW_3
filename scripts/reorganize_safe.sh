#!/bin/bash
# 🏴 SOVEREIGN SHADOW - SAFE REORGANIZATION SCRIPT
# 
# This script reorganizes your empire into clean, logical folders
# WITHOUT deleting anything. All files are copied first for safety.
#
# Usage:
#   ./scripts/reorganize_safe.sh          # Dry run (copy only)
#   ./scripts/reorganize_safe.sh commit   # Finalize with git mv

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "🏴 SOVEREIGN SHADOW - SAFE REORGANIZATION"
echo "=========================================="
echo "Root: $ROOT_DIR"
echo ""

# Parse command
MODE="${1:-copy}"  # Default to copy mode

if [ "$MODE" = "commit" ]; then
    echo "⚠️  COMMIT MODE - Will use 'git mv' to finalize"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read -r
else
    echo "📋 COPY MODE - Files will be copied (not moved)"
    echo "   Run with 'commit' argument to finalize"
fi

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 1: Create new folder structure
# ═══════════════════════════════════════════════════════════

echo "📁 Creating new folder structure..."

mkdir -p trading
mkdir -p deepagent/handoff
mkdir -p ARCHIVE/old_backups_$(date +"%Y%m%d")
mkdir -p docker
mkdir -p claude_sdk

echo "   ✅ Folders created"
echo ""

# ═══════════════════════════════════════════════════════════
# STEP 2: Organize Trading Logic
# ═══════════════════════════════════════════════════════════

echo "⚡ Organizing Trading Logic → trading/"

TRADING_FILES=(
    "sovereign_shadow_orchestrator.py"
    "shadow_scope.py"
    "live_market_scanner.py"
    "strategy_knowledge_base.py"
    "REAL_PORTFOLIO_BRIDGE.py"
    "REAL_PORTFOLIO_CONNECTOR.py"
    "REAL_PORTFOLIO_ENV.txt"
    "SAFETY_RULES_IMPLEMENTATION.py"
    "MASTER_CONNECTION_MAP.py"
    "check_accounts.py"
    "test_coinbase_new.py"
)

for file in "${TRADING_FILES[@]}"; do
    if [ -f "$file" ]; then
        if [ "$MODE" = "commit" ]; then
            git mv "$file" trading/ 2>/dev/null || mv "$file" trading/
            echo "   📦 Moved: $file"
        else
            cp "$file" trading/
            echo "   📋 Copied: $file"
        fi
    else
        echo "   ⚠️  Not found: $file"
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 3: Organize DeepAgent Files
# ═══════════════════════════════════════════════════════════

echo "🧠 Organizing DeepAgent Files → deepagent/"

DEEPAGENT_FILES=(
    "DEEPAGENT_HANDOFF_PACKAGE.md"
    "DEEPAGENT_INTEGRATION_PACKAGE.tar.gz"
    "PROMPT_TO_SEND_DEEPAGENT.md"
)

for file in "${DEEPAGENT_FILES[@]}"; do
    if [ -f "$file" ]; then
        if [ "$MODE" = "commit" ]; then
            git mv "$file" deepagent/handoff/ 2>/dev/null || mv "$file" deepagent/handoff/
            echo "   📦 Moved: $file"
        else
            cp "$file" deepagent/handoff/
            echo "   📋 Copied: $file"
        fi
    else
        echo "   ⚠️  Not found: $file"
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 4: Archive Old Files
# ═══════════════════════════════════════════════════════════

echo "📦 Archiving Old Files → ARCHIVE/"

ARCHIVE_ITEMS=(
    "CLEANUP_BACKUP"
    "Master_LOOP_Creation.zip"
)

for item in "${ARCHIVE_ITEMS[@]}"; do
    if [ -e "$item" ]; then
        if [ "$MODE" = "commit" ]; then
            git mv "$item" ARCHIVE/old_backups_$(date +"%Y%m%d")/ 2>/dev/null || mv "$item" ARCHIVE/old_backups_$(date +"%Y%m%d")/
            echo "   📦 Moved: $item"
        else
            cp -r "$item" ARCHIVE/old_backups_$(date +"%Y%m%d")/
            echo "   📋 Copied: $item"
        fi
    else
        echo "   ⚠️  Not found: $item"
    fi
done

echo ""

# ═══════════════════════════════════════════════════════════
# STEP 5: Create README files in new folders
# ═══════════════════════════════════════════════════════════

echo "📝 Creating README files..."

# Trading folder README
cat > trading/README.md << 'TRADING_README'
# 🏴 Trading Logic - Sovereign Shadow

This folder contains all trading execution logic and strategies.

## Files:
- `sovereign_shadow_orchestrator.py` - Main mesh network controller
- `shadow_scope.py` - Market intelligence scanner (standalone)
- `live_market_scanner.py` - 100% failproof market scanner
- `strategy_knowledge_base.py` - 9 trading strategies
- `REAL_PORTFOLIO_*.py` - Portfolio connection & bridge
- `SAFETY_RULES_IMPLEMENTATION.py` - Risk management

## Usage:
```python
from trading.sovereign_shadow_orchestrator import SovereignShadowOrchestrator

orchestrator = SovereignShadowOrchestrator()
await orchestrator.execute_unified_trade(signal)
```

## Import Path:
Make sure PYTHONPATH includes root: `/Volumes/LegacySafe/SovereignShadow`
TRADING_README

# DeepAgent folder README
cat > deepagent/README.md << 'DEEPAGENT_README'
# 🧠 DeepAgent Integration - Web Dashboard

This folder contains all files for DeepAgent web integration on Abacus AI.

## Structure:
- `handoff/` - Complete handoff package for DeepAgent
  - `DEEPAGENT_HANDOFF_PACKAGE.md` - Technical specifications
  - `PROMPT_TO_SEND_DEEPAGENT.md` - Ready-to-send prompt
  - `DEEPAGENT_INTEGRATION_PACKAGE.tar.gz` - Compressed package

## Website:
https://legacyloopshadowai.abacusai.app

## Usage:
1. Send `PROMPT_TO_SEND_DEEPAGENT.md` to DeepAgent
2. DeepAgent builds 6 API endpoints
3. Creates live dashboard with portfolio tracking
4. Implements real-time market scanner

## Timeline:
5 weeks to production launch
DEEPAGENT_README

echo "   ✅ README files created"
echo ""

# ═══════════════════════════════════════════════════════════
# STEP 6: Verification
# ═══════════════════════════════════════════════════════════

echo "🔍 Verifying new structure..."
echo ""

echo "📁 Trading folder:"
ls -1 trading/ | head -5
echo "   ... ($(ls -1 trading/ | wc -l | tr -d ' ') files total)"
echo ""

echo "📁 DeepAgent folder:"
ls -1 deepagent/handoff/ 2>/dev/null | head -5
echo "   ... ($(ls -1 deepagent/handoff/ 2>/dev/null | wc -l | tr -d ' ') files total)"
echo ""

echo "📁 Archive folder:"
ls -1 ARCHIVE/ | head -3
echo ""

# ═══════════════════════════════════════════════════════════
# STEP 7: Test Imports
# ═══════════════════════════════════════════════════════════

echo "🧪 Testing Python imports..."

if [ "$MODE" = "commit" ]; then
    # Only test imports after commit
    python3 << 'PYEOF'
import sys
sys.path.insert(0, '/Volumes/LegacySafe/SovereignShadow')

try:
    from trading.sovereign_shadow_orchestrator import SovereignShadowOrchestrator
    print("   ✅ trading.sovereign_shadow_orchestrator - OK")
except Exception as e:
    print(f"   ❌ trading.sovereign_shadow_orchestrator - FAILED: {e}")

try:
    from trading.strategy_knowledge_base import StrategyKnowledgeBase
    print("   ✅ trading.strategy_knowledge_base - OK")
except Exception as e:
    print(f"   ❌ trading.strategy_knowledge_base - FAILED: {e}")

try:
    from shadow_sdk import ShadowScope
    print("   ✅ shadow_sdk.ShadowScope - OK")
except Exception as e:
    print(f"   ❌ shadow_sdk.ShadowScope - FAILED: {e}")
PYEOF
else
    echo "   ⏭️  Skipped (run with 'commit' to test)"
fi

echo ""

# ═══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════

echo "=========================================="
echo "🏴 REORGANIZATION COMPLETE"
echo "=========================================="
echo ""

if [ "$MODE" = "commit" ]; then
    echo "✅ FILES MOVED (Permanent)"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Test your imports in Python"
    echo "   2. Run your orchestrator to verify"
    echo "   3. Commit to Git:"
    echo "      git add ."
    echo "      git commit -m '🏗️ Clean folder structure - organized by purpose'"
    echo "      git tag v1.4-CLEAN-STRUCTURE"
else
    echo "📋 FILES COPIED (Dry run)"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Review the new folders"
    echo "   2. Check files are where you expect"
    echo "   3. When ready, finalize with:"
    echo "      ./scripts/reorganize_safe.sh commit"
    echo ""
    echo "💡 Or manually run 'git mv' commands if you prefer"
fi

echo ""
echo "🏴 Your empire is organized and ready!"

