#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - TRADE JOURNAL
Comprehensive trade logging and analysis system

Philosophy: "Every trade is a lesson. Log it. Learn from it."
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TradeType(Enum):
    """Trade direction"""
    LONG = "long"
    SHORT = "short"


class TradeStatus(Enum):
    """Trade lifecycle status"""
    PLANNED = "planned"
    EXECUTED = "executed"
    STOPPED = "stopped"
    TARGET_HIT = "target_hit"
    MANUALLY_CLOSED = "manually_closed"
    CANCELLED = "cancelled"


class MistakeType(Enum):
    """Common trading mistakes"""
    NO_MISTAKE = "none"
    MOVED_STOP = "moved_stop_loss"
    NO_STOP = "no_stop_loss"
    WRONG_TIMEFRAME = "wrong_timeframe_alignment"
    TOO_MUCH_RISK = "risk_too_high"
    FOMO_ENTRY = "fomo_entry"
    REVENGE_TRADE = "revenge_trade"
    DIDNT_TAKE_PROFIT = "didnt_take_profit"
    CUT_WINNER = "cut_winner_early"


@dataclass
class TradeEntry:
    """Complete trade journal entry"""
    # Identification
    trade_id: str
    timestamp: str
    symbol: str
    trade_type: str  # long/short

    # Trade Plan
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    position_value: float
    risk_amount: float
    risk_percent: float
    risk_reward_ratio: float

    # Validation (from SHADE//AGENT)
    validation_passed: bool
    validation_checks: Dict[str, Any]
    shade_approved: bool

    # Psychology (from Psychology Tracker)
    emotion_before: str
    emotion_after: Optional[str] = None
    emotional_intensity: int = 5
    followed_system: bool = True

    # Market Context
    timeframe_4h_trend: str = "unknown"
    timeframe_15m_setup: str = "unknown"
    support_resistance_level: Optional[float] = None
    confluence_count: int = 0

    # Execution
    status: str = TradeStatus.PLANNED.value
    executed_at: Optional[str] = None
    actual_entry: Optional[float] = None
    actual_exit: Optional[float] = None
    exit_timestamp: Optional[str] = None

    # Results
    profitable: Optional[bool] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    actual_rr: Optional[float] = None
    held_duration_minutes: Optional[int] = None

    # Analysis
    mistakes: List[str] = None
    what_went_right: List[str] = None
    what_went_wrong: List[str] = None
    lessons_learned: Optional[str] = None
    tags: List[str] = None

    # Screenshots/Charts (file paths)
    chart_screenshot: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if self.mistakes is None:
            self.mistakes = []
        if self.what_went_right is None:
            self.what_went_right = []
        if self.what_went_wrong is None:
            self.what_went_wrong = []
        if self.tags is None:
            self.tags = []


