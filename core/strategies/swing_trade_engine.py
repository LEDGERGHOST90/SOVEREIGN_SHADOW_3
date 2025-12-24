#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Swing Trade Engine
Complete swing trading system with entry/exit logic, risk management, and automation

Features:
- Entry signals (RSI + Volume + EMA)
- Exit signals (RSI overbought, TP, SL)
- Position sizing (2% risk rule)
- Stop loss automation (15%)
- Take profit triggers (TP1: 30%, TP2: 75%)
- Risk management (max daily loss, max positions)
- Paper trade mode

Usage:
    python strategies/swing_trade_engine.py --scan           # Scan for entries
    python strategies/swing_trade_engine.py --monitor        # Monitor open positions
    python strategies/swing_trade_engine.py --paper          # Paper trade mode
    python strategies/swing_trade_engine.py --status         # Show system status
"""

import os
import sys
import json
import time
import requests
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict
from enum import Enum

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# CONFIGURATION
# =============================================================================

class TradeMode(Enum):
    PAPER = "paper"
    SIGNAL = "signal"      # Signal + manual confirm
    AUTO = "auto"          # Full automation (dangerous)

@dataclass
class SwingConfig:
    """Swing trade configuration"""
    # Capital
    portfolio_value: float = 500.0
    risk_per_trade_pct: float = 2.0      # Risk 2% per trade

    # Entry conditions
    rsi_oversold: float = 30.0           # RSI below this = oversold
    rsi_overbought: float = 70.0         # RSI above this = overbought
    volume_spike_multiplier: float = 2.0 # Volume must be 2x average
    ema_period: int = 20                 # 20-period EMA

    # Exit conditions
    stop_loss_pct: float = 15.0          # 15% stop loss
    take_profit_1_pct: float = 30.0      # TP1 at 30%
    take_profit_2_pct: float = 75.0      # TP2 at 75%
    tp1_sell_pct: float = 50.0           # Sell 50% at TP1

    # Risk management
    max_positions: int = 5               # Max concurrent positions
    max_daily_loss_usd: float = 150.0    # Stop trading after $150 loss/day
    max_position_usd: float = 100.0      # Max $100 per position

    # Mode
    mode: TradeMode = TradeMode.PAPER

    # Watchlist
    watchlist: List[str] = field(default_factory=lambda: [
        "BTC", "ETH", "SOL", "XRP",           # Core
        "RENDER", "SUI", "ADA", "APT", "DOGE", # Alt majors
        "BONK", "TURBO", "PEPE", "WIF"         # Memes
    ])

# =============================================================================
# DATA STRUCTURES
# =============================================================================

class PositionStatus(Enum):
    OPEN = "open"
    TP1_HIT = "tp1_hit"      # First take profit hit, trailing
    CLOSED = "closed"
    STOPPED = "stopped"      # Stop loss hit

@dataclass
class Position:
    """Represents an open or closed position"""
    id: str
    symbol: str
    entry_price: float
    entry_time: str
    quantity: float
    position_value: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    status: str = "open"
    tp1_hit: bool = False
    remaining_quantity: float = 0.0
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: Optional[str] = None

    def __post_init__(self):
        self.remaining_quantity = self.quantity

@dataclass
class TradeSignal:
    """Represents a trade signal"""
    symbol: str
    signal_type: str          # "entry" or "exit"
    direction: str            # "long" or "short" (we only do long for now)
    strength: float           # 0-100 signal strength
    price: float
    rsi: float
    volume_ratio: float
    ema_20: float
    reasons: List[str]
    timestamp: str

@dataclass
class DailyStats:
    """Daily trading statistics"""
    date: str
    trades_opened: int = 0
    trades_closed: int = 0
    wins: int = 0
    losses: int = 0
    total_pnl: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0

# =============================================================================
# TECHNICAL INDICATORS
# =============================================================================

class TechnicalAnalysis:
    """Calculate technical indicators"""

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0  # Neutral if not enough data

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return round(ema, 6)

    @staticmethod
    def calculate_volume_ratio(current_volume: float, avg_volume: float) -> float:
        """Calculate volume ratio vs average"""
        if avg_volume == 0:
            return 1.0
        return round(current_volume / avg_volume, 2)

    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range for volatility-based stops"""
        if len(highs) < period + 1:
            return 0

        true_ranges = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            true_ranges.append(tr)

        return np.mean(true_ranges[-period:])

