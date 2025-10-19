#!/bin/bash

################################################################################
# SOVEREIGN SHADOW AI - INTELLIGENT STRUCTURE ANALYZER
# Scans the sovereign_legacy_loop directory and generates detailed audit report
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop"
OUTPUT_FILE="$HOME/Desktop/SOVEREIGN_STRUCTURE_AUDIT_$(date +%Y%m%d_%H%M%S).txt"
TEMP_DIR="/tmp/sovereign_scan_$$"

echo -e "${CYAN}🏴 SOVEREIGN SHADOW AI - STRUCTURE ANALYZER${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Check if project exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

echo -e "${YELLOW}📍 Scanning: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}📄 Output: $OUTPUT_FILE${NC}"
echo ""

# Create temp directory
mkdir -p "$TEMP_DIR"

# Start audit report
{
    echo "═══════════════════════════════════════════════════════════════════"
    echo "🏴 SOVEREIGN SHADOW AI - COMPLETE STRUCTURE AUDIT"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "📅 Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📍 Project: $PROJECT_ROOT"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    cd "$PROJECT_ROOT" || exit 1

    # === OVERALL STATISTICS ===
    echo "📊 OVERALL PROJECT STATISTICS"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    
    total_files=$(find . -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" | wc -l | tr -d ' ')
    total_dirs=$(find . -type d -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" | wc -l | tr -d ' ')
    
    echo "Total Directories: $total_dirs"
    echo "Total Files: $total_files"
    echo ""
    
    echo "File Type Breakdown:"
    find . -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" | sed 's|.*\.||' | sort | uniq -c | sort -rn | head -20
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === MAIN DIRECTORY STRUCTURE ===
    echo "📁 ROOT DIRECTORY STRUCTURE (3 LEVELS)"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    
    if command -v tree &> /dev/null; then
        tree -L 3 -I 'node_modules|.next|.git|dist|build' -a --dirsfirst
    else
        find . -maxdepth 3 -type d -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" | sort
    fi
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === NEXT.JS APP ROUTES ===
    if [ -d "app" ]; then
        echo "🚀 NEXT.JS APP ROUTES (app/ directory)"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        echo "All route files:"
        find app -type f \( -name "page.tsx" -o -name "page.ts" -o -name "layout.tsx" -o -name "layout.ts" \) | sort
        echo ""
        echo "API routes:"
        find app -path "*/api/*" -type f \( -name "route.ts" -o -name "route.tsx" \) | sort
        echo ""
        echo "All TypeScript/React files in app/:"
        find app -type f \( -name "*.tsx" -o -name "*.ts" \) -not -path "*/node_modules/*" | sort
        echo ""
    else
        echo "⚠️  No app/ directory found (Next.js App Router)"
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === PAGES DIRECTORY (Legacy) ===
    if [ -d "pages" ]; then
        echo "📄 PAGES DIRECTORY (Legacy Next.js routing)"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        find pages -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) | sort
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === COMPONENTS ===
    if [ -d "components" ]; then
        echo "🧩 COMPONENTS DIRECTORY"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        echo "Component structure:"
        if command -v tree &> /dev/null; then
            tree -L 3 -I 'node_modules|.next|.git' components/
        else
            find components -type f -name "*.tsx" -o -name "*.ts" | sort
        fi
        echo ""
        echo "Total components: $(find components -type f \( -name "*.tsx" -o -name "*.ts" \) | wc -l | tr -d ' ')"
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === LIB DIRECTORY ===
    if [ -d "lib" ]; then
        echo "📚 LIB DIRECTORY (Utilities & Core Logic)"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        if command -v tree &> /dev/null; then
            tree -L 3 -I 'node_modules|.next|.git' lib/
        else
            find lib -type f \( -name "*.ts" -o -name "*.tsx" \) | sort
        fi
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === TRADING ENGINES ===
    echo "⚡ TRADING ENGINE ANALYSIS"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    echo "Files containing 'engine' (case-insensitive):"
    find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" -exec grep -l -i "engine" {} \; | sort
    echo ""
    echo "Files containing 'trading' (case-insensitive):"
    find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" -exec grep -l -i "trading" {} \; | sort
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === DUPLICATE FILES ===
    echo "🔍 POTENTIAL DUPLICATE FILES"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    echo "Files with similar names (excluding extensions):"
    find . -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/.git/*" -not -path "*/dist/*" | 
        sed 's|.*/||; s|\.[^.]*$||' | 
        sort | 
        uniq -d | 
        head -20
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === LOOSE FILES IN ROOT ===
    echo "⚠️  LOOSE FILES IN ROOT DIRECTORY"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    find . -maxdepth 1 -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" \) | sort
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === CONFIGURATION FILES ===
    echo "⚙️  CONFIGURATION FILES"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    find . -maxdepth 2 -type f \( \
        -name "*.config.ts" -o -name "*.config.js" -o \
        -name "tsconfig.json" -o -name "package.json" -o \
        -name ".env*" -o -name "*.yaml" -o -name "*.yml" \
    \) -not -path "*/node_modules/*" | sort
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === HOOKS ===
    if [ -d "hooks" ]; then
        echo "🪝 CUSTOM HOOKS"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        find hooks -type f \( -name "*.ts" -o -name "*.tsx" \) | sort
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === TYPES ===
    if [ -d "types" ]; then
        echo "📋 TYPE DEFINITIONS"
        echo "─────────────────────────────────────────────────────────────────"
        echo ""
        find types -type f \( -name "*.ts" -o -name "*.d.ts" \) | sort
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === PYTHON FILES ===
    echo "🐍 PYTHON FILES (Backend/Scripts)"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    python_files=$(find . -type f -name "*.py" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*" | wc -l | tr -d ' ')
    echo "Total Python files: $python_files"
    echo ""
    if [ "$python_files" -gt 0 ]; then
        echo "Python file locations:"
        find . -type f -name "*.py" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*" | sort
    fi
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === IMPORT ANALYSIS ===
    echo "📦 IMPORT PATTERN ANALYSIS"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    echo "Relative imports (../...):"
    find . -type f \( -name "*.ts" -o -name "*.tsx" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -exec grep -h "from ['\"]\.\./" {} \; 2>/dev/null | sort | uniq -c | sort -rn | head -20
    echo ""
    echo "Absolute imports (@/...):"
    find . -type f \( -name "*.ts" -o -name "*.tsx" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -exec grep -h "from ['\"]@/" {} \; 2>/dev/null | sort | uniq -c | sort -rn | head -20
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""

    # === RECOMMENDATIONS ===
    echo "💡 INITIAL RECOMMENDATIONS"
    echo "─────────────────────────────────────────────────────────────────"
    echo ""
    
    loose_count=$(find . -maxdepth 1 -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) | wc -l | tr -d ' ')
    if [ "$loose_count" -gt 5 ]; then
        echo "⚠️  HIGH PRIORITY: $loose_count loose files in root directory"
        echo "   → Move to appropriate domain directories (lib/, components/, etc.)"
        echo ""
    fi
    
    if [ -d "app" ] && [ -d "pages" ]; then
        echo "⚠️  WARNING: Both app/ and pages/ directories exist"
        echo "   → You're mixing Next.js App Router and Pages Router"
        echo "   → Consider migrating fully to App Router"
        echo ""
    fi
    
    if [ "$python_files" -gt 50 ]; then
        echo "📊 INFO: Large Python codebase detected ($python_files files)"
        echo "   → Consider separating Python backend into dedicated service"
        echo ""
    fi
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "✅ AUDIT COMPLETE"
    echo ""
    echo "Next Steps:"
    echo "1. Review this audit report carefully"
    echo "2. Identify priority areas for reorganization"
    echo "3. Share with Claude for custom migration plan"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"

} > "$OUTPUT_FILE"

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Audit complete!${NC}"
echo ""
echo -e "${CYAN}📄 Report saved to: ${NC}$OUTPUT_FILE"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "   ${BLUE}1.${NC} Open the report: ${GREEN}open '$OUTPUT_FILE'${NC}"
echo -e "   ${BLUE}2.${NC} Review the findings"
echo -e "   ${BLUE}3.${NC} Copy the report contents"
echo -e "   ${BLUE}4.${NC} Share with Claude for custom reorganization plan"
echo ""

# Optionally open the file
if command -v open &> /dev/null; then
    echo -e "${CYAN}Opening report...${NC}"
    open "$OUTPUT_FILE"
fi

echo -e "${GREEN}🏴 Scan complete!${NC}"

