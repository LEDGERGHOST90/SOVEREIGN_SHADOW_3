#!/usr/bin/env python3
"""
🪜 UNIFIED LADDER SYSTEM
Complete ladder trading architecture combining entry, exit, and profit extraction

Components:
1. Entry Ladder - Multi-tier buy orders (Sigma-Omega style)
2. TP/SL Ladder - Progressive take profit and stop loss
3. Profit Extraction - Tiered milestone siphoning
4. Ray Score Filtering - Cognitive validation
5. Vault Routing - 30% VAULT / 70% BUFFER

Integration:
- Shadow Sniper (Coinbase execution)
- Unified Profit Tracker (P&L aggregation)
- AAVE Monitor (health factor safety)
- Income Capital Tracker (true profit calculation)
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("unified_ladder")

@dataclass
class LadderTier:
    """Individual ladder tier"""
    tier: int
    price: float
    quantity: float
    weight_pct: float
    tier_type: str  # 'entry', 'tp', 'sl'
    status: str = 'pending'  # pending, filled, cancelled
    filled_at: Optional[str] = None
    filled_price: Optional[float] = None

@dataclass
class EntryLadder:
    """Entry ladder configuration (buy tiers)"""
    symbol: str
    entry_low: float  # Lowest entry price
    entry_high: float  # Highest entry price
    total_capital: float
    tier_count: int = 6
    tier_weights: List[float] = None  # [30%, 25%, 20%, 15%, 8%, 2%]

    def __post_init__(self):
        if self.tier_weights is None:
            # Default Sigma-Omega weights (heavier at lower prices)
            self.tier_weights = [0.30, 0.25, 0.20, 0.15, 0.08, 0.02]

@dataclass
class ExitLadder:
    """Exit ladder configuration (TP/SL tiers)"""
    tp1_price: float  # First take profit
    tp1_percent: float = 50.0  # Sell 50% at TP1
    tp2_price: float = None  # Second take profit
    tp2_percent: float = 30.0  # Sell 30% at TP2
    tp3_price: float = None  # Third take profit (moon)
    tp3_percent: float = 20.0  # Sell remaining 20% at TP3
    sl_price: float = None  # Stop loss
    sl_percent: float = 100.0  # Sell all at stop loss

class UnifiedLadderSystem:
    """
    Complete ladder trading system

    Workflow:
    1. Validate signal with Ray Score
    2. Deploy entry ladder (6 buy tiers)
    3. Monitor fills and adjust
    4. Deploy TP/SL exit ladder
    5. Calculate profit when closed
    6. Check extraction milestone
    7. Siphon to VAULT if milestone hit
    """

    def __init__(self):
        self.base_path = Path("/Volumes/LegacySafe/SOVEREIGN_SHADOW_3")
        self.logs_path = self.base_path / "logs" / "ladder_executions"
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Ray Score thresholds
        self.min_ray_score = 60.0
        self.min_tp1_roi = 20.0  # 20% minimum
        self.min_tp2_roi = 30.0  # 30% minimum
        self.max_drawdown = 7.0  # 7% maximum

        # Active ladders
        self.active_ladders = {}
        self.execution_history = []

        logger.info("🪜 Unified Ladder System initialized")

    def calculate_ray_score(self, signal: Dict[str, Any]) -> float:
        """
        Calculate Ray Score for signal validation

        Ray Score = weighted average of:
        - Entry quality (30%)
        - Risk/reward ratio (25%)
        - Market conditions (20%)
        - Technical indicators (15%)
        - Volume/liquidity (10%)

        Score > 60 = PASS
        Score < 60 = REJECT
        """
        try:
            entry_price = signal['entry_price']
            tp1 = signal['tp1_price']
            sl = signal.get('sl_price', entry_price * 0.93)  # Default 7% stop

            # Calculate risk/reward
            potential_gain = (tp1 - entry_price) / entry_price * 100
            potential_loss = (entry_price - sl) / entry_price * 100
            risk_reward = potential_gain / potential_loss if potential_loss > 0 else 0

            # Score components
            entry_quality = min(100, (potential_gain / 20) * 100)  # 20%+ = full score
            risk_reward_score = min(100, (risk_reward / 3) * 100)  # 3:1+ = full score
            market_score = 75  # TODO: Add market sentiment analysis
            technical_score = 70  # TODO: Add RSI, MACD, etc.
            volume_score = 80  # TODO: Add volume analysis

            # Weighted average
            ray_score = (
                entry_quality * 0.30 +
                risk_reward_score * 0.25 +
                market_score * 0.20 +
                technical_score * 0.15 +
                volume_score * 0.10
            )

            return round(ray_score, 2)

        except Exception as e:
            logger.error(f"Ray Score calculation failed: {e}")
            return 0.0

    def validate_signal(self, signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate trading signal before ladder deployment

        Returns:
            (is_valid, rejection_reasons)
        """
        rejection_reasons = []

        try:
            # Calculate Ray Score
            ray_score = self.calculate_ray_score(signal)
            signal['ray_score'] = ray_score

            if ray_score < self.min_ray_score:
                rejection_reasons.append(f"Ray Score {ray_score:.1f} < {self.min_ray_score}")

            # Validate ROI
            entry_price = signal['entry_price']
            tp1 = signal['tp1_price']
            tp2 = signal.get('tp2_price', tp1 * 1.10)
            sl = signal.get('sl_price', entry_price * 0.93)

            tp1_roi = (tp1 - entry_price) / entry_price * 100
            tp2_roi = (tp2 - entry_price) / entry_price * 100
            drawdown = (entry_price - sl) / entry_price * 100

            if tp1_roi < self.min_tp1_roi:
                rejection_reasons.append(f"TP1 ROI {tp1_roi:.1f}% < {self.min_tp1_roi}%")

            if tp2_roi < self.min_tp2_roi:
                rejection_reasons.append(f"TP2 ROI {tp2_roi:.1f}% < {self.min_tp2_roi}%")

            if drawdown > self.max_drawdown:
                rejection_reasons.append(f"Drawdown {drawdown:.1f}% > {self.max_drawdown}%")

            # Add metrics to signal
            signal['validation'] = {
                'ray_score': ray_score,
                'tp1_roi': tp1_roi,
                'tp2_roi': tp2_roi,
                'drawdown': drawdown,
                'risk_reward': tp1_roi / drawdown if drawdown > 0 else 0
            }

            is_valid = len(rejection_reasons) == 0

            if is_valid:
                logger.info(f"✅ Signal VALIDATED (Ray Score: {ray_score:.1f})")
            else:
                logger.warning(f"❌ Signal REJECTED: {', '.join(rejection_reasons)}")

            return is_valid, rejection_reasons

        except Exception as e:
            logger.error(f"Signal validation failed: {e}")
            return False, [f"Validation error: {str(e)}"]

    def create_entry_ladder(self, signal: Dict[str, Any], capital: float) -> List[LadderTier]:
        """
        Create 6-tier entry ladder

        Tiers are weighted toward lower prices (buy more when cheaper)
        """
        try:
            entry_low = signal.get('entry_low', signal['entry_price'] * 0.995)
            entry_high = signal.get('entry_high', signal['entry_price'] * 1.005)

            ladder = EntryLadder(
                symbol=signal['symbol'],
                entry_low=entry_low,
                entry_high=entry_high,
                total_capital=capital
            )

            tiers = []
            for i in range(ladder.tier_count):
                # Calculate tier price (bias toward lower)
                ratio = i / (ladder.tier_count - 1)
                curved_ratio = ratio ** 1.2  # Curve for lower bias
                price = entry_low + (entry_high - entry_low) * curved_ratio

                # Calculate allocation
                weight = ladder.tier_weights[i]
                tier_capital = capital * weight
                quantity = tier_capital / price

                tier = LadderTier(
                    tier=i + 1,
                    price=price,
                    quantity=quantity,
                    weight_pct=weight * 100,
                    tier_type='entry'
                )

                tiers.append(tier)

                logger.debug(f"Tier {i+1}: ${price:.4f} | {weight*100:.0f}% | {quantity:.4f} units")

            return tiers

        except Exception as e:
            logger.error(f"Entry ladder creation failed: {e}")
            return []

    def create_exit_ladder(self, signal: Dict[str, Any], entry_tiers: List[LadderTier]) -> List[LadderTier]:
        """
        Create TP/SL exit ladder

        Progressive profit taking + stop loss protection
        """
        try:
            tp1 = signal['tp1_price']
            tp2 = signal.get('tp2_price', tp1 * 1.10)
            tp3 = signal.get('tp3_price', tp1 * 1.25)
            sl = signal.get('sl_price', signal['entry_price'] * 0.93)

            # Calculate total filled quantity
            total_qty = sum(t.quantity for t in entry_tiers if t.status == 'filled')

            exit_tiers = []

            # TP1: Sell 50%
            exit_tiers.append(LadderTier(
                tier=1,
                price=tp1,
                quantity=total_qty * 0.50,
                weight_pct=50.0,
                tier_type='tp'
            ))

            # TP2: Sell 30%
            exit_tiers.append(LadderTier(
                tier=2,
                price=tp2,
                quantity=total_qty * 0.30,
                weight_pct=30.0,
                tier_type='tp'
            ))

            # TP3: Sell remaining 20%
            exit_tiers.append(LadderTier(
                tier=3,
                price=tp3,
                quantity=total_qty * 0.20,
                weight_pct=20.0,
                tier_type='tp'
            ))

            # Stop Loss: Emergency exit
            exit_tiers.append(LadderTier(
                tier=0,
                price=sl,
                quantity=total_qty,  # Sell ALL
                weight_pct=100.0,
                tier_type='sl'
            ))

            return exit_tiers

        except Exception as e:
            logger.error(f"Exit ladder creation failed: {e}")
            return []

    def deploy_ladder(self, signal: Dict[str, Any], capital: float,
                     mode: str = 'paper') -> Dict[str, Any]:
        """
        Deploy complete ladder system

        Args:
            signal: Trading signal with entry/tp/sl prices
            capital: Capital to allocate
            mode: 'paper' or 'live'

        Returns:
            Deployment result with ladder IDs
        """
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"🪜 DEPLOYING LADDER SYSTEM")
            logger.info(f"{'='*70}")

            # 1. Validate signal
            is_valid, rejection_reasons = self.validate_signal(signal)

            if not is_valid:
                return {
                    'success': False,
                    'status': 'rejected',
                    'reasons': rejection_reasons
                }

            # 2. Create entry ladder
            entry_tiers = self.create_entry_ladder(signal, capital)

            logger.info(f"\n📊 ENTRY LADDER ({len(entry_tiers)} tiers):")
            for tier in entry_tiers:
                logger.info(f"   Tier {tier.tier}: ${tier.price:.4f} | {tier.weight_pct:.0f}% | {tier.quantity:.4f} units")

            # 3. Simulate fills (in paper mode) or execute live
            if mode == 'paper':
                logger.info(f"\n📝 PAPER TRADING MODE - Simulating fills...")
                for tier in entry_tiers:
                    tier.status = 'filled'
                    tier.filled_at = datetime.now(timezone.utc).isoformat()
                    tier.filled_price = tier.price
            else:
                logger.info(f"\n🚀 LIVE TRADING MODE - Executing via Shadow Sniper...")
                # TODO: Execute via Shadow Sniper
                pass

            # 4. Create exit ladder
            exit_tiers = self.create_exit_ladder(signal, entry_tiers)

            logger.info(f"\n📈 EXIT LADDER ({len(exit_tiers)} tiers):")
            for tier in exit_tiers:
                tier_label = "STOP LOSS" if tier.tier == 0 else f"TP{tier.tier}"
                logger.info(f"   {tier_label}: ${tier.price:.4f} | {tier.weight_pct:.0f}% | {tier.quantity:.4f} units")

            # 5. Calculate profit projection
            avg_entry = sum(t.price * t.quantity for t in entry_tiers) / sum(t.quantity for t in entry_tiers)
            tp1_profit = (signal['tp1_price'] - avg_entry) * sum(t.quantity for t in entry_tiers) * 0.50
            tp2_profit = (signal.get('tp2_price', signal['tp1_price'] * 1.10) - avg_entry) * sum(t.quantity for t in entry_tiers) * 0.30
            total_profit = tp1_profit + tp2_profit

            logger.info(f"\n💰 PROFIT PROJECTION:")
            logger.info(f"   Average Entry: ${avg_entry:.4f}")
            logger.info(f"   TP1 Profit: ${tp1_profit:.2f}")
            logger.info(f"   TP2 Profit: ${tp2_profit:.2f}")
            logger.info(f"   Total Projected: ${total_profit:.2f}")

            # 6. Save deployment
            ladder_id = f"ladder_{signal['symbol'].lower()}_{int(datetime.now(timezone.utc).timestamp())}"

            deployment = {
                'ladder_id': ladder_id,
                'symbol': signal['symbol'],
                'mode': mode,
                'capital': capital,
                'entry_tiers': [asdict(t) for t in entry_tiers],
                'exit_tiers': [asdict(t) for t in exit_tiers],
                'validation': signal['validation'],
                'profit_projection': {
                    'avg_entry': avg_entry,
                    'tp1_profit': tp1_profit,
                    'tp2_profit': tp2_profit,
                    'total_profit': total_profit
                },
                'deployed_at': datetime.now(timezone.utc).isoformat(),
                'status': 'active'
            }

            self.active_ladders[ladder_id] = deployment
            self._save_deployment(deployment)

            logger.info(f"\n✅ LADDER DEPLOYED: {ladder_id}")
            logger.info(f"{'='*70}\n")

            return {
                'success': True,
                'ladder_id': ladder_id,
                'deployment': deployment
            }

        except Exception as e:
            logger.error(f"Ladder deployment failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _save_deployment(self, deployment: Dict[str, Any]):
        """Save ladder deployment to file"""
        try:
            filepath = self.logs_path / f"{deployment['ladder_id']}.json"
            with open(filepath, 'w') as f:
                json.dump(deployment, f, indent=2)
            logger.debug(f"📁 Saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save deployment: {e}")

    def get_active_ladders(self) -> Dict[str, Any]:
        """Get all active ladder deployments"""
        return {
            'count': len(self.active_ladders),
            'ladders': self.active_ladders
        }


def main():
    """Test deployment"""
    print("\n" + "="*70)
    print("🪜 UNIFIED LADDER SYSTEM - TEST DEPLOYMENT")
    print("="*70)
    print()

    ladder = UnifiedLadderSystem()

    # Test signal
    signal = {
        'symbol': 'XRP-USD',
        'entry_price': 2.50,
        'entry_low': 2.48,
        'entry_high': 2.52,
        'tp1_price': 3.00,  # 20% gain
        'tp2_price': 3.25,  # 30% gain
        'tp3_price': 3.50,  # 40% gain
        'sl_price': 2.33,   # 7% loss
    }

    capital = 100.0  # $100 test

    # Deploy
    result = ladder.deploy_ladder(signal, capital, mode='paper')

    if result['success']:
        print(f"✅ Test deployment successful!")
        print(f"   Ladder ID: {result['ladder_id']}")
    else:
        print(f"❌ Test deployment failed!")
        if 'reasons' in result:
            for reason in result['reasons']:
                print(f"   - {reason}")

    print()
    print("="*70)
    print()

if __name__ == "__main__":
    main()
