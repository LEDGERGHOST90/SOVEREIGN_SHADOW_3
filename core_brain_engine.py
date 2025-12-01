#!/usr/bin/env python3
"""
SOVEREIGN BRAIN - Central Automation Layer
Connects all three tiers of your trading automation

Usage:
    python3 sovereign_brain.py --auto      # Run automation cycle
    python3 sovereign_brain.py --list      # Show pending actions & alerts
    python3 sovereign_brain.py --approve N # Approve action #N
    python3 sovereign_brain.py --reject N  # Reject action #N
    python3 sovereign_brain.py --status    # Quick status
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Load environment
from dotenv import load_dotenv
load_dotenv('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/.env')

import ccxt

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3')
STATE_FILE = BASE_DIR / 'brain_state.json'
PSYCHOLOGY_FILE = BASE_DIR / 'logs' / 'psychology' / 'loss_streak.json'
JOURNAL_FILE = BASE_DIR / 'logs' / 'trading' / 'brain_journal.json'

# Your target allocation
TARGET_ALLOCATION = {
    'BTC': 40,
    'ETH': 30,
    'SOL': 20,
    'XRP': 10
}

# Thresholds
TRIM_THRESHOLD = 0.50      # 50% gain triggers trim suggestion
REBALANCE_THRESHOLD = 0.10 # 10% off target triggers rebalance suggestion
AAVE_WARNING = 2.5
AAVE_CRITICAL = 2.0
AAVE_EMERGENCY = 1.5

# Action expiration
ACTION_EXPIRE_HOURS = 48
ACTION_REMINDER_COUNT = 3

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_cost_basis() -> Dict[str, float]:
    """Load cost basis from latest SESSION_STATE file"""
    try:
        # Find latest session state
        session_files = sorted(BASE_DIR.glob('SESSION_STATE_*.json'), reverse=True)
        if not session_files:
            return {}

        with open(session_files[0]) as f:
            session = json.load(f)

        cost_basis = {}
        holdings = session.get('holdings_ledger', {})

        # Extract avg_cost where available
        for asset, data in holdings.items():
            if isinstance(data, dict) and 'avg_cost' in data:
                # Map asset names to standard symbols
                symbol_map = {'xrp': 'XRP', 'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL'}
                symbol = symbol_map.get(asset.lower(), asset.upper())
                cost_basis[symbol] = data['avg_cost']

        return cost_basis
    except Exception as e:
        print(f"[!] Error loading cost basis: {e}")
        return {}

def load_portfolio_from_session() -> Dict:
    """Load full portfolio data from SESSION_STATE"""
    try:
        session_files = sorted(BASE_DIR.glob('SESSION_STATE_*.json'), reverse=True)
        if not session_files:
            return {}

        with open(session_files[0]) as f:
            session = json.load(f)

        return {
            'total_value': session.get('portfolio_summary', {}).get('total_value', 0),
            'net_worth': session.get('portfolio_summary', {}).get('net_worth', 0),
            'holdings': session.get('holdings_ledger', {}),
            'aave': session.get('aave_position', {}),
            'source_file': str(session_files[0].name)
        }
    except Exception as e:
        print(f"[!] Error loading portfolio: {e}")
        return {}

def get_aave_health() -> Dict:
    """Get AAVE health factor using existing monitor"""
    try:
        # Import the existing AAVE monitor
        import sys
        sys.path.insert(0, str(BASE_DIR / 'core' / 'portfolio'))
        from aave_monitor import AAVEMonitor

        monitor = AAVEMonitor()
        summary = monitor.get_position_summary()

        return {
            'health_factor': summary.get('metrics', {}).get('health_factor', 0),
            'collateral_usd': summary.get('position', {}).get('total_collateral_usd', 0),
            'debt_usd': summary.get('position', {}).get('total_debt_usd', 0),
            'net_value_usd': summary.get('position', {}).get('net_value_usd', 0),
            'risk_level': summary.get('risk', {}).get('risk_level', 'UNKNOWN'),
            'risk_status': summary.get('risk', {}).get('status', ''),
            'timestamp': summary.get('timestamp', '')
        }
    except Exception as e:
        print(f"[!] AAVE monitor error: {e}")
        return {'error': str(e)}

def write_journal_entry(entry: Dict):
    """Write entry to brain journal"""
    try:
        JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Load existing journal
        if JOURNAL_FILE.exists():
            with open(JOURNAL_FILE) as f:
                journal = json.load(f)
        else:
            journal = {'entries': []}

        # Add timestamp
        entry['timestamp'] = datetime.now().isoformat()
        journal['entries'].append(entry)

        # Keep last 500 entries
        journal['entries'] = journal['entries'][-500:]

        with open(JOURNAL_FILE, 'w') as f:
            json.dump(journal, f, indent=2)

    except Exception as e:
        print(f"[!] Journal write error: {e}")

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def load_state() -> Dict:
    """Load brain state from file"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return create_initial_state()

