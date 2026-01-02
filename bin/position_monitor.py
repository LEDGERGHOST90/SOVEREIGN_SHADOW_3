#!/usr/bin/env python3
"""
POSITION MONITOR - Automatic TP/SL Execution

Watches open positions and auto-sells when take-profit or stop-loss hits.

Usage:
    python bin/position_monitor.py              # Run once
    python bin/position_monitor.py --daemon     # Run continuously (every 60s)
    python bin/position_monitor.py --dry-run    # Check prices without executing

Config: BRAIN.json → positions_monitor section
"""

import os
import sys
import json
import time
import argparse
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Paths
SS3_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SS3_ROOT))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('position_monitor')

# NTFY for notifications
NTFY_TOPIC = "sovereignshadow_dc4d2fa1"


@dataclass
class Position:
    """Tracked position with TP/SL targets"""
    symbol: str
    qty: float
    entry_price: float
    take_profit: float
    stop_loss: float
    take_profit_2: Optional[float] = None  # Optional second TP
    partial_sell_pct: float = 0.5  # Sell 50% at TP1, rest at TP2
    category: str = ""

    @property
    def tp_pct(self) -> float:
        return ((self.take_profit / self.entry_price) - 1) * 100

    @property
    def sl_pct(self) -> float:
        return ((self.stop_loss / self.entry_price) - 1) * 100


@dataclass
class WatchItem:
    """Watchlist item with price alerts"""
    symbol: str
    alert_below: float
    alert_above: float
    note: str = ""