class TradeJournal:
    """
    Comprehensive Trade Journal System

    Logs every trade with:
    - Full validation context
    - Emotional state
    - Market conditions
    - Outcomes and lessons
    """

    def __init__(self, journal_file: str = "logs/trading/trade_journal.json"):
        self.journal_file = Path(journal_file)
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)

        self.trades = self._load_trades()
        self.trade_counter = len(self.trades) + 1

        print("📔 TRADE JOURNAL initialized")
        print(f"   Total Trades: {len(self.trades)}")
        if self.trades:
            wins = len([t for t in self.trades if t.get("profitable")])
            print(f"   Win Rate: {wins/len(self.trades)*100:.1f}%")

    def _load_trades(self) -> List[Dict[str, Any]]:
        """Load existing trade journal"""
        if self.journal_file.exists():
            with open(self.journal_file) as f:
                return json.load(f)
        return []

    def _save_trades(self):
        """Save trade journal"""
        with open(self.journal_file, 'w') as f:
            json.dump(self.trades, f, indent=2)

    def create_trade_plan(
        self,
        symbol: str,
        trade_type: TradeType,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        validation_result: Dict[str, Any],
        psychology_state: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Create a new trade plan (before execution)

        Returns trade_id
        """
        trade_id = f"T{self.trade_counter:04d}"
        self.trade_counter += 1

        # Calculate trade metrics
        risk_amount = validation_result.get("position_sizing", {}).get("risk_amount", 0)
        risk_percent = validation_result.get("position_sizing", {}).get("risk_percent", 0)
        position_value = position_size * entry_price
        risk_reward = validation_result.get("position_sizing", {}).get("risk_reward_ratio", 0)

        # Create trade entry
        trade = TradeEntry(
            trade_id=trade_id,
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            trade_type=trade_type.value,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            position_value=position_value,
            risk_amount=risk_amount,
            risk_percent=risk_percent,
            risk_reward_ratio=risk_reward,
            validation_passed=validation_result.get("approved", False),
            validation_checks=validation_result.get("checks", {}),
            shade_approved=validation_result.get("approved", False),
            emotion_before=psychology_state.get("emotion", "neutral"),
            emotional_intensity=psychology_state.get("intensity", 5),
            followed_system=True,
            notes=notes
        )

        # Add market context if provided
        if market_context:
            trade.timeframe_4h_trend = market_context.get("trend_4h", "unknown")
            trade.timeframe_15m_setup = market_context.get("setup_15m", "unknown")
            trade.support_resistance_level = market_context.get("key_level")
            trade.confluence_count = market_context.get("confluences", 0)

        # Save trade
        self.trades.append(asdict(trade))
        self._save_trades()

        print(f"\n✅ Trade plan created: {trade_id}")
        print(f"   {symbol} {trade_type.value.upper()} @ ${entry_price:,.2f}")
        print(f"   Stop: ${stop_loss:,.2f} | Target: ${take_profit:,.2f}")
        print(f"   Risk: ${risk_amount:.2f} ({risk_percent:.1%}) | R:R: 1:{risk_reward:.1f}")

        return trade_id

    def execute_trade(
        self,
        trade_id: str,
        actual_entry: float,
        executed_at: Optional[str] = None
    ):
        """Mark trade as executed with actual entry price"""
        trade = self._find_trade(trade_id)
        if not trade:
            print(f"❌ Trade {trade_id} not found")
            return

        trade["status"] = TradeStatus.EXECUTED.value
        trade["executed_at"] = executed_at or datetime.now().isoformat()
        trade["actual_entry"] = actual_entry

        # Check for slippage
        slippage = abs(actual_entry - trade["entry_price"]) / trade["entry_price"]
        if slippage > 0.01:  # >1% slippage
            trade["tags"].append("high_slippage")
            print(f"⚠️  High slippage: {slippage:.2%}")

        self._save_trades()
        print(f"✅ Trade {trade_id} executed @ ${actual_entry:,.2f}")

    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        emotion_after: str,
        status: TradeStatus = TradeStatus.MANUALLY_CLOSED,
        mistakes: Optional[List[MistakeType]] = None,
        lessons_learned: Optional[str] = None
    ):
        """Close trade and record outcome"""
        trade = self._find_trade(trade_id)
        if not trade:
            print(f"❌ Trade {trade_id} not found")
            return

        # Use actual entry or planned entry
        entry = trade.get("actual_entry") or trade["entry_price"]

        # Calculate P&L
        if trade["trade_type"] == "long":
            profit_loss = (exit_price - entry) * trade["position_size"]
        else:  # short
            profit_loss = (entry - exit_price) * trade["position_size"]

        profit_loss_percent = profit_loss / trade["position_value"]
        profitable = profit_loss > 0

        # Calculate actual R:R
        if profitable:
            actual_rr = abs(profit_loss) / trade["risk_amount"]
        else:
            actual_rr = -abs(profit_loss) / trade["risk_amount"]

        # Calculate duration
        executed_time = datetime.fromisoformat(trade.get("executed_at") or trade["timestamp"])
        exit_time = datetime.now()
        duration = int((exit_time - executed_time).total_seconds() / 60)

        # Update trade
        trade["status"] = status.value
        trade["actual_exit"] = exit_price
        trade["exit_timestamp"] = exit_time.isoformat()
        trade["profitable"] = profitable
        trade["profit_loss"] = profit_loss
        trade["profit_loss_percent"] = profit_loss_percent
        trade["actual_rr"] = actual_rr
        trade["held_duration_minutes"] = duration
        trade["emotion_after"] = emotion_after

        # Log mistakes
        if mistakes:
            trade["mistakes"] = [m.value for m in mistakes]

        if lessons_learned:
            trade["lessons_learned"] = lessons_learned

        # Auto-analyze
        self._auto_analyze_trade(trade)

        self._save_trades()

        # Print summary
        print(f"\n{'🟢' if profitable else '🔴'} Trade {trade_id} closed")
        print(f"   P&L: ${profit_loss:+.2f} ({profit_loss_percent:+.2%})")
        print(f"   R:R: {actual_rr:+.2f}")
        print(f"   Duration: {duration} minutes")

    def _auto_analyze_trade(self, trade: Dict[str, Any]):
        """Automatically analyze trade and populate what went right/wrong"""
        # What went right
        if trade.get("profitable"):
            trade["what_went_right"].append("Trade was profitable")
        if trade.get("followed_system"):
            trade["what_went_right"].append("Followed the system")
        if trade.get("shade_approved"):
            trade["what_went_right"].append("SHADE//AGENT approved setup")
        if trade.get("actual_rr", 0) >= trade.get("risk_reward_ratio", 0):
            trade["what_went_right"].append("Hit or exceeded target R:R")

        # What went wrong
        if not trade.get("profitable"):
            trade["what_went_wrong"].append("Trade was unprofitable")
        if not trade.get("followed_system"):
            trade["what_went_wrong"].append("Did not follow system rules")
        if trade.get("mistakes"):
            for mistake in trade["mistakes"]:
                trade["what_went_wrong"].append(f"Mistake: {mistake}")

        # Add tags
        if trade.get("profitable"):
            trade["tags"].append("winner")
        else:
            trade["tags"].append("loser")

        if abs(trade.get("actual_rr", 0)) >= 2:
            trade["tags"].append("good_rr")

    def _find_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Find trade by ID"""
        for trade in self.trades:
            if trade["trade_id"] == trade_id:
                return trade
        return None

    def get_trade_statistics(self) -> Dict[str, Any]:
        """Calculate comprehensive trading statistics"""
        if not self.trades:
            return {"error": "No trades in journal"}

        closed_trades = [t for t in self.trades if t.get("profitable") is not None]
        if not closed_trades:
            return {"error": "No closed trades yet"}

        # Basic stats
        total = len(closed_trades)
        winners = [t for t in closed_trades if t["profitable"]]
        losers = [t for t in closed_trades if not t["profitable"]]
        win_rate = len(winners) / total

        # P&L stats
        total_pnl = sum(t["profit_loss"] for t in closed_trades)
        avg_win = sum(t["profit_loss"] for t in winners) / len(winners) if winners else 0
        avg_loss = sum(t["profit_loss"] for t in losers) / len(losers) if losers else 0
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        # R:R stats
        avg_rr = sum(abs(t.get("actual_rr", 0)) for t in winners) / len(winners) if winners else 0

        # Psychology stats
        emotion_distribution = {}
        for trade in closed_trades:
            emotion = trade.get("emotion_before", "unknown")
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1

        # Mistake analysis
        mistake_counts = {}
        for trade in closed_trades:
            for mistake in trade.get("mistakes", []):
                mistake_counts[mistake] = mistake_counts.get(mistake, 0) + 1

        # System adherence
        followed_system = [t for t in closed_trades if t.get("followed_system")]
        adherence_rate = len(followed_system) / total

        return {
            "total_trades": total,
            "winners": len(winners),
            "losers": len(losers),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
            "avg_rr": avg_rr,
            "system_adherence": adherence_rate,
            "emotion_distribution": emotion_distribution,
            "common_mistakes": mistake_counts,
            "best_trade": max(closed_trades, key=lambda t: t["profit_loss"]),
            "worst_trade": min(closed_trades, key=lambda t: t["profit_loss"])
        }

    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades"""
        return self.trades[-limit:][::-1]  # Reverse for newest first

    def find_patterns(self) -> Dict[str, Any]:
        """Identify trading patterns and insights"""
        closed = [t for t in self.trades if t.get("profitable") is not None]
        if len(closed) < 5:
            return {"message": "Need at least 5 closed trades for pattern analysis"}

        patterns = {}

        # Best/worst emotions
        emotion_performance = {}
        for trade in closed:
            emotion = trade.get("emotion_before", "unknown")
            if emotion not in emotion_performance:
                emotion_performance[emotion] = {"wins": 0, "losses": 0}

            if trade["profitable"]:
                emotion_performance[emotion]["wins"] += 1
            else:
                emotion_performance[emotion]["losses"] += 1

        # Calculate win rate per emotion
        for emotion, stats in emotion_performance.items():
            total = stats["wins"] + stats["losses"]
            stats["win_rate"] = stats["wins"] / total if total > 0 else 0

        patterns["emotion_performance"] = emotion_performance

        # Best/worst symbols
        symbol_performance = {}
        for trade in closed:
            symbol = trade["symbol"]
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {"wins": 0, "losses": 0}

            if trade["profitable"]:
                symbol_performance[symbol]["wins"] += 1
            else:
                symbol_performance[symbol]["losses"] += 1

        patterns["symbol_performance"] = symbol_performance

        # Timeframe alignment impact
        aligned = [t for t in closed if "aligned" in t.get("validation_checks", {}).get("timeframe", "")]
        if aligned:
            aligned_win_rate = len([t for t in aligned if t["profitable"]]) / len(aligned)
            patterns["timeframe_alignment_impact"] = {
                "aligned_trades": len(aligned),
                "aligned_win_rate": aligned_win_rate
            }

        return patterns

    def export_to_csv(self, output_file: str = "logs/trading/trade_journal.csv"):
        """Export journal to CSV for analysis"""
        import csv

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        closed_trades = [t for t in self.trades if t.get("profitable") is not None]

        with open(output_path, 'w', newline='') as f:
            if not closed_trades:
                print("No closed trades to export")
                return

            writer = csv.DictWriter(f, fieldnames=[
                "trade_id", "timestamp", "symbol", "trade_type",
                "entry_price", "exit_price", "position_size",
                "profit_loss", "profit_loss_percent", "actual_rr",
                "emotion_before", "followed_system", "mistakes"
            ])

            writer.writeheader()
            for trade in closed_trades:
                writer.writerow({
                    "trade_id": trade["trade_id"],
                    "timestamp": trade["timestamp"],
                    "symbol": trade["symbol"],
                    "trade_type": trade["trade_type"],
                    "entry_price": trade["entry_price"],
                    "exit_price": trade.get("actual_exit"),
                    "position_size": trade["position_size"],
                    "profit_loss": trade["profit_loss"],
                    "profit_loss_percent": trade["profit_loss_percent"],
                    "actual_rr": trade.get("actual_rr"),
                    "emotion_before": trade["emotion_before"],
                    "followed_system": trade["followed_system"],
                    "mistakes": ", ".join(trade.get("mistakes", []))
                })

        print(f"✅ Exported {len(closed_trades)} trades to {output_path}")


def demo():
    """Demo the trade journal"""
    journal = TradeJournal()

    print("\n" + "="*70)
    print("📔 TRADE JOURNAL DEMO")
    print("="*70)

    # Create sample trade plan
    trade_id = journal.create_trade_plan(
        symbol="BTC/USDT",
        trade_type=TradeType.LONG,
        entry_price=99000,
        stop_loss=97000,
        take_profit=103000,
        position_size=0.0166,
        validation_result={
            "approved": True,
            "checks": {"timeframe": "aligned", "risk": "acceptable"},
            "position_sizing": {
                "risk_amount": 33.20,
                "risk_percent": 0.02,
                "risk_reward_ratio": 2.0
            }
        },
        psychology_state={
            "emotion": "confident",
            "intensity": 5
        },
        market_context={
            "trend_4h": "bullish",
            "setup_15m": "pullback_bounce",
            "key_level": 98500,
            "confluences": 5
        },
        notes="Clean setup, 5 confluences, patient entry"
    )

    # Execute trade
    journal.execute_trade(trade_id, actual_entry=99100)

    # Close trade (winner)
    journal.close_trade(
        trade_id=trade_id,
        exit_price=103000,
        emotion_after="satisfied",
        status=TradeStatus.TARGET_HIT,
        lessons_learned="Patience paid off, waited for all confirmations"
    )

    # Get statistics
    print("\n" + "="*70)
    print("📊 JOURNAL STATISTICS")
    print("="*70)
    stats = journal.get_trade_statistics()
    if "error" not in stats:
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Win Rate: {stats['win_rate']:.1%}")
        print(f"Total P&L: ${stats['total_pnl']:,.2f}")
        print(f"Avg Win: ${stats['avg_win']:,.2f}")
        print(f"Avg Loss: ${stats['avg_loss']:,.2f}")
        print(f"Expectancy: ${stats['expectancy']:,.2f}")
        print(f"Avg R:R: {stats['avg_rr']:.2f}")
        print(f"System Adherence: {stats['system_adherence']:.1%}")

    print("="*70)


if __name__ == "__main__":
    demo()
