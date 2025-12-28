#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - MASTER TRADING SYSTEM
Unified interface integrating all trading components

Philosophy: "System over emotion. Every single time."
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import our agent systems (use relative imports for package compatibility)
try:
    from .shade_agent import ShadeAgent
    from .psychology_tracker import PsychologyTracker, EmotionState
    from .trade_journal import TradeJournal, TradeType, TradeStatus, MistakeType
    from .mentor_system import MentorSystem
except ImportError:
    # Fallback for direct execution
    from shade_agent import ShadeAgent
    from psychology_tracker import PsychologyTracker, EmotionState
    from trade_journal import TradeJournal, TradeType, TradeStatus, MistakeType
    from mentor_system import MentorSystem


class MasterTradingSystem:
    """
    Unified Trading System

    Integrates:
    - SHADE//AGENT: Strategy enforcement
    - Psychology Tracker: Emotion & discipline
    - Trade Journal: Logging & analysis
    - Mentor System: Learning progress

    This is the ONE interface for all trading decisions.
    """

    def __init__(self, account_balance: float = 1660.0):
        print("\n" + "="*70)
        print("🏴 SOVEREIGN SHADOW II - MASTER TRADING SYSTEM")
        print("   'System over emotion. Every single time.'")
        print("="*70)

        # Initialize all subsystems
        print("\n🔧 Initializing subsystems...")
        self.shade = ShadeAgent(account_balance=account_balance)
        self.psychology = PsychologyTracker()
        self.journal = TradeJournal()
        self.mentor = MentorSystem()

        self.account_balance = account_balance
        self.active_trades = []

        print("\n✅ All systems operational")
        print("="*70)

    def pre_trade_check(
        self,
        symbol: str,
        trade_type: str,  # "long" or "short"
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        emotion_state: str,  # Current emotion
        emotion_intensity: int,  # 1-10
        market_context: Dict[str, Any],
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete pre-trade validation workflow

        This runs through ALL checks before allowing a trade:
        1. Psychology check (3-strike rule, emotions)
        2. SHADE//AGENT validation (strategy, risk, R:R)
        3. Trade plan creation (if approved)

        Returns comprehensive result with:
        - approved: bool
        - trade_id: str (if approved)
        - reasons: List[str] (why approved/rejected)
        - warnings: List[str]
        """
        print("\n" + "="*70)
        print("🔍 PRE-TRADE CHECK INITIATED")
        print("="*70)
        print(f"Symbol: {symbol} {trade_type.upper()}")
        print(f"Entry: ${entry_price:,.2f} | Stop: ${stop_loss:,.2f} | Target: ${take_profit:,.2f}")
        print(f"Emotion: {emotion_state} (intensity: {emotion_intensity}/10)")

        reasons = []
        warnings = []
        approved = True

        # ====================
        # STEP 1: PSYCHOLOGY CHECK
        # ====================
        print("\n📍 STEP 1: Psychology Check...")

        # Check trading allowed
        psych_check = self.psychology.check_trading_allowed()
        if not psych_check["allowed"]:
            print(f"❌ {psych_check['reason']}")
            return {
                "approved": False,
                "trade_id": None,
                "reasons": [psych_check["reason"]],
                "warnings": [],
                "system": "psychology",
                "step_failed": 1
            }

        warnings.extend(psych_check.get("warnings", []))

        # Check emotion state
        emotion_check = self.psychology.log_pre_trade_emotion(
            emotion=EmotionState[emotion_state.upper()],
            intensity=emotion_intensity,
            notes=notes
        )

        if not emotion_check["should_trade"]:
            print(f"❌ Emotion Check Failed: {emotion_check['reason']}")
            return {
                "approved": False,
                "trade_id": None,
                "reasons": [f"Emotion check: {emotion_check['reason']}"],
                "warnings": warnings,
                "system": "psychology",
                "step_failed": 1
            }

        print(f"✅ Psychology: {emotion_check['recommendation']}")
        reasons.append(f"Psychology: {emotion_check['recommendation']}")

        # ====================
        # STEP 2: SHADE//AGENT VALIDATION
        # ====================
        print("\n📍 STEP 2: SHADE//AGENT Strategy Validation...")

        # Prepare trade for SHADE validation
        trade_data = {
            "symbol": symbol,
            "direction": trade_type,
            "entry": entry_price,
            "stop": stop_loss,
            "target": take_profit,
            "timeframe_4h": market_context.get("trend_4h", "unknown"),
            "timeframe_15m": market_context.get("setup_15m", "unknown"),
            "indicators": market_context.get("indicators", {}),
            "existing_positions": self.active_trades
        }

        validation = self.shade.validate_trade(trade_data)

        if not validation["approved"]:
            print(f"❌ SHADE//AGENT REJECTED: {validation['reason']}")
            print("\nFailed Checks:")
            for check, result in validation["checks"].items():
                if "❌" in result:
                    print(f"  {result}")

            return {
                "approved": False,
                "trade_id": None,
                "reasons": [f"SHADE rejection: {validation['reason']}"],
                "warnings": warnings,
                "validation_details": validation,
                "system": "shade_agent",
                "step_failed": 2
            }

        print("✅ SHADE//AGENT: Trade approved")
        for check, result in validation["checks"].items():
            print(f"  {result}")

        reasons.append("SHADE//AGENT: All checks passed")

        # ====================
        # STEP 3: CREATE TRADE PLAN
        # ====================
        print("\n📍 STEP 3: Creating Trade Plan...")

        trade_id = self.journal.create_trade_plan(
            symbol=symbol,
            trade_type=TradeType[trade_type.upper()],
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=validation["position_sizing"]["position_size"],
            validation_result=validation,
            psychology_state=emotion_check,
            market_context=market_context,
            notes=notes
        )

        # Track active trade
        self.active_trades.append({
            "trade_id": trade_id,
            "symbol": symbol,
            "position_value": validation["position_sizing"]["position_value"]
        })

        print("\n" + "="*70)
        print("✅ TRADE APPROVED - READY FOR EXECUTION")
        print("="*70)
        print(f"\nTrade ID: {trade_id}")
        print(f"Position Size: {validation['position_sizing']['position_size']:.4f} coins")
        print(f"Position Value: ${validation['position_sizing']['position_value']:,.2f}")
        print(f"Risk: ${validation['position_sizing']['risk_amount']:.2f} ({validation['position_sizing']['risk_percent']:.1%})")
        print(f"R:R: 1:{validation['position_sizing']['risk_reward_ratio']:.1f}")

        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")

        print("\n" + "="*70)

        return {
            "approved": True,
            "trade_id": trade_id,
            "reasons": reasons,
            "warnings": warnings,
            "validation": validation,
            "psychology": emotion_check,
            "position_sizing": validation["position_sizing"]
        }

    def execute_trade(self, trade_id: str, actual_entry: float):
        """Execute approved trade"""
        print(f"\n🚀 Executing trade {trade_id}...")
        self.journal.execute_trade(trade_id, actual_entry)
        print("✅ Trade executed and logged")

    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        emotion_after: str,
        status: str = "manually_closed",  # "target_hit", "stopped", "manually_closed"
        mistakes: Optional[List[str]] = None,
        lessons_learned: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close trade and update all systems

        Returns:
        - Psychology update (lockout status, warnings)
        - Trade statistics
        - Lessons learned
        """
        print(f"\n🔚 Closing trade {trade_id}...")

        # Close in journal
        status_enum = TradeStatus[status.upper()]
        mistakes_enum = [MistakeType[m.upper()] for m in mistakes] if mistakes else None

        self.journal.close_trade(
            trade_id=trade_id,
            exit_price=exit_price,
            emotion_after=emotion_after,
            status=status_enum,
            mistakes=mistakes_enum,
            lessons_learned=lessons_learned
        )

        # Get trade result
        trade = self.journal._find_trade(trade_id)
        profitable = trade.get("profitable", False)

        # Update psychology
        psych_result = self.psychology.log_trade_outcome(
            profitable=profitable,
            profit_loss=trade.get("profit_loss", 0),
            emotion_before=EmotionState[trade["emotion_before"].upper()],
            emotion_after=EmotionState[emotion_after.upper()],
            followed_system=not bool(mistakes),
            notes=lessons_learned
        )

        # Remove from active trades
        self.active_trades = [t for t in self.active_trades if t["trade_id"] != trade_id]

        result = {
            "trade_id": trade_id,
            "profitable": profitable,
            "profit_loss": trade.get("profit_loss"),
            "psychology": {
                "lockout_triggered": psych_result["lockout_triggered"],
                "trading_allowed": psych_result["trading_allowed"],
                "warnings": psych_result["warnings"]
            },
            "lessons": lessons_learned
        }

        # Show lockout message if triggered
        if psych_result["lockout_triggered"]:
            print("\n🔴 WARNING: Trading lockout triggered!")
            print("You are done for today. Review your trades and come back tomorrow.")

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "account_balance": self.account_balance,
            "psychology": self.psychology.get_psychology_report(),
            "journal_stats": self.journal.get_trade_statistics() if self.journal.trades else {},
            "mentor_progress": self.mentor.get_progress_summary(),
            "active_trades": len(self.active_trades),
            "total_exposure": sum(t["position_value"] for t in self.active_trades)
        }

    def display_dashboard(self):
        """Display comprehensive trading dashboard"""
        status = self.get_system_status()

        print("\n" + "="*70)
        print("📊 SOVEREIGN SHADOW II - TRADING DASHBOARD")
        print("="*70)

        # Account
        print(f"\n💰 ACCOUNT")
        print(f"   Balance: ${status['account_balance']:,.2f}")
        print(f"   Active Trades: {status['active_trades']}")
        print(f"   Total Exposure: ${status['total_exposure']:,.2f}")

        # Psychology
        psych = status["psychology"]
        print(f"\n🧠 PSYCHOLOGY")
        trading_status = "🟢 ALLOWED" if psych["trading_status"]["allowed"] else "🔴 LOCKED OUT"
        print(f"   Status: {trading_status}")
        print(f"   Trades Today: {psych['daily_stats']['trades']}")
        print(f"   3-Strike Rule: {psych['strike_rule']['losses']} ({psych['strike_rule']['strikes_remaining']} remaining)")
        print(f"   Dominant Emotion: {psych['emotional_state']['dominant']}")

        if psych['warnings']:
            print(f"\n   ⚠️  Warnings:")
            for warning in psych['warnings']:
                print(f"      {warning}")

        # Journal Stats
        if status['journal_stats']:
            stats = status['journal_stats']
            if "error" not in stats:
                print(f"\n📔 TRADING JOURNAL")
                print(f"   Total Trades: {stats['total_trades']}")
                print(f"   Win Rate: {stats['win_rate']:.1%}")
                print(f"   Total P&L: ${stats['total_pnl']:,.2f}")
                print(f"   Expectancy: ${stats['expectancy']:,.2f}")
                print(f"   System Adherence: {stats['system_adherence']:.1%}")

        # Mentor Progress
        mentor = status["mentor_progress"]
        print(f"\n🎓 LEARNING PROGRESS")
        print(f"   Chapter: {mentor['current_chapter']}")
        print(f"   Progress: {mentor['total_progress']}")
        print(f"   Paper Trades: {mentor['paper_trading']['trades']}")
        print(f"   Next Lesson: {mentor['next_lesson']}")

        print("\n" + "="*70)


