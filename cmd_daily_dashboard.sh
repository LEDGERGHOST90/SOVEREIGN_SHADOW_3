#!/bin/bash
#
# SOVEREIGN SHADOW II - Daily Command Center
# One command to rule them all
#
# Usage: ./sovereign.sh
#

cd /Volumes/LegacySafe/SOVEREIGN_SHADOW_3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏴 SOVEREIGN SHADOW II - COMMAND CENTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Run brain and record check-in (silent)
python3 sovereign_brain.py --auto > /dev/null 2>&1
python3 sovereign_brain.py --checkin > /dev/null 2>&1

# Section 0: Brain Status (Pending Actions)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 BRAIN STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "brain_state.json" ]; then
    python3 -c "
import json
with open('brain_state.json') as f:
    state = json.load(f)

# Pending actions
pending = [a for a in state.get('pending_actions', []) if a.get('status') == 'pending']
if pending:
    print('⚡ PENDING ACTIONS:')
    for a in pending[:3]:  # Show top 3
        print(f\"   [{a['id']}] {a['type']}: {a['asset']} - {a['reason'][:40]}...\")
    if len(pending) > 3:
        print(f'   ... and {len(pending)-3} more')
    print('')
    print('   To approve: python3 sovereign_brain.py --approve N')
    print('   To see all: python3 sovereign_brain.py --list')
else:
    print('✅ No pending actions')

print('')

# Alerts
alerts = [a for a in state.get('alerts', []) if not a.get('acknowledged')]
critical = [a for a in alerts if a.get('level') in ['CRITICAL', 'EMERGENCY']]
if critical:
    print('🚨 CRITICAL ALERTS:')
    for a in critical:
        print(f\"   {a['message']}\")
elif alerts:
    print(f'📢 {len(alerts)} unread alerts (python3 sovereign_brain.py --list)')
else:
    print('✅ No alerts')
" 2>/dev/null || echo "Brain state not available"
else
    echo "Brain not initialized. Run: python3 sovereign_brain.py --auto"
fi
echo ""

# Section 1: Daily Report
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DAILY REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "daily_reports/LATEST.txt" ]; then
    cat daily_reports/LATEST.txt
else
    echo "⚠️  No daily report found. Running autopilot..."
    python3 DAILY_AUTOPILOT.py 2>/dev/null || echo "❌ Autopilot failed"
fi
echo ""

# Section 2: Psychology State
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 PSYCHOLOGY STATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "logs/psychology/loss_streak.json" ]; then
    LOSSES=$(cat logs/psychology/loss_streak.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('losses', 0))" 2>/dev/null || echo "0")
    LOSS_DATE=$(cat logs/psychology/loss_streak.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('date', 'unknown'))" 2>/dev/null || echo "unknown")

    if [ "$LOSSES" = "0" ]; then
        echo "✅ Clean slate - 0 losses today"
        echo "   Full 2% risk allowed"
    elif [ "$LOSSES" = "1" ]; then
        echo "⚠️  1 loss recorded ($LOSS_DATE)"
        echo "   Risk reduced to 1.5%"
    elif [ "$LOSSES" = "2" ]; then
        echo "⚠️  2 losses recorded ($LOSS_DATE)"
        echo "   Risk reduced to 1%"
    else
        echo "🛑 3+ LOSSES - TRADING LOCKED"
        echo "   No trades allowed today"
    fi
else
    echo "✅ No loss history found - clean slate"
fi
echo ""

# Section 3: AAVE Health Reminder
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏦 AAVE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  Check Ledger Live or debank.com for health factor"
echo ""
echo "   Health > 3.0  → ✅ Safe"
echo "   Health 2-3    → ⚠️  Watch closely"
echo "   Health < 2    → 🚨 REPAY DEBT NOW"
echo ""
echo "   Current debt: ~\$660"
echo ""

# Section 4: Session State
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💼 PORTFOLIO ALLOCATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LATEST_STATE=$(ls -t SESSION_STATE_*.json 2>/dev/null | head -1)
if [ -n "$LATEST_STATE" ]; then
    echo "From: $LATEST_STATE"
    echo ""
    python3 -c "
import json
with open('$LATEST_STATE') as f:
    d = json.load(f)
    holdings = d.get('holdings_ledger', {})
    print('Asset          | Allocation | Target | Status')
    print('---------------|------------|--------|-------')
    targets = {'bitcoin': 40, 'aave_wsteth': 30, 'xrp': 10, 'solana': 20}
    for asset, data in holdings.items():
        if isinstance(data, dict) and 'allocation' in data:
            alloc = data['allocation']
            target = targets.get(asset, '-')
            if isinstance(target, int):
                if alloc > target + 5:
                    status = 'OVER'
                elif alloc < target - 5:
                    status = 'UNDER'
                else:
                    status = 'OK'
            else:
                status = '-'
            print(f'{asset:14} | {alloc:>9.1f}% | {str(target):>6} | {status}')
" 2>/dev/null || echo "Could not parse session state"
else
    echo "No session state found"
fi
echo ""

# Section 5: Decision
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 TODAY'S DIRECTIVE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Determine if it's a rebalance month
MONTH=$(date +%m)
if [ "$MONTH" = "01" ] || [ "$MONTH" = "04" ] || [ "$MONTH" = "07" ] || [ "$MONTH" = "10" ]; then
    DAY=$(date +%d)
    if [ "$DAY" -le "07" ]; then
        echo "📅 QUARTERLY REBALANCE WINDOW"
        echo "   Consider rebalancing to target allocation"
        echo ""
    fi
fi

if [ "$LOSSES" -ge "3" ]; then
    echo "🛑 STOP. NO TRADING TODAY."
    echo "   3-strike rule in effect."
    echo "   Review your losses. Come back tomorrow."
else
    echo "✅ No action required."
    echo ""
    echo "   Unless:"
    echo "   • AAVE health < 2.0 → Repay debt"
    echo "   • Asset up 50%+ → Trim position"
    echo "   • It's quarterly rebalance time"
    echo ""
    echo "   Otherwise: CLOSE THIS TERMINAL"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Need the full playbook? cat PLAYBOOK.md"
echo "🔍 Want to validate a trade? python3 agents/shade_agent.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
