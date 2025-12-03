#!/usr/bin/env python3
"""
AUTOMATED PAPER TRADER v2 - DEBT DESTROYER
Ladder entries, OCO exits, trailing stops
"""

import json
import os
import time
import requests
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TRADES_FILE = BASE_DIR / "data" / "paper_trades.json"
JOURNAL_FILE = BASE_DIR / "logs" / "trading" / "trade_journal.json"
SOUNDS_DIR = BASE_DIR / "sounds"
NTFY_TOPIC = "sovereignshadow_dc4d2fa1"

# SOUND EFFECTS
SOUNDS = {
    "entry": SOUNDS_DIR / "vegas_trap.mp3",
    "win": SOUNDS_DIR / "jackpot.mp3",
    "loss": SOUNDS_DIR / "radar_lock.mp3",
    "alert": SOUNDS_DIR / "casino_alert.mp3",
    "scan": SOUNDS_DIR / "808_synth.mp3",
    "trailing": SOUNDS_DIR / "target_acquired.mp3",
}

# TRADING RULES
RULES = {
    "total_capital": 50,           # $50 total per trade
    "ladder_levels": 3,            # 3 entry levels
    "ladder_spacing_pct": 1.5,     # 1.5% between ladder levels
    "stop_loss_pct": 5,            # 5% hard stop from avg entry
    "take_profit_pct": 8,          # 8% take profit target
    "trailing_stop_pct": 3,        # 3% trailing stop (activates at 3% profit)
    "trailing_activate_pct": 3,    # Activate trailing at 3% profit
    "max_open_trades": 2,          # Max concurrent positions
    "scan_interval": 120,          # 2 min between scans
}

# COINBASE + BINANCE US tradeable assets
WATCHLIST = [
    # Core holdings
    'BTC', 'ETH', 'SOL', 'XRP',
    # Coinbase
    'AVAX', 'LINK', 'ADA', 'DOT', 'NEAR', 'INJ', 'ARB', 'OP', 'SUI', 'APT', 'RENDER', 'FET', 'AAVE', 'UNI', 'LTC',
    # Binance US additions
    'ATOM', 'QNT', 'HBAR', 'ONDO', 'HYPE', 'VIRTUAL', 'ENS', 'BONK', 'BAND', 'FLUX', 'QTUM',
]