def demo():
    """Demo the complete system"""
    system = MasterTradingSystem(account_balance=1660.0)

    # Show initial dashboard
    system.display_dashboard()

    # Scenario 1: Good trade that passes all checks
    print("\n" + "="*70)
    print("🧪 DEMO SCENARIO 1: Good Trade (Should APPROVE)")
    print("="*70)

    result = system.pre_trade_check(
        symbol="BTC/USDT",
        trade_type="long",
        entry_price=99000,
        stop_loss=97000,
        take_profit=103000,
        emotion_state="confident",
        emotion_intensity=5,
        market_context={
            "trend_4h": "bullish",
            "setup_15m": "pullback_bounce",
            "key_level": 98500,
            "confluences": 5,
            "indicators": {
                "ema_21": "above",
                "ema_50": "above",
                "ema_200": "above",
                "rsi": 55,
                "volume": "increasing"
            }
        },
        notes="Clean 5-confluence setup"
    )

    if result["approved"]:
        # Execute trade
        system.execute_trade(result["trade_id"], actual_entry=99100)

        # Simulate trade hitting target
        system.close_trade(
            trade_id=result["trade_id"],
            exit_price=103000,
            emotion_after="satisfied",
            status="target_hit",
            lessons_learned="Patience and discipline paid off"
        )

    # Scenario 2: Bad emotional state (Should REJECT)
    print("\n" + "="*70)
    print("🧪 DEMO SCENARIO 2: Revenge Trading (Should REJECT)")
    print("="*70)

    result = system.pre_trade_check(
        symbol="BTC/USDT",
        trade_type="long",
        entry_price=99000,
        stop_loss=97000,
        take_profit=103000,
        emotion_state="revenge",
        emotion_intensity=9,
        market_context={
            "trend_4h": "bullish",
            "setup_15m": "pullback_bounce",
            "key_level": 98500,
            "confluences": 5,
            "indicators": {
                "ema_21": "above",
                "ema_50": "above",
                "ema_200": "above",
                "rsi": 55,
                "volume": "increasing"
            }
        },
        notes="Want to get back last loss"
    )

    # Show final dashboard
    system.display_dashboard()

    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    demo()
