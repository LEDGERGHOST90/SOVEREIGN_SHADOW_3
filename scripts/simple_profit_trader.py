#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Simple Profit Trader
Clean auto-trader using working CoinbaseConnector

GOAL: $5-20/day from small scalps
CAPITAL: $15-20 per position
PAIRS: SOL-USD, XRP-USD
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchanges.coinbase_connector import CoinbaseConnector
from exchanges.base_connector import OrderSide, OrderType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/logs/simple_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleProfitTrader:
    """
    Simple auto-trader that makes small, consistent profits

    Strategy:
    - Buy below mid, sell above mid
    - 0.5-1.5% profit targets
    - -2% stop loss
    - Max 5 trades per day
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        position_size_usd: float = 20.0,
        max_daily_trades: int = 5
    ):
        """Initialize trader"""
        self.coinbase = CoinbaseConnector(api_key, api_secret, passphrase)
        self.position_size_usd = position_size_usd
        self.max_daily_trades = max_daily_trades

        # Trading pairs
        self.pairs = ["SOL/USD", "XRP/USD"]

        # Track trades
        self.trades_today = []
        self.active_positions = {}
        self.last_reset = datetime.now().date()

        # Connect
        if not self.coinbase.connect():
            raise Exception("Failed to connect to Coinbase")

        logger.info(f"✅ SimpleProfitTrader initialized")
        logger.info(f"💰 Position size: ${position_size_usd}")
        logger.info(f"📊 Pairs: {', '.join(self.pairs)}")
        logger.info(f"🎯 Max daily trades: {max_daily_trades}")

    def reset_daily_counter(self):
        """Reset trade counter at midnight"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.trades_today = []
            self.last_reset = today
            logger.info(f"🔄 Daily trade counter reset")

    def can_trade(self) -> bool:
        """Check if we can open new trades"""
        self.reset_daily_counter()
        return len(self.trades_today) < self.max_daily_trades

    def get_entry_signal(self, pair: str) -> Optional[Dict]:
        """
        Simple entry logic: Buy when price dips below recent mid

        Returns:
            Dict with entry details or None
        """
        try:
            ticker = self.coinbase.fetch_ticker(pair)

            if "error" in ticker:
                logger.warning(f"⚠️  Failed to fetch {pair} ticker")
                return None

            bid = ticker["bid"]
            ask = ticker["ask"]
            mid = (bid + ask) / 2
            spread_pct = ((ask - bid) / mid) * 100

            # Only trade if spread is tight (< 0.3%)
            if spread_pct > 0.3:
                return None

            # Calculate position size
            position_size = self.position_size_usd / mid

            # Entry: Buy at bid (0.5% below mid on average)
            entry_price = bid

            # Targets
            tp1 = round(mid * 1.005, 2)  # +0.5% from mid
            tp2 = round(mid * 1.015, 2)  # +1.5% from mid
            stop_loss = round(mid * 0.98, 2)  # -2% from mid

            # Expected profit
            expected_profit_pct = ((tp1 - entry_price) / entry_price) * 100

            # Only trade if expected profit > 0.5%
            if expected_profit_pct < 0.5:
                return None

            return {
                "pair": pair,
                "entry_price": entry_price,
                "position_size": round(position_size, 6),
                "tp1": tp1,
                "tp2": tp2,
                "stop_loss": stop_loss,
                "mid": mid,
                "expected_profit_pct": expected_profit_pct
            }

        except Exception as e:
            logger.error(f"❌ Error getting entry signal for {pair}: {e}")
            return None

    def execute_trade(self, signal: Dict) -> bool:
        """
        Execute trade based on signal

        Returns:
            bool: True if trade executed successfully
        """
        try:
            pair = signal["pair"]
            position_size = signal["position_size"]
            entry_price = signal["entry_price"]

            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 TRADE SIGNAL: {pair}")
            logger.info(f"   Entry: ${entry_price:,.2f} | Size: {position_size}")
            logger.info(f"   TP1: ${signal['tp1']:,.2f} | TP2: ${signal['tp2']:,.2f}")
            logger.info(f"   SL: ${signal['stop_loss']:,.2f}")
            logger.info(f"   Expected: +{signal['expected_profit_pct']:.2f}%")
            logger.info(f"{'='*60}\n")

            # Place limit buy order at entry price
            order = self.coinbase.create_order(
                symbol=pair,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                amount=position_size,
                price=entry_price
            )

            if "error" in order:
                logger.error(f"❌ Order failed: {order['error']}")
                return False

            # Track trade
            self.trades_today.append({
                "timestamp": datetime.now(),
                "pair": pair,
                "order_id": order.get("order_id"),
                "entry_price": entry_price,
                "size": position_size
            })

            # Track active position
            self.active_positions[pair] = {
                "order_id": order.get("order_id"),
                "entry_price": entry_price,
                "size": position_size,
                "tp1": signal["tp1"],
                "tp2": signal["tp2"],
                "stop_loss": signal["stop_loss"],
                "timestamp": datetime.now()
            }

            logger.info(f"✅ Order placed: {order.get('order_id')}")
            logger.info(f"📊 Trades today: {len(self.trades_today)}/{self.max_daily_trades}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to execute trade: {e}")
            return False

    def monitor_positions(self):
        """
        Monitor active positions and manage exits

        This checks if positions hit TP or SL
        """
        for pair, position in list(self.active_positions.items()):
            try:
                ticker = self.coinbase.fetch_ticker(pair)
                current_price = ticker["last"]
                entry_price = position["entry_price"]

                pnl_pct = ((current_price - entry_price) / entry_price) * 100

                # Check stop loss
                if current_price <= position["stop_loss"]:
                    logger.warning(f"🛑 STOP LOSS HIT: {pair} at ${current_price:,.2f} ({pnl_pct:.2f}%)")
                    self.close_position(pair, current_price, "STOP_LOSS")

                # Check take profit 1
                elif current_price >= position["tp1"]:
                    logger.info(f"🎯 TARGET HIT: {pair} at ${current_price:,.2f} (+{pnl_pct:.2f}%)")
                    self.close_position(pair, current_price, "TAKE_PROFIT")

            except Exception as e:
                logger.error(f"❌ Error monitoring {pair}: {e}")

    def close_position(self, pair: str, price: float, reason: str):
        """
        Close a position

        Args:
            pair: Trading pair
            price: Exit price
            reason: STOP_LOSS or TAKE_PROFIT
        """
        try:
            position = self.active_positions.get(pair)
            if not position:
                return

            # Calculate P&L
            pnl_pct = ((price - position["entry_price"]) / position["entry_price"]) * 100
            pnl_usd = position["size"] * (price - position["entry_price"])

            # Place market sell order
            order = self.coinbase.create_order(
                symbol=pair,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                amount=position["size"]
            )

            logger.info(f"\n{'='*60}")
            logger.info(f"💰 POSITION CLOSED: {pair}")
            logger.info(f"   Entry: ${position['entry_price']:,.2f} | Exit: ${price:,.2f}")
            logger.info(f"   P&L: ${pnl_usd:,.2f} ({pnl_pct:+.2f}%)")
            logger.info(f"   Reason: {reason}")
            logger.info(f"{'='*60}\n")

            # Remove from active positions
            del self.active_positions[pair]

        except Exception as e:
            logger.error(f"❌ Failed to close position {pair}: {e}")

    def run_cycle(self):
        """Run one trading cycle"""
        try:
            # Monitor existing positions first
            if self.active_positions:
                self.monitor_positions()

            # Look for new entries if we can trade
            if self.can_trade():
                for pair in self.pairs:
                    # Skip if already have position in this pair
                    if pair in self.active_positions:
                        continue

                    # Get entry signal
                    signal = self.get_entry_signal(pair)

                    if signal:
                        self.execute_trade(signal)
                        # Only 1 new trade per cycle
                        break

        except Exception as e:
            logger.error(f"❌ Error in trading cycle: {e}")

    def run(self, check_interval: int = 60):
        """
        Run trader continuously

        Args:
            check_interval: Seconds between checks (default 60)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 SIMPLE PROFIT TRADER STARTED")
        logger.info(f"{'='*60}\n")

        try:
            while True:
                self.run_cycle()
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("\n🛑 Trader stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")


def main():
    """Main entry point"""
    from dotenv import load_dotenv

    # Load API keys from .env
    load_dotenv()

    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")
    passphrase = os.getenv("COINBASE_PASSPHRASE")

    if not all([api_key, api_secret, passphrase]):
        logger.error("❌ Missing Coinbase credentials in .env file")
        logger.error("Required: COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_PASSPHRASE")
        sys.exit(1)

    # Create and run trader
    trader = SimpleProfitTrader(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        position_size_usd=20.0,  # $20 per trade
        max_daily_trades=5       # Max 5 trades per day
    )

    # Run continuously (checks every 60 seconds)
    trader.run(check_interval=60)


if __name__ == "__main__":
    main()