# =============================================================================
# MARKET DATA
# =============================================================================

class MarketData:
    """Fetch market data from APIs"""

    def __init__(self):
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> Optional[str]:
        """Load CryptoCompare API key"""
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("CRYPTOCOMPARE_API_KEY="):
                    return line.split("=", 1)[1].strip()
        return os.environ.get("CRYPTOCOMPARE_API_KEY")

    def get_ohlcv(self, symbol: str, limit: int = 100) -> Dict:
        """Get OHLCV data for a symbol"""
        try:
            url = "https://min-api.cryptocompare.com/data/v2/histohour"
            params = {
                "fsym": symbol,
                "tsym": "USD",
                "limit": limit,
                "api_key": self.api_key
            }

            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            if data.get("Response") == "Success":
                ohlcv = data["Data"]["Data"]
                return {
                    "open": [x["open"] for x in ohlcv],
                    "high": [x["high"] for x in ohlcv],
                    "low": [x["low"] for x in ohlcv],
                    "close": [x["close"] for x in ohlcv],
                    "volume": [x["volumeto"] for x in ohlcv],
                    "timestamp": [x["time"] for x in ohlcv]
                }
            return {}

        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return {}

    def get_current_price(self, symbol: str) -> float:
        """Get current price"""
        try:
            url = "https://min-api.cryptocompare.com/data/price"
            params = {
                "fsym": symbol,
                "tsyms": "USD",
                "api_key": self.api_key
            }

            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            return data.get("USD", 0)

        except Exception:
            return 0

# =============================================================================
# SIGNAL GENERATOR
# =============================================================================

class SignalGenerator:
    """Generate entry and exit signals"""

    def __init__(self, config: SwingConfig):
        self.config = config
        self.ta = TechnicalAnalysis()
        self.market = MarketData()

    def analyze_symbol(self, symbol: str) -> Optional[TradeSignal]:
        """Analyze a symbol for entry/exit signals"""

        # Get OHLCV data
        ohlcv = self.market.get_ohlcv(symbol, limit=100)
        if not ohlcv or not ohlcv.get("close"):
            return None

        closes = ohlcv["close"]
        volumes = ohlcv["volume"]
        current_price = closes[-1]

        # Calculate indicators
        rsi = self.ta.calculate_rsi(closes, period=14)
        ema_20 = self.ta.calculate_ema(closes, period=self.config.ema_period)
        avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
        volume_ratio = self.ta.calculate_volume_ratio(volumes[-1], avg_volume)

        # Check entry conditions
        reasons = []
        strength = 0
        signal_type = None

        # ENTRY SIGNAL: RSI oversold + Volume spike + Price above EMA
        if rsi < self.config.rsi_oversold:
            reasons.append(f"RSI oversold ({rsi:.1f})")
            strength += 35

        if volume_ratio >= self.config.volume_spike_multiplier:
            reasons.append(f"Volume spike ({volume_ratio:.1f}x)")
            strength += 35

        if current_price > ema_20:
            reasons.append(f"Price above EMA20 (${ema_20:.4f})")
            strength += 30

        # Strong entry signal if all conditions met
        if len(reasons) >= 2 and strength >= 65:
            signal_type = "entry"

        # EXIT SIGNAL: RSI overbought
        if rsi > self.config.rsi_overbought:
            signal_type = "exit"
            reasons = [f"RSI overbought ({rsi:.1f})"]
            strength = 80

        if not signal_type:
            return None

        return TradeSignal(
            symbol=symbol,
            signal_type=signal_type,
            direction="long",
            strength=strength,
            price=current_price,
            rsi=rsi,
            volume_ratio=volume_ratio,
            ema_20=ema_20,
            reasons=reasons,
            timestamp=datetime.now().isoformat()
        )

    def scan_watchlist(self) -> List[TradeSignal]:
        """Scan entire watchlist for signals"""
        signals = []

        for symbol in self.config.watchlist:
            signal = self.analyze_symbol(symbol)
            if signal:
                signals.append(signal)
            time.sleep(0.1)  # Rate limiting

        # Sort by strength
        signals.sort(key=lambda x: x.strength, reverse=True)
        return signals