def save_state(state: Dict):
    """Save brain state to file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, default=str)

def create_initial_state() -> Dict:
    """Create initial state structure"""
    return {
        "last_run": None,
        "last_human_checkin": None,
        "balances": {
            "coinbase": {},
            "binance_us": {},
            "total_usd": 0
        },
        "prices": {},
        "portfolio": {
            "total_value": 0,
            "allocation": {}
        },
        "pending_actions": [],
        "alerts": [],
        "history": {
            "snapshots": []
        },
        "psychology": {
            "losses_today": 0,
            "last_loss_date": None,
            "trading_allowed": True
        }
    }

# =============================================================================
# TIER 1: AUTOMATED TASKS
# =============================================================================

def fetch_prices() -> Dict[str, float]:
    """Fetch current prices"""
    try:
        cb = ccxt.coinbase()
        symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
        prices = {}
        for symbol in symbols:
            try:
                ticker = cb.fetch_ticker(symbol)
                prices[symbol.split('/')[0]] = ticker['last']
            except:
                continue
        return prices
    except Exception as e:
        print(f"[!] Price fetch error: {e}")
        return {}

def fetch_coinbase_balance() -> Dict[str, float]:
    """Fetch Coinbase balances"""
    try:
        cb = ccxt.coinbase({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
        })
        balance = cb.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v and v > 0}
    except Exception as e:
        print(f"[!] Coinbase error: {e}")
        return {}

def fetch_binance_us_balance() -> Dict[str, float]:
    """Fetch Binance US balances"""
    try:
        binance = ccxt.binanceus({
            'apiKey': os.getenv('BINANCE_US_API_KEY'),
            'secret': os.getenv('BINANCE_US_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {'warnOnFetchOpenOrdersWithoutSymbol': False}
        })
        balance = binance.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v and v > 0}
    except Exception as e:
        print(f"[!] Binance US error: {e}")
        return {}

def calculate_portfolio_value(balances: Dict, prices: Dict) -> float:
    """Calculate total portfolio value in USD"""
    total = 0

    # Coinbase
    for asset, amount in balances.get('coinbase', {}).items():
        if asset in prices:
            total += amount * prices[asset]
        elif asset in ['USD', 'USDC', 'USDT']:
            total += amount

    # Binance US
    for asset, amount in balances.get('binance_us', {}).items():
        if asset in prices:
            total += amount * prices[asset]
        elif asset in ['USD', 'USDC', 'USDT']:
            total += amount

    return total

def run_tier1(state: Dict) -> Dict:
    """Execute all Tier 1 automated tasks"""
    print("[TIER 1] Running automated tasks...")

    # Fetch prices
    prices = fetch_prices()
    if prices:
        state['prices'] = prices
        print(f"  Prices: BTC=${prices.get('BTC', 0):,.0f} ETH=${prices.get('ETH', 0):,.0f}")

    # Fetch balances
    cb_balance = fetch_coinbase_balance()
    bn_balance = fetch_binance_us_balance()

    state['balances']['coinbase'] = cb_balance
    state['balances']['binance_us'] = bn_balance

    # Calculate total
    total = calculate_portfolio_value(state['balances'], prices)
    state['balances']['total_usd'] = total
    print(f"  Exchange Total: ${total:,.2f}")

    # Load portfolio from SESSION_STATE (includes Ledger)
    portfolio = load_portfolio_from_session()
    if portfolio:
        state['portfolio']['total_value'] = portfolio.get('total_value', 0)
        state['portfolio']['net_worth'] = portfolio.get('net_worth', 0)
        state['portfolio']['source'] = portfolio.get('source_file', '')

        # Calculate allocation from holdings
        holdings = portfolio.get('holdings', {})
        total_val = portfolio.get('total_value', 1)
        for asset, data in holdings.items():
            if isinstance(data, dict) and 'allocation' in data:
                symbol_map = {'xrp': 'XRP', 'bitcoin': 'BTC', 'aave_wsteth': 'ETH', 'solana': 'SOL'}
                symbol = symbol_map.get(asset.lower())
                if symbol:
                    target = TARGET_ALLOCATION.get(symbol, 0)
                    current = data['allocation']
                    state['portfolio']['allocation'][symbol] = {
                        'percent': current,
                        'target': target,
                        'status': 'OVER' if current > target + 5 else ('UNDER' if current < target - 5 else 'OK')
                    }
        print(f"  Portfolio: ${portfolio.get('net_worth', 0):,.0f} net worth")

    # Fetch AAVE health (live from blockchain)
    print("  Checking AAVE health...")
    aave = get_aave_health()
    if 'error' not in aave:
        state['aave'] = aave
        hf = aave.get('health_factor', 0)
        print(f"  AAVE Health: {hf:.2f} ({aave.get('risk_status', '')})")
    else:
        print(f"  AAVE: Error - {aave.get('error', 'unknown')[:50]}")

    # Load cost basis
    cost_basis = load_cost_basis()
    if cost_basis:
        state['cost_basis'] = cost_basis
        print(f"  Cost basis loaded: {list(cost_basis.keys())}")

    # Update timestamp
    state['last_run'] = datetime.now().isoformat()

    # Take snapshot every 4 hours
    last_snapshot = state['history']['snapshots'][-1] if state['history']['snapshots'] else None
    if not last_snapshot or (datetime.now() - datetime.fromisoformat(last_snapshot.get('timestamp', '2000-01-01'))).seconds > 14400:
        state['history']['snapshots'].append({
            'timestamp': datetime.now().isoformat(),
            'total': total,
            'prices': prices.copy(),
            'aave_health': aave.get('health_factor', 0) if 'error' not in aave else None
        })
        # Keep only last 30 days
        state['history']['snapshots'] = state['history']['snapshots'][-720:]
        print("  Snapshot saved")

    # Sync psychology state
    if PSYCHOLOGY_FILE.exists():
        with open(PSYCHOLOGY_FILE) as f:
            psych = json.load(f)
            state['psychology']['losses_today'] = psych.get('losses', 0)
            state['psychology']['last_loss_date'] = psych.get('date')
            state['psychology']['trading_allowed'] = psych.get('losses', 0) < 3

    # Check for expired actions
    state = check_action_expiration(state)

    return state


def check_action_expiration(state: Dict) -> Dict:
    """Check pending actions for expiration and send reminders"""
    now = datetime.now()

    for action in state.get('pending_actions', []):
        if action.get('status') != 'pending':
            continue

        created = datetime.fromisoformat(action.get('created', now.isoformat()))
        age_hours = (now - created).total_seconds() / 3600
        reminders_sent = action.get('reminders_sent', 0)

        # Check if action should expire
        if age_hours >= ACTION_EXPIRE_HOURS:
            action['status'] = 'expired'
            action['expired_at'] = now.isoformat()

            # Log to journal with outcome analysis
            prices = state.get('prices', {})
            asset = action.get('asset', '')
            entry_price = action.get('price_at_creation', prices.get(asset, 0))
            current_price = prices.get(asset, 0)

            if entry_price and current_price:
                change = ((current_price - entry_price) / entry_price) * 100
                outcome = 'GAIN' if change > 0 else 'LOSS'
            else:
                change = 0
                outcome = 'UNKNOWN'

            write_journal_entry({
                'type': 'ACTION_EXPIRED',
                'action': action,
                'reason': f"No response after {ACTION_EXPIRE_HOURS}h and {ACTION_REMINDER_COUNT} reminders",
                'outcome': outcome,
                'price_change_percent': round(change, 2),
                'entry_price': entry_price,
                'current_price': current_price,
                'lesson': f"Missed {action['type']} opportunity on {asset}. Would have been a {outcome}."
            })
            print(f"  EXPIRED: [{action['id']}] {action['type']} {asset} - {outcome} {change:+.1f}%")

        # Check if we should send a reminder
        elif reminders_sent < ACTION_REMINDER_COUNT:
            reminder_interval = ACTION_EXPIRE_HOURS / (ACTION_REMINDER_COUNT + 1)
            next_reminder_at = reminder_interval * (reminders_sent + 1)

            if age_hours >= next_reminder_at:
                action['reminders_sent'] = reminders_sent + 1
                action['last_reminder'] = now.isoformat()

                # Add reminder alert
                state['alerts'].append({
                    'timestamp': now.isoformat(),
                    'level': 'REMINDER',
                    'message': f"Action #{action['id']} ({action['type']} {action['asset']}) needs your attention! ({action['reminders_sent']}/{ACTION_REMINDER_COUNT})",
                    'acknowledged': False
                })
                print(f"  REMINDER {action['reminders_sent']}/{ACTION_REMINDER_COUNT}: Action #{action['id']}")

    return state

# =============================================================================
# TIER 2: OPPORTUNITY DETECTION
# =============================================================================

def check_trim_opportunities(state: Dict) -> List[Dict]:
    """Check if any assets should be trimmed (up 50%+)"""
    opportunities = []
    prices = state.get('prices', {})
    cost_basis = state.get('cost_basis', {})

    for asset, cost in cost_basis.items():
        current_price = prices.get(asset, 0)
        if current_price > 0 and cost > 0:
            gain = (current_price - cost) / cost
            if gain >= TRIM_THRESHOLD:
                opportunities.append({
                    'type': 'TRIM',
                    'asset': asset,
                    'reason': f"Up {gain*100:.0f}% from cost (${cost:.2f} -> ${current_price:.2f})",
                    'suggested_action': f"Sell 25% of {asset} position",
                    'priority': 'MEDIUM',
                    'price_at_creation': current_price
                })

    return opportunities

def check_rebalance_opportunities(state: Dict) -> List[Dict]:
    """Check if portfolio needs rebalancing"""
    opportunities = []
    allocation = state.get('portfolio', {}).get('allocation', {})

    for asset, target in TARGET_ALLOCATION.items():
        current = allocation.get(asset, {}).get('percent', 0)
        diff = current - target

        if abs(diff) > REBALANCE_THRESHOLD * 100:
            if diff > 0:
                action_type = 'SELL'
                reason = f"Overweight by {diff:.0f}% ({current:.0f}% vs {target}% target)"
            else:
                action_type = 'BUY'
                reason = f"Underweight by {abs(diff):.0f}% ({current:.0f}% vs {target}% target)"

            opportunities.append({
                'type': 'REBALANCE',
                'asset': asset,
                'reason': reason,
                'suggested_action': f"{action_type} {asset} to reach {target}% allocation",
                'priority': 'LOW'
            })

    return opportunities

def check_quarterly_rebalance() -> Optional[Dict]:
    """Check if it's quarterly rebalance window"""
    now = datetime.now()
    if now.month in [1, 4, 7, 10] and now.day <= 7:
        return {
            'type': 'QUARTERLY',
            'asset': 'ALL',
            'reason': f"Quarterly rebalance window (Q{(now.month-1)//3 + 1})",
            'suggested_action': "Review full portfolio allocation",
            'priority': 'HIGH'
        }
    return None

