#!/bin/bash
# Sovereign Shadow Daily Health Check
# Cross-platform compatible (Mac + Linux)

echo "📊 Sovereign Shadow Daily Health Check - $(date)"
echo "=================================================================="

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REBALANCE_DIR="$BASE_DIR/core/rebalancing"

cd "$REBALANCE_DIR" || exit 1

# Load environment if .env exists
if [ -f "$BASE_DIR/.env" ]; then
    set -a
    source "$BASE_DIR/.env"
    set +a
fi

# Portfolio status
python3 portfolio_state.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Portfolio state refreshed"
else
    echo "⚠️  Portfolio state check failed"
fi

# AAVE health
python3 -c "from aave_client import get_health_factor; print(f'AAVE Health Factor: {get_health_factor():.2f}')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  AAVE health check unavailable"
fi

# Allocation drift (dynamic from config)
python3 << 'PYTHON_EOF'
from config_loader import load_portfolio_targets
from portfolio_state import get_portfolio_allocation

try:
    p = get_portfolio_allocation()
    targets = load_portfolio_targets()

    print('\nAllocation Drift:')
    for asset, target in targets.items():
        if asset in p:
            drift = (p[asset]['weight'] - target) * 100
            status = '✅' if abs(drift) < 5 else '⚠️'
            print(f'  {status} {asset}: {drift:+.1f}pp (target: {target:.1%})')
except Exception as e:
    print(f'⚠️  Drift calculation failed: {e}')
PYTHON_EOF

echo ""
echo "💡 Run 'python3 rebalance_sim.py' to check if rebalance needed"
echo "📁 Working directory: $REBALANCE_DIR"
