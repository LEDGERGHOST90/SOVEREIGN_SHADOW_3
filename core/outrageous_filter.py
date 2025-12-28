#!/usr/bin/env python3
"""
OUTRAGEOUS FILTER
=================
The final gate. Only undeniable signals pass through.

"I don't want to trade. I want the trade to find me."
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger('outrageous_filter')

SS3_ROOT = Path(__file__).parent.parent


class OutrageousFilter:
    """
    Filters signals to only allow OUTRAGEOUS setups.
    Sits on top of MoonDev + Manus + SHADE.
    """

    def __init__(self):
        self.config = self._load_config()
        self.bias = self._load_manus_bias()
        logger.info("OutrageousFilter initialized - Only undeniable signals pass")

    def _load_config(self) -> dict:
        """Load outrageous signal requirements"""
        try:
            # Import from config
            from config.outrageous_signals import (
                OUTRAGEOUS_REQUIREMENTS,
                POSITION_CONFIG,
                EXECUTION_CONFIG
            )
            return {
                'requirements': OUTRAGEOUS_REQUIREMENTS,
                'position': POSITION_CONFIG,
                'execution': EXECUTION_CONFIG
            }
        except ImportError:
            # Fallback defaults
            return {
                'requirements': {
                    'final_confidence_min': 90,
                    'min_risk_reward': 3.0,
                    'min_agents_agreeing': 5,
                    'moondev_min_score': 1.5,
                },
                'position': {
                    'max_position_usd': 200,
                    'risk_per_trade_pct': 1.5,
                },
                'execution': {
                    'mode': 'paper',
                }
            }

    def _load_manus_bias(self) -> dict:
        """Load Manus research bias"""
        bias_path = SS3_ROOT / 'config' / 'alpha_bias.json'
        try:
            with open(bias_path) as f:
                return json.load(f)
        except:
            return {}

    def check(self, signal: dict) -> Tuple[bool, dict]:
        """
        Check if signal is OUTRAGEOUS enough to execute.

        Args:
            signal: {
                'symbol': str,
                'direction': 'LONG' | 'SHORT',
                'moondev_score': float,      # Weighted consensus (-2 to +2)
                'moondev_strategies': int,   # Number of strategies agreeing
                'confidence': float,         # Base confidence
                'biased_confidence': float,  # After Manus bias
                'risk_reward': float,
                'agents_agreeing': int,      # Agent council votes
                'rsi': float,
                'volume_ratio': float,
                'at_support': bool,
                'trend_aligned': bool,
                'whale_accumulating': bool,
            }

        Returns:
            (is_outrageous, details_dict)
        """
        req = self.config['requirements']
        checks = {}
        all_passed = True

        # 1. MOONDEV CONSENSUS
        moondev_score = signal.get('moondev_score', 0)
        moondev_pass = moondev_score >= req.get('moondev_min_score', 1.5)
        checks['moondev_consensus'] = {
            'passed': moondev_pass,
            'value': moondev_score,
            'required': req.get('moondev_min_score', 1.5),
            'reason': f"Score {moondev_score:.2f} {'≥' if moondev_pass else '<'} {req.get('moondev_min_score', 1.5)}"
        }
        if not moondev_pass:
            all_passed = False

        # 2. MANUS ALIGNMENT
        symbol = signal.get('symbol', '')
        immediate = self.bias.get('watchlist', {}).get('immediate', [])
        hayes = self.bias.get('whale_signals', {}).get('hayes_rotation', {}).get('tokens', [])
        on_watchlist = symbol in immediate or symbol in hayes

        checks['manus_alignment'] = {
            'passed': on_watchlist,
            'value': symbol,
            'required': 'On immediate/Hayes watchlist',
            'reason': f"{symbol} {'IS' if on_watchlist else 'NOT'} on priority watchlist"
        }
        # Don't fail on this alone, but track it

        # 3. AGENT COUNCIL
        agents = signal.get('agents_agreeing', 0)
        agents_pass = agents >= req.get('min_agents_agreeing', 5)
        checks['agent_council'] = {
            'passed': agents_pass,
            'value': agents,
            'required': req.get('min_agents_agreeing', 5),
            'reason': f"{agents}/7 agents agree {'≥' if agents_pass else '<'} {req.get('min_agents_agreeing', 5)}"
        }
        if not agents_pass:
            all_passed = False

        # 4. RISK/REWARD
        rr = signal.get('risk_reward', 0)
        rr_pass = rr >= req.get('min_risk_reward', 3.0)
        checks['risk_reward'] = {
            'passed': rr_pass,
            'value': rr,
            'required': req.get('min_risk_reward', 3.0),
            'reason': f"R:R 1:{rr:.1f} {'≥' if rr_pass else '<'} 1:{req.get('min_risk_reward', 3.0)}"
        }
        if not rr_pass:
            all_passed = False

        # 5. TECHNICALS
        tech_checks = []
        if signal.get('rsi'):
            direction = signal.get('direction', 'LONG')
            if direction == 'LONG':
                rsi_ok = signal['rsi'] <= req.get('rsi_oversold_max', 35)
            else:
                rsi_ok = signal['rsi'] >= req.get('rsi_overbought_min', 65)
            tech_checks.append(('RSI', rsi_ok, signal['rsi']))

        volume_ok = signal.get('volume_ratio', 0) >= 1.5
        tech_checks.append(('Volume spike', volume_ok, signal.get('volume_ratio', 0)))

        support_ok = signal.get('at_support', False)
        tech_checks.append(('At support', support_ok, 'Yes' if support_ok else 'No'))

        trend_ok = signal.get('trend_aligned', False)
        tech_checks.append(('Trend aligned', trend_ok, 'Yes' if trend_ok else 'No'))

        tech_passed = sum(1 for _, ok, _ in tech_checks if ok) >= 3  # Need 3/4 technicals
        checks['technicals'] = {
            'passed': tech_passed,
            'value': f"{sum(1 for _, ok, _ in tech_checks if ok)}/4",
            'required': '3/4',
            'details': tech_checks,
            'reason': f"{sum(1 for _, ok, _ in tech_checks if ok)}/4 technical checks passed"
        }
        if not tech_passed:
            all_passed = False

        # 6. WHALE CONFIRMATION
        whale_ok = signal.get('whale_accumulating', False)
        checks['whale_confirmation'] = {
            'passed': whale_ok,
            'value': 'Accumulating' if whale_ok else 'Not confirmed',
            'required': 'Accumulation',
            'reason': f"Whales {'ARE' if whale_ok else 'NOT'} accumulating"
        }
        # Not a hard requirement, but tracked

        # 7. FINAL CONFIDENCE (after all boosts)
        final_conf = signal.get('biased_confidence', signal.get('confidence', 0))

        # Extreme fear bonus
        fear = self.bias.get('market_regime', {}).get('fear_greed_index', 50)
        if fear <= req.get('fear_greed_extreme_threshold', 25):
            final_conf += req.get('extreme_fear_confidence_boost', 10)
            checks['contrarian_bonus'] = {
                'passed': True,
                'value': f"+{req.get('extreme_fear_confidence_boost', 10)}%",
                'reason': f"Extreme fear ({fear}) bonus applied"
            }

        conf_pass = final_conf >= req.get('final_confidence_min', 90)
        checks['final_confidence'] = {
            'passed': conf_pass,
            'value': final_conf,
            'required': req.get('final_confidence_min', 90),
            'reason': f"Confidence {final_conf:.0f}% {'≥' if conf_pass else '<'} {req.get('final_confidence_min', 90)}%"
        }
        if not conf_pass:
            all_passed = False

        # VERDICT
        result = {
            'is_outrageous': all_passed,
            'symbol': signal.get('symbol'),
            'direction': signal.get('direction'),
            'final_confidence': final_conf,
            'checks': checks,
            'timestamp': datetime.now().isoformat(),
            'execution_mode': self.config['execution'].get('mode', 'paper'),
        }

        if all_passed:
            result['position_size'] = min(
                self.config['position']['max_position_usd'],
                signal.get('position_size', 100)
            )
            logger.info(f"🚨 OUTRAGEOUS SIGNAL: {signal.get('symbol')} {signal.get('direction')}")
        else:
            failed = [k for k, v in checks.items() if not v.get('passed', True)]
            logger.debug(f"Signal filtered: {signal.get('symbol')} - Failed: {failed}")

        return all_passed, result

    def print_check(self, result: dict):
        """Print formatted check result"""
        print()
        print("=" * 70)
        if result['is_outrageous']:
            print("🚨 OUTRAGEOUS SIGNAL DETECTED 🚨")
        else:
            print("❌ SIGNAL FILTERED (Not outrageous enough)")
        print("=" * 70)
        print(f"Symbol: {result['symbol']}")
        print(f"Direction: {result['direction']}")
        print(f"Final Confidence: {result['final_confidence']:.0f}%")
        print("-" * 70)

        for check_name, check_data in result['checks'].items():
            icon = "✓" if check_data.get('passed', False) else "✗"
            print(f"  {icon} {check_name}: {check_data.get('reason', '')}")

        print("-" * 70)
        if result['is_outrageous']:
            print(f">>> EXECUTE: {result['direction']} ${result.get('position_size', 0):.0f}")
            print(f">>> Mode: {result['execution_mode'].upper()}")
        else:
            print(">>> NO TRADE - Waiting for undeniable setup")
        print("=" * 70)


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    filter = OutrageousFilter()

    # Test signal (not quite outrageous)
    test_signal = {
        'symbol': 'ENA',
        'direction': 'LONG',
        'moondev_score': 1.2,  # Below threshold
        'confidence': 70,
        'biased_confidence': 85,
        'risk_reward': 2.5,  # Below 3:1
        'agents_agreeing': 4,  # Below 5
        'rsi': 32,
        'volume_ratio': 1.8,
        'at_support': True,
        'trend_aligned': True,
        'whale_accumulating': False,
    }

    is_outrageous, result = filter.check(test_signal)
    filter.print_check(result)

    print("\n--- Now with OUTRAGEOUS signal ---\n")

    # Outrageous signal
    outrageous_signal = {
        'symbol': 'ENA',
        'direction': 'LONG',
        'moondev_score': 1.8,  # Strong consensus
        'confidence': 82,
        'biased_confidence': 92,
        'risk_reward': 3.5,
        'agents_agreeing': 6,
        'rsi': 28,
        'volume_ratio': 2.1,
        'at_support': True,
        'trend_aligned': True,
        'whale_accumulating': True,
    }

    is_outrageous, result = filter.check(outrageous_signal)
    filter.print_check(result)