def run_tier2(state: Dict) -> Dict:
    """Execute all Tier 2 opportunity detection"""
    print("[TIER 2] Checking for opportunities...")

    new_opportunities = []

    # Check trim opportunities
    trims = check_trim_opportunities(state)
    new_opportunities.extend(trims)

    # Check rebalance opportunities
    rebalances = check_rebalance_opportunities(state)
    new_opportunities.extend(rebalances)

    # Check quarterly
    quarterly = check_quarterly_rebalance()
    if quarterly:
        new_opportunities.append(quarterly)

    # Add new opportunities (avoid duplicates)
    existing_keys = {(a['type'], a['asset']) for a in state['pending_actions']}
    next_id = max([a.get('id', 0) for a in state['pending_actions']], default=0) + 1

    for opp in new_opportunities:
        key = (opp['type'], opp['asset'])
        if key not in existing_keys:
            opp['id'] = next_id
            opp['created'] = datetime.now().isoformat()
            opp['status'] = 'pending'
            state['pending_actions'].append(opp)
            print(f"  NEW: [{opp['type']}] {opp['asset']} - {opp['reason']}")
            next_id += 1

    if not new_opportunities:
        print("  No new opportunities detected")

    return state

# =============================================================================
# TIER 3: MONITORING & ALERTS
# =============================================================================

