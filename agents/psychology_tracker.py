#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - PSYCHOLOGY TRACKER
Emotion monitoring and discipline enforcement system

Philosophy: "The market doesn't care about your feelings. Neither should you."
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class EmotionState(Enum):
    """Trading emotions"""
    NEUTRAL = "neutral"
    FEAR = "fear"
    GREED = "greed"
    REVENGE = "revenge"
    FOMO = "fomo"
    HOPE = "hope"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"


class TradingBehavior(Enum):
    """Trading behavior patterns"""
    DISCIPLINED = "disciplined"
    IMPULSIVE = "impulsive"
    REVENGE_TRADING = "revenge_trading"
    OVERTRADING = "overtrading"
    FEAR_BASED = "fear_based"
    GREED_BASED = "greed_based"


@dataclass
class EmotionLog:
    """Single emotion log entry"""
    timestamp: str
    emotion: str
    intensity: int  # 1-10 scale
    trigger: str
    action_taken: str
    notes: Optional[str] = None


@dataclass
class DailyPsychology:
    """Daily psychology tracking"""
    date: str
    losses_today: int = 0
    wins_today: int = 0
    trades_today: int = 0
    locked_out: bool = False
    lockout_reason: Optional[str] = None
    dominant_emotion: str = EmotionState.NEUTRAL.value
    behaviors: List[str] = None
    emotion_logs: List[Dict] = None
    trading_allowed: bool = True

    def __post_init__(self):
        if self.behaviors is None:
            self.behaviors = []
        if self.emotion_logs is None:
            self.emotion_logs = []


