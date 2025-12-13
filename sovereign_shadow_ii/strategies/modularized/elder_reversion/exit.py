#!/usr/bin/env python3
"""
Elder Reversion Strategy - Exit Module

Exit Logic:
- Bull Power > 0 (reversal complete, bears back in control)
- Take Profit: 2%
- Stop Loss: 1%
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import ExitModule, ExitSignal


class ElderReversionExit(ExitModule):
    """Elder Ray Reversion exit logic"""
    
    def __init__(
        self,
        take_profit_percent: float = 2.0,
        stop_loss_percent: float = 1.0,
        ema_period: int = 13
    ):
        super().__init__()
        self.name = "elder_reversion_exit"
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.ema_period = ema_period
    
    def generate_signal(self, df: pd.DataFrame, entry_price: float) -> ExitSignal:
        """
        Generate exit signal
        
        Exit conditions:
        1. Take profit hit (2% gain)
        2. Stop loss hit (1% loss)
        3. Bull Power > 0 (reversal complete)
        """
        # Calculate EMA-13
        ema_13 = df['close'].ewm(span=self.ema_period).mean()
        
        # Calculate Elder Ray
        bull_power = df['high'] - ema_13
        
        # Current values
        current_bull = bull_power.iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Calculate PnL
        pnl = current_price - entry_price
        pnl_percent = (pnl / entry_price) * 100
        
        # Take profit
        if pnl_percent >= self.take_profit_percent:
            return ExitSignal(
                signal="SELL",
                reason="TAKE_PROFIT",
                pnl=pnl,
                pnl_percent=pnl_percent
            )
        
        # Stop loss
        if pnl_percent <= -self.stop_loss_percent:
            return ExitSignal(
                signal="SELL",
                reason="STOP_LOSS",
                pnl=pnl,
                pnl_percent=pnl_percent
            )
        
        # Signal exit: Bull Power positive (reversal complete)
        if current_bull > 0:
            # Check if it's been positive for 2+ candles (confirmation)
            prev_bull = bull_power.iloc[-2]
            if prev_bull > 0:
                return ExitSignal(
                    signal="SELL",
                    reason="SIGNAL_EXIT",
                    pnl=pnl,
                    pnl_percent=pnl_percent
                )
        
        # Hold position
        return ExitSignal(
            signal="HOLD",
            reason="CONDITIONS_NOT_MET",
            pnl=pnl,
            pnl_percent=pnl_percent
        )


if __name__ == "__main__":
    import numpy as np
    
    print("\n" + "="*70)
    print("🧪 TESTING ELDER REVERSION EXIT MODULE")
    print("="*70)
    
    # Create sample data showing price rising after entry
    dates = pd.date_range(start='2024-01-01', periods=30, freq='15min')
    
    # Entry at 99000, price rises to 101000
    entry_price = 99000
    prices = np.linspace(99000, 101000, 30) + np.random.normal(0, 50, 30)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p - 20 for p in prices],
        'high': [p + 50 for p in prices],
        'low': [p - 50 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 30)
    })
    
    # Test exit module
    exit_module = ElderReversionExit()
    
    # Test at different points
    for i in [10, 20, 29]:
        df_slice = df.iloc[:i+1]
        signal = exit_module.generate_signal(df_slice, entry_price)
        
        print(f"\n📊 Candle {i+1}:")
        print(f"   Signal: {signal.signal}")
        print(f"   Reason: {signal.reason}")
        print(f"   PnL: ${signal.pnl:.2f} ({signal.pnl_percent:.2f}%)")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
