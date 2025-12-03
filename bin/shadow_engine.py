#!/usr/bin/env python3
"""
SHADOW ENGINE v1 - THE SOVEREIGN SHADOW EFFECT
===============================================
The self-propelling wealth engine for retail traders.

This IS ShadowNinja. This is what it was always meant to be.

FLOW:
1. DEPLOY - Pull working capital from core asset
2. DETECT - Monitor for reversals (overbought/oversold)
3. ROTATE - Move to stables before dumps, buy dips
4. HARVEST - Hit profit target, send gains to Ledger
5. REPEAT - Shadow grows, vault accumulates

Usage:
    python bin/shadow_engine.py --watch           # Run the engine
    python bin/shadow_engine.py --status          # Check current state
    python bin/shadow_engine.py --deploy BTC 500  # Deploy $500 from BTC
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum

# Paths
BASE_DIR = Path(__file__).parent.parent
ENGINE_STATE = BASE_DIR / "data/shadow_engine_state.json"
ENGINE_LOG = BASE_DIR / "logs/shadow_engine.log"
BRAIN_FILE = BASE_DIR / "BRAIN.json"

# Ensure directories exist
ENGINE_STATE.parent.mkdir(parents=True, exist_ok=True)
ENGINE_LOG.parent.mkdir(parents=True, exist_ok=True)


class EngineState(Enum):
    """Shadow Engine operating states"""
    IDLE = "idle"                    # No capital deployed
    DEPLOYED = "deployed"            # Capital in core asset, riding
    ROTATING_OUT = "rotating_out"    # Selling to stables (overbought detected)
    SNIPER_MODE = "sniper_mode"      # In stables, hunting for entry
    ROTATING_IN = "rotating_in"      # Buying back in (oversold detected)
    HARVESTING = "harvesting"        # Goal hit, moving to Ledger


class SignalType(Enum):
    """Instant signal types"""
    NONE = "none"
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Position:
    """Active position in the shadow"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    value_usd: float
    pnl: float
    pnl_pct: float
    entry_time: str


@dataclass
class ShadowState:
    """Complete state of the Shadow Engine"""
    state: str
    deployed_capital: float
    current_value: float
    profit_target: float
    harvest_threshold: float
    positions: List[dict]
    stables_balance: float
    total_harvested: float
    cycles_completed: int
    last_signal: str
    last_signal_time: str
    market_condition: str
    fear_greed: int
    last_update: str


