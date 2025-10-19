#!/bin/bash

################################################################################
# 🏴 SOVEREIGN LEGACY LOOP - SOLO TRADER STRUCTURE SCANNER
# Reality-based analysis for personal systematic trading
################################################################################

set -e

PROJECT_PATH="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop"
REPORT_FILE="$HOME/Desktop/sovereign_structure_analysis.md"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🏴 SCANNING YOUR ACTUAL TRADING EMPIRE STRUCTURE${NC}"
echo ""

# Check if path exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}❌ Path not found: $PROJECT_PATH${NC}"
    echo ""
    echo "Please update PROJECT_PATH in this script to match your actual directory."
    exit 1
fi

cd "$PROJECT_PATH" || exit 1

{
    echo "# 🏴 SOVEREIGN LEGACY LOOP - STRUCTURE ANALYSIS"
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**Path:** \`$PROJECT_PATH\`"
    echo ""
    echo "---"
    echo ""
    
    echo "## 📊 PROJECT OVERVIEW"
    echo ""
    
    # Basic stats
    total_ts=$(find . -name "*.ts" -o -name "*.tsx" | grep -v node_modules | grep -v ".next" | wc -l | tr -d ' ')
    total_py=$(find . -name "*.py" | grep -v node_modules | grep -v venv | wc -l | tr -d ' ')
    total_dirs=$(find . -type d | grep -v node_modules | grep -v ".next" | grep -v ".git" | wc -l | tr -d ' ')
    
    echo "### File Counts"
    echo "- **TypeScript files:** $total_ts"
    echo "- **Python files:** $total_py"
    echo "- **Directories:** $total_dirs"
    echo ""
    
    echo "---"
    echo ""
    
    echo "## 📁 TOP-LEVEL STRUCTURE"
    echo ""
    echo "\`\`\`"
    ls -1 | grep -v node_modules | head -30
    echo "\`\`\`"
    echo ""
    
    echo "---"
    echo ""
    
    # APP directory
    if [ -d "app" ]; then
        echo "## 🎯 APP/ DIRECTORY (Next.js Routes)"
        echo ""
        echo "### Current Route Structure:"
        echo "\`\`\`"
        find app -maxdepth 3 -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) 2>/dev/null | grep -v node_modules | sort
        echo "\`\`\`"
        echo ""
        
        echo "### ⚠️  Issues Detected:"
        echo ""
        
        # Loose files in app root
        loose_app_files=$(find app -maxdepth 1 -type f \( -name "*.tsx" -o -name "*.ts" \) 2>/dev/null | grep -v "layout\|page\|loading\|error\|globals\|providers" | wc -l | tr -d ' ')
        if [ "$loose_app_files" -gt 0 ]; then
            echo "**Loose files in app/ root:**"
            find app -maxdepth 1 -type f \( -name "*.tsx" -o -name "*.ts" \) 2>/dev/null | grep -v "layout\|page\|loading\|error\|globals\|providers" | while read -r file; do
                echo "- 🚨 \`$file\` - Should be organized by domain"
            done
            echo ""
        fi
        
        # Check for API routes
        if [ -d "app/api" ]; then
            echo "**API Routes Found:**"
            echo "\`\`\`"
            find app/api -type f -name "*.ts" 2>/dev/null | sort
            echo "\`\`\`"
            echo ""
        fi
        
    else
        echo "## ⚠️  No app/ directory found"
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # LIB directory - CRITICAL for trading logic
    if [ -d "lib" ]; then
        echo "## 🧠 LIB/ DIRECTORY (Core Logic - CRITICAL)"
        echo ""
        echo "### Current Structure:"
        echo "\`\`\`"
        find lib -maxdepth 3 -type f \( -name "*.ts" -o -name "*.js" \) 2>/dev/null | grep -v node_modules | sort
        echo "\`\`\`"
        echo ""
        
        echo "### 🔍 Trading Logic Analysis:"
        echo ""
        
        # Find trading-related files
        echo "**Trading Engine Files:**"
        find lib -type f \( -name "*.ts" -o -name "*.js" \) 2>/dev/null | while read -r file; do
            if grep -qi "class.*engine\|trading.*class\|arbitrage" "$file" 2>/dev/null; then
                lines=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
                echo "- 🎯 \`$file\` ($lines lines)"
            fi
        done
        echo ""
        
        echo "**Exchange Integration Files:**"
        find lib -type f \( -name "*.ts" -o -name "*.js" \) 2>/dev/null | while read -r file; do
            if grep -qi "binance\|okx\|kraken\|coinbase\|exchange.*class" "$file" 2>/dev/null; then
                lines=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
                echo "- 🔌 \`$file\` ($lines lines)"
            fi
        done
        echo ""
        
        echo "**DeFi Integration Files:**"
        find lib -type f \( -name "*.ts" -o -name "*.js" \) 2>/dev/null | while read -r file; do
            if grep -qi "lido\|aave\|curve\|uniswap\|defi" "$file" 2>/dev/null; then
                lines=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
                echo "- 💎 \`$file\` ($lines lines)"
            fi
        done
        echo ""
        
    else
        echo "## ⚠️  No lib/ directory found - NEEDS CREATION"
        echo ""
        echo "This is where ALL your trading logic should live!"
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # COMPONENTS
    if [ -d "components" ]; then
        echo "## 🧩 COMPONENTS/ DIRECTORY"
        echo ""
        echo "### Current Components:"
        echo "\`\`\`"
        find components -maxdepth 2 -type f -name "*.tsx" 2>/dev/null | grep -v node_modules | sort
        echo "\`\`\`"
        echo ""
        
        # Check for disorganization
        loose_components=$(find components -maxdepth 1 -type f -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$loose_components" -gt 5 ]; then
            echo "### ⚠️  Too Many Loose Components ($loose_components files need organizing):"
            echo ""
            echo "Should be organized into:"
            echo "- \`components/portfolio/\` - Portfolio UI"
            echo "- \`components/trading/\` - Trading interface"
            echo "- \`components/defi/\` - DeFi dashboards"
            echo "- \`components/ui/\` - Base components (shadcn)"
            echo ""
        fi
    else
        echo "## ⚠️  No components/ directory found"
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # HOOKS
    if [ -d "hooks" ]; then
        echo "## 🎣 HOOKS/ DIRECTORY"
        echo ""
        echo "\`\`\`"
        ls -1 hooks/ 2>/dev/null | head -20
        echo "\`\`\`"
        echo ""
        
        # Analyze hooks
        echo "### Hook Analysis:"
        find hooks -maxdepth 1 -type f \( -name "*.ts" -o -name "*.tsx" \) 2>/dev/null | while read -r hook; do
            if [ -f "$hook" ]; then
                lines=$(wc -l < "$hook" 2>/dev/null | tr -d ' ')
                echo "- \`$hook\` ($lines lines)"
            fi
        done
        echo ""
    else
        echo "## ⚠️  No hooks/ directory found"
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # PYTHON BACKEND
    if [ "$total_py" -gt 10 ]; then
        echo "## 🐍 PYTHON BACKEND DETECTED ($total_py files)"
        echo ""
        echo "### Python File Locations:"
        echo "\`\`\`"
        find . -name "*.py" -type f | grep -v node_modules | grep -v venv | grep -v "__pycache__" | sort | head -20
        echo "\`\`\`"
        echo ""
        
        echo "### Trading-Related Python Files:"
        find . -name "*.py" -type f 2>/dev/null | grep -v node_modules | grep -v venv | while read -r file; do
            if grep -qi "class.*Engine\|trading\|arbitrage\|exchange" "$file" 2>/dev/null; then
                lines=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
                echo "- 🐍 \`$file\` ($lines lines)"
            fi
        done
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # PACKAGE.JSON analysis
    if [ -f "package.json" ]; then
        echo "## 📦 DEPENDENCIES"
        echo ""
        echo "### Key Trading-Related Packages:"
        echo "\`\`\`json"
        grep -E "ccxt|ethers|web3|@ledgerhq|binance|okx|kraken|viem|wagmi" package.json 2>/dev/null || echo "{}"
        echo "\`\`\`"
        echo ""
    fi
    
    echo "---"
    echo ""
    
    # DUPLICATE DETECTION
    echo "## 🔍 DUPLICATE DETECTION"
    echo ""
    echo "### Potential Duplicate Files (same base name):"
    find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/venv/*" | 
        sed 's|.*/||; s|\.[^.]*$||' | 
        sort | 
        uniq -d | 
        head -10 | 
        while read -r basename; do
            echo "**\`$basename\`** - Found in multiple locations:"
            find . -type f -name "${basename}.*" -not -path "*/node_modules/*" -not -path "*/.next/*" | while read -r file; do
                echo "  - \`$file\`"
            done
            echo ""
        done
    echo ""
    
    echo "---"
    echo ""
    
    echo "## 🎯 LEAN ARCHITECTURE RECOMMENDATIONS"
    echo ""
    
    echo "### ✅ WHAT YOU NEED (Lean Solo Trader Structure)"
    echo ""
    echo "#### Core Logic (\`lib/\`)"
    echo "- \`lib/portfolio/\` - Aggregation, allocation, rebalancing"
    echo "- \`lib/exchanges/\` - Binance, OKX, Kraken clients (BaseExchange pattern)"
    echo "- \`lib/strategies/\` - Arbitrage detector, rebalancing logic, DCA"
    echo "- \`lib/defi/\` - LIDO, AAVE, Curve integrations"
    echo "- \`lib/vaults/\` - Ledger monitor, hot wallet management"
    echo "- \`lib/analytics/\` - Performance, cost basis, risk metrics"
    echo "- \`lib/utils/\` - Fee calculator, gas tracker, slippage estimator"
    echo ""
    
    echo "#### Routes (\`app/\`)"
    echo "- \`app/page.tsx\` - Dashboard overview"
    echo "- \`app/portfolio/\` - Portfolio views & rebalancing"
    echo "- \`app/trading/\` - Manual trading interface"
    echo "- \`app/defi/\` - DeFi protocol dashboards (lido, aave, curve)"
    echo "- \`app/vaults/\` - Cold storage + hot wallet view"
    echo "- \`app/api/\` - Backend routes"
    echo ""
    
    echo "#### UI (\`components/\`)"
    echo "- \`components/portfolio/\` - Portfolio widgets"
    echo "- \`components/trading/\` - Trading UI"
    echo "- \`components/defi/\` - DeFi protocol components"
    echo "- \`components/ui/\` - Base components (shadcn)"
    echo ""
    
    echo "### ❌ WHAT YOU DON'T NEED (Avoid Overengineering)"
    echo ""
    echo "- ❌ Multiple auth routes (you're the only user)"
    echo "- ❌ Admin dashboards (you're the admin)"
    echo "- ❌ Real-time order book WebSockets (too expensive)"
    echo "- ❌ Complex route groups (adds cognitive load)"
    echo "- ❌ Microservices (premature optimization)"
    echo ""
    
    echo "### 💰 FEE-CONSCIOUS PRINCIPLES"
    echo ""
    echo "1. **Arbitrage:** Only execute when spread > 2x total fees"
    echo "2. **Rebalancing:** Threshold-based (>5% drift), not time-based"
    echo "3. **DCA:** Weekly/monthly, not daily"
    echo "4. **Gas Monitoring:** Only execute DeFi moves when gas < threshold"
    echo "5. **Slippage:** Always estimate before large trades"
    echo ""
    
    echo "---"
    echo ""
    
    echo "## 🚀 NEXT STEPS"
    echo ""
    echo "1. **Copy this entire report**"
    echo "2. **Paste it to Claude**"
    echo "3. **Claude will generate:**"
    echo "   - Custom migration scripts for YOUR files"
    echo "   - Lean architecture implementation"
    echo "   - Fee-conscious strategy templates"
    echo "   - Exchange client abstractions"
    echo "   - DeFi integration patterns"
    echo ""
    echo "4. **Execute reorganization with Claude's guidance**"
    echo "5. **Build your systematic trading empire** 🏴"
    echo ""
    
    echo "---"
    echo ""
    echo "*Generated by Sovereign Legacy Loop Lean Structure Scanner*"
    echo ""
    echo "**Philosophy:** Fee-conscious, systematic, scalable for one operator"
    
} > "$REPORT_FILE"

echo -e "${GREEN}✅ Analysis complete!${NC}"
echo ""
echo -e "📄 Report saved to: ${CYAN}$REPORT_FILE${NC}"
echo ""

# Open the report
if command -v open &> /dev/null; then
    echo "Opening report..."
    open "$REPORT_FILE"
else
    echo "Displaying report:"
    echo ""
    cat "$REPORT_FILE"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📋 NEXT: Copy the report contents and paste to Claude${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