def play_sound(sound_type: str):
    """Play notification sound"""
    sound_file = SOUNDS.get(sound_type)
    if sound_file and sound_file.exists():
        subprocess.Popen(['afplay', str(sound_file)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def push_alert(msg: str, priority: str = "default"):
    """Send push notification"""
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode('utf-8'),
                     headers={"Priority": priority}, timeout=5)
    except:
        pass


def load_trades() -> dict:
    """Load paper trades from file"""
    if TRADES_FILE.exists():
        return json.loads(TRADES_FILE.read_text())
    return {
        "open": [],
        "closed": [],
        "pending_ladders": [],  # Unfilled ladder orders
        "stats": {"wins": 0, "losses": 0, "total_pnl": 0}
    }


def save_trades(trades: dict):
    """Save paper trades"""
    TRADES_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRADES_FILE.write_text(json.dumps(trades, indent=2))


def log_to_journal(trade: dict, exit_price: float, pnl_value: float, pnl_pct: float, reason: str):
    """Log closed trade to main trade journal"""
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing journal
    journal = []
    if JOURNAL_FILE.exists():
        try:
            journal = json.loads(JOURNAL_FILE.read_text())
        except:
            journal = []

    # Create journal entry matching existing format
    entry = {
        "trade_id": f"PAPER_{trade['id']}",
        "timestamp": trade['entry_time'],
        "symbol": f"{trade['symbol']}/USD",
        "trade_type": "long",
        "entry_price": trade['avg_entry'],
        "stop_loss": trade['hard_stop'],
        "take_profit": trade['take_profit'],
        "position_size": trade['total_size'],
        "position_value": trade['total_value'],
        "risk_amount": trade['total_value'] * 0.05,
        "risk_percent": 0.05,
        "validation_passed": True,
        "shade_approved": True,
        "score": trade.get('score', 0),
        "reasons": trade.get('reasons', []),
        "status": reason.lower(),
        "executed_at": trade['entry_time'],
        "actual_entry": trade['avg_entry'],
        "actual_exit": exit_price,
        "exit_timestamp": datetime.now().isoformat(),
        "profitable": pnl_value > 0,
        "profit_loss": round(pnl_value, 2),
        "profit_loss_percent": round(pnl_pct / 100, 4),
        "ladder_fills": len([o for o in trade['ladder_orders'] if o['filled']]),
        "trailing_activated": trade['trailing_stop'] is not None,
        "tags": ["paper_trade", "automated", "winner" if pnl_value > 0 else "loser"],
        "notes": f"Auto paper trade - {reason}"
    }

    journal.append(entry)
    JOURNAL_FILE.write_text(json.dumps(journal, indent=2))


def get_prices() -> dict:
    """Get current prices with 24h and 7d changes"""
    try:
        # Coinbase + Binance US assets
        ids = "bitcoin,ethereum,solana,ripple,avalanche-2,chainlink,cardano,polkadot,near,injective-protocol,arbitrum,optimism,sui,aptos,render-token,fetch-ai,aave,uniswap,litecoin,cosmos,quant-network,hedera-hashgraph,ondo-finance,hyperliquid,virtual-protocol,ethereum-name-service,bonk,band-protocol,flux,qtum"
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, timeout=10).json()

        mapping = {
            # Core + Coinbase
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL', 'ripple': 'XRP',
            'avalanche-2': 'AVAX', 'chainlink': 'LINK', 'cardano': 'ADA', 'polkadot': 'DOT',
            'near': 'NEAR', 'injective-protocol': 'INJ', 'arbitrum': 'ARB', 'optimism': 'OP',
            'sui': 'SUI', 'aptos': 'APT', 'render-token': 'RENDER', 'fetch-ai': 'FET',
            'aave': 'AAVE', 'uniswap': 'UNI', 'litecoin': 'LTC',
            # Binance US
            'cosmos': 'ATOM', 'quant-network': 'QNT', 'hedera-hashgraph': 'HBAR',
            'ondo-finance': 'ONDO', 'hyperliquid': 'HYPE', 'virtual-protocol': 'VIRTUAL',
            'ethereum-name-service': 'ENS', 'bonk': 'BONK', 'band-protocol': 'BAND',
            'flux': 'FLUX', 'qtum': 'QTUM',
        }

        prices = {}
        for coin_id, symbol in mapping.items():
            if coin_id in data:
                prices[symbol] = {
                    'price': data[coin_id]['usd'],
                    'change_24h': data[coin_id].get('usd_24h_change', 0) or 0
                }
        return prices
    except Exception as e:
        print(f"  Price fetch error: {e}")
        return {}


def calculate_score(symbol: str, data: dict, avg_change: float) -> tuple:
    """Self-correcting score calculation"""
    price = data['price']
    change = data['change_24h']

    score = 50
    reasons = []

    # Laggard bonus (below average = catch-up potential)
    if 0 < change < avg_change - 2:
        score += 20
        reasons.append("laggard")
    elif 0 < change < avg_change:
        score += 10
        reasons.append("below-avg")

    # Healthy momentum (not too hot)
    if 2 < change < 8:
        score += 10
        reasons.append("healthy")
    elif 0 < change < 2:
        score += 5
        reasons.append("steady")

    # Overextension penalty
    if change > 18:
        score -= 30
        reasons.append("FOMO-TRAP")
    elif change > 15:
        score -= 20
        reasons.append("overextended")
    elif change > 12:
        score -= 10
        reasons.append("hot")

    # Negative = potential bounce but risky
    if -3 < change < 0:
        score += 5
        reasons.append("dip")
    elif change < -5:
        score -= 10
        reasons.append("falling-knife")

    return score, reasons


