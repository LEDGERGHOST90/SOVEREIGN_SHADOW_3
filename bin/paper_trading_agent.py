#!/usr/bin/env python3
"""
PAPER TRADING AGENT - MISSION 001: DEBT_DESTROYER
Automated paper trading using smart signals

This agent:
1. Scans for smart signals (Fear & Greed, Funding, DEX, Sentiment)
2. Auto-executes paper trades when criteria met
3. Monitors open positions for SL/TP
4. Tracks mission progress toward $661.46
5. Checks gateway unlock conditions

Usage:
    python bin/paper_trading_agent.py              # Single scan
    python bin/paper_trading_agent.py --watch      # Continuous monitoring
    python bin/paper_trading_agent.py --aggressive # Lower thresholds
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

BASE_DIR = Path(__file__).parent.parent
MISSION_FILE = BASE_DIR / "data/missions/mission_001_aave_debt.json"
BRAIN_FILE = BASE_DIR / "BRAIN.json"
SIGNALS_FILE = BASE_DIR / "logs/smart_signals.json"
AGENT_LOG = BASE_DIR / "logs/paper_trading_agent.log"

# Trading parameters from mission
MAX_POSITION_SIZE = 500  # $500 full stack per trade
STOP_LOSS_PCT = 3.0      # 3% stop loss
TAKE_PROFIT_PCT = 5.0    # 5% take profit
MIN_CONFIDENCE = 70      # Minimum signal confidence to trade
MAX_OPEN_POSITIONS = 1   # One trade at a time, full conviction

@dataclass
class Position:
    id: str
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    entry_time: str
    pnl: float = 0.0
    pnl_pct: float = 0.0

class PaperTradingAgent:
    def __init__(self, aggressive: bool = False, verbose: bool = False):
        self.aggressive = aggressive
        self.verbose = verbose
        self.min_confidence = 60 if aggressive else MIN_CONFIDENCE
        self.positions: List[Position] = []
        self.load_open_positions()

    def think(self, message: str):
        """Show agent's thought process"""
        if self.verbose:
            print(f"   💭 {message}")

    def log(self, message: str):
        """Log to file and stdout"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)

        # Append to log file
        with open(AGENT_LOG, "a") as f:
            f.write(log_line + "\n")

    def load_mission(self) -> dict:
        return json.loads(MISSION_FILE.read_text())

    def save_mission(self, mission: dict):
        MISSION_FILE.write_text(json.dumps(mission, indent=2))

    def load_brain(self) -> dict:
        return json.loads(BRAIN_FILE.read_text())

    def save_brain(self, brain: dict):
        BRAIN_FILE.write_text(json.dumps(brain, indent=2))

    def load_open_positions(self):
        """Load open positions from mission file"""
        mission = self.load_mission()
        self.positions = []

        for trade in mission.get("paper_trades", []):
            if trade.get("status") == "open":
                self.positions.append(Position(
                    id=trade["id"],
                    symbol=trade["symbol"],
                    direction=trade["direction"],
                    entry_price=trade["entry_price"],
                    current_price=trade["entry_price"],
                    position_size=trade["position_size"],
                    stop_loss=trade["stop_loss"],
                    take_profit=trade.get("take_profit", 0),
                    entry_time=trade["entry_time"]
                ))

    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            # Use CoinGecko for free price data
            coin_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "XRP": "ripple",
                "DOGE": "dogecoin",
                "PEPE": "pepe"
            }

            coin_id = coin_map.get(symbol.upper())
            if not coin_id:
                return None

            resp = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd",
                timeout=10
            )
            data = resp.json()
            return data.get(coin_id, {}).get("usd")
        except Exception as e:
            self.log(f"Price fetch error for {symbol}: {e}")
            return None

    def get_prices_batch(self, symbols: List[str] = None) -> Dict[str, float]:
        """Get prices for multiple symbols"""
        try:
            coin_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "XRP": "ripple",
                "RENDER": "render-token",
                "SUI": "sui",
                "BONK": "bonk",
                "WIF": "dogwifcoin"
            }

            # If no symbols specified, get all that we have positions for
            if symbols is None:
                symbols = list(coin_map.keys())

            coin_ids = [coin_map[s] for s in symbols if s in coin_map]

            resp = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coin_ids)}&vs_currencies=usd",
                timeout=10
            )
            data = resp.json()

            prices = {}
            for symbol, coin_id in coin_map.items():
                if coin_id in data:
                    prices[symbol] = data[coin_id]["usd"]

            return prices
        except Exception as e:
            self.log(f"Batch price fetch error: {e}")
            return {}

    def get_smart_signals(self) -> List[dict]:
        """Get smart signals from signal generator"""
        try:
            # First try to run smart_signals.py to get fresh signals
            import subprocess
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "bin/smart_signals.py")],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Load the output file
            if SIGNALS_FILE.exists():
                signals_data = json.loads(SIGNALS_FILE.read_text())
                return signals_data.get("signals", [])
        except Exception as e:
            self.log(f"Signal generation error: {e}")

        return []

    def should_enter_trade(self, signal: dict) -> bool:
        """Determine if we should enter a paper trade"""
        symbol = signal["symbol"]
        self.think(f"Analyzing {symbol}...")

        # Check if we have too many open positions
        if len(self.positions) >= MAX_OPEN_POSITIONS:
            self.think(f"SKIP {symbol}: Max positions ({MAX_OPEN_POSITIONS}) reached")
            return False

        # Check if we already have a position in this symbol
        if any(p.symbol == symbol for p in self.positions):
            self.think(f"SKIP {symbol}: Already holding position")
            return False

        # Only trade on BUY/STRONG_BUY signals (no shorting for now)
        if signal["action"] not in ["BUY", "STRONG_BUY"]:
            self.think(f"SKIP {symbol}: Signal is {signal['action']}, need BUY or STRONG_BUY")
            return False

        # Check confidence threshold
        if signal["confidence"] < self.min_confidence:
            self.think(f"SKIP {symbol}: Confidence {signal['confidence']}% < {self.min_confidence}% threshold")
            return False

        self.think(f"✓ {symbol} PASSES all checks - confidence {signal['confidence']}%, action {signal['action']}")
        return True

    def enter_paper_trade(self, signal: dict, price: float):
        """Execute a paper trade entry"""
        mission = self.load_mission()

        trade_id = f"PT{len(mission['paper_trades']) + 1:03d}"

        # Calculate stop loss and take profit
        direction = "long"  # Only longs for now

        stop_loss = price * (1 - STOP_LOSS_PCT / 100)
        take_profit = price * (1 + TAKE_PROFIT_PCT / 100)

        trade = {
            "id": trade_id,
            "symbol": signal["symbol"],
            "direction": direction,
            "entry_price": price,
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "position_size": MAX_POSITION_SIZE,
            "position_value": MAX_POSITION_SIZE,
            "status": "open",
            "entry_time": datetime.now().isoformat(),
            "signal_confidence": signal["confidence"],
            "signal_action": signal["action"],
            "signal_reasons": signal.get("reasons", []),
            "exit_price": None,
            "exit_time": None,
            "pnl": None,
            "pnl_pct": None
        }

        mission["paper_trades"].append(trade)
        self.save_mission(mission)

        # Add to active positions
        self.positions.append(Position(
            id=trade_id,
            symbol=signal["symbol"],
            direction=direction,
            entry_price=price,
            current_price=price,
            position_size=MAX_POSITION_SIZE,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=trade["entry_time"]
        ))

        self.log(f"{'=' * 60}")
        self.log(f"📈 PAPER TRADE OPENED: {trade_id}")
        self.log(f"   Symbol:      {signal['symbol']}")
        self.log(f"   Direction:   LONG")
        self.log(f"   Entry:       ${price:,.2f}")
        self.log(f"   Stop Loss:   ${stop_loss:,.2f} (-{STOP_LOSS_PCT}%)")
        self.log(f"   Take Profit: ${take_profit:,.2f} (+{TAKE_PROFIT_PCT}%)")
        self.log(f"   Size:        ${MAX_POSITION_SIZE}")
        self.log(f"   Confidence:  {signal['confidence']}%")
        self.log(f"{'=' * 60}")

        return trade_id

    def check_position_exits(self, prices: Dict[str, float]):
        """Check if any positions hit SL or TP"""
        self.think("Checking open positions for exit conditions...")

        for position in self.positions[:]:  # Copy list to allow modification
            current_price = prices.get(position.symbol)
            if not current_price:
                self.think(f"No price data for {position.symbol}, skipping")
                continue

            position.current_price = current_price

            # Calculate current P&L
            if position.direction == "long":
                position.pnl_pct = (current_price - position.entry_price) / position.entry_price * 100
            else:
                position.pnl_pct = (position.entry_price - current_price) / position.entry_price * 100

            position.pnl = position.position_size * (position.pnl_pct / 100)

            self.think(f"{position.id} {position.symbol}: Entry ${position.entry_price:,.2f} → Current ${current_price:,.2f} ({position.pnl_pct:+.2f}%)")
            self.think(f"   SL: ${position.stop_loss:,.2f} | TP: ${position.take_profit:,.2f}")

            # Check stop loss
            should_close = False
            close_reason = ""

            if position.direction == "long":
                if current_price <= position.stop_loss:
                    should_close = True
                    close_reason = "STOP LOSS HIT"
                    self.think(f"   ⚠️  STOP LOSS TRIGGERED! ${current_price:,.2f} <= ${position.stop_loss:,.2f}")
                elif current_price >= position.take_profit:
                    should_close = True
                    close_reason = "TAKE PROFIT HIT"
                    self.think(f"   🎯 TAKE PROFIT TRIGGERED! ${current_price:,.2f} >= ${position.take_profit:,.2f}")
                else:
                    self.think(f"   ↔️  Position still running, no exit triggered")

            if should_close:
                self.close_paper_trade(position, current_price, close_reason)

    def close_paper_trade(self, position: Position, exit_price: float, reason: str):
        """Close a paper trade"""
        mission = self.load_mission()

        # Find and update the trade
        for trade in mission["paper_trades"]:
            if trade["id"] == position.id and trade["status"] == "open":
                # Calculate final P&L
                if position.direction == "long":
                    pnl_pct = (exit_price - position.entry_price) / position.entry_price * 100
                else:
                    pnl_pct = (position.entry_price - exit_price) / position.entry_price * 100

                pnl = position.position_size * (pnl_pct / 100)

                trade["exit_price"] = exit_price
                trade["exit_time"] = datetime.now().isoformat()
                trade["pnl"] = round(pnl, 2)
                trade["pnl_pct"] = round(pnl_pct, 2)
                trade["status"] = "closed"
                trade["close_reason"] = reason

                # Update mission progress
                progress = mission["progress"]
                progress["paper_trades"] += 1
                progress["paper_pnl"] = round(progress["paper_pnl"] + pnl, 2)

                if pnl > 0:
                    progress["paper_wins"] += 1
                    if progress["best_trade"] is None or pnl > progress["best_trade"]:
                        progress["best_trade"] = pnl
                else:
                    progress["paper_losses"] += 1
                    if progress["worst_trade"] is None or pnl < progress["worst_trade"]:
                        progress["worst_trade"] = pnl

                # Calculate win rate
                if progress["paper_trades"] > 0:
                    progress["paper_win_rate"] = round(
                        progress["paper_wins"] / progress["paper_trades"] * 100, 1
                    )

                # Check milestones
                for milestone in mission["milestones"]:
                    if not milestone["reached"] and progress["paper_pnl"] >= milestone["target"]:
                        milestone["reached"] = True
                        milestone["date"] = datetime.now().strftime("%Y-%m-%d")
                        self.log(f"🎯 MILESTONE REACHED: {milestone['pct']}% (${milestone['target']:,.2f})")

                self.save_mission(mission)

                # Update BRAIN.json
                brain = self.load_brain()
                brain["active_mission"]["current_profit"] = progress["paper_pnl"]
                brain["active_mission"]["progress_pct"] = round(
                    progress["paper_pnl"] / mission["objective"]["target_profit"] * 100, 1
                )
                self.save_brain(brain)

                # Remove from active positions
                self.positions = [p for p in self.positions if p.id != position.id]

                emoji = "✅" if pnl > 0 else "❌"
                self.log(f"{'=' * 60}")
                self.log(f"{emoji} PAPER TRADE CLOSED: {position.id}")
                self.log(f"   Reason:  {reason}")
                self.log(f"   Symbol:  {position.symbol}")
                self.log(f"   Entry:   ${position.entry_price:,.2f}")
                self.log(f"   Exit:    ${exit_price:,.2f}")
                self.log(f"   P&L:     ${pnl:+,.2f} ({pnl_pct:+.1f}%)")
                self.log(f"   Mission Progress: ${progress['paper_pnl']:,.2f} / $661.46")
                self.log(f"{'=' * 60}")

                return

    def print_status(self):
        """Print current status"""
        mission = self.load_mission()
        progress = mission["progress"]
        target = mission["objective"]["target_profit"]

        print(f"\n{'=' * 60}")
        print(f"🤖 PAPER TRADING AGENT - MISSION 001")
        print(f"{'=' * 60}")
        print(f"Target:      ${target:,.2f}")
        print(f"Progress:    ${progress['paper_pnl']:+,.2f} ({progress['paper_pnl']/target*100:.1f}%)")
        print(f"Trades:      {progress['paper_trades']} ({progress['paper_wins']}W/{progress['paper_losses']}L)")
        print(f"Win Rate:    {progress['paper_win_rate']:.1f}%")
        print(f"Open Pos:    {len(self.positions)}/{MAX_OPEN_POSITIONS}")
        print(f"{'=' * 60}")

        if self.positions:
            print("📊 OPEN POSITIONS:")
            for p in self.positions:
                emoji = "🟢" if p.pnl >= 0 else "🔴"
                print(f"   {emoji} {p.id}: {p.symbol} @ ${p.entry_price:,.2f} | P&L: ${p.pnl:+,.2f}")
            print(f"{'=' * 60}")

    def check_gateway(self) -> bool:
        """Check if gateway is unlocked"""
        mission = self.load_mission()
        progress = mission["progress"]
        req = mission["objective"]["success_criteria"]

        profit_met = progress["paper_pnl"] >= req["paper_profit"]
        win_rate_met = progress["paper_win_rate"] >= req["win_rate_min"]
        trades_met = progress["paper_trades"] >= req["trades_min"]

        if all([profit_met, win_rate_met, trades_met]):
            self.log("🚀 GATEWAY UNLOCKED! Heavy artillery ready for deployment!")
            return True

        return False

    def run_scan(self):
        """Run a single scan cycle"""
        self.log("📡 Scanning for signals...")
        self.think("=" * 50)
        self.think("SCAN CYCLE STARTING")
        self.think("=" * 50)

        # Get current prices for all supported assets
        self.think("Fetching current prices from CoinGecko...")
        prices = self.get_prices_batch()  # Gets all supported coins
        for sym, price in prices.items():
            if price < 0.001:
                self.think(f"   {sym}: ${price:.10f}")
            else:
                self.think(f"   {sym}: ${price:,.2f}")

        # Check open positions for exits
        if self.positions:
            self.think(f"\nFound {len(self.positions)} open positions to check")
            self.check_position_exits(prices)
        else:
            self.think("\nNo open positions to check")

        # Get smart signals
        self.think("\nGenerating smart signals (Fear & Greed, DEX Volume, Funding)...")
        signals = self.get_smart_signals()
        self.think(f"Received {len(signals)} signals")

        # Look for entry opportunities
        self.think("\nEvaluating signals for entry opportunities...")
        for signal in signals:
            if self.should_enter_trade(signal):
                price = prices.get(signal["symbol"])
                if price:
                    self.think(f"🚀 EXECUTING ENTRY for {signal['symbol']} @ ${price:,.2f}")
                    self.enter_paper_trade(signal, price)

        # Print status
        self.print_status()

        # Check gateway
        self.think("\nChecking gateway unlock conditions...")
        self.check_gateway()

    def run_watch(self, interval: int = 60):
        """Run continuous monitoring"""
        self.log(f"🔄 Starting continuous monitoring (interval: {interval}s)")

        try:
            while True:
                self.run_scan()

                # Check gateway
                if self.check_gateway():
                    self.log("🎯 MISSION COMPLETE - Awaiting Commander approval for live trading")

                time.sleep(interval)

        except KeyboardInterrupt:
            self.log("👋 Agent stopped by user")

def main():
    parser = argparse.ArgumentParser(description="Paper Trading Agent for Mission 001")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show agent thought process")
    parser.add_argument("--aggressive", action="store_true", help="Lower confidence threshold (60%)")
    parser.add_argument("--interval", type=int, default=60, help="Scan interval in seconds")

    args = parser.parse_args()

    agent = PaperTradingAgent(aggressive=args.aggressive, verbose=args.verbose)

    if args.verbose:
        print("\n🧠 VERBOSE MODE: Showing agent thought process\n")

    if args.watch:
        agent.run_watch(interval=args.interval)
    else:
        agent.run_scan()

if __name__ == "__main__":
    main()
