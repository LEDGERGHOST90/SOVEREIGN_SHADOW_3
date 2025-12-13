#!/usr/bin/env python3
"""
Elder Reversion Strategy - Risk Module

Risk parameters optimized for mean reversion:
- Max position: 10% of portfolio
- Risk per trade: 1%
- Stop loss: 1%
- Take profit: 2% (2:1 R:R)
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import BaseRiskModule


class ElderReversionRisk(BaseRiskModule):
    """Elder Reversion risk management"""
    
    def __init__(self):
        super().__init__(
            max_position_size=0.10,  # 10% max
            stop_loss_percent=1.0,    # 1% stop
            take_profit_percent=2.0,  # 2% target (2:1 R:R)
            risk_per_trade=0.01       # 1% risk
        )
        self.name = "elder_reversion_risk"


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING ELDER REVERSION RISK MODULE")
    print("="*70)
    
    risk = ElderReversionRisk()
    
    # Test position sizing
    portfolio_value = 10000
    current_price = 99000
    atr = 500  # $500 ATR
    confidence = 75
    
    sizing = risk.calculate_position_size(
        portfolio_value=portfolio_value,
        current_price=current_price,
        atr=atr,
        confidence=confidence
    )
    
    print(f"\n📊 Position Sizing:")
    print(f"   Portfolio: ${portfolio_value:,.2f}")
    print(f"   Price: ${current_price:,.2f}")
    print(f"   Confidence: {confidence}%")
    print(f"\n💰 Results:")
    print(f"   Position Value: ${sizing.position_value_usd:,.2f}")
    print(f"   Quantity: {sizing.quantity:.6f}")
    print(f"   Risk Amount: ${sizing.risk_amount_usd:.2f} ({sizing.risk_percent:.1%})")
    print(f"   Stop Loss: ${sizing.stop_loss_price:,.2f}")
    print(f"   Take Profit: ${sizing.take_profit_price:,.2f}")
    print(f"   R:R Ratio: 1:{(sizing.take_profit_price - current_price) / (current_price - sizing.stop_loss_price):.1f}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