def find_setups(prices: dict, trades: dict) -> list:
    """Find trading setups using self-correcting strategy"""
    setups = []

    changes = [p['change_24h'] for p in prices.values()]
    avg_change = sum(changes) / len(changes) if changes else 0

    # Already in positions or have pending ladders
    blocked = [t['symbol'] for t in trades['open']]
    blocked += [t['symbol'] for t in trades.get('pending_ladders', [])]

    for symbol in WATCHLIST:
        if symbol not in prices or symbol in blocked:
            continue

        data = prices[symbol]
        score, reasons = calculate_score(symbol, data, avg_change)

        if score >= 65:
            setups.append({
                'symbol': symbol,
                'price': data['price'],
                'score': score,
                'change': data['change_24h'],
                'reasons': reasons
            })

    setups.sort(key=lambda x: x['score'], reverse=True)
    return setups[:2]


def create_ladder_entry(setup: dict, trades: dict) -> bool:
    """Create laddered entry orders"""
    if len(trades['open']) + len(trades.get('pending_ladders', [])) >= RULES['max_open_trades']:
        return False

    price = setup['price']
    symbol = setup['symbol']

    # Create 3 ladder levels
    capital_per_level = RULES['total_capital'] / RULES['ladder_levels']
    ladder_orders = []

    for i in range(RULES['ladder_levels']):
        # Each level is 1.5% lower than previous
        level_price = price * (1 - (i * RULES['ladder_spacing_pct'] / 100))
        size = capital_per_level / level_price

        ladder_orders.append({
            'level': i + 1,
            'price': level_price,
            'size': size,
            'value': capital_per_level,
            'filled': i == 0,  # First level fills immediately at market
            'fill_time': datetime.now().isoformat() if i == 0 else None
        })

    # Calculate stops based on lowest ladder level
    lowest_entry = ladder_orders[-1]['price']
    hard_stop = lowest_entry * (1 - RULES['stop_loss_pct'] / 100)
    take_profit = price * (1 + RULES['take_profit_pct'] / 100)

    trade = {
        'id': f"PT{len(trades['closed']) + len(trades['open']) + 1:04d}",
        'symbol': symbol,
        'ladder_orders': ladder_orders,
        'avg_entry': price,  # Will update as ladders fill
        'total_size': ladder_orders[0]['size'],  # Start with first level
        'total_value': capital_per_level,
        'hard_stop': hard_stop,
        'take_profit': take_profit,
        'trailing_stop': None,  # Activates at profit threshold
        'trailing_high': price,
        'score': setup['score'],
        'reasons': setup['reasons'],
        'entry_time': datetime.now().isoformat(),
        'status': 'active'
    }

    trades['open'].append(trade)
    save_trades(trades)

    msg = f"""🎯 LADDER ENTRY: {symbol}
L1: ${price:.2f} ✅ FILLED
L2: ${ladder_orders[1]['price']:.2f} (pending)
L3: ${ladder_orders[2]['price']:.2f} (pending)
Stop: ${hard_stop:.2f} | TP: ${take_profit:.2f}
Score: {setup['score']}/100"""

    push_alert(msg, "high")
    play_sound("entry")
    print(f"\n{msg}\n")

    return True


def check_ladder_fills(prices: dict, trades: dict):
    """Check if any ladder orders should fill"""
    for trade in trades['open']:
        if trade['symbol'] not in prices:
            continue

        current_price = prices[trade['symbol']]['price']

        for order in trade['ladder_orders']:
            if not order['filled'] and current_price <= order['price']:
                # Fill this ladder level
                order['filled'] = True
                order['fill_time'] = datetime.now().isoformat()

                # Update average entry and total size
                filled_orders = [o for o in trade['ladder_orders'] if o['filled']]
                total_value = sum(o['value'] for o in filled_orders)
                total_size = sum(o['size'] for o in filled_orders)
                trade['avg_entry'] = total_value / total_size if total_size > 0 else current_price
                trade['total_size'] = total_size
                trade['total_value'] = total_value

                msg = f"📥 LADDER FILL: {trade['symbol']} L{order['level']} @ ${order['price']:.2f}"
                push_alert(msg, "default")
                play_sound("alert")
                print(f"  {msg}")

                save_trades(trades)


