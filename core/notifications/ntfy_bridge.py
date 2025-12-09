#!/usr/bin/env python3
"""
NTFY Bridge - ECO SYSTEM 4
Two-way communication with ntfy.sh

- Subscribe: Pull signals from Paper Trader v2 (Replit)
- Publish: Push ECO SYSTEM 4 signals/alerts
- Sync: Auto-add trades to BRAIN.json
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List

# Your ntfy.sh topics
NTFY_TOPICS = [
    "sovereignshadow_dc4d2f",    # ECO4 outbound
    "sovereignshadow_dc4d2fa1",  # Replit Paper Trader
]
NTFY_PRIMARY = NTFY_TOPICS[0]  # For pushing
NTFY_URL = f"https://ntfy.sh/{NTFY_PRIMARY}"

# BRAIN path
BRAIN_PATH = "/Volumes/LegacySafe/ECO_SYSTEM_4/BRAIN.json"


def push_signal(title: str, message: str, priority: str = "default", tags: List[str] = None) -> bool:
    """
    Push a signal/alert to ntfy.sh

    Priority: min, low, default, high, urgent
    Tags: emoji shortcodes like 'chart_with_upwards_trend', 'warning', 'moneybag'
    """
    try:
        headers = {
            "Title": title,
            "Priority": priority,
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        response = requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers=headers,
            timeout=10
        )

        return response.status_code == 200
    except Exception as e:
        print(f"[NTFY] Push error: {e}")
        return False


def push_trade_signal(symbol: str, action: str, price: float,
                      stop_loss: float = None, take_profit: float = None,
                      confidence: int = None, source: str = "ECO4") -> bool:
    """Push a formatted trade signal"""

    emoji = "🟢" if action.upper() == "BUY" else "🔴"

    title = f"{emoji} {action.upper()}: {symbol}"

    lines = [
        f"Entry: ${price:,.2f}" if price > 10 else f"Entry: ${price:.4f}",
    ]

    if stop_loss:
        sl_str = f"${stop_loss:,.2f}" if stop_loss > 10 else f"${stop_loss:.4f}"
        lines.append(f"Stop: {sl_str}")

    if take_profit:
        tp_str = f"${take_profit:,.2f}" if take_profit > 10 else f"${take_profit:.4f}"
        lines.append(f"TP: {tp_str}")

    if confidence:
        lines.append(f"Confidence: {confidence}%")

    lines.append(f"Source: {source}")

    message = "\n".join(lines)
    tags = ["chart_with_upwards_trend"] if action.upper() == "BUY" else ["chart_with_downwards_trend"]

    return push_signal(title, message, priority="high", tags=tags)


def push_exit(symbol: str, entry: float, exit_price: float, pnl: float, pnl_pct: float) -> bool:
    """Push trade exit notification"""

    emoji = "✅" if pnl > 0 else "❌"
    result = "WIN" if pnl > 0 else "LOSS"

    title = f"{emoji} EXIT: {symbol} ({result})"

    message = f"""Entry: ${entry:,.2f}