def check_price_alerts(state: Dict) -> List[Dict]:
    """Check for significant price movements"""
    alerts = []
    prices = state.get('prices', {})
    snapshots = state.get('history', {}).get('snapshots', [])

    # Get price from 24h ago
    if len(snapshots) >= 96:  # 96 * 15min = 24h
        old_prices = snapshots[-96].get('prices', {})

        for asset in ['BTC', 'ETH', 'SOL', 'XRP']:
            old = old_prices.get(asset, 0)
            new = prices.get(asset, 0)
            if old > 0 and new > 0:
                change = (new - old) / old
                if change <= -0.10:
                    alerts.append({
                        'level': 'WARNING',
                        'message': f"{asset} down {abs(change)*100:.1f}% in 24h (${old:,.0f} -> ${new:,.0f})"
                    })
                elif change >= 0.15:
                    alerts.append({
                        'level': 'INFO',
                        'message': f"{asset} up {change*100:.1f}% in 24h"
                    })

    return alerts

def check_inactivity(state: Dict) -> Optional[Dict]:
    """Check if human hasn't checked in"""
    last_checkin = state.get('last_human_checkin')
    if last_checkin:
        last = datetime.fromisoformat(last_checkin)
        hours_since = (datetime.now() - last).total_seconds() / 3600
        if hours_since > 48:
            return {
                'level': 'REMINDER',
                'message': f"No check-in for {hours_since:.0f} hours. Run ./sovereign.sh"
            }
    return None