def update_trailing_stops(prices: dict, trades: dict):
    """Update trailing stops for profitable positions"""
    for trade in trades['open']:
        if trade['symbol'] not in prices:
            continue

        current_price = prices[trade['symbol']]['price']
        avg_entry = trade['avg_entry']
        pnl_pct = ((current_price - avg_entry) / avg_entry) * 100

        # Activate trailing stop at threshold
        if pnl_pct >= RULES['trailing_activate_pct']:
            # Update trailing high
            if current_price > trade['trailing_high']:
                trade['trailing_high'] = current_price

            # Set trailing stop
            new_trailing = trade['trailing_high'] * (1 - RULES['trailing_stop_pct'] / 100)

            if trade['trailing_stop'] is None or new_trailing > trade['trailing_stop']:
                old_stop = trade['trailing_stop']
                trade['trailing_stop'] = new_trailing

                if old_stop is None:
                    msg = f"🔒 TRAILING ACTIVATED: {trade['symbol']} @ ${new_trailing:.2f}"
                    push_alert(msg, "default")
                    play_sound("trailing")
                    print(f"  {msg}")

                save_trades(trades)


def check_exits(prices: dict, trades: dict) -> list:
    """Check OCO exits: hard stop, trailing stop, or take profit"""
    exits = []

    for trade in trades['open']:
        symbol = trade['symbol']
        if symbol not in prices:
            continue

        current_price = prices[symbol]['price']
        avg_entry = trade['avg_entry']
        pnl_pct = ((current_price - avg_entry) / avg_entry) * 100

        exit_reason = None

        # Check hard stop
        if current_price <= trade['hard_stop']:
            exit_reason = 'HARD_STOP'

        # Check trailing stop (if active)
        elif trade['trailing_stop'] and current_price <= trade['trailing_stop']:
            exit_reason = 'TRAILING_STOP'

        # Check take profit
        elif current_price >= trade['take_profit']:
            exit_reason = 'TAKE_PROFIT'

        if exit_reason:
            exits.append({
                'trade': trade,
                'exit_price': current_price,
                'reason': exit_reason,
                'pnl_pct': pnl_pct
            })

    return exits


def execute_exit(exit_info: dict, trades: dict):
    """Execute paper trade exit"""
    trade = exit_info['trade']
    exit_price = exit_info['exit_price']
    reason = exit_info['reason']

    pnl_value = (exit_price - trade['avg_entry']) * trade['total_size']
    pnl_pct = exit_info['pnl_pct']

    # Update stats
    if pnl_value > 0:
        trades['stats']['wins'] += 1
        emoji = "✅"
    else:
        trades['stats']['losses'] += 1
        emoji = "❌"

    trades['stats']['total_pnl'] += pnl_value

    # Record exit details
    trade['exit'] = exit_price
    trade['exit_time'] = datetime.now().isoformat()
    trade['pnl'] = pnl_value
    trade['pnl_pct'] = pnl_pct
    trade['exit_reason'] = reason
    trade['status'] = 'closed'

    # Move to closed
    trades['open'].remove(trade)
    trades['closed'].append(trade)
    save_trades(trades)

    # Log to main trade journal
    log_to_journal(trade, exit_price, pnl_value, pnl_pct, reason)

    wins = trades['stats']['wins']
    losses = trades['stats']['losses']
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0

    msg = f"""{emoji} EXIT: {trade['symbol']}
{reason} @ ${exit_price:.2f}
Entry: ${trade['avg_entry']:.2f}
P&L: ${pnl_value:+.2f} ({pnl_pct:+.1f}%)
Record: {wins}W/{losses}L ({win_rate:.0f}%)
Total P&L: ${trades['stats']['total_pnl']:+.2f}"""

    push_alert(msg, "high")
    play_sound("win" if pnl_value > 0 else "loss")
    print(f"\n{msg}\n")


