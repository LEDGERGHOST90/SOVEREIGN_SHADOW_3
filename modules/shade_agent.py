#!/usr/bin/env python3
"""
🏴 SHADE//AGENT - Strategy Enforcement Engine
Validates all trades against the 15m/4h strategy rules
Enforces risk management and psychology discipline

Based on NetworkChuck Trading Education System
Integrated into SovereignShadow_II

Author: SovereignShadow Trading System
Created: 2025-11-04
"""

import os
import sys
import json
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent))

class ShadeAgent:
    """
    Strategy Enforcement Agent

    Validates trades against:
    - 15m/4h timeframe alignment
    - Risk management rules (1-2% per trade)
    - Position sizing calculations
    - Stop loss requirements
    - R:R ratio minimums (1:2)
    - Total exposure limits (10%)
    - 3-strike rule (psychology)
    """

    def __init__(self, account_balance: float = 1660.0):
        self.account_balance = account_balance
        self.max_risk_per_trade = 0.02  # 2%
        self.min_risk_per_trade = 0.01  # 1%
        self.min_risk_reward = 2.0  # 1:2 minimum
        self.max_total_exposure = 0.10  # 10% of total portfolio
        self.max_daily_losses = 3  # 3-strike rule

        # Track daily losses
        self.today = datetime.now().date()
        self.daily_losses = 0

        # Load loss history
        self.loss_log_file = Path(__file__).parent.parent / "logs" / "psychology" / "loss_streak.json"
        self._load_loss_history()

        print("🏴 SHADE//AGENT initialized")
        print(f"   Account: ${account_balance:,.2f}")
        print(f"   Max Risk/Trade: {self.max_risk_per_trade*100}%")
        print(f"   Min R:R: 1:{self.min_risk_reward}")
        print(f"   Daily Loss Count: {self.daily_losses}/{self.max_daily_losses}")

    def _load_loss_history(self):
        """Load today's loss count from file"""
        try:
            if self.loss_log_file.exists():
                with open(self.loss_log_file, 'r') as f:
                    data = json.load(f)
                    log_date = datetime.fromisoformat(data.get('date', '')).date()

                    if log_date == self.today:
                        self.daily_losses = data.get('losses', 0)
                    else:
                        # New day, reset counter
                        self.daily_losses = 0
                        self._save_loss_history()
        except Exception as e:
            print(f"⚠️  Could not load loss history: {e}")
            self.daily_losses = 0

    def _save_loss_history(self):
        """Save loss count to file"""
        try:
            self.loss_log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.loss_log_file, 'w') as f:
                json.dump({
                    'date': self.today.isoformat(),
                    'losses': self.daily_losses
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save loss history: {e}")

    def validate_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation function
        Checks ALL criteria before approving trade

        Args:
            trade: {
                'symbol': str,
                'direction': 'LONG' | 'SHORT',
                'entry': float,
                'stop': float,
                'target_1': float,
                'target_2': float (optional),
                '4h_trend': 'bullish' | 'bearish' | 'neutral',
                '4h_rsi': float,
                '4h_at_sr': bool,
                '15m_at_level': bool,
                '15m_candle_pattern': bool,
                '15m_volume_spike': bool,
                '15m_rsi': float
            }

        Returns:
            {
                'approved': bool,
                'reason': str,
                'position_size': float,
                'position_value': float,
                'risk_amount': float,
                'risk_reward': float,
                'checks': {...}
            }
        """

        result = {
            'approved': False,
            'reason': '',
            'position_size': 0,
            'position_value': 0,
            'risk_amount': 0,
            'risk_reward': 0,
            'checks': {}
        }

        # Run all validation checks
        checks = {
            'psychology': self._check_psychology(),
            'timeframe_alignment': self._check_timeframe_alignment(trade),
            'risk_management': self._check_risk_management(trade),
            'stop_loss': self._check_stop_loss(trade),
            'risk_reward': self._check_risk_reward(trade),
            'total_exposure': self._check_total_exposure(trade),
            'technical_setup': self._check_technical_setup(trade)
        }

        result['checks'] = checks

        # Determine approval
        all_passed = all(check['passed'] for check in checks.values())

        if all_passed:
            # Calculate position size
            position_calc = self.calculate_position_size(
                entry=trade['entry'],
                stop=trade['stop'],
                risk_percent=2.0  # Use 2% for approved trades
            )

            result['approved'] = True
            result['reason'] = '✅ ALL CHECKS PASSED - Trade approved'
            result['position_size'] = position_calc['position_size']
            result['position_value'] = position_calc['position_value']
            result['risk_amount'] = position_calc['risk_amount']
            result['risk_reward'] = position_calc['risk_reward']
        else:
            # Find first failure
            failed = [name for name, check in checks.items() if not check['passed']]
            result['reason'] = f"❌ REJECTED: {checks[failed[0]]['reason']}"

        return result

    def _check_psychology(self) -> Dict[str, Any]:
        """Check 3-strike rule"""
        passed = self.daily_losses < self.max_daily_losses

        return {
            'passed': passed,
            'reason': f"3-Strike Rule: {self.daily_losses}/{self.max_daily_losses} losses today" if passed else f"❌ 3 LOSSES TODAY - STOP TRADING",
            'data': {
                'daily_losses': self.daily_losses,
                'max_losses': self.max_daily_losses
            }
        }

    def _check_timeframe_alignment(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Check 4h and 15m alignment"""

        # Check 4h trend matches direction
        if trade['direction'] == 'LONG':
            trend_ok = trade.get('4h_trend') == 'bullish'
        else:
            trend_ok = trade.get('4h_trend') == 'bearish'

        # Check 15m setup exists
        setup_ok = trade.get('15m_at_level', False)

        passed = trend_ok and setup_ok

        if not trend_ok:
            reason = f"4h trend is {trade.get('4h_trend')}, not aligned with {trade['direction']}"
        elif not setup_ok:
            reason = "15m not at key level (EMA 21 or S/R)"
        else:
            reason = "4h trend + 15m setup aligned"

        return {
            'passed': passed,
            'reason': reason,
            'data': {
                '4h_trend': trade.get('4h_trend'),
                '15m_at_level': trade.get('15m_at_level'),
                'direction': trade['direction']
            }
        }

    def _check_risk_management(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Check risk is 1-2% of account"""

        entry = trade['entry']
        stop = trade['stop']
        stop_distance = abs(entry - stop)

        # Calculate risk for 2%
        risk_amount_2pct = self.account_balance * 0.02
        position_size = risk_amount_2pct / stop_distance
        position_value = position_size * entry

        # Check if position is reasonable (not too large)
        max_position_value = self.account_balance * 2  # 2x leverage max
        passed = position_value <= max_position_value

        return {
            'passed': passed,
            'reason': f"Position ${position_value:,.2f} (2% risk)" if passed else f"Position too large: ${position_value:,.2f}",
            'data': {
                'risk_percent': 2.0,
                'risk_amount': risk_amount_2pct,
                'position_value': position_value,
                'position_size': position_size
            }
        }

    def _check_stop_loss(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Verify stop loss is set and reasonable"""

        has_stop = 'stop' in trade and trade['stop'] is not None

        if not has_stop:
            return {
                'passed': False,
                'reason': "No stop loss set",
                'data': {}
            }

        entry = trade['entry']
        stop = trade['stop']

        # Check stop is in correct direction
        if trade['direction'] == 'LONG':
            stop_ok = stop < entry
        else:
            stop_ok = stop > entry

        # Check stop distance is reasonable (not too tight, not too wide)
        stop_distance_pct = abs((entry - stop) / entry) * 100
        reasonable = 0.5 <= stop_distance_pct <= 10  # Between 0.5% and 10%

        passed = stop_ok and reasonable

        return {
            'passed': passed,
            'reason': f"Stop at {stop_distance_pct:.2f}% from entry" if passed else f"Stop placement issue: {stop_distance_pct:.2f}%",
            'data': {
                'stop': stop,
                'entry': entry,
                'distance_pct': stop_distance_pct
            }
        }

    def _check_risk_reward(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Check R:R is at least 1:2"""

        entry = trade['entry']
        stop = trade['stop']
        target = trade.get('target_1')

        if not target:
            return {
                'passed': False,
                'reason': "No target set",
                'data': {}
            }

        stop_distance = abs(entry - stop)
        target_distance = abs(target - entry)

        risk_reward = target_distance / stop_distance if stop_distance > 0 else 0
        passed = risk_reward >= self.min_risk_reward

        return {
            'passed': passed,
            'reason': f"R:R is 1:{risk_reward:.1f}" if passed else f"R:R too low: 1:{risk_reward:.1f} (need 1:{self.min_risk_reward})",
            'data': {
                'risk_reward': risk_reward,
                'min_required': self.min_risk_reward,
                'stop_distance': stop_distance,
                'target_distance': target_distance
            }
        }

    def _check_total_exposure(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Check total portfolio exposure under 10%"""

        # TODO: Get current open positions value
        # For now, assume this is the first/only position
        current_exposure_pct = 0.0

        # Calculate new position exposure
        entry = trade['entry']
        stop = trade['stop']
        stop_distance = abs(entry - stop)
        risk_amount = self.account_balance * 0.02
        position_size = risk_amount / stop_distance
        new_position_value = position_size * entry

        # Calculate as percentage of TOTAL portfolio (not just trading account)
        # Assuming total portfolio is account_balance / 0.1 (10% active trading)
        total_portfolio = self.account_balance / 0.1  # Reverse calculate total
        new_exposure_pct = new_position_value / total_portfolio

        total_exposure_pct = current_exposure_pct + new_exposure_pct
        passed = total_exposure_pct <= self.max_total_exposure

        return {
            'passed': passed,
            'reason': f"Total exposure: {total_exposure_pct*100:.1f}%" if passed else f"Exposure too high: {total_exposure_pct*100:.1f}% (max 10%)",
            'data': {
                'current_exposure_pct': current_exposure_pct,
                'new_exposure_pct': new_exposure_pct,
                'total_exposure_pct': total_exposure_pct,
                'max_allowed': self.max_total_exposure
            }
        }

    def _check_technical_setup(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Check technical indicators support the trade"""

        checks = []

        # 4h RSI check
        if trade['direction'] == 'LONG':
            rsi_ok = trade.get('4h_rsi', 50) > 50
            checks.append(('4h RSI > 50', rsi_ok))
        else:
            rsi_ok = trade.get('4h_rsi', 50) < 50
            checks.append(('4h RSI < 50', rsi_ok))

        # 4h at S/R
        at_sr = trade.get('4h_at_sr', False)
        checks.append(('At 4h S/R level', at_sr))

        # 15m candle pattern
        candle_ok = trade.get('15m_candle_pattern', False)
        checks.append(('15m candle pattern', candle_ok))

        # 15m volume
        volume_ok = trade.get('15m_volume_spike', False)
        checks.append(('15m volume spike', volume_ok))

        # 15m RSI not extreme
        rsi_15m = trade.get('15m_rsi', 50)
        if trade['direction'] == 'LONG':
            rsi_not_extreme = rsi_15m < 70
            checks.append(('15m RSI not overbought', rsi_not_extreme))
        else:
            rsi_not_extreme = rsi_15m > 30
            checks.append(('15m RSI not oversold', rsi_not_extreme))

        passed_checks = [name for name, passed in checks if passed]
        failed_checks = [name for name, passed in checks if not passed]

        # Need at least 4 out of 5 checks
        passed = len(passed_checks) >= 4

        return {
            'passed': passed,
            'reason': f"{len(passed_checks)}/5 technical checks passed" if passed else f"Only {len(passed_checks)}/5 technical checks (need 4+)",
            'data': {
                'passed': passed_checks,
                'failed': failed_checks,
                'checks': dict(checks)
            }
        }

    def calculate_position_size(self, entry: float, stop: float, risk_percent: float = 2.0) -> Dict[str, Any]:
        """
        Calculate position size based on risk management

        Args:
            entry: Entry price
            stop: Stop loss price
            risk_percent: Risk percentage (1-2)

        Returns:
            Position sizing details
        """

        risk_amount = self.account_balance * (risk_percent / 100)
        stop_distance = abs(entry - stop)
        position_size = risk_amount / stop_distance
        position_value = position_size * entry

        # Calculate R:R if targets provided
        risk_reward = 0

        return {
            'account_balance': self.account_balance,
            'risk_percent': risk_percent,
            'risk_amount': risk_amount,
            'entry': entry,
            'stop': stop,
            'stop_distance': stop_distance,
            'position_size': position_size,
            'position_value': position_value,
            'risk_reward': risk_reward
        }

    def record_trade_result(self, win: bool):
        """
        Record trade result for psychology tracking

        Args:
            win: True if trade was profitable, False if loss
        """

        # Check if date changed
        if datetime.now().date() != self.today:
            self.today = datetime.now().date()
            self.daily_losses = 0

        if not win:
            self.daily_losses += 1
            self._save_loss_history()

            if self.daily_losses >= self.max_daily_losses:
                print("\n" + "="*70)
                print("🛑 3-STRIKE RULE TRIGGERED")
                print("="*70)
                print("You've lost 3 trades today.")
                print("STOP TRADING FOR THE REST OF THE DAY.")
                print("Review your trades. Come back tomorrow.")
                print("="*70 + "\n")
        else:
            # Win resets streak? (optional behavior)
            pass

    def print_validation_report(self, result: Dict[str, Any]):
        """Print formatted validation report"""

        print("\n" + "="*70)
        print("🏴 SHADE//AGENT - TRADE VALIDATION REPORT")
        print("="*70)

        if result['approved']:
            print("✅ TRADE APPROVED")
            print(f"\nPosition Size: {result['position_size']:.4f} coins")
            print(f"Position Value: ${result['position_value']:,.2f}")
            print(f"Risk Amount: ${result['risk_amount']:,.2f} ({(result['risk_amount']/self.account_balance)*100:.1f}%)")
            print(f"Risk:Reward: 1:{result['risk_reward']:.1f}")
        else:
            print("❌ TRADE REJECTED")
            print(f"\nReason: {result['reason']}")

        print("\n" + "-"*70)
        print("VALIDATION CHECKS:")
        print("-"*70)

        for check_name, check_data in result['checks'].items():
            emoji = "✅" if check_data['passed'] else "❌"
            print(f"{emoji} {check_name.replace('_', ' ').title()}: {check_data['reason']}")

        print("="*70 + "\n")


def demo():
    """Demo SHADE//AGENT validation"""

    agent = ShadeAgent(account_balance=1660)

    # Example trade
    trade = {
        'symbol': 'BTC/USDT',
        'direction': 'LONG',
        'entry': 99000,
        'stop': 97000,
        'target_1': 103000,
        'target_2': 107000,
        '4h_trend': 'bullish',
        '4h_rsi': 55,
        '4h_at_sr': True,
        '15m_at_level': True,
        '15m_candle_pattern': True,
        '15m_volume_spike': True,
        '15m_rsi': 45
    }

    print("\n📋 TESTING TRADE:")
    print(f"   {trade['direction']} {trade['symbol']}")
    print(f"   Entry: ${trade['entry']:,}")
    print(f"   Stop: ${trade['stop']:,}")
    print(f"   Target: ${trade['target_1']:,}")

    result = agent.validate_trade(trade)
    agent.print_validation_report(result)

    # Test bad trade
    print("\n" + "="*70)
    print("Testing REJECTED trade (wrong timeframe alignment)...")
    print("="*70)

    bad_trade = trade.copy()
    bad_trade['4h_trend'] = 'bearish'  # Conflict!

    result2 = agent.validate_trade(bad_trade)
    agent.print_validation_report(result2)


if __name__ == "__main__":
    demo()
