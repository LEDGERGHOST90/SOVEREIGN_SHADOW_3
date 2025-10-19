#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# SovereignShadow.Ai[LegacyLoop] Bootstrap Script
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Initialize the complete Shadow.AI II ecosystem
# Usage: bash infra/scripts/bootstrap.sh "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]"
# ═══════════════════════════════════════════════════════════════════════════

set -e
ROOT="${1:-/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]}"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  SovereignShadow.Ai[LegacyLoop] Bootstrap"
echo "  Root: $ROOT"
echo "═══════════════════════════════════════════════════════════════════════════"

# Validate root exists
if [ ! -d "$ROOT" ]; then
    echo "❌ Error: Root directory does not exist: $ROOT"
    exit 1
fi

cd "$ROOT"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p apps/{claudesdk,sovereign_legacy_loop,multi-exchange-mcp}
mkdir -p infra/{scripts,config/{grafana,prometheus},docker}
mkdir -p docs/{architecture,api,guides}
mkdir -p data/{ledgerlive,backups,exports}
mkdir -p logs/{app,system,trading}

# Check for YAML config
if [ -f "SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml" ]; then
    echo "✅ Unified architecture config found"
else
    echo "⚠️  Warning: SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml not found"
fi

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."
command -v docker >/dev/null 2>&1 && echo "  ✅ Docker installed" || echo "  ❌ Docker not found"
command -v docker-compose >/dev/null 2>&1 && echo "  ✅ Docker Compose installed" || echo "  ❌ Docker Compose not found"
command -v node >/dev/null 2>&1 && echo "  ✅ Node.js installed ($(node --version))" || echo "  ❌ Node.js not found"
command -v python3 >/dev/null 2>&1 && echo "  ✅ Python installed ($(python3 --version))" || echo "  ❌ Python not found"

# Display structure
echo ""
echo "📊 Directory tree:"
tree -L 2 "$ROOT" 2>/dev/null || ls -la "$ROOT"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  ✅ Bootstrap complete!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Review: $ROOT/SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml"
echo "  2. Migrate apps (see MIGRATION_GUIDE.md)"
echo "  3. Configure .env files"
echo "  4. Run: docker-compose up -d"
echo ""