def show_status(trades: dict, prices: dict):
    """Show current status"""
    now = datetime.now().strftime('%H:%M:%S')
    print(f"\n{'='*60}")
    print(f"  🥷 DEBT DESTROYER v2 - {now}")
    print(f"{'='*60}")

    # Market overview
    if prices:
        changes = [p['change_24h'] for p in prices.values()]
        avg = sum(changes) / len(changes)
        print(f"\n  Market Avg: {avg:+.1f}% | Scanning {len(WATCHLIST)} assets")

    # Open positions with live P&L
    if trades['open']:
        print(f"\n  OPEN POSITIONS:")
        for t in trades['open']:
            if t['symbol'] in prices:
                current = prices[t['symbol']]['price']
                pnl_pct = ((current - t['avg_entry']) / t['avg_entry']) * 100
                pnl_val = (current - t['avg_entry']) * t['total_size']

                # Show ladder status
                filled = len([o for o in t['ladder_orders'] if o['filled']])

                trail_info = f" | Trail: ${t['trailing_stop']:.2f}" if t['trailing_stop'] else ""

                print(f"    {t['symbol']}: ${t['avg_entry']:.2f} → ${current:.2f} ({pnl_pct:+.1f}%) ${pnl_val:+.2f}")
                print(f"         Ladders: {filled}/3 | Stop: ${t['hard_stop']:.2f} | TP: ${t['take_profit']:.2f}{trail_info}")
    else:
        print(f"\n  No open positions - scanning for setups...")

    # Stats
    w, l = trades['stats']['wins'], trades['stats']['losses']
    total = w + l
    wr = (w / total * 100) if total > 0 else 0
    pnl = trades['stats']['total_pnl']

    print(f"\n  STATS: {w}W/{l}L ({wr:.0f}%) | Total P&L: ${pnl:+.2f}")
    print(f"{'='*60}\n")


def run():
    """Main trading loop"""
    print("\n" + "="*60)
    print("  🥷 DEBT DESTROYER v2 - LADDER + TRAILING STOPS")
    print("  Started:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("  Press Ctrl+C to stop")
    print("="*60 + "\n")

    push_alert("🥷 Paper Trader v2 Started\nLadders + Trailing Stops Active", "default")
    play_sound("scan")

    trades = load_trades()

    # Initialize pending_ladders if missing
    if 'pending_ladders' not in trades:
        trades['pending_ladders'] = []
        save_trades(trades)

    scan_count = 0

    while True:
        try:
            scan_count += 1
            prices = get_prices()

            if not prices:
                print("  Waiting for price data...")
                time.sleep(30)
                continue

            # 1. Check ladder fills
            check_ladder_fills(prices, trades)

            # 2. Update trailing stops
            update_trailing_stops(prices, trades)

            # 3. Check exits (OCO: hard stop, trailing, or TP)
            exits = check_exits(prices, trades)
            for exit_info in exits:
                execute_exit(exit_info, trades)
                trades = load_trades()

            # 4. Find new setups
            if len(trades['open']) < RULES['max_open_trades']:
                setups = find_setups(prices, trades)
                for setup in setups:
                    if setup['score'] >= 65 and len(trades['open']) < RULES['max_open_trades']:
                        create_ladder_entry(setup, trades)
                        trades = load_trades()

            # 5. Show status
            show_status(trades, prices)

            # Wait for next scan
            print(f"  Scan #{scan_count} complete. Next in {RULES['scan_interval']}s...")
            time.sleep(RULES['scan_interval'])

        except KeyboardInterrupt:
            print("\n\n  Stopping paper trader...")
            push_alert("🛑 Paper Trader Stopped", "low")
            break
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run()
