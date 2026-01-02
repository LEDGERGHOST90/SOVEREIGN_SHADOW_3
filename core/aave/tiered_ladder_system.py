#!/usr/bin/env python3
"""
🪜 TIERED LADDER SYSTEM
Progressive profit extraction with automatic tier advancement

Tier Structure:
- Tier 1: $1,000  → Extract 20%, Keep 80% buffer
- Tier 2: $2,000  → Extract 30%, Keep 70% buffer
- Tier 3: $3,500  → Extract ALL, Reset with $1,000
- Tier 4: $5,000  → Extract 40%, Keep 60% buffer
- Tier 5: $10,000 → Extract 50%, Keep 50% buffer
- Tier 6: $25,000 → Extract 60%, Keep 40% buffer

Safety Protocol:
1. ALWAYS pay AAVE debt FIRST
2. ALWAYS maintain Health Factor > 2.5
3. Only extract from TRUE trading profits (exclude capital injections)
4. Log every tier achievement
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Import centralized portfolio config
try:
    sys.path.insert(0, '/Volumes/LegacySafe/SS_III')
    from core.config.portfolio_config import get_initial_capital
except ImportError:
    def get_initial_capital(exchange=None):
        return 5438 if exchange is None else 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tiered_ladder")

class TieredLadderSystem:
    """
    Progressive profit extraction system with automatic tier advancement

    Integrates with:
    - unified_profit_tracker.py (current portfolio state)
    - income_capital_tracker.py (true profit calculation)
    - aave_monitor.py (debt and health factor)
    """

    def __init__(self):
        self.base_path = Path("/Volumes/LegacySafe/SovereignShadow 2")
        self.logs_path = self.base_path / "logs" / "ladder"
        self.logs_path.mkdir(parents=True, exist_ok=True)

        self.state_file = self.logs_path / "ladder_state.json"
        self.history_file = self.logs_path / "ladder_history.json"

        # Define tier structure
        self.tiers = [
            {
                'tier': 1,
                'threshold': 1000.0,
                'extract_pct': 20.0,
                'keep_pct': 80.0,
                'description': 'First milestone - conservative extraction',
                'reset': False
            },
            {
                'tier': 2,
                'threshold': 2000.0,
                'extract_pct': 30.0,
                'keep_pct': 70.0,
                'description': 'Building momentum',
                'reset': False
            },
            {
                'tier': 3,
                'threshold': 3500.0,
                'extract_pct': 100.0,
                'keep_pct': 0.0,
                'description': 'FULL EXTRACTION - Reset with $1,000',
                'reset': True,
                'reset_capital': 1000.0
            },
            {
                'tier': 4,
                'threshold': 5000.0,
                'extract_pct': 40.0,
                'keep_pct': 60.0,
                'description': 'Post-reset milestone',
                'reset': False
            },
            {
                'tier': 5,
                'threshold': 10000.0,
                'extract_pct': 50.0,
                'keep_pct': 50.0,
                'description': 'Major milestone - balanced extraction',
                'reset': False
            },
            {
                'tier': 6,
                'threshold': 25000.0,
                'extract_pct': 60.0,
                'keep_pct': 40.0,
                'description': 'Elite tier - aggressive extraction',
                'reset': False
            }
        ]

        # Load or initialize state
        self.state = self._load_state()

        logger.info("🪜 Tiered Ladder System initialized")
        logger.info(f"   Current Tier: {self.state['current_tier']}")
        logger.info(f"   Total Extractions: {self.state['total_extractions']}")
        logger.info(f"   Total Extracted USD: ${self.state['total_extracted_usd']:,.2f}")

    def _load_state(self) -> Dict[str, Any]:
        """Load ladder state or create new"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)

        # Initialize new state
        return {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'current_tier': 0,
            'highest_tier_achieved': 0,
            'total_extractions': 0,
            'total_extracted_usd': 0.0,
            'tiers_achieved': [],
            'last_extraction': None,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    def _save_state(self):
        """Save ladder state"""
        self.state['last_updated'] = datetime.now(timezone.utc).isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

        logger.debug(f"📁 State saved to: {self.state_file}")

    def _log_extraction(self, extraction_data: Dict[str, Any]):
        """Log extraction to history"""
        # Load existing history
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)

        # Add new extraction
        history.append(extraction_data)

        # Save updated history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

        logger.debug(f"📁 Extraction logged to: {self.history_file}")

    def check_tier_eligibility(self, true_profit: float) -> Optional[Dict[str, Any]]:
        """
        Check if current profit qualifies for next tier

        Args:
            true_profit: TRUE trading profit (excluding capital injections)

        Returns:
            Tier data if eligible, None otherwise
        """
        current_tier = self.state['current_tier']

        # Find next eligible tier
        for tier in self.tiers:
            if tier['tier'] > current_tier and true_profit >= tier['threshold']:
                return tier

        return None

    def calculate_extraction(self,
                           true_profit: float,
                           tier: Dict[str, Any],
                           aave_debt: float = 0.0,
                           health_factor: float = 0.0) -> Dict[str, Any]:
        """
        Calculate extraction amounts with safety checks

        Safety Protocol:
        1. Pay AAVE debt FIRST
        2. Check health factor (must be > 2.5)
        3. Calculate extraction based on tier
        4. Split: VAULT (30%) + BUFFER (70%)

        Returns:
            Extraction plan with amounts and safety status
        """
        # SAFETY CHECK 1: Health Factor
        if health_factor > 0 and health_factor < 2.5:
            return {
                'safe_to_extract': False,
                'reason': f'Health factor too low: {health_factor:.4f} < 2.5',
                'recommended_action': 'Add collateral or reduce debt first'
            }

        # Calculate profit above threshold
        profit_above_threshold = true_profit - tier['threshold']

        if profit_above_threshold <= 0:
            return {
                'safe_to_extract': False,
                'reason': f'Profit ${true_profit:.2f} below tier threshold ${tier["threshold"]:.2f}'
            }

        # Calculate extraction amount
        if tier['reset']:
            # Tier 3: Extract ALL, reset with $1,000
            total_extraction = true_profit - tier['reset_capital']
        else:
            # Extract percentage of profit above threshold
            total_extraction = profit_above_threshold * (tier['extract_pct'] / 100.0)

        # SAFETY CHECK 2: Pay debt FIRST
        debt_payment = min(aave_debt, total_extraction)
        remaining_after_debt = total_extraction - debt_payment

        # Split remaining between VAULT (30%) and BUFFER (70%)
        vault_amount = remaining_after_debt * 0.30
        buffer_amount = remaining_after_debt * 0.70

        return {
            'safe_to_extract': True,
            'tier': tier['tier'],
            'tier_description': tier['description'],
            'true_profit': true_profit,
            'threshold': tier['threshold'],
            'profit_above_threshold': profit_above_threshold,
            'extract_pct': tier['extract_pct'],
            'total_extraction': total_extraction,
            'debt_payment': debt_payment,
            'remaining_after_debt': remaining_after_debt,
            'vault_30pct': vault_amount,
            'buffer_70pct': buffer_amount,
            'reset': tier['reset'],
            'reset_capital': tier.get('reset_capital', 0.0),
            'health_factor': health_factor,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def execute_extraction(self, extraction_plan: Dict[str, Any]) -> bool:
        """
        Execute extraction (simulated for now)

        In production, this would:
        1. Pay AAVE debt via aave_monitor.py
        2. Transfer vault_30pct to Ledger cold storage
        3. Keep buffer_70pct in trading capital
        4. Update all tracking systems

        Args:
            extraction_plan: Plan from calculate_extraction()

        Returns:
            Success status
        """
        if not extraction_plan.get('safe_to_extract', False):
            logger.warning(f"❌ Extraction not safe: {extraction_plan.get('reason')}")
            return False

        try:
            tier = extraction_plan['tier']

            logger.info(f"🪜 TIER {tier} EXTRACTION INITIATED")
            logger.info(f"   Description: {extraction_plan['tier_description']}")
            logger.info(f"   True Profit: ${extraction_plan['true_profit']:,.2f}")
            logger.info(f"   Threshold: ${extraction_plan['threshold']:,.2f}")
            logger.info(f"   Total Extraction: ${extraction_plan['total_extraction']:,.2f}")

            if extraction_plan['debt_payment'] > 0:
                logger.info(f"   💳 Debt Payment: ${extraction_plan['debt_payment']:,.2f}")
                # TODO: Call aave_monitor.repay_debt(amount)

            logger.info(f"   🏦 VAULT (30%): ${extraction_plan['vault_30pct']:,.2f}")
            logger.info(f"   🔄 BUFFER (70%): ${extraction_plan['buffer_70pct']:,.2f}")

            if extraction_plan['reset']:
                logger.info(f"   🔄 RESET Capital: ${extraction_plan['reset_capital']:,.2f}")

            # Update state
            self.state['current_tier'] = tier
            self.state['highest_tier_achieved'] = max(
                self.state['highest_tier_achieved'],
                tier
            )
            self.state['total_extractions'] += 1
            self.state['total_extracted_usd'] += extraction_plan['total_extraction']
            self.state['last_extraction'] = extraction_plan['timestamp']

            # Add to achieved tiers if not already there
            if tier not in self.state['tiers_achieved']:
                self.state['tiers_achieved'].append(tier)
                self.state['tiers_achieved'].sort()

            # Save state
            self._save_state()

            # Log to history
            self._log_extraction(extraction_plan)

            logger.info(f"✅ Tier {tier} extraction completed successfully")

            return True

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False

    def run_ladder_check(self) -> Dict[str, Any]:
        """
        Main ladder check - evaluates current state and recommends actions

        This should be called periodically (e.g., every 6 hours) to check
        if we've hit a new tier milestone

        Returns:
            Status with recommendations
        """
        logger.info("🪜 Running ladder check...")

        try:
            # Import required modules
            from unified_profit_tracker import UnifiedProfitTracker
            from income_capital_tracker import IncomeCapitalTracker
            from aave_monitor import AAVEMonitor

            # Get current state
            profit_tracker = UnifiedProfitTracker()
            capital_tracker = IncomeCapitalTracker()
            aave = AAVEMonitor()

            # Get portfolio data
            portfolio_data = profit_tracker.get_total_profit()
            current_portfolio = portfolio_data['current_portfolio_value']

            # Get AAVE data
            position = aave.get_position_summary()
            aave_debt = position.get('debt_usd', 0.0)
            health_factor = position.get('health_factor', 0.0)

            # Calculate true trading profit - use centralized config
            initial_capital = get_initial_capital()  # From portfolio_config.py
            total_withdrawn = self.state['total_extracted_usd']

            true_profit_data = capital_tracker.calculate_true_profit(
                current_portfolio=current_portfolio,
                initial_capital=initial_capital,
                total_withdrawn=total_withdrawn
            )

            true_profit = true_profit_data['true_trading_profit']

            logger.info(f"   Portfolio: ${current_portfolio:,.2f}")
            logger.info(f"   AAVE Debt: ${aave_debt:,.2f}")
            logger.info(f"   Health Factor: {health_factor:.4f}")
            logger.info(f"   True Profit: ${true_profit:,.2f}")
            logger.info(f"   Current Tier: {self.state['current_tier']}")

            # Check tier eligibility
            eligible_tier = self.check_tier_eligibility(true_profit)

            if eligible_tier:
                logger.info(f"✨ TIER {eligible_tier['tier']} ELIGIBLE!")

                # Calculate extraction plan
                extraction_plan = self.calculate_extraction(
                    true_profit=true_profit,
                    tier=eligible_tier,
                    aave_debt=aave_debt,
                    health_factor=health_factor
                )

                return {
                    'status': 'tier_eligible',
                    'eligible_tier': eligible_tier,
                    'extraction_plan': extraction_plan,
                    'current_state': self.state,
                    'portfolio_data': {
                        'current_portfolio': current_portfolio,
                        'true_profit': true_profit,
                        'aave_debt': aave_debt,
                        'health_factor': health_factor
                    }
                }
            else:
                # Calculate progress to next tier
                next_tier = None
                for tier in self.tiers:
                    if tier['tier'] > self.state['current_tier']:
                        next_tier = tier
                        break

                progress = None
                if next_tier:
                    progress = {
                        'next_tier': next_tier['tier'],
                        'threshold': next_tier['threshold'],
                        'current_profit': true_profit,
                        'needed': next_tier['threshold'] - true_profit,
                        'progress_pct': (true_profit / next_tier['threshold']) * 100
                    }

                    logger.info(f"   Next Tier: {next_tier['tier']} (${next_tier['threshold']:,.2f})")
                    logger.info(f"   Progress: {progress['progress_pct']:.1f}%")
                    logger.info(f"   Needed: ${progress['needed']:,.2f}")

                return {
                    'status': 'no_tier_eligible',
                    'current_state': self.state,
                    'progress': progress,
                    'portfolio_data': {
                        'current_portfolio': current_portfolio,
                        'true_profit': true_profit,
                        'aave_debt': aave_debt,
                        'health_factor': health_factor
                    }
                }

        except Exception as e:
            logger.error(f"❌ Ladder check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_tier_summary(self) -> Dict[str, Any]:
        """Get comprehensive tier summary"""
        return {
            'current_tier': self.state['current_tier'],
            'highest_tier_achieved': self.state['highest_tier_achieved'],
            'tiers_achieved': self.state['tiers_achieved'],
            'total_extractions': self.state['total_extractions'],
            'total_extracted_usd': self.state['total_extracted_usd'],
            'last_extraction': self.state['last_extraction'],
            'available_tiers': [
                {
                    'tier': t['tier'],
                    'threshold': t['threshold'],
                    'extract_pct': t['extract_pct'],
                    'description': t['description'],
                    'achieved': t['tier'] in self.state['tiers_achieved']
                }
                for t in self.tiers
            ]
        }


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🪜 TIERED LADDER SYSTEM")
    print("="*70)
    print()

    ladder = TieredLadderSystem()

    # Show tier structure
    print("📊 TIER STRUCTURE:")
    print()
    for tier in ladder.tiers:
        achieved = "✅" if tier['tier'] in ladder.state['tiers_achieved'] else "⬜"
        current = "👉" if tier['tier'] == ladder.state['current_tier'] + 1 else "  "

        print(f"{achieved} {current} Tier {tier['tier']}: ${tier['threshold']:,.2f}")
        print(f"      Extract: {tier['extract_pct']:.0f}% | Keep: {tier['keep_pct']:.0f}%")
        print(f"      {tier['description']}")
        if tier.get('reset'):
            print(f"      🔄 RESET with ${tier['reset_capital']:,.2f}")
        print()

    print("="*70)
    print("📈 CURRENT STATUS:")
    print("="*70)
    print()

    summary = ladder.get_tier_summary()
    print(f"Current Tier: {summary['current_tier']}")
    print(f"Highest Achieved: {summary['highest_tier_achieved']}")
    print(f"Total Extractions: {summary['total_extractions']}")
    print(f"Total Extracted: ${summary['total_extracted_usd']:,.2f}")
    print()

    print("="*70)
    print("🔍 RUNNING LADDER CHECK...")
    print("="*70)
    print()

    # Run ladder check
    result = ladder.run_ladder_check()

    if result['status'] == 'tier_eligible':
        print("✨ TIER MILESTONE REACHED!")
        print()
        tier = result['eligible_tier']
        plan = result['extraction_plan']

        if plan['safe_to_extract']:
            print(f"🎯 Tier {tier['tier']}: ${tier['threshold']:,.2f}")
            print(f"   {tier['description']}")
            print()
            print(f"💰 TRUE PROFIT: ${plan['true_profit']:,.2f}")
            print(f"   Threshold: ${plan['threshold']:,.2f}")
            print(f"   Above Threshold: ${plan['profit_above_threshold']:,.2f}")
            print()
            print(f"📤 EXTRACTION PLAN:")
            print(f"   Total: ${plan['total_extraction']:,.2f}")

            if plan['debt_payment'] > 0:
                print(f"   💳 Debt Payment: ${plan['debt_payment']:,.2f}")

            print(f"   🏦 VAULT (30%): ${plan['vault_30pct']:,.2f}")
            print(f"   🔄 BUFFER (70%): ${plan['buffer_70pct']:,.2f}")

            if plan['reset']:
                print(f"   🔄 Reset Capital: ${plan['reset_capital']:,.2f}")

            print()
            print(f"✅ SAFE TO EXTRACT (HF: {plan['health_factor']:.4f})")
        else:
            print(f"⚠️  NOT SAFE TO EXTRACT")
            print(f"   Reason: {plan.get('reason')}")
            if 'recommended_action' in plan:
                print(f"   Action: {plan['recommended_action']}")

    elif result['status'] == 'no_tier_eligible':
        print("📊 No tier milestone reached yet")
        print()

        if result.get('progress'):
            prog = result['progress']
            print(f"Next Milestone: Tier {prog['next_tier']} (${prog['threshold']:,.2f})")
            print(f"Current Profit: ${prog['current_profit']:,.2f}")
            print(f"Progress: {prog['progress_pct']:.1f}%")
            print(f"Needed: ${prog['needed']:,.2f}")

    else:
        print(f"❌ Error: {result.get('error')}")

    print()
    print("="*70)
    print(f"📁 State saved to: {ladder.state_file}")
    print(f"📁 History saved to: {ladder.history_file}")
    print("="*70)
    print()

if __name__ == "__main__":
    main()
