"""
Trade Gate - Must pass before any trade executes
Prevents signals from firing against macro trend

Updated 2025-12-21: Added Manus research integration
- Key level checks (BTC critical support $81,300)
- Regime-aware position sizing
- Auto kill switch triggers
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, '/Volumes/LegacySafe/SS_III')

from core.filters.market_filters import MarketFilters
from typing import Dict, Tuple

BRAIN_PATH = Path('/Volumes/LegacySafe/SS_III/BRAIN.json')


def load_brain() -> dict:
    """Load BRAIN.json for regime and key levels."""
    try:
        return json.loads(BRAIN_PATH.read_text())
    except:
        return {}


class TradeGate:
    """
    Gate that validates trades against macro context before execution.

    Rule: Signal direction must align with market filter direction.
    """

    def __init__(self):
        self.filters = MarketFilters()
        self.brain = load_brain()
        self.last_check = None

    def check_key_levels(self, symbol: str, current_price: float) -> Tuple[bool, str]:
        """
        Check if price is at critical levels from Manus research.

        Returns:
            Tuple of (safe_to_trade: bool, warning: str)
        """
        market_analysis = self.brain.get('market_analysis', {})
        key_levels = market_analysis.get('key_levels', {}).get(symbol, {})

        if not key_levels:
            return True, "No key levels defined"

        critical_support = key_levels.get('critical_support', 0)

        # KILL SWITCH: If below critical support, block all longs
        if critical_support and current_price < critical_support:
            return False, f"BLOCKED: {symbol} (${current_price:,.0f}) below critical support ${critical_support:,}. Risk of further breakdown."

        # WARNING: If within 5% of critical support, reduce size
        if critical_support and current_price < critical_support * 1.05:
            return True, f"WARNING: {symbol} within 5% of critical support ${critical_support:,}. Use reduced position size."

        # Check overhead supply zone
        supply_low = key_levels.get('overhead_supply_low', 0)
        supply_high = key_levels.get('overhead_supply_high', 0)

        if supply_low and supply_high and supply_low <= current_price <= supply_high:
            return True, f"WARNING: {symbol} in overhead supply zone ${supply_low:,}-${supply_high:,}. Expect resistance."

        return True, "Key levels OK"

    def get_regime_adjustment(self) -> Dict:
        """Get position size multiplier based on current regime."""
        market_analysis = self.brain.get('market_analysis', {})
        regime = market_analysis.get('regime', 'unknown')

        regime_adjustments = self.brain.get('autonomous_execution', {}).get('regime_adjustments', {})
        adjustment = regime_adjustments.get(regime, {})

        return {
            'regime': regime,
            'position_multiplier': adjustment.get('position_multiplier', 1.0),
            'prefer_strategies': adjustment.get('prefer_strategies', []),
            'avoid_strategies': adjustment.get('avoid_strategies', [])
        }

    def check(self, signal_action: str, symbol: str = "BTC", current_price: float = None) -> Tuple[bool, str]:
        """
        Check if a trade should be allowed.

        Args:
            signal_action: "BUY" or "SHORT"
            symbol: Trading pair symbol
            current_price: Current price of the asset (optional, for key level checks)

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Reload brain for fresh data
        self.brain = load_brain()

        # Check key levels first (Manus research)
        if current_price:
            level_ok, level_msg = self.check_key_levels(symbol, current_price)
            if not level_ok:
                return False, level_msg

        # Get regime adjustment
        regime_info = self.get_regime_adjustment()

        # Get current market filter
        fgi = self.filters.get_fear_greed()
        market_signal = fgi['signal']
        confidence = fgi['confidence']
        fgi_value = fgi['value']

        self.last_check = {
            'fgi': fgi_value,
            'market_signal': market_signal,
            'confidence': confidence,
            'requested_action': signal_action,
            'regime': regime_info['regime'],
            'position_multiplier': regime_info['position_multiplier'],
            'key_level_warning': level_msg if current_price else None
        }

        # Alignment check
        signal_is_long = signal_action.upper() in ['BUY', 'LONG']
        signal_is_short = signal_action.upper() in ['SHORT', 'SELL']

        # BULLISH market = allow longs, block shorts
        if market_signal == 'BULLISH':
            if signal_is_long:
                return True, f"APPROVED: BUY aligns with BULLISH market (FGI={fgi_value}, conf={confidence}%)"
            else:
                return False, f"BLOCKED: SHORT conflicts with BULLISH market (FGI={fgi_value}). Wait for bearish conditions."

        # BEARISH market = allow shorts, block longs
        elif market_signal == 'BEARISH':
            if signal_is_short:
                return True, f"APPROVED: SHORT aligns with BEARISH market (FGI={fgi_value}, conf={confidence}%)"
            else:
                return False, f"BLOCKED: BUY conflicts with BEARISH market (FGI={fgi_value}). Wait for bullish conditions."

        # NEUTRAL = allow with reduced size warning
        else:
            return True, f"ALLOWED (NEUTRAL): Market neutral (FGI={fgi_value}). Use reduced position size."

    def get_recommended_action(self) -> Dict:
        """Get the recommended action based on current market conditions."""
        fgi = self.filters.get_fear_greed()

        if fgi['signal'] == 'BULLISH':
            action = 'BUY'
            reason = f"Extreme Fear ({fgi['value']}) = buying opportunity"
        elif fgi['signal'] == 'BEARISH':
            action = 'SHORT'
            reason = f"Extreme Greed ({fgi['value']}) = take profits/short"
        else:
            action = 'WAIT'
            reason = f"Neutral market ({fgi['value']}) = no strong edge"

        return {
            'recommended_action': action,
            'reason': reason,
            'fgi': fgi['value'],
            'fgi_classification': fgi['classification'],
            'confidence': fgi['confidence']
        }


# Quick test
if __name__ == "__main__":
    gate = TradeGate()

    print("=== TRADE GATE STATUS ===")
    print()

    rec = gate.get_recommended_action()
    print(f"FGI: {rec['fgi']}/100 ({rec['fgi_classification']})")
    print(f"Recommended Action: {rec['recommended_action']}")
    print(f"Reason: {rec['reason']}")
    print(f"Confidence: {rec['confidence']}%")
    print()

    print("Gate Checks:")
    for action in ['BUY', 'SHORT']:
        allowed, reason = gate.check(action)
        emoji = "✅" if allowed else "❌"
        print(f"  {emoji} {action}: {reason}")