# =============================================================================
# POSITION MANAGER
# =============================================================================

class PositionManager:
    """Manage open positions and risk"""

    def __init__(self, config: SwingConfig):
        self.config = config
        self.positions_file = PROJECT_ROOT / "memory" / "swing_positions.json"
        self.stats_file = PROJECT_ROOT / "memory" / "swing_stats.json"
        self.positions: List[Position] = []
        self.daily_stats: DailyStats = None
        self._load_state()

    def _load_state(self):
        """Load positions and stats from disk"""
        self.positions_file.parent.mkdir(exist_ok=True)

        if self.positions_file.exists():
            try:
                data = json.loads(self.positions_file.read_text())
                self.positions = [Position(**p) for p in data.get("positions", [])]
            except:
                self.positions = []

        today = datetime.now().strftime("%Y-%m-%d")
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text())
                if data.get("date") == today:
                    self.daily_stats = DailyStats(**data)
                else:
                    self.daily_stats = DailyStats(date=today)
            except:
                self.daily_stats = DailyStats(date=today)
        else:
            self.daily_stats = DailyStats(date=today)

    def _save_state(self):
        """Save positions and stats to disk"""
        positions_data = {
            "positions": [asdict(p) for p in self.positions],
            "updated": datetime.now().isoformat()
        }
        self.positions_file.write_text(json.dumps(positions_data, indent=2))
        self.stats_file.write_text(json.dumps(asdict(self.daily_stats), indent=2))

    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return [p for p in self.positions if p.status in ["open", "tp1_hit"]]

    def can_open_position(self) -> tuple[bool, str]:
        """Check if we can open a new position"""
        open_count = len(self.get_open_positions())

        if open_count >= self.config.max_positions:
            return False, f"Max positions reached ({open_count}/{self.config.max_positions})"

        if self.daily_stats.total_pnl <= -self.config.max_daily_loss_usd:
            return False, f"Daily loss limit reached (${self.daily_stats.total_pnl:.2f})"

        return True, "OK"

    def calculate_position_size(self, entry_price: float, stop_loss_price: float) -> tuple[float, float]:
        """
        Calculate position size based on risk
        Risk amount = Portfolio * risk_pct
        Position size = Risk amount / (entry - stop_loss)
        """
        risk_amount = self.config.portfolio_value * (self.config.risk_per_trade_pct / 100)
        risk_per_unit = entry_price - stop_loss_price

        if risk_per_unit <= 0:
            return 0, 0

        # Calculate quantity based on risk
        quantity = risk_amount / risk_per_unit
        position_value = quantity * entry_price

        # Cap at max position size
        if position_value > self.config.max_position_usd:
            position_value = self.config.max_position_usd
            quantity = position_value / entry_price

        return round(quantity, 8), round(position_value, 2)

    def open_position(self, signal: TradeSignal) -> Optional[Position]:
        """Open a new position based on signal"""
        can_open, reason = self.can_open_position()
        if not can_open:
            print(f"Cannot open position: {reason}")
            return None

        entry_price = signal.price
        stop_loss = entry_price * (1 - self.config.stop_loss_pct / 100)
        take_profit_1 = entry_price * (1 + self.config.take_profit_1_pct / 100)
        take_profit_2 = entry_price * (1 + self.config.take_profit_2_pct / 100)

        quantity, position_value = self.calculate_position_size(entry_price, stop_loss)

        if quantity <= 0:
            print("Position size too small")
            return None

        position = Position(
            id=f"SW{datetime.now().strftime('%Y%m%d%H%M%S')}",
            symbol=signal.symbol,
            entry_price=entry_price,
            entry_time=datetime.now().isoformat(),
            quantity=quantity,
            position_value=position_value,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2
        )

        self.positions.append(position)
        self.daily_stats.trades_opened += 1
        self._save_state()

        return position

    def check_position_exits(self, position: Position, current_price: float) -> Optional[str]:
        """Check if position should exit"""

        # Stop loss hit
        if current_price <= position.stop_loss:
            return "stop_loss"

        # TP1 hit (sell 50%)
        if not position.tp1_hit and current_price >= position.take_profit_1:
            return "tp1"

        # TP2 hit (sell remaining)
        if position.tp1_hit and current_price >= position.take_profit_2:
            return "tp2"

        return None

    def close_position(self, position: Position, exit_price: float, reason: str):
        """Close a position"""

        if reason == "tp1":
            # Partial close at TP1
            sell_quantity = position.quantity * (self.config.tp1_sell_pct / 100)
            position.remaining_quantity = position.quantity - sell_quantity
            position.tp1_hit = True
            position.status = "tp1_hit"

            # Calculate partial PnL
            partial_pnl = (exit_price - position.entry_price) * sell_quantity
            position.pnl += partial_pnl

            # Move stop loss to breakeven
            position.stop_loss = position.entry_price

        else:
            # Full close
            close_quantity = position.remaining_quantity if position.tp1_hit else position.quantity
            final_pnl = (exit_price - position.entry_price) * close_quantity
            position.pnl += final_pnl
            position.pnl_pct = (position.pnl / position.position_value) * 100
            position.exit_price = exit_price
            position.exit_time = datetime.now().isoformat()
            position.exit_reason = reason
            position.status = "closed" if reason in ["tp2", "rsi_exit", "manual"] else "stopped"
            position.remaining_quantity = 0

            # Update daily stats
            self.daily_stats.trades_closed += 1
            self.daily_stats.total_pnl += position.pnl

            if position.pnl > 0:
                self.daily_stats.wins += 1
                self.daily_stats.largest_win = max(self.daily_stats.largest_win, position.pnl)
            else:
                self.daily_stats.losses += 1
                self.daily_stats.largest_loss = min(self.daily_stats.largest_loss, position.pnl)

        self._save_state()
        return position

