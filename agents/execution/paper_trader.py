"""
Paper Trader - ECO SYSTEM 4
Simulates trades without real money.
Tracks all paper trades for win rate calculation.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Volumes/LegacySafe/ECO_SYSTEM_4')

from agents.base_agent import BaseAgent, Signal, Trade, SS3_ROOT, LOGS_PATH

TRADES_PATH = LOGS_PATH / 'trades'
PAPER_TRADES_FILE = SS3_ROOT / 'data' / 'paper_trades.json'


class PaperTrader(BaseAgent):
    """
    Paper Trader - Risk-Free Learning

    Simulates trade execution without real money.
    All trades logged and tracked for performance analysis.
    Used during Stage 1 to prove strategy before going live.
    """

    def __init__(self):
        super().__init__("paper_trader")
        TRADES_PATH.mkdir(parents=True, exist_ok=True)
        self.trades = self._load_trades()

    def _load_trades(self) -> list:
        """Load existing paper trades."""
        if PAPER_TRADES_FILE.exists():
            with open(PAPER_TRADES_FILE, 'r') as f:
                return json.load(f)
        return []

    def _save_trades(self) -> None:
        """Save paper trades."""
        with open(PAPER_TRADES_FILE, 'w') as f:
            json.dump(self.trades, f, indent=2)

    def execute_signal(self, signal: Signal, position_size_usd: float) -> dict:
        """Execute a signal as a paper trade (wrapper for open_trade)."""
        trade = self.open_trade(signal, position_size_usd)
        return {
            'status': 'opened',
            'trade_id': trade.id,
            'symbol': trade.symbol,
            'action': trade.action,
            'entry_price': trade.entry_price,
            'position_size_usd': trade.position_size_usd,
            'stop_loss': trade.stop_loss,
            'take_profit': trade.take_profit
        }

    def open_trade(self, signal: Signal, position_size_usd: float) -> Trade:
        """Open a new paper trade."""
        self.update_status("opening_trade")
        self.log(f"Opening paper trade: {signal.symbol} {signal.action}")

        trade = Trade(signal, position_size_usd, is_paper=True)
        self.trades.append(trade.to_dict())
        self._save_trades()

        # Update BRAIN
        self.brain['active_positions'].append({
            'trade_id': trade.id,
            'symbol': trade.symbol,
            'action': trade.action,
            'entry_price': trade.entry_price,
            'position_size_usd': trade.position_size_usd,
            'stop_loss': trade.stop_loss,
            'take_profit': trade.take_profit,
            'timestamp': trade.timestamp
        })
        self.brain['session']['trades_today'] = self.brain['session'].get('trades_today', 0) + 1
        self._save_brain()

        self.log(f"Trade opened: {trade.id} - {trade.symbol} {trade.action} @ ${trade.entry_price}")
        self.update_status("idle")

        return trade

    def close_trade(self, trade_id: str, exit_price: float) -> dict:
        """Close a paper trade and calculate PnL."""
        self.update_status("closing_trade")
        self.log(f"Closing paper trade: {trade_id}")

        # Find trade
        trade_data = None
        for t in self.trades:
            if t['id'] == trade_id:
                trade_data = t
                break

        if not trade_data:
            self.log(f"Trade not found: {trade_id}", "ERROR")
            return {'error': 'Trade not found'}

        # Calculate PnL
        if trade_data['action'] == "BUY":
            pnl_pct = ((exit_price - trade_data['entry_price']) / trade_data['entry_price']) * 100
        else:
            pnl_pct = ((trade_data['entry_price'] - exit_price) / trade_data['entry_price']) * 100

        pnl_usd = trade_data['position_size_usd'] * (pnl_pct / 100)

        # Update trade
        trade_data['exit_price'] = exit_price
        trade_data['exit_timestamp'] = datetime.now().isoformat()
        trade_data['status'] = 'CLOSED'
        trade_data['pnl_usd'] = pnl_usd
        trade_data['pnl_pct'] = pnl_pct

        self._save_trades()

        # Update BRAIN
        self.brain['active_positions'] = [
            p for p in self.brain.get('active_positions', [])
            if p.get('trade_id') != trade_id
        ]

        # Update stats
        trading = self.brain.get('trading', {})
        trading['total_trades'] = trading.get('total_trades', 0) + 1

        if pnl_usd > 0:
            trading['wins'] = trading.get('wins', 0) + 1
        else:
            trading['losses'] = trading.get('losses', 0) + 1

        trading['total_pnl_usd'] = trading.get('total_pnl_usd', 0) + pnl_usd
        trading['win_rate_pct'] = (trading['wins'] / trading['total_trades'] * 100) if trading['total_trades'] > 0 else 0

        self.brain['trading'] = trading

        # Update session
        self.brain['session']['pnl_today_usd'] = self.brain['session'].get('pnl_today_usd', 0) + pnl_usd

        # Update mission progress if profitable
        if pnl_usd > 0:
            self.brain['mission']['progress_usd'] = self.brain['mission'].get('progress_usd', 0) + pnl_usd

        self._save_brain()

        emoji = "+" if pnl_usd > 0 else ""
        self.log(f"Trade closed: {trade_id} - P&L: {emoji}${pnl_usd:.2f} ({emoji}{pnl_pct:.1f}%)")
        self.update_status("idle")

        return {
            'trade_id': trade_id,
            'pnl_usd': pnl_usd,
            'pnl_pct': pnl_pct,
            'exit_price': exit_price,
            'result': 'WIN' if pnl_usd > 0 else 'LOSS'
        }

    def check_stops(self, current_prices: dict) -> list:
        """Check all open positions for stop loss / take profit."""
        triggered = []

        for position in self.brain.get('active_positions', []):
            symbol = position['symbol']
            if symbol not in current_prices:
                continue

            current_price = current_prices[symbol]
            entry_price = position['entry_price']
            stop_loss = position.get('stop_loss')
            take_profit = position.get('take_profit')

            action = position['action']

            # Check stop loss
            if stop_loss:
                if action == "BUY" and current_price <= stop_loss:
                    triggered.append((position['trade_id'], current_price, 'STOP_LOSS'))
                elif action == "SELL" and current_price >= stop_loss:
                    triggered.append((position['trade_id'], current_price, 'STOP_LOSS'))

            # Check take profit
            if take_profit:
                if action == "BUY" and current_price >= take_profit:
                    triggered.append((position['trade_id'], current_price, 'TAKE_PROFIT'))
                elif action == "SELL" and current_price <= take_profit:
                    triggered.append((position['trade_id'], current_price, 'TAKE_PROFIT'))

        return triggered

    def get_stats(self) -> dict:
        """Get paper trading statistics."""
        trading = self.brain.get('trading', {})

        return {
            'total_trades': trading.get('total_trades', 0),
            'wins': trading.get('wins', 0),
            'losses': trading.get('losses', 0),
            'win_rate': trading.get('win_rate_pct', 0),
            'total_pnl': trading.get('total_pnl_usd', 0),
            'active_positions': len(self.brain.get('active_positions', [])),
            'ready_for_live': trading.get('total_trades', 0) >= 10 and trading.get('win_rate_pct', 0) >= 60
        }

    def run(self) -> dict:
        """Run paper trader status check."""
        self.update_status("running")
        stats = self.get_stats()
        self.log(f"Stats: {stats['total_trades']} trades, {stats['win_rate']:.1f}% win rate")
        self.update_status("idle")
        return stats


if __name__ == "__main__":
    trader = PaperTrader()
    stats = trader.run()
    print(f"\nPaper Trading Stats:")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.1f}%")
    print(f"  Total P&L: ${stats['total_pnl']:.2f}")
    print(f"  Ready for Live: {'YES' if stats['ready_for_live'] else 'NO'}")