class PsychologyTracker:
    """
    Trading Psychology Monitoring System

    Enforces:
    - 3-strike rule (stop after 3 losses)
    - Emotion logging
    - Revenge trading detection
    - FOMO pattern recognition
    - Overtrading prevention
    """

    def __init__(self, state_file: str = "logs/psychology/psychology_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.daily_state = self._load_or_create_daily_state()

        # Rules
        self.max_daily_losses = 3  # 3-strike rule
        self.max_daily_trades = 10  # Prevent overtrading
        self.min_time_between_trades = 15  # minutes
        self.revenge_trading_window = 30  # minutes (trade within 30min of loss = revenge?)

        print("🧠 PSYCHOLOGY TRACKER initialized")
        print(f"   Date: {self.daily_state.date}")
        print(f"   Losses: {self.daily_state.losses_today}/3")
        print(f"   Trades: {self.daily_state.trades_today}/{self.max_daily_trades}")
        print(f"   Status: {'🔴 LOCKED OUT' if self.daily_state.locked_out else '🟢 TRADING ALLOWED'}")

    def _load_or_create_daily_state(self) -> DailyPsychology:
        """Load or create today's psychology state"""
        today = datetime.now().date().isoformat()

        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)

                # Check if it's today's data
                if data.get("date") == today:
                    return DailyPsychology(**data)

        # New day or first time - create fresh state
        return DailyPsychology(date=today)

    def _save_state(self):
        """Save psychology state"""
        with open(self.state_file, 'w') as f:
            json.dump(asdict(self.daily_state), f, indent=2)

    def _archive_daily_state(self):
        """Archive today's state to history"""
        archive_file = self.state_file.parent / f"history/psychology_{self.daily_state.date}.json"
        archive_file.parent.mkdir(parents=True, exist_ok=True)

        with open(archive_file, 'w') as f:
            json.dump(asdict(self.daily_state), f, indent=2)

    def check_trading_allowed(self) -> Dict[str, Any]:
        """
        Check if user is allowed to trade

        Returns validation result with:
        - allowed: bool
        - reason: str (if not allowed)
        - warnings: List[str]
        """
        warnings = []

        # Check if locked out
        if self.daily_state.locked_out:
            return {
                "allowed": False,
                "reason": f"🔴 LOCKED OUT: {self.daily_state.lockout_reason}",
                "warnings": []
            }

        # Check 3-strike rule
        if self.daily_state.losses_today >= self.max_daily_losses:
            self._lockout("3-strike rule triggered (3 losses today)")
            return {
                "allowed": False,
                "reason": "🔴 3-STRIKE RULE: Stop trading for today",
                "warnings": []
            }

        # Check overtrading
        if self.daily_state.trades_today >= self.max_daily_trades:
            self._lockout("Overtrading prevention (10 trades today)")
            return {
                "allowed": False,
                "reason": "🔴 OVERTRADING: Maximum 10 trades per day",
                "warnings": []
            }

        # Warnings (not blocking, but concerning)
        if self.daily_state.losses_today == 2:
            warnings.append("⚠️  2 losses today - one more triggers 3-strike rule")

        if self.daily_state.trades_today >= 7:
            warnings.append("⚠️  High trade count - approaching daily limit")

        if self._detect_revenge_trading():
            warnings.append("⚠️  REVENGE TRADING DETECTED - Take a break")

        return {
            "allowed": True,
            "reason": None,
            "warnings": warnings
        }

    def _lockout(self, reason: str):
        """Lock out trading for the day"""
        self.daily_state.locked_out = True
        self.daily_state.lockout_reason = reason
        self.daily_state.trading_allowed = False
        self._save_state()
        self._archive_daily_state()

        print("\n" + "="*70)
        print("🔴 TRADING LOCKOUT ACTIVATED")
        print("="*70)
        print(f"Reason: {reason}")
        print("\nYou are DONE for today. Close the charts and walk away.")
        print("\nWhat to do now:")
        print("  1. Close your trading platform")
        print("  2. Review your trades (find the mistakes)")
        print("  3. Take a break (gym, walk, coffee)")
        print("  4. Come back tomorrow with fresh perspective")
        print("="*70)

    def log_trade_outcome(
        self,
        profitable: bool,
        profit_loss: float,
        emotion_before: EmotionState,
        emotion_after: EmotionState,
        followed_system: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log trade outcome and update psychology state

        Returns:
        - updated_state: DailyPsychology
        - lockout_triggered: bool
        - warnings: List[str]
        """
        self.daily_state.trades_today += 1

        if profitable:
            self.daily_state.wins_today += 1
        else:
            self.daily_state.losses_today += 1

        # Log emotions
        self._log_emotion(
            emotion=emotion_after,
            intensity=8 if not profitable else 5,
            trigger="trade_result",
            action_taken="logged_outcome",
            notes=notes
        )

        # Detect behavior patterns
        if not followed_system:
            self.daily_state.behaviors.append(TradingBehavior.IMPULSIVE.value)

        if self._detect_revenge_trading():
            self.daily_state.behaviors.append(TradingBehavior.REVENGE_TRADING.value)

        self._save_state()

        # Check if lockout triggered
        check = self.check_trading_allowed()

        return {
            "updated_state": self.daily_state,
            "lockout_triggered": self.daily_state.locked_out,
            "warnings": check.get("warnings", []),
            "trading_allowed": check["allowed"]
        }

    def _log_emotion(
        self,
        emotion: EmotionState,
        intensity: int,
        trigger: str,
        action_taken: str,
        notes: Optional[str] = None
    ):
        """Log an emotion entry"""
        log = EmotionLog(
            timestamp=datetime.now().isoformat(),
            emotion=emotion.value,
            intensity=min(max(intensity, 1), 10),  # Clamp 1-10
            trigger=trigger,
            action_taken=action_taken,
            notes=notes
        )

        self.daily_state.emotion_logs.append(asdict(log))
        self._update_dominant_emotion()

    def _update_dominant_emotion(self):
        """Calculate dominant emotion from recent logs"""
        if not self.daily_state.emotion_logs:
            return

        # Get last 5 emotions
        recent = self.daily_state.emotion_logs[-5:]
        emotion_counts = {}

        for log in recent:
            emotion = log["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Set dominant emotion
        if emotion_counts:
            self.daily_state.dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    def _detect_revenge_trading(self) -> bool:
        """Detect if user is revenge trading"""
        if self.daily_state.losses_today == 0:
            return False

        # Check if last trade was within revenge window of a loss
        if len(self.daily_state.emotion_logs) < 2:
            return False

        last_two = self.daily_state.emotion_logs[-2:]

        # Simple heuristic: if lost, then traded again within 30min
        # (Real implementation would check actual trade timestamps)
        return (
            TradingBehavior.REVENGE_TRADING.value in self.daily_state.behaviors
            or self.daily_state.dominant_emotion == EmotionState.REVENGE.value
        )

    def log_pre_trade_emotion(
        self,
        emotion: EmotionState,
        intensity: int,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log emotion BEFORE taking a trade

        Returns analysis of emotional state and recommendation
        """
        self._log_emotion(
            emotion=emotion,
            intensity=intensity,
            trigger="pre_trade",
            action_taken="logged",
            notes=notes
        )

        # Analyze if emotion is problematic
        dangerous_emotions = [
            EmotionState.REVENGE,
            EmotionState.FOMO,
            EmotionState.GREED,
            EmotionState.HOPE
        ]

        is_dangerous = emotion in dangerous_emotions
        high_intensity = intensity >= 7

        recommendation = "PROCEED" if not (is_dangerous or high_intensity) else "WAIT"

        if is_dangerous:
            reason = f"Dangerous emotion: {emotion.value.upper()}"
        elif high_intensity:
            reason = f"High intensity ({intensity}/10) - Not thinking clearly"
        else:
            reason = "Emotional state is acceptable"

        self._save_state()

        return {
            "emotion": emotion.value,
            "intensity": intensity,
            "recommendation": recommendation,
            "reason": reason,
            "should_trade": recommendation == "PROCEED"
        }

    def get_psychology_report(self) -> Dict[str, Any]:
        """Get comprehensive psychology report"""
        return {
            "date": self.daily_state.date,
            "trading_status": {
                "allowed": not self.daily_state.locked_out,
                "lockout_reason": self.daily_state.lockout_reason
            },
            "daily_stats": {
                "trades": self.daily_state.trades_today,
                "wins": self.daily_state.wins_today,
                "losses": self.daily_state.losses_today,
                "win_rate": f"{(self.daily_state.wins_today / max(self.daily_state.trades_today, 1) * 100):.1f}%"
            },
            "strike_rule": {
                "losses": f"{self.daily_state.losses_today}/3",
                "strikes_remaining": max(0, 3 - self.daily_state.losses_today)
            },
            "emotional_state": {
                "dominant": self.daily_state.dominant_emotion,
                "recent_logs": self.daily_state.emotion_logs[-5:] if self.daily_state.emotion_logs else []
            },
            "behaviors": {
                "detected": list(set(self.daily_state.behaviors)),
                "revenge_trading": self._detect_revenge_trading()
            },
            "warnings": self.check_trading_allowed().get("warnings", [])
        }

    def reset_daily_state(self):
        """Manually reset daily state (for testing or new day)"""
        self._archive_daily_state()
        self.daily_state = DailyPsychology(date=datetime.now().date().isoformat())
        self._save_state()
        print("✅ Daily psychology state reset")


def demo():
    """Demo the psychology tracker"""
    tracker = PsychologyTracker()

    print("\n" + "="*70)
    print("📊 DAILY PSYCHOLOGY REPORT")
    print("="*70)

    report = tracker.get_psychology_report()
    print(f"Date: {report['date']}")
    print(f"\nTrading Status: {'🟢 ALLOWED' if report['trading_status']['allowed'] else '🔴 LOCKED OUT'}")
    if report['trading_status']['lockout_reason']:
        print(f"Reason: {report['trading_status']['lockout_reason']}")

    print(f"\nDaily Stats:")
    print(f"  Trades: {report['daily_stats']['trades']}")
    print(f"  Wins: {report['daily_stats']['wins']}")
    print(f"  Losses: {report['daily_stats']['losses']}")
    print(f"  Win Rate: {report['daily_stats']['win_rate']}")

    print(f"\n3-Strike Rule:")
    print(f"  Losses: {report['strike_rule']['losses']}")
    print(f"  Strikes Remaining: {report['strike_rule']['strikes_remaining']}")

    print(f"\nEmotional State:")
    print(f"  Dominant: {report['emotional_state']['dominant']}")

    if report['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            print(f"  {warning}")

    # Test scenarios
    print("\n" + "="*70)
    print("🧪 TESTING SCENARIO: Pre-trade emotion check")
    print("="*70)

    # Scenario 1: Good emotional state
    result = tracker.log_pre_trade_emotion(
        emotion=EmotionState.CONFIDENT,
        intensity=5,
        notes="Following setup, patient entry"
    )
    print(f"\nScenario 1: CONFIDENT (intensity 5)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Should Trade: {result['should_trade']}")

    # Scenario 2: Revenge trading
    result = tracker.log_pre_trade_emotion(
        emotion=EmotionState.REVENGE,
        intensity=9,
        notes="Just lost last trade, want to get it back"
    )
    print(f"\nScenario 2: REVENGE (intensity 9)")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Should Trade: {result['should_trade']}")

    # Scenario 3: Simulate losing streak
    print("\n" + "="*70)
    print("🧪 TESTING SCENARIO: 3-Strike Rule")
    print("="*70)

    print("\nSimulating 3 consecutive losses...")
    for i in range(3):
        result = tracker.log_trade_outcome(
            profitable=False,
            profit_loss=-33.20,
            emotion_before=EmotionState.CONFIDENT,
            emotion_after=EmotionState.ANXIOUS if i < 2 else EmotionState.REVENGE,
            followed_system=True,
            notes=f"Loss #{i+1}"
        )
        print(f"\nLoss {i+1}:")
        print(f"  Losses: {result['updated_state'].losses_today}/3")
        print(f"  Lockout: {'🔴 YES' if result['lockout_triggered'] else '🟢 No'}")
        if result['warnings']:
            for warning in result['warnings']:
                print(f"  {warning}")

    # Try to trade after lockout
    print("\n" + "="*70)
    print("🧪 TESTING: Attempt to trade after lockout")
    print("="*70)
    check = tracker.check_trading_allowed()
    print(f"Allowed: {'✅ Yes' if check['allowed'] else '❌ No'}")
    if check['reason']:
        print(f"Reason: {check['reason']}")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo()