# =============================================================================
# SWING TRADE ENGINE
# =============================================================================

class SwingTradeEngine:
    """Main swing trade engine"""

    def __init__(self, config: SwingConfig = None):
        self.config = config or SwingConfig()
        self.signal_gen = SignalGenerator(self.config)
        self.position_mgr = PositionManager(self.config)
        self.market = MarketData()

    def scan_for_entries(self) -> List[TradeSignal]:
        """Scan watchlist for entry signals"""
        print(f"\n{'='*60}")
        print("SWING TRADE ENGINE - Entry Scanner")
        print(f"Mode: {self.config.mode.value.upper()}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        signals = self.signal_gen.scan_watchlist()
        entry_signals = [s for s in signals if s.signal_type == "entry"]

        if not entry_signals:
            print("\nNo entry signals found.")
            return []

        print(f"\n{'='*60}")
        print(f"ENTRY SIGNALS FOUND: {len(entry_signals)}")
        print(f"{'='*60}")

        for signal in entry_signals:
            print(f"\n{signal.symbol}")
            print(f"  Price: ${signal.price:,.6f}")
            print(f"  RSI: {signal.rsi:.1f}")
            print(f"  Volume: {signal.volume_ratio:.1f}x")
            print(f"  EMA20: ${signal.ema_20:,.6f}")
            print(f"  Strength: {signal.strength}/100")
            print(f"  Reasons: {', '.join(signal.reasons)}")

            # Calculate position sizing
            stop_loss = signal.price * (1 - self.config.stop_loss_pct / 100)
            qty, value = self.position_mgr.calculate_position_size(signal.price, stop_loss)

            print(f"  --- Position Sizing ---")
            print(f"  Size: {qty:.8f} ({signal.symbol})")
            print(f"  Value: ${value:.2f}")
            print(f"  Stop Loss: ${stop_loss:,.6f} (-{self.config.stop_loss_pct}%)")
            print(f"  TP1: ${signal.price * 1.30:,.6f} (+30%)")
            print(f"  TP2: ${signal.price * 1.75:,.6f} (+75%)")

        return entry_signals

    def monitor_positions(self):
        """Monitor open positions for exits"""
        print(f"\n{'='*60}")
        print("SWING TRADE ENGINE - Position Monitor")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        positions = self.position_mgr.get_open_positions()

        if not positions:
            print("\nNo open positions.")
            return

        print(f"\nOPEN POSITIONS: {len(positions)}")
        print("-" * 60)

        alerts = []

        for pos in positions:
            current_price = self.market.get_current_price(pos.symbol)
            if current_price <= 0:
                continue

            unrealized_pnl = (current_price - pos.entry_price) * pos.remaining_quantity
            unrealized_pct = ((current_price / pos.entry_price) - 1) * 100

            status_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
            tp1_marker = " [TP1 HIT]" if pos.tp1_hit else ""

            print(f"\n{status_emoji} {pos.symbol}{tp1_marker}")
            print(f"   Entry: ${pos.entry_price:,.6f}")
            print(f"   Current: ${current_price:,.6f}")
            print(f"   P&L: ${unrealized_pnl:+.2f} ({unrealized_pct:+.1f}%)")
            print(f"   Stop: ${pos.stop_loss:,.6f}")
            print(f"   TP1: ${pos.take_profit_1:,.6f} | TP2: ${pos.take_profit_2:,.6f}")

            # Check for exits
            exit_trigger = self.position_mgr.check_position_exits(pos, current_price)

            if exit_trigger:
                alerts.append({
                    "position": pos,
                    "trigger": exit_trigger,
                    "price": current_price
                })
                print(f"   ⚠️  EXIT TRIGGER: {exit_trigger.upper()}")

        return alerts

    def execute_paper_trade(self, signal: TradeSignal) -> Optional[Position]:
        """Execute a paper trade"""
        if self.config.mode != TradeMode.PAPER:
            print("Not in paper mode!")
            return None

        position = self.position_mgr.open_position(signal)

        if position:
            print(f"\n📝 PAPER TRADE OPENED")
            print(f"   ID: {position.id}")
            print(f"   Symbol: {position.symbol}")
            print(f"   Entry: ${position.entry_price:,.6f}")
            print(f"   Size: ${position.position_value:.2f}")
            print(f"   Stop: ${position.stop_loss:,.6f}")
            print(f"   TP1: ${position.take_profit_1:,.6f}")
            print(f"   TP2: ${position.take_profit_2:,.6f}")

            self._send_alert(f"Paper trade opened: {position.symbol} at ${position.entry_price:,.2f}")

        return position

    def show_status(self):
        """Show system status"""
        print(f"\n{'='*60}")
        print("SWING TRADE ENGINE - Status")
        print(f"{'='*60}")

        print(f"\n[CONFIG]")
        print(f"  Mode: {self.config.mode.value.upper()}")
        print(f"  Portfolio: ${self.config.portfolio_value:.2f}")
        print(f"  Risk/Trade: {self.config.risk_per_trade_pct}%")
        print(f"  Max Position: ${self.config.max_position_usd:.2f}")
        print(f"  Max Positions: {self.config.max_positions}")
        print(f"  Max Daily Loss: ${self.config.max_daily_loss_usd:.2f}")

        print(f"\n[ENTRY RULES]")
        print(f"  RSI Oversold: < {self.config.rsi_oversold}")
        print(f"  Volume Spike: > {self.config.volume_spike_multiplier}x")
        print(f"  Price above EMA{self.config.ema_period}")

        print(f"\n[EXIT RULES]")
        print(f"  Stop Loss: {self.config.stop_loss_pct}%")
        print(f"  TP1: {self.config.take_profit_1_pct}% (sell {self.config.tp1_sell_pct}%)")
        print(f"  TP2: {self.config.take_profit_2_pct}% (sell remaining)")
        print(f"  RSI Overbought: > {self.config.rsi_overbought}")

        print(f"\n[DAILY STATS]")
        stats = self.position_mgr.daily_stats
        print(f"  Date: {stats.date}")
        print(f"  Trades Opened: {stats.trades_opened}")
        print(f"  Trades Closed: {stats.trades_closed}")
        print(f"  Wins: {stats.wins} | Losses: {stats.losses}")
        print(f"  Total P&L: ${stats.total_pnl:+.2f}")

        print(f"\n[OPEN POSITIONS]")
        positions = self.position_mgr.get_open_positions()
        print(f"  Count: {len(positions)}/{self.config.max_positions}")
        for pos in positions:
            print(f"  - {pos.symbol}: ${pos.position_value:.2f} @ ${pos.entry_price:,.4f}")

        print(f"\n[WATCHLIST]")
        print(f"  {', '.join(self.config.watchlist)}")

    def _send_alert(self, message: str, voice: bool = True):
        """Send alert via ntfy + Aurora voice"""
        # Push notification
        try:
            requests.post(
                "https://ntfy.sh/sovereignshadow_dc4d2fa1",
                headers={
                    "Title": "Swing Trade Alert",
                    "Priority": "high",
                    "Tags": "chart_with_upwards_trend"
                },
                data=message.encode('utf-8'),
                timeout=5
            )
        except:
            pass

        # Aurora voice alert
        if voice:
            self._speak(message)

    def _speak(self, text: str):
        """Speak using Aurora voice"""
        try:
            import subprocess
            import tempfile

            # Load ElevenLabs key
            api_key = None
            env_path = PROJECT_ROOT / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("ELEVENLABS_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

            if not api_key:
                subprocess.run(["say", "-v", "Alex", text], capture_output=True)
                return

            from elevenlabs import ElevenLabs
            from elevenlabs.types import VoiceSettings

            client = ElevenLabs(api_key=api_key)
            audio = client.text_to_speech.convert(
                text=text,
                voice_id="cgSgspJ2msm6clMCkdW9",  # Aurora/Jessica
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.8,
                    style=0.6,
                    use_speaker_boost=True
                )
            )

            # Play Vegas sound first
            vegas = PROJECT_ROOT / "sounds" / "vegas_trap.mp3"
            if vegas.exists():
                subprocess.run(["afplay", str(vegas)], capture_output=True)

            # Then voice
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                for chunk in audio:
                    f.write(chunk)
                temp_path = f.name

            subprocess.run(["afplay", temp_path], capture_output=True)
            os.unlink(temp_path)

        except Exception as e:
            print(f"Voice error: {e}")

# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sovereign Shadow Swing Trade Engine")
    parser.add_argument("--scan", action="store_true", help="Scan for entry signals")
    parser.add_argument("--monitor", action="store_true", help="Monitor open positions")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--paper", action="store_true", help="Enable paper trade mode")
    parser.add_argument("--execute", type=str, help="Execute paper trade for symbol")
    parser.add_argument("--close", type=str, help="Close position by ID")
    parser.add_argument("--portfolio", type=float, default=500, help="Portfolio value")
    parser.add_argument("--daemon", action="store_true", help="Run continuous monitoring")

    args = parser.parse_args()

    # Create config
    config = SwingConfig(
        portfolio_value=args.portfolio,
        mode=TradeMode.PAPER if args.paper else TradeMode.SIGNAL
    )

    engine = SwingTradeEngine(config)

    if args.execute:
        # Execute paper trade
        if config.mode != TradeMode.PAPER:
            print("Add --paper flag to execute paper trades")
            return

        signal = engine.signal_gen.analyze_symbol(args.execute.upper())
        if signal and signal.signal_type == "entry":
            position = engine.execute_paper_trade(signal)
            if position:
                print(f"\n✅ Paper trade executed successfully!")
        else:
            print(f"No valid entry signal for {args.execute.upper()}")
            print("Running fresh scan...")
            signal = engine.signal_gen.analyze_symbol(args.execute.upper())
            if signal:
                print(f"Signal found: {signal.signal_type} - Strength: {signal.strength}")
            else:
                # Force create signal from current price for testing
                price = engine.market.get_current_price(args.execute.upper())
                if price > 0:
                    print(f"\nNo signal but creating test paper trade at ${price:,.4f}")
                    test_signal = TradeSignal(
                        symbol=args.execute.upper(),
                        signal_type="entry",
                        direction="long",
                        strength=50,
                        price=price,
                        rsi=50,
                        volume_ratio=1.0,
                        ema_20=price,
                        reasons=["Manual paper trade"],
                        timestamp=datetime.now().isoformat()
                    )
                    engine.execute_paper_trade(test_signal)

    elif args.close:
        # Close position manually
        positions = engine.position_mgr.get_open_positions()
        for pos in positions:
            if pos.id == args.close or pos.symbol == args.close.upper():
                price = engine.market.get_current_price(pos.symbol)
                engine.position_mgr.close_position(pos, price, "manual")
                print(f"Closed position {pos.id} at ${price:,.4f}")
                break
        else:
            print(f"Position not found: {args.close}")

    elif args.daemon:
        # Continuous monitoring
        print("Starting swing trade daemon... Press Ctrl+C to stop")
        while True:
            try:
                print(f"\n{'='*60}")
                print(f"SCAN @ {datetime.now().strftime('%H:%M:%S')}")

                # Scan for entries
                signals = engine.scan_for_entries()

                # Auto-execute in paper mode if strong signal
                if config.mode == TradeMode.PAPER and signals:
                    for sig in signals:
                        if sig.strength >= 80:
                            print(f"\n🎯 Strong signal! Auto-executing paper trade...")
                            engine.execute_paper_trade(sig)
                            break

                # Monitor positions
                alerts = engine.monitor_positions()

                # Process exit alerts in paper mode
                if config.mode == TradeMode.PAPER and alerts:
                    for alert in alerts:
                        pos = alert["position"]
                        trigger = alert["trigger"]
                        price = alert["price"]
                        print(f"\n⚡ Processing {trigger} for {pos.symbol}")
                        engine.position_mgr.close_position(pos, price, trigger)
                        engine._send_alert(f"{pos.symbol} {trigger} triggered at ${price:,.2f}")

                print(f"\nNext scan in 60 seconds...")
                time.sleep(60)

            except KeyboardInterrupt:
                print("\nDaemon stopped.")
                break

    elif args.status:
        engine.show_status()
    elif args.scan:
        signals = engine.scan_for_entries()
        if signals and config.mode == TradeMode.PAPER:
            print(f"\n💡 To paper trade the top signal, run:")
            print(f"   python strategies/swing_trade_engine.py --paper --execute {signals[0].symbol}")
    elif args.monitor:
        engine.monitor_positions()
    else:
        engine.show_status()
        print("\n" + "="*60)
        engine.scan_for_entries()
        print("\n" + "="*60)
        engine.monitor_positions()

if __name__ == "__main__":
    main()
