#!/usr/bin/env python3
"""
🤖 UNIFIED AUTONOMOUS TRADING SYSTEM
Combines the best of all 3 systems into one cohesive engine

Architecture:
1. Advanced Ray Score Engine (System 1 - 5-factor scoring)
2. Autonomous Trading Loop (System 3 - 24/7 cycle)
3. Safety Rules (System 1 - Re-enabled and enforced)
4. Brutal Critic (System 1 - Final validation)

This is the spine you've been building across 3 systems.
Now it's all in one place.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add local modules to path
sys.path.insert(0, str(Path(__file__).parent / "ladder_systems" / ">--LadderEngine--cloud< 2"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UnifiedSystem")


class SafetyRules:
    """
    Re-enabled safety system with proper enforcement
    """
    def __init__(self, total_capital: float = 1660.0):
        self.total_capital = total_capital

        # Capital allocation
        self.ledger_vault = 6600.0  # NEVER touched by automation
        self.active_capital = total_capital  # Coinbase active trading

        # Risk limits
        self.max_position_size_pct = 0.25  # 25% max per trade
        self.max_position_size_usd = self.active_capital * self.max_position_size_pct
        self.daily_loss_limit = 100.0  # $100 max daily loss
        self.weekly_loss_limit = 500.0  # $500 max weekly loss
        self.emergency_stop_loss = 1000.0  # Emergency circuit breaker

        # Trading phases
        self.phases = {
            "phase_1_paper": {"duration_days": 14, "max_risk": 0, "description": "Paper trading only"},
            "phase_2_micro": {"duration_days": 7, "max_risk": 100, "description": "Test with $100"},
            "phase_3_small": {"duration_days": 14, "max_risk": 500, "description": "Scale to $500"},
            "phase_4_production": {"duration_days": 365, "max_risk": 415, "description": "Full production"}
        }

        self.current_phase = "phase_2_micro"  # Start conservative

        # Performance tracking
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.total_pnl = 0.0
        self.last_reset_daily = datetime.now().date()
        self.last_reset_weekly = self._get_week_start()
        self.emergency_stop_active = False

        logger.info(f"🛡️ Safety Rules initialized - Active capital: ${self.active_capital:,.2f}")
        logger.info(f"   Current phase: {self.current_phase}")
        logger.info(f"   Max position: ${self.max_position_size_usd:.2f} ({self.max_position_size_pct*100}%)")
        logger.info(f"   Ledger vault: ${self.ledger_vault:,.2f} (PROTECTED)")

    def _get_week_start(self):
        today = datetime.now().date()
        return today - timedelta(days=today.weekday())

    def reset_daily_if_needed(self):
        """Reset daily counters at start of new day"""
        today = datetime.now().date()
        if today > self.last_reset_daily:
            logger.info(f"📅 New trading day - Yesterday's P&L: ${self.daily_pnl:.2f}")
            self.daily_pnl = 0.0
            self.last_reset_daily = today

    def reset_weekly_if_needed(self):
        """Reset weekly counters at start of new week"""
        week_start = self._get_week_start()
        if week_start > self.last_reset_weekly:
            logger.info(f"📅 New trading week - Last week's P&L: ${self.weekly_pnl:.2f}")
            self.weekly_pnl = 0.0
            self.last_reset_weekly = week_start

    def validate_trade(self, amount_usd: float, symbol: str) -> tuple[bool, str]:
        """
        Validate if trade meets all safety criteria
        Returns: (approved, reason)
        """
        # Emergency stop check
        if self.emergency_stop_active:
            return False, "🚨 EMERGENCY STOP ACTIVE"

        # Check if Ledger funds
        if "ledger" in symbol.lower():
            return False, "🔒 LEDGER FUNDS PROTECTED - Never auto-traded"

        # Phase-specific risk limits
        phase_max_risk = self.phases[self.current_phase]["max_risk"]
        if amount_usd > phase_max_risk:
            return False, f"⛔ Trade size ${amount_usd:.2f} exceeds phase limit ${phase_max_risk}"

        # Position size check
        if amount_usd > self.max_position_size_usd:
            return False, f"⛔ Trade size ${amount_usd:.2f} exceeds max ${self.max_position_size_usd:.2f}"

        # Daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit:
            return False, f"⛔ Daily loss limit reached: ${self.daily_pnl:.2f}"

        # Weekly loss limit
        if self.weekly_pnl <= -self.weekly_loss_limit:
            return False, f"⛔ Weekly loss limit reached: ${self.weekly_pnl:.2f}"

        # Emergency circuit breaker
        if self.total_pnl <= -self.emergency_stop_loss:
            self.emergency_stop_active = True
            return False, f"🚨 EMERGENCY STOP - Total loss: ${self.total_pnl:.2f}"

        return True, "✅ Trade approved"

    def record_trade_result(self, pnl_usd: float):
        """Record trade result and update P&L tracking"""
        self.daily_pnl += pnl_usd
        self.weekly_pnl += pnl_usd
        self.total_pnl += pnl_usd

        logger.info(f"💰 Trade result recorded: ${pnl_usd:+.2f}")
        logger.info(f"   Daily P&L: ${self.daily_pnl:+.2f}")
        logger.info(f"   Weekly P&L: ${self.weekly_pnl:+.2f}")
        logger.info(f"   Total P&L: ${self.total_pnl:+.2f}")


class BrutalCritic:
    """
    Final validation layer - "Better to miss 10 good trades than take 1 bad one"
    """
    def __init__(self):
        self.rejection_count = 0
        self.approval_count = 0
        logger.info("👹 Brutal Critic initialized - Assume every trade is bad until proven otherwise")

    def validate(self, signal: Dict[str, Any], ray_score: float, safety_approved: bool) -> tuple[bool, str, int]:
        """
        Final brutal validation
        Returns: (approved, reasoning, risk_rating_0_to_10)
        """
        risk_rating = 0
        fatal_flaws = []
        warnings = []

        # Fatal Flaw #1: Safety not approved
        if not safety_approved:
            fatal_flaws.append("Safety rules rejected trade")
            risk_rating += 10

        # Fatal Flaw #2: Low Ray Score
        if ray_score < 60:
            fatal_flaws.append(f"Ray Score too low: {ray_score:.1f}/100")
            risk_rating += 3
        elif ray_score < 75:
            warnings.append(f"Ray Score marginal: {ray_score:.1f}/100")
            risk_rating += 1

        # Fatal Flaw #3: No stop loss defined
        if not signal.get('sl_price') and not signal.get('stop_loss'):
            fatal_flaws.append("No stop loss defined")
            risk_rating += 3

        # Fatal Flaw #4: Poor risk/reward ratio
        entry = signal.get('entry_price') or signal.get('price', 0)
        tp = signal.get('tp1_price') or signal.get('take_profit')
        sl = signal.get('sl_price') or signal.get('stop_loss')

        if entry and tp and sl:
            reward = abs(tp - entry)
            risk = abs(entry - sl)
            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio < 1.5:
                    fatal_flaws.append(f"Poor R:R ratio: {rr_ratio:.2f}:1")
                    risk_rating += 2
        else:
            warnings.append("Incomplete price data for R:R calculation")
            risk_rating += 1

        # Warning: Low confidence
        confidence = signal.get('confidence', 0)
        if confidence < 70:
            warnings.append(f"Low confidence: {confidence}/100")
            risk_rating += 1

        # Warning: Unknown source
        source = signal.get('source', 'unknown')
        if source in ['unknown', 'mock', 'mock_generator']:
            warnings.append(f"Untrusted source: {source}")
            risk_rating += 1

        # Verdict
        risk_rating = min(10, risk_rating)

        if fatal_flaws:
            self.rejection_count += 1
            reasoning = f"⛔ REJECTED (Risk: {risk_rating}/10)\n"
            reasoning += "Fatal flaws:\n"
            for flaw in fatal_flaws:
                reasoning += f"  • {flaw}\n"
            if warnings:
                reasoning += "Warnings:\n"
                for warning in warnings:
                    reasoning += f"  • {warning}\n"
            return False, reasoning, risk_rating

        if risk_rating >= 5:
            self.rejection_count += 1
            reasoning = f"⚠️ HIGH RISK - REJECTED (Risk: {risk_rating}/10)\n"
            reasoning += "Concerns:\n"
            for warning in warnings:
                reasoning += f"  • {warning}\n"
            return False, reasoning, risk_rating

        self.approval_count += 1
        reasoning = f"✅ APPROVED (Risk: {risk_rating}/10)\n"
        if warnings:
            reasoning += "Minor concerns:\n"
            for warning in warnings:
                reasoning += f"  • {warning}\n"

        return True, reasoning, risk_rating

    def get_stats(self) -> Dict[str, int]:
        total = self.approval_count + self.rejection_count
        return {
            "total_reviews": total,
            "approvals": self.approval_count,
            "rejections": self.rejection_count,
            "rejection_rate": (self.rejection_count / total * 100) if total > 0 else 0
        }


class UnifiedAutonomousSystem:
    """
    The complete autonomous trading system
    Combines all pieces into one cohesive engine
    """
    def __init__(
        self,
        mode: str = 'paper',
        active_capital: float = 1660.0,
        cycle_interval_seconds: int = 600  # 10 minutes
    ):
        self.mode = mode
        self.cycle_interval = cycle_interval_seconds
        self.running = False

        # Initialize components
        self.safety = SafetyRules(total_capital=active_capital)
        self.brutal_critic = BrutalCritic()

        # Import Ray Score Engine from local system
        try:
            from ray_score_engine import RayScoreEngine
            self.ray_score_engine = RayScoreEngine()
            logger.info("✅ Advanced Ray Score Engine loaded (5-factor)")
        except ImportError:
            logger.warning("⚠️ Could not import advanced Ray Score Engine - using simplified version")
            self.ray_score_engine = None

        # State tracking
        self.cycle_count = 0
        self.total_signals = 0
        self.total_approved = 0
        self.total_rejected = 0

        logger.info("="*70)
        logger.info("🤖 UNIFIED AUTONOMOUS SYSTEM INITIALIZED")
        logger.info("="*70)
        logger.info(f"Mode: {mode}")
        logger.info(f"Cycle interval: {cycle_interval_seconds}s ({cycle_interval_seconds/60:.1f} min)")
        logger.info("="*70)

    def calculate_ray_score(self, signal: Dict[str, Any]) -> float:
        """Calculate Ray Score using advanced engine if available"""
        if self.ray_score_engine:
            # Use advanced 5-factor Ray Score Engine
            components = self.ray_score_engine.calculate_ray_score(signal)
            return components.total_score
        else:
            # Fallback to simplified scoring
            score = 0.0
            score += signal.get('confidence', 50) * 0.4
            score += 20 if signal.get('source') in ['verified', 'premium'] else 10
            score += 20 if signal.get('tp1_price') and signal.get('sl_price') else 10
            score += 10
            return min(100, score)

    async def process_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Process a trading signal through the complete pipeline

        Pipeline:
        1. Calculate Ray Score (5-factor technical analysis)
        2. Validate safety rules (capital protection)
        3. Brutal critic review (final quality check)
        4. Execute if all pass
        """
        symbol = signal.get('symbol', 'Unknown')
        action = signal.get('action', 'hold')

        logger.info(f"\n{'='*70}")
        logger.info(f"📊 PROCESSING SIGNAL: {symbol} {action.upper()}")
        logger.info(f"{'='*70}")

        self.total_signals += 1

        # Step 1: Ray Score calculation
        logger.info("\n🧮 STEP 1: Ray Score Calculation")
        ray_score = self.calculate_ray_score(signal)
        logger.info(f"   Ray Score: {ray_score:.1f}/100")

        if ray_score < 60:
            logger.info(f"   ❌ Rejected: Below threshold (60)")
            self.total_rejected += 1
            return False

        # Step 2: Safety validation
        logger.info("\n🛡️ STEP 2: Safety Rules Validation")
        amount = signal.get('position_size_usd', 100.0)
        safety_approved, safety_reason = self.safety.validate_trade(amount, symbol)
        logger.info(f"   {safety_reason}")

        # Step 3: Brutal Critic final review
        logger.info("\n👹 STEP 3: Brutal Critic Review")
        critic_approved, critic_reasoning, risk_rating = self.brutal_critic.validate(
            signal, ray_score, safety_approved
        )
        logger.info(f"{critic_reasoning}")

        # Final verdict
        if not critic_approved:
            logger.info(f"\n❌ SIGNAL REJECTED")
            logger.info(f"{'='*70}")
            self.total_rejected += 1
            return False

        logger.info(f"\n✅ SIGNAL APPROVED FOR EXECUTION")
        logger.info(f"   Ray Score: {ray_score:.1f}/100")
        logger.info(f"   Risk Rating: {risk_rating}/10")
        logger.info(f"   Mode: {self.mode.upper()}")
        logger.info(f"{'='*70}")

        self.total_approved += 1

        # TODO: Execute trade (implement exchange connector)
        if self.mode == 'live':
            logger.warning("⚠️ LIVE TRADING NOT YET IMPLEMENTED - Would execute here")
        else:
            logger.info("📝 Paper mode - Trade logged but not executed")

        return True

    def get_mock_signals(self) -> List[Dict[str, Any]]:
        """Generate mock trading signals for testing"""
        import random

        signals = []
        num_signals = random.randint(1, 3)

        for i in range(num_signals):
            price = random.uniform(50, 200)
            signal = {
                'symbol': random.choice(['SOL/USDT', 'ETH/USDT', 'BTC/USDT']),
                'action': 'buy',
                'entry_price': price,
                'tp1_price': price * 1.02,  # 2% TP
                'sl_price': price * 0.97,  # 3% SL
                'confidence': random.randint(50, 95),
                'source': random.choice(['verified', 'mock_generator', 'premium']),
                'position_size_usd': random.uniform(50, 200),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            signals.append(signal)

        return signals

    async def run_cycle(self):
        """Execute one complete trading cycle"""
        self.cycle_count += 1
        cycle_start = datetime.now(timezone.utc)

        logger.info(f"\n{'='*70}")
        logger.info(f"🔄 CYCLE #{self.cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"{'='*70}")

        # Reset daily/weekly counters if needed
        self.safety.reset_daily_if_needed()
        self.safety.reset_weekly_if_needed()

        # Fetch signals (currently mock - replace with real signal source)
        logger.info("\n📡 Fetching trading signals...")
        signals = self.get_mock_signals()
        logger.info(f"   Found {len(signals)} signals")

        # Process each signal
        approved_count = 0
        for signal in signals:
            approved = await self.process_signal(signal)
            if approved:
                approved_count += 1

        # Cycle summary
        cycle_duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ CYCLE #{self.cycle_count} COMPLETE ({cycle_duration:.1f}s)")
        logger.info(f"{'='*70}")
        logger.info(f"Signals processed: {len(signals)}")
        logger.info(f"Approved: {approved_count}")
        logger.info(f"Rejected: {len(signals) - approved_count}")
        logger.info(f"\nLifetime stats:")
        logger.info(f"  Total signals: {self.total_signals}")
        logger.info(f"  Approvals: {self.total_approved} ({self.total_approved/self.total_signals*100:.1f}%)")
        logger.info(f"  Rejections: {self.total_rejected} ({self.total_rejected/self.total_signals*100:.1f}%)")

        # Brutal Critic stats
        critic_stats = self.brutal_critic.get_stats()
        logger.info(f"\nBrutal Critic stats:")
        logger.info(f"  Total reviews: {critic_stats['total_reviews']}")
        logger.info(f"  Rejection rate: {critic_stats['rejection_rate']:.1f}%")
        logger.info(f"{'='*70}")

    async def run(self):
        """Main autonomous loop"""
        logger.info(f"\n{'='*70}")
        logger.info("🚀 STARTING UNIFIED AUTONOMOUS SYSTEM")
        logger.info(f"{'='*70}")
        logger.info("\nPress Ctrl+C to stop\n")

        self.running = True

        try:
            while self.running:
                await self.run_cycle()

                logger.info(f"\n⏳ Next cycle in {self.cycle_interval}s...\n")
                await asyncio.sleep(self.cycle_interval)

        except KeyboardInterrupt:
            logger.info("\n\n🛑 Shutdown requested by user")
            self.running = False

        except Exception as e:
            logger.error(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            self.running = False

        finally:
            logger.info(f"\n{'='*70}")
            logger.info("🛑 UNIFIED AUTONOMOUS SYSTEM STOPPED")
            logger.info(f"{'='*70}")
            logger.info(f"Total cycles: {self.cycle_count}")
            logger.info(f"Total signals: {self.total_signals}")
            logger.info(f"Total approved: {self.total_approved}")
            logger.info(f"Total rejected: {self.total_rejected}")
            logger.info(f"{'='*70}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Unified Autonomous Trading System')
    parser.add_argument(
        '--mode',
        choices=['paper', 'live'],
        default='paper',
        help='Trading mode (default: paper)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=1660.0,
        help='Active trading capital in USD (default: 1660)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=600,
        help='Cycle interval in seconds (default: 600 = 10 min)'
    )

    args = parser.parse_args()

    system = UnifiedAutonomousSystem(
        mode=args.mode,
        active_capital=args.capital,
        cycle_interval_seconds=args.interval
    )

    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