class PositionMonitor:
    """
    Monitors positions and executes TP/SL automatically.

    Workflow:
    1. Load positions from BRAIN.json
    2. Fetch current prices from Coinbase
    3. Check if any position hit TP or SL
    4. Execute sell order if triggered
    5. Send notification
    6. Update BRAIN.json
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.brain_path = SS3_ROOT / 'BRAIN.json'
        self.config_path = SS3_ROOT / 'freqtrade' / 'config.json'

        # Load exchange credentials
        self.exchange = self._init_exchange()

        # Load positions and watchlist
        self.positions = self._load_positions()
        self.watchlist = self._load_watchlist()

        # Watchlist check counter (check every N cycles to reduce API calls)
        self.watchlist_check_interval = 5  # Check watchlist every 5 position cycles
        self.cycle_count = 0

        logger.info(f"PositionMonitor initialized ({'DRY RUN' if dry_run else 'LIVE'})")
        logger.info(f"Tracking {len(self.positions)} positions, {len(self.watchlist)} watchlist")

    def _init_exchange(self):
        """Initialize Coinbase connection via ccxt"""
        try:
            import ccxt
            config = json.load(open(self.config_path))

            exchange = ccxt.coinbase({
                'apiKey': config['exchange']['key'],
                'secret': config['exchange']['secret'],
            })

            # Test connection
            exchange.fetch_balance()
            logger.info("✓ Coinbase connection OK")
            return exchange

        except Exception as e:
            logger.error(f"Failed to connect to Coinbase: {e}")
            return None

    def _load_positions(self) -> List[Position]:
        """Load tracked positions from BRAIN.json"""
        brain = json.load(open(self.brain_path))

        positions_config = brain.get('positions_monitor', {}).get('positions', [])

        positions = []
        for p in positions_config:
            positions.append(Position(
                symbol=p['symbol'],
                qty=p['qty'],
                entry_price=p['entry_price'],
                take_profit=p['take_profit'],
                stop_loss=p['stop_loss'],
                take_profit_2=p.get('take_profit_2'),
                partial_sell_pct=p.get('partial_sell_pct', 0.5)
            ))

        return positions

    def _load_watchlist(self) -> List[WatchItem]:
        """Load watchlist from BRAIN.json"""
        brain = json.load(open(self.brain_path))

        watchlist_config = brain.get('positions_monitor', {}).get('watchlist', [])

        watchlist = []
        for w in watchlist_config:
            watchlist.append(WatchItem(
                symbol=w['symbol'],
                alert_below=w['alert_below'],
                alert_above=w['alert_above'],
                note=w.get('note', '')
            ))

        return watchlist

    def _save_positions(self):
        """Save updated positions back to BRAIN.json"""
        brain = json.load(open(self.brain_path))

        brain['positions_monitor']['positions'] = [
            {
                'symbol': p.symbol,
                'qty': p.qty,
                'entry_price': p.entry_price,
                'take_profit': p.take_profit,
                'stop_loss': p.stop_loss,
                'take_profit_2': p.take_profit_2,
                'partial_sell_pct': p.partial_sell_pct
            }
            for p in self.positions
        ]

        brain['positions_monitor']['last_check'] = datetime.now().isoformat()

        with open(self.brain_path, 'w') as f:
            json.dump(brain, f, indent=2)

    def get_current_price(self, symbol: str, delay: float = 0.1) -> Optional[float]:
        """Fetch current price from Coinbase with rate limiting"""
        if not self.exchange:
            return None

        try:
            time.sleep(delay)  # Rate limiting
            ticker = self.exchange.fetch_ticker(f"{symbol}/USDC")
            return ticker['last']
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    def check_position(self, position: Position) -> Dict:
        """Check if position hit TP or SL"""
        current_price = self.get_current_price(position.symbol)

        if current_price is None:
            return {'action': 'ERROR', 'reason': 'Could not fetch price'}

        pnl_pct = ((current_price / position.entry_price) - 1) * 100
        pnl_usd = (current_price - position.entry_price) * position.qty

        result = {
            'symbol': position.symbol,
            'current_price': current_price,
            'entry_price': position.entry_price,
            'pnl_pct': pnl_pct,
            'pnl_usd': pnl_usd,
            'qty': position.qty,
            'action': 'HOLD',
            'reason': None
        }

        # Check STOP LOSS
        if current_price <= position.stop_loss:
            result['action'] = 'SELL_SL'
            result['reason'] = f"Stop loss hit: ${current_price:.4f} <= ${position.stop_loss:.4f}"
            result['sell_qty'] = position.qty  # Sell all

        # Check TAKE PROFIT
        elif current_price >= position.take_profit:
            if position.take_profit_2 and current_price < position.take_profit_2:
                # Partial sell at TP1
                result['action'] = 'SELL_TP1'
                result['reason'] = f"TP1 hit: ${current_price:.4f} >= ${position.take_profit:.4f}"
                result['sell_qty'] = position.qty * position.partial_sell_pct
            else:
                # Full sell at TP2 or single TP
                result['action'] = 'SELL_TP'
                result['reason'] = f"Take profit hit: ${current_price:.4f} >= ${position.take_profit:.4f}"
                result['sell_qty'] = position.qty

        return result

    def execute_sell(self, symbol: str, qty: float, reason: str) -> bool:
        """Execute sell order on Coinbase"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would sell {qty:.6f} {symbol}")
            return True

        if not self.exchange:
            logger.error("No exchange connection")
            return False

        try:
            # Create market sell order
            order = self.exchange.create_market_sell_order(
                symbol=f"{symbol}/USDC",
                amount=qty
            )

            logger.info(f"✓ SOLD {qty:.6f} {symbol} @ ${order.get('average', 'market')}")

            # Send notification
            self.notify(
                title=f"🔴 SOLD {symbol}",
                message=f"Qty: {qty:.4f}\nReason: {reason}\nOrder ID: {order.get('id', 'N/A')}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to sell {symbol}: {e}")
            self.notify(
                title=f"⚠️ SELL FAILED {symbol}",
                message=f"Error: {str(e)}"
            )
            return False

    def notify(self, title: str, message: str):
        """Send notification via ntfy"""
        try:
            # Remove emojis for ntfy compatibility and strip whitespace
            clean_title = title.encode('ascii', 'ignore').decode('ascii').strip()
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=message.encode('utf-8'),
                headers={"Title": clean_title}
            )
        except Exception as e:
            logger.error(f"Notification failed: {e}")

    def check_watchlist(self) -> List[Dict]:
        """Check watchlist items for price alerts"""
        alerts = []

        for item in self.watchlist:
            price = self.get_current_price(item.symbol)
            if price is None:
                continue

            alert = None
            if price <= item.alert_below:
                alert = {
                    'symbol': item.symbol,
                    'price': price,
                    'trigger': 'below',
                    'level': item.alert_below,
                    'note': item.note
                }
                logger.info(f"[ALERT] {item.symbol} at ${price:.4f} - BELOW ${item.alert_below}")
                self.notify(
                    title=f"ALERT: {item.symbol} below ${item.alert_below}",
                    message=f"Current: ${price:.4f}\n{item.note}"
                )
            elif price >= item.alert_above:
                alert = {
                    'symbol': item.symbol,
                    'price': price,
                    'trigger': 'above',
                    'level': item.alert_above,
                    'note': item.note
                }
                logger.info(f"[ALERT] {item.symbol} at ${price:.4f} - ABOVE ${item.alert_above}")
                self.notify(
                    title=f"ALERT: {item.symbol} above ${item.alert_above}",
                    message=f"Current: ${price:.4f}\n{item.note}"
                )

            if alert:
                alerts.append(alert)

        return alerts

    def run_check(self) -> List[Dict]:
        """Run one check cycle on all positions and watchlist"""
        results = []
        self.cycle_count += 1

        logger.info(f"{'='*50}")
        logger.info(f"Position Check @ {datetime.now().strftime('%H:%M:%S')} (cycle {self.cycle_count})")
        logger.info(f"{'='*50}")

        for position in self.positions:
            result = self.check_position(position)
            results.append(result)

            # Handle error case
            if result['action'] == 'ERROR':
                logger.warning(f"[!] {position.symbol}: {result.get('reason', 'Unknown error')}")
                continue

            # Log status
            status_icon = {
                'HOLD': '[HOLD]',
                'SELL_SL': '[STOP]',
                'SELL_TP': '[TP]',
                'SELL_TP1': '[TP1]',
                'ERROR': '[ERR]'
            }.get(result['action'], '[?]')

            logger.info(
                f"{status_icon} {result['symbol']}: "
                f"${result.get('current_price', 0):.4f} "
                f"({result.get('pnl_pct', 0):+.2f}%)"
            )

            # Execute if needed
            if result['action'] in ['SELL_SL', 'SELL_TP', 'SELL_TP1']:
                success = self.execute_sell(
                    symbol=result['symbol'],
                    qty=result['sell_qty'],
                    reason=result['reason']
                )

                if success and result['action'] == 'SELL_TP1':
                    # Update position with remaining qty
                    position.qty -= result['sell_qty']
                    position.entry_price = result['current_price']  # Reset entry for trailing
                elif success:
                    # Remove position entirely
                    self.positions.remove(position)

        # Save updated positions
        if not self.dry_run:
            self._save_positions()

        # Check watchlist only every N cycles (to reduce API calls - 34 items is a lot)
        if self.watchlist and (self.cycle_count % self.watchlist_check_interval == 0):
            logger.info(f"\n{'='*50}")
            logger.info(f"Watchlist Check ({len(self.watchlist)} items)")
            logger.info(f"{'='*50}")
            alerts = self.check_watchlist()
            if alerts:
                logger.info(f"Triggered {len(alerts)} watchlist alert(s)")
        elif self.watchlist:
            next_check = self.watchlist_check_interval - (self.cycle_count % self.watchlist_check_interval)
            logger.info(f"Watchlist check in {next_check} cycles")

        return results

    def run_daemon(self, interval_seconds: int = 60):
        """Run continuously"""
        logger.info(f"Starting daemon mode (checking every {interval_seconds}s)")

        self.notify(
            title="🟢 Position Monitor Started",
            message=f"Tracking {len(self.positions)} positions\nInterval: {interval_seconds}s"
        )

        try:
            while True:
                self.run_check()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Stopped by user")
            self.notify(
                title="🔴 Position Monitor Stopped",
                message="Manual shutdown"
            )


def main():
    parser = argparse.ArgumentParser(description='Position Monitor - Auto TP/SL')
    parser.add_argument('--daemon', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--dry-run', action='store_true', help='Check only, no execution')
    args = parser.parse_args()

    monitor = PositionMonitor(dry_run=args.dry_run)

    if not monitor.positions:
        logger.warning("No positions configured in BRAIN.json")
        logger.info("Add positions to: BRAIN.json → positions_monitor → positions")
        logger.info("Example:")
        print(json.dumps({
            "positions_monitor": {
                "enabled": True,
                "positions": [
                    {
                        "symbol": "RENDER",
                        "qty": 123.8,
                        "entry_price": 1.28,
                        "take_profit": 1.60,
                        "stop_loss": 1.15
                    }
                ]
            }
        }, indent=2))
        return

    if args.daemon:
        monitor.run_daemon(interval_seconds=args.interval)
    else:
        monitor.run_check()


if __name__ == '__main__':
    main()