def check_market_crash(state: Dict) -> Optional[Dict]:
    """Check for market crash"""
    prices = state.get('prices', {})
    snapshots = state.get('history', {}).get('snapshots', [])

    if len(snapshots) >= 4:  # 1 hour of data
        old_btc = snapshots[-4].get('prices', {}).get('BTC', 0)
        new_btc = prices.get('BTC', 0)
        if old_btc > 0 and new_btc > 0:
            change = (new_btc - old_btc) / old_btc
            if change <= -0.05:
                return {
                    'level': 'CRITICAL',
                    'message': f"BTC down {abs(change)*100:.1f}% in 1hr! Check positions."
                }
    return None

def check_aave_health_alert(state: Dict) -> Optional[Dict]:
    """Check AAVE health factor and generate alerts"""
    aave = state.get('aave', {})
    if 'error' in aave or not aave:
        return None

    health_factor = aave.get('health_factor', 999)

    if health_factor < AAVE_EMERGENCY:
        return {
            'level': 'EMERGENCY',
            'message': f"AAVE HEALTH {health_factor:.2f} - LIQUIDATION IMMINENT! Repay debt NOW!"
        }
    elif health_factor < AAVE_CRITICAL:
        return {
            'level': 'CRITICAL',
            'message': f"AAVE health {health_factor:.2f} - Below safe threshold. Consider repaying debt."
        }
    elif health_factor < AAVE_WARNING:
        return {
            'level': 'WARNING',
            'message': f"AAVE health {health_factor:.2f} - Watch closely. Debt: ${aave.get('debt_usd', 0):,.0f}"
        }

    return None

def run_tier3(state: Dict) -> Dict:
    """Execute all Tier 3 monitoring"""
    print("[TIER 3] Running monitors...")

    new_alerts = []

    # AAVE health check (PRIORITY - live blockchain data)
    aave_alert = check_aave_health_alert(state)
    if aave_alert:
        new_alerts.append(aave_alert)

    # Price alerts
    price_alerts = check_price_alerts(state)
    new_alerts.extend(price_alerts)

    # Inactivity check
    inactivity = check_inactivity(state)
    if inactivity:
        new_alerts.append(inactivity)

    # Market crash check
    crash = check_market_crash(state)
    if crash:
        new_alerts.append(crash)

    # Add timestamps and store
    for alert in new_alerts:
        alert['timestamp'] = datetime.now().isoformat()
        alert['acknowledged'] = False
        state['alerts'].append(alert)
        level_icon = {'INFO': 'i', 'WARNING': '!', 'CRITICAL': '!!', 'EMERGENCY': '!!!', 'REMINDER': '?'}
        print(f"  [{level_icon.get(alert['level'], '?')}] {alert['message']}")

    # Keep only last 100 alerts
    state['alerts'] = state['alerts'][-100:]

    if not new_alerts:
        print("  No new alerts")

    return state

# =============================================================================
# USER COMMANDS
# =============================================================================