class ShadowEngine:
    """
    The Sovereign Shadow Effect Engine

    Manages the cycle of:
    Deploy -> Ride/Rotate -> Sniper -> Harvest -> Repeat
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.state = self.load_state()

    def log(self, msg: str):
        """Log with timestamp"""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(ENGINE_LOG, "a") as f:
            f.write(line + "\n")

    def think(self, msg: str):
        """Show engine thought process"""
        if self.verbose:
            print(f"   💭 {msg}")

    def load_state(self) -> ShadowState:
        """Load engine state from disk"""
        if ENGINE_STATE.exists():
            with open(ENGINE_STATE) as f:
                data = json.load(f)
                return ShadowState(**data)
        return self.default_state()

    def default_state(self) -> ShadowState:
        """Create default initial state"""
        return ShadowState(
            state=EngineState.IDLE.value,
            deployed_capital=0,
            current_value=0,
            profit_target=0,
            harvest_threshold=0,
            positions=[],
            stables_balance=0,
            total_harvested=0,
            cycles_completed=0,
            last_signal=SignalType.NONE.value,
            last_signal_time="",
            market_condition="unknown",
            fear_greed=50,
            last_update=datetime.now().isoformat()
        )

    def save_state(self):
        """Persist engine state to disk"""
        self.state.last_update = datetime.now().isoformat()
        with open(ENGINE_STATE, "w") as f:
            json.dump(asdict(self.state), f, indent=2)

    # =========================================================================
    # MARKET DATA
    # =========================================================================

    def get_fear_greed(self) -> int:
        """Fetch Fear & Greed Index"""
        try:
            r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
            data = r.json()
            return int(data["data"][0]["value"])
        except:
            return 50  # Neutral default

    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        coin_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "ripple",
            "USDC": "usd-coin",
            "USDT": "tether",
            "SUI": "sui",
            "RENDER": "render-token",
            "BONK": "bonk",
            "WIF": "dogwifcoin"
        }
        cg_id = coin_map.get(symbol.upper(), symbol.lower())
        try:
            r = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd",
                timeout=10
            )
            return r.json()[cg_id]["usd"]
        except:
            return 0

    def get_market_condition(self, fg: int) -> str:
        """Determine market condition from Fear & Greed"""
        if fg <= 25:
            return "EXTREME_FEAR"
        elif fg <= 40:
            return "FEAR"
        elif fg <= 60:
            return "NEUTRAL"
        elif fg <= 75:
            return "GREED"
        else:
            return "EXTREME_GREED"

    # =========================================================================
    # REVERSAL DETECTION
    # =========================================================================

    def detect_reversal(self, symbol: str, current_price: float, entry_price: float) -> SignalType:
        """
        Detect if a position is about to reverse

        Uses:
        - Price momentum (% change from entry)
        - Market condition (Fear & Greed)
        - Position in cycle
        """
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        fg = self.state.fear_greed
        condition = self.state.market_condition

        self.think(f"Analyzing {symbol}: PnL {pnl_pct:.2f}%, F&G {fg}, Market {condition}")

        # SELL SIGNALS (reversal DOWN coming)
        if pnl_pct >= 5.0:
            self.think(f"  🔴 {symbol} hit +5% TP - SELL SIGNAL")
            return SignalType.SELL

        if pnl_pct >= 3.0 and condition in ["GREED", "EXTREME_GREED"]:
            self.think(f"  🔴 {symbol} +{pnl_pct:.1f}% in GREED market - SELL SIGNAL")
            return SignalType.SELL

        if condition == "EXTREME_GREED" and pnl_pct > 0:
            self.think(f"  🟡 {symbol} profitable in EXTREME GREED - consider SELL")
            return SignalType.SELL

        # STOP LOSS
        if pnl_pct <= -3.0:
            self.think(f"  🔴 {symbol} hit -3% SL - SELL SIGNAL")
            return SignalType.SELL

        # HOLD
        self.think(f"  🟢 {symbol} holding, no reversal detected")
        return SignalType.HOLD

    def detect_buy_opportunity(self, symbol: str) -> SignalType:
        """Detect if it's time to buy (reversal UP coming)"""
        fg = self.state.fear_greed
        condition = self.state.market_condition

        self.think(f"Scanning {symbol} for entry: F&G {fg}, Market {condition}")

        # BUY SIGNALS (reversal UP coming)
        if condition == "EXTREME_FEAR":
            self.think(f"  🟢 EXTREME FEAR - strong BUY SIGNAL for {symbol}")
            return SignalType.BUY

        if condition == "FEAR" and fg <= 30:
            self.think(f"  🟢 Deep FEAR ({fg}) - BUY SIGNAL for {symbol}")
            return SignalType.BUY

        if condition == "NEUTRAL":
            self.think(f"  🟡 NEUTRAL market - weak buy for {symbol}")
            return SignalType.BUY

        self.think(f"  ⚪ No buy signal for {symbol}")
        return SignalType.NONE

    # =========================================================================
    # ENGINE OPERATIONS
    # =========================================================================

    def deploy(self, symbol: str, amount_usd: float, profit_target_pct: float = 10.0):
        """
        Deploy capital from core asset into the Shadow

        Args:
            symbol: Core asset to deploy (BTC, ETH, etc)
            amount_usd: Dollar amount to deploy
            profit_target_pct: % gain before harvesting
        """
        self.log(f"🚀 DEPLOYING ${amount_usd} from {symbol}")

        price = self.get_price(symbol)
        if price == 0:
            self.log(f"❌ Could not get price for {symbol}")
            return

        quantity = amount_usd / price
        harvest_threshold = amount_usd * (1 + profit_target_pct / 100)

        position = {
            "symbol": symbol,
            "entry_price": price,
            "current_price": price,
            "quantity": quantity,
            "value_usd": amount_usd,
            "pnl": 0,
            "pnl_pct": 0,
            "entry_time": datetime.now().isoformat()
        }

        self.state.state = EngineState.DEPLOYED.value
        self.state.deployed_capital = amount_usd
        self.state.current_value = amount_usd
        self.state.profit_target = profit_target_pct
        self.state.harvest_threshold = harvest_threshold
        self.state.positions = [position]
        self.state.stables_balance = 0

        self.save_state()

        self.log(f"✅ DEPLOYED: {quantity:.8f} {symbol} @ ${price:.2f}")
        self.log(f"   Target: ${harvest_threshold:.2f} (+{profit_target_pct}%)")
        self.log(f"   State: {self.state.state}")

    def rotate_to_stables(self, reason: str = "overbought"):
        """Sell positions and move to stablecoins"""
        self.log(f"🔄 ROTATING TO STABLES - Reason: {reason}")

        total_value = 0
        for pos in self.state.positions:
            symbol = pos["symbol"]
            price = self.get_price(symbol)
            value = pos["quantity"] * price
            total_value += value
            self.log(f"   Sold {pos['quantity']:.8f} {symbol} @ ${price:.2f} = ${value:.2f}")

        self.state.state = EngineState.SNIPER_MODE.value
        self.state.positions = []
        self.state.stables_balance = total_value
        self.state.current_value = total_value

        self.save_state()

        self.log(f"✅ IN STABLES: ${total_value:.2f} USDC ready for sniper mode")

    def sniper_buy(self, symbol: str):
        """Deploy stables back into an asset"""
        self.log(f"🎯 SNIPER BUY: {symbol}")

        amount = self.state.stables_balance
        price = self.get_price(symbol)

        if price == 0:
            self.log(f"❌ Could not get price for {symbol}")
            return

        quantity = amount / price

        position = {
            "symbol": symbol,
            "entry_price": price,
            "current_price": price,
            "quantity": quantity,
            "value_usd": amount,
            "pnl": 0,
            "pnl_pct": 0,
            "entry_time": datetime.now().isoformat()
        }

        self.state.state = EngineState.DEPLOYED.value
        self.state.positions = [position]
        self.state.stables_balance = 0

        self.save_state()

        self.log(f"✅ BOUGHT: {quantity:.8f} {symbol} @ ${price:.2f}")

    def harvest(self):
        """Goal reached - harvest profits back to Ledger"""
        self.log(f"🏆 HARVESTING - Goal Reached!")

        profit = self.state.current_value - self.state.deployed_capital

        self.log(f"   Deployed: ${self.state.deployed_capital:.2f}")
        self.log(f"   Final:    ${self.state.current_value:.2f}")
        self.log(f"   Profit:   ${profit:.2f}")

        self.state.total_harvested += profit
        self.state.cycles_completed += 1
        self.state.state = EngineState.IDLE.value
        self.state.deployed_capital = 0
        self.state.current_value = 0
        self.state.positions = []
        self.state.stables_balance = 0

        self.save_state()

        self.log(f"✅ CYCLE COMPLETE #{self.state.cycles_completed}")
        self.log(f"   Total Harvested: ${self.state.total_harvested:.2f}")
        self.log(f"   → Transfer ${profit:.2f} to Ledger")

    # =========================================================================
    # MAIN ENGINE LOOP
    # =========================================================================

    def update_market_data(self):
        """Refresh market indicators"""
        self.state.fear_greed = self.get_fear_greed()
        self.state.market_condition = self.get_market_condition(self.state.fear_greed)
        self.think(f"Market: F&G={self.state.fear_greed} ({self.state.market_condition})")

    def update_positions(self):
        """Update all position prices and P&L"""
        total_value = 0
        for pos in self.state.positions:
            price = self.get_price(pos["symbol"])
            if price > 0:
                pos["current_price"] = price
                pos["value_usd"] = pos["quantity"] * price
                pos["pnl"] = pos["value_usd"] - (pos["quantity"] * pos["entry_price"])
                pos["pnl_pct"] = ((price - pos["entry_price"]) / pos["entry_price"]) * 100
                total_value += pos["value_usd"]

        self.state.current_value = total_value + self.state.stables_balance

    def check_signals(self) -> List[tuple]:
        """Check all positions for reversal signals"""
        signals = []

        for pos in self.state.positions:
            signal = self.detect_reversal(
                pos["symbol"],
                pos["current_price"],
                pos["entry_price"]
            )
            if signal != SignalType.HOLD:
                signals.append((pos["symbol"], signal, pos))

        return signals

    def check_harvest(self) -> bool:
        """Check if harvest threshold is reached"""
        if self.state.current_value >= self.state.harvest_threshold:
            return True
        return False

    def run_cycle(self):
        """Execute one engine cycle"""
        self.log("=" * 60)
        self.log("🔄 SHADOW ENGINE CYCLE")
        self.log("=" * 60)

        # Update market data
        self.update_market_data()

        state = EngineState(self.state.state)

        # STATE MACHINE
        if state == EngineState.IDLE:
            self.log("⏸️  IDLE - No capital deployed")
            self.log("   Use: shadow_engine.py --deploy BTC 500")
            return

        elif state == EngineState.DEPLOYED:
            self.log("📈 DEPLOYED - Monitoring positions")
            self.update_positions()

            # Check for harvest
            if self.check_harvest():
                self.harvest()
                return

            # Check for reversal signals
            signals = self.check_signals()
            for symbol, signal, pos in signals:
                if signal == SignalType.SELL:
                    self.log(f"🔴 SELL SIGNAL: {symbol}")
                    self.rotate_to_stables(f"{symbol} reversal detected")
                    return

            # Display positions
            self.display_positions()

        elif state == EngineState.SNIPER_MODE:
            self.log("🎯 SNIPER MODE - Hunting for entry")
            self.log(f"   Stables: ${self.state.stables_balance:.2f}")

            # Check for buy opportunity
            for symbol in ["BTC", "ETH", "SOL"]:
                signal = self.detect_buy_opportunity(symbol)
                if signal == SignalType.BUY:
                    self.sniper_buy(symbol)
                    return

            self.log("   ⏳ Waiting for better entry...")

        self.save_state()

    def display_positions(self):
        """Display current positions"""
        print()
        print("=" * 60)
        print("💰 SHADOW POSITIONS")
        print("=" * 60)
        print(f"Deployed:  ${self.state.deployed_capital:.2f}")
        print(f"Current:   ${self.state.current_value:.2f}")
        print(f"Target:    ${self.state.harvest_threshold:.2f}")
        pnl = self.state.current_value - self.state.deployed_capital
        pnl_pct = (pnl / self.state.deployed_capital * 100) if self.state.deployed_capital > 0 else 0
        print(f"P&L:       ${pnl:.2f} ({pnl_pct:+.2f}%)")
        print("-" * 60)

        for pos in self.state.positions:
            icon = "🟢" if pos["pnl"] >= 0 else "🔴"
            print(f"{icon} {pos['symbol']}: {pos['quantity']:.8f} @ ${pos['entry_price']:.2f}")
            print(f"   Now: ${pos['current_price']:.2f} | P&L: ${pos['pnl']:.2f} ({pos['pnl_pct']:+.2f}%)")

        print("=" * 60)

    def display_status(self):
        """Display full engine status"""
        self.update_market_data()
        if self.state.positions:
            self.update_positions()

        print()
        print("╔" + "═" * 58 + "╗")
        print("║" + " SHADOW ENGINE STATUS ".center(58) + "║")
        print("╠" + "═" * 58 + "╣")
        print(f"║  State:        {self.state.state:<41}║")
        print(f"║  Market:       {self.state.market_condition:<41}║")
        print(f"║  Fear & Greed: {self.state.fear_greed:<41}║")
        print("╠" + "═" * 58 + "╣")
        print(f"║  Deployed:     ${self.state.deployed_capital:<39.2f}║")
        print(f"║  Current:      ${self.state.current_value:<39.2f}║")
        print(f"║  Target:       ${self.state.harvest_threshold:<39.2f}║")
        print(f"║  Stables:      ${self.state.stables_balance:<39.2f}║")
        print("╠" + "═" * 58 + "╣")
        print(f"║  Cycles:       {self.state.cycles_completed:<41}║")
        print(f"║  Harvested:    ${self.state.total_harvested:<39.2f}║")
        print("╚" + "═" * 58 + "╝")

        if self.state.positions:
            self.display_positions()

    def run_watch(self, interval: int = 60):
        """Continuous monitoring mode"""
        self.log(f"🚀 SHADOW ENGINE STARTED - Interval: {interval}s")

        while True:
            try:
                self.run_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log("🛑 Engine stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error: {e}")
                time.sleep(30)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Shadow Engine - The Sovereign Shadow Effect")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--deploy", nargs=2, metavar=("SYMBOL", "AMOUNT"), help="Deploy capital")
    parser.add_argument("--harvest", action="store_true", help="Force harvest")
    parser.add_argument("--interval", type=int, default=60, help="Scan interval in seconds")
    parser.add_argument("--target", type=float, default=10.0, help="Profit target percentage")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Verbose output")

    args = parser.parse_args()
    engine = ShadowEngine(verbose=args.verbose)

    if args.status:
        engine.display_status()
    elif args.deploy:
        symbol, amount = args.deploy
        engine.deploy(symbol.upper(), float(amount), args.target)
    elif args.harvest:
        engine.harvest()
    elif args.watch:
        engine.run_watch(interval=args.interval)
    else:
        engine.run_cycle()


if __name__ == "__main__":
    main()