Exit: ${exit_price:,.2f}
P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)"""

    tags = ["moneybag"] if pnl > 0 else ["warning"]
    priority = "high" if abs(pnl) > 10 else "default"

    return push_signal(title, message, priority=priority, tags=tags)


def push_alert(message: str, priority: str = "default") -> bool:
    """Push a general alert"""
    return push_signal("ECO4 Alert", message, priority=priority, tags=["bell"])


def fetch_recent_messages(limit: int = 10, topic: str = None) -> List[Dict]:
    """
    Fetch recent messages from ntfy.sh topic(s)
    Returns list of message dicts
    """
    topics_to_check = [topic] if topic else NTFY_TOPICS
    all_messages = []

    for t in topics_to_check:
        try:
            url = f"https://ntfy.sh/{t}/json?poll=1"
            response = requests.get(url, timeout=10)

            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        msg = json.loads(line)
                        if msg.get('event') == 'message':
                            all_messages.append({
                                'id': msg.get('id'),
                                'time': datetime.fromtimestamp(msg.get('time', 0)),
                                'title': msg.get('title', ''),
                                'message': msg.get('message', ''),
                                'tags': msg.get('tags', []),
                                'priority': msg.get('priority', 3),
                                'topic': t
                            })
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"[NTFY] Fetch error for {t}: {e}")

    # Sort by time and return latest
    all_messages.sort(key=lambda x: x['time'])
    return all_messages[-limit:]


def parse_trade_from_message(msg: Dict) -> Optional[Dict]:
    """
    Parse a trade signal from ntfy message
    Returns trade dict or None

    Paper Trader v2 format (in body):
    - 📥 LADDER FILL: HBAR L2 @ $0.14
    - ✅ EXIT: AVAX +8.12% ($4.06 profit)
    - 🎯 ENTRY: BTC @ $95,000
    """
    import re

    title = msg.get('title', '')
    body = msg.get('message', '')

    # Check both title and body for signals
    text = f"{title} {body}"

    trade = {
        'timestamp': msg.get('time'),
        'raw_title': title,
        'raw_body': body
    }

    # Parse LADDER FILL signals (Paper Trader v2 format)
    if 'LADDER FILL' in text or 'FILL' in text:
        trade['action'] = 'FILL'

        # Extract symbol - word before "L1/L2/L3" or after FILL:
        match = re.search(r'FILL[:\s]+(\w+)', text)
        if match:
            trade['symbol'] = match.group(1).upper()

        # Extract price
        price_match = re.search(r'\$(\d+\.?\d*)', text)
        if price_match:
            trade['price'] = float(price_match.group(1))

    # Parse EXIT signals
    elif 'EXIT' in text:
        trade['action'] = 'EXIT'

        # Extract symbol after EXIT:
        match = re.search(r'EXIT[:\s]+(\w+)', text)
        if match:
            trade['symbol'] = match.group(1).upper()

        # Parse P&L - formats: "+8.12% ($4.06 profit)" or "P&L: $4.06"
        pnl_match = re.search(r'\$([+-]?\d+\.?\d*)\s*(?:profit|loss)?', text)
        if pnl_match:
            pnl = float(pnl_match.group(1))
            # Check if it's a loss
            if 'loss' in text.lower() or '-' in text.split('EXIT')[1][:20]:
                pnl = -abs(pnl)
            trade['pnl'] = pnl

    # Parse ENTRY/BUY signals
    elif 'ENTRY' in text or 'BUY' in text:
        trade['action'] = 'BUY'

        # Extract symbol after ENTRY: or BUY:
        match = re.search(r'(?:ENTRY|BUY)[:\s]+(\w+)', text)
        if match:
            trade['symbol'] = match.group(1).upper()

        # Extract price
        price_match = re.search(r'\$(\d+[,\d]*\.?\d*)', text)
        if price_match:
            trade['price'] = float(price_match.group(1).replace(',', ''))

    return trade if trade.get('symbol') else None


def sync_to_brain(trade: Dict) -> bool:
    """
    Sync a parsed trade to BRAIN.json
    Handles: ENTRY (new position), EXIT (close + P&L), FILL (ladder)
    """
    try:
        with open(BRAIN_PATH, 'r') as f:
            brain = json.load(f)

        action = trade.get('action')
        symbol = trade.get('symbol')
        timestamp = trade.get('timestamp')

        if not symbol:
            return False

        # Initialize replit_trades if missing
        if 'replit_trades' not in brain:
            brain['replit_trades'] = {
                'synced_from': 'Paper Trader v2 via ntfy',
                'trades': [],
                'stats': {'total': 0, 'wins': 0, 'losses': 0, 'pnl_usd': 0.0}
            }

        # ENTRY - New position opened
        if action == 'BUY':
            entry = {
                'id': f"REPLIT-{symbol}-{datetime.now().strftime('%H%M%S')}",
                'symbol': symbol,
                'action': 'BUY',
                'price': trade.get('price'),
                'timestamp': str(timestamp) if timestamp else datetime.now().isoformat(),
                'source': 'Paper Trader v2',
                'status': 'OPEN'
            }
            brain['replit_trades']['trades'].append(entry)
            brain['replit_trades']['stats']['total'] += 1
            print(f"[SYNC] Added ENTRY: {symbol}")

        # EXIT - Position closed
        elif action == 'EXIT':
            pnl = trade.get('pnl', 0)
            exit_record = {
                'id': f"REPLIT-{symbol}-EXIT-{datetime.now().strftime('%H%M%S')}",
                'symbol': symbol,
                'action': 'EXIT',
                'pnl': pnl,
                'timestamp': str(timestamp) if timestamp else datetime.now().isoformat(),
                'source': 'Paper Trader v2',
                'status': 'CLOSED'
            }
            brain['replit_trades']['trades'].append(exit_record)
            brain['replit_trades']['stats']['pnl_usd'] += pnl
            if pnl > 0:
                brain['replit_trades']['stats']['wins'] += 1
            else:
                brain['replit_trades']['stats']['losses'] += 1
            print(f"[SYNC] Added EXIT: {symbol} P&L: ${pnl:+.2f}")

        # FILL - Ladder fill
        elif action == 'FILL':
            fill = {
                'id': f"REPLIT-{symbol}-FILL-{datetime.now().strftime('%H%M%S')}",
                'symbol': symbol,
                'action': 'FILL',
                'price': trade.get('price'),
                'timestamp': str(timestamp) if timestamp else datetime.now().isoformat(),
                'source': 'Paper Trader v2'
            }
            brain['replit_trades']['trades'].append(fill)
            print(f"[SYNC] Added FILL: {symbol} @ ${trade.get('price', 0):.4f}")

        brain['last_updated'] = datetime.now().isoformat()

        with open(BRAIN_PATH, 'w') as f:
            json.dump(brain, f, indent=2)

        return True
    except Exception as e:
        print(f"[NTFY] Sync error: {e}")
        return False


def sync_all_recent(limit: int = 20) -> Dict:
    """
    Fetch recent messages and sync all trades to BRAIN
    Returns summary of what was synced
    """
    messages = fetch_recent_messages(limit)
    synced = {'entries': 0, 'exits': 0, 'fills': 0, 'errors': 0}

    for msg in messages:
        trade = parse_trade_from_message(msg)
        if trade:
            action = trade.get('action')
            if sync_to_brain(trade):
                if action == 'BUY':
                    synced['entries'] += 1
                elif action == 'EXIT':
                    synced['exits'] += 1
                elif action == 'FILL':
                    synced['fills'] += 1
            else:
                synced['errors'] += 1

    return synced


# Quick test
if __name__ == "__main__":
    print("=" * 50)
    print("  NTFY BRIDGE TEST")
    print("=" * 50)

    # Test push
    print("\n1. Testing PUSH...")
    success = push_alert("ECO4 Bridge Connected!", priority="low")
    print(f"   Push: {'✅ Success' if success else '❌ Failed'}")

    # Test fetch
    print("\n2. Testing FETCH...")
    messages = fetch_recent_messages(5)
    print(f"   Found {len(messages)} recent messages")

    for msg in messages[-3:]:
        print(f"\n   [{msg['time']}]")
        print(f"   Title: {msg['title']}")
        print(f"   Body: {msg['message'][:50]}...")

    print("\n" + "=" * 50)