def cmd_auto():
    """Run full automation cycle"""
    print("=" * 50)
    print("SOVEREIGN BRAIN - Automation Cycle")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    state = load_state()
    state = run_tier1(state)
    state = run_tier2(state)
    state = run_tier3(state)
    save_state(state)

    print("=" * 50)
    print("Cycle complete. State saved.")

def cmd_list():
    """List pending actions and alerts"""
    state = load_state()

    print("\n" + "=" * 50)
    print("PENDING ACTIONS")
    print("=" * 50)

    pending = [a for a in state.get('pending_actions', []) if a.get('status') == 'pending']
    if pending:
        for action in pending:
            print(f"[{action['id']}] {action['type']}: {action['asset']}")
            print(f"    Reason: {action['reason']}")
            print(f"    Action: {action['suggested_action']}")
            print()
    else:
        print("No pending actions.")

    print("=" * 50)
    print("RECENT ALERTS")
    print("=" * 50)

    alerts = [a for a in state.get('alerts', [])[-10:] if not a.get('acknowledged')]
    if alerts:
        for alert in alerts:
            level_icon = {'INFO': 'i', 'WARNING': '!', 'CRITICAL': '!!', 'EMERGENCY': '!!!', 'REMINDER': '?'}
            print(f"[{level_icon.get(alert['level'], '?')}] {alert['level']}: {alert['message']}")
    else:
        print("No unacknowledged alerts.")

def cmd_approve(action_id: int):
    """Approve a pending action"""
    state = load_state()

    for action in state['pending_actions']:
        if action.get('id') == action_id and action.get('status') == 'pending':
            action['status'] = 'approved'
            action['approved_at'] = datetime.now().isoformat()
            save_state(state)
            print(f"Approved action #{action_id}: {action['type']} {action['asset']}")
            print(f"Next step: Execute the trade manually or via connector")
            return

    print(f"Action #{action_id} not found or not pending")

def cmd_reject(action_id: int):
    """Reject a pending action"""
    state = load_state()

    for action in state['pending_actions']:
        if action.get('id') == action_id and action.get('status') == 'pending':
            action['status'] = 'rejected'
            action['rejected_at'] = datetime.now().isoformat()
            save_state(state)
            print(f"Rejected action #{action_id}")
            return

    print(f"Action #{action_id} not found or not pending")

def cmd_status():
    """Quick status check"""
    state = load_state()

    print("\n" + "=" * 50)
    print("SOVEREIGN BRAIN STATUS")
    print("=" * 50)

    last_run = state.get('last_run', 'Never')
    print(f"Last run: {last_run}")

    prices = state.get('prices', {})
    print(f"BTC: ${prices.get('BTC', 0):,.0f} | ETH: ${prices.get('ETH', 0):,.0f}")

    total = state.get('balances', {}).get('total_usd', 0)
    print(f"Exchange total: ${total:,.2f}")

    pending = len([a for a in state.get('pending_actions', []) if a.get('status') == 'pending'])
    alerts = len([a for a in state.get('alerts', []) if not a.get('acknowledged')])
    print(f"Pending actions: {pending}")
    print(f"Unread alerts: {alerts}")

    psych = state.get('psychology', {})
    if psych.get('trading_allowed'):
        print(f"Trading: ALLOWED ({psych.get('losses_today', 0)} losses today)")
    else:
        print("Trading: LOCKED (3+ losses)")

def cmd_checkin():
    """Record human check-in"""
    state = load_state()
    state['last_human_checkin'] = datetime.now().isoformat()
    save_state(state)
    print(f"Check-in recorded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Sovereign Brain - Central Automation')
    parser.add_argument('--auto', action='store_true', help='Run automation cycle')
    parser.add_argument('--list', action='store_true', help='List pending actions & alerts')
    parser.add_argument('--approve', type=int, metavar='N', help='Approve action #N')
    parser.add_argument('--reject', type=int, metavar='N', help='Reject action #N')
    parser.add_argument('--status', action='store_true', help='Quick status')
    parser.add_argument('--checkin', action='store_true', help='Record human check-in')

    args = parser.parse_args()

    if args.auto:
        cmd_auto()
    elif args.list:
        cmd_list()
    elif args.approve:
        cmd_approve(args.approve)
    elif args.reject:
        cmd_reject(args.reject)
    elif args.status:
        cmd_status()
    elif args.checkin:
        cmd_checkin()
    else:
        # Default: show status
        cmd_status()

if __name__ == '__main__':
    main()
