# SovereignShadow.Ai[LegacyLoop] Makefile
# Quick commands for system management

.PHONY: help separation-status bootstrap deploy clean

help:
	@echo "SovereignShadow.Ai[LegacyLoop] - Available Commands"
	@echo ""
	@echo "  make separation-status  - Show KeybladeAi integration policy"
	@echo "  make bootstrap          - Initialize system structure"
	@echo "  make deploy             - Deploy all services"
	@echo "  make clean              - Clean temporary files"
	@echo ""

separation-status:
	@echo "════════════════════════════════════════════════════════════"
	@echo "  KeybladeAi Integration Policy"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Status: SEPARATE (manual flips only)"
	@echo "Path:   /Volumes/LegacySafe/GitHub/KeybladeAi"
	@echo ""
	@echo "Policy:"
	@echo "  - Keep as separate specialized tool"
	@echo "  - Use for opportunistic manual trades (20% of time)"
	@echo "  - NO full integration or database merge"
	@echo ""
	@echo "Extraction Staging:"
	@echo "  - Risk engine:        _extractions/keyblade/risk/"
	@echo "  - Vault siphon:       _extractions/keyblade/siphon/"
	@echo "  - Emergency protocols: _extractions/keyblade/protocols/"
	@echo ""
	@echo "Documentation:"
	@echo "  - YAML: SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml"
	@echo "  - Analysis: KEYBLADE_INTEGRATION_ANALYSIS.md"
	@echo "  - Runbook: docs/RUNBOOK.md"
	@echo ""
	@echo "✅ KeybladeAi properly separated and documented"
	@echo ""

bootstrap:
	@echo "Running bootstrap script..."
	@bash infra/scripts/bootstrap.sh "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]"

deploy:
	@echo "Deploying ClaudeSDK..."
	@cd apps/claudesdk && docker-compose up -d
	@echo "Deploying Sovereign Legacy Loop..."
	@cd apps/sovereign_legacy_loop && npm start &

clean:
	@echo "Cleaning temporary files..."
	@find . -name ".DS_Store" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@echo "✅ Cleanup complete"
