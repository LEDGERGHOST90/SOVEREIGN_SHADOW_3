I'll help fix the code while maintaining the original strategy logic. Here's the corrected version with Moon Dev themed debug prints and proper position sizing:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Data preprocessing
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format columns 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class FractalVolumeBreakout(Strategy):
    risk_pct = 0.01  # 1% risk per trade 🌕
    vma_period = 20
    volume_multiplier = 1.5
    trailing_stop_pct = 0.02  # 2% trailing stop 🌙

    def init(self):
        # Fractal indicators using TA-Lib ✨
        self.max_high = self.I(talib.MAX, self.data.High, timeperiod=5, name='FRACTAL_HIGH')
        self.min_low = self.I(talib.MIN, self.data.Low, timeperiod=5, name='FRACTAL_LOW')
        self.vma = self.I(talib.SMA, self.data.Volume, self.vma_period, name='VMA')
        
        self.last_resistance = None
        self.last_support = None

    def next(self):
        # Need at least 5 bars for reliable indicators 🌙
        if len(self.data) < 5:
            return

        # Update fractal levels with cosmic alignment ✨
        current_max = self.max_high[-1]
        fractal_high = self.data.High[-3]  # 2 bars delay for confirmation
        if fractal_high == current_max:
            self.last_resistance = fractal_high
            print(f"🌙✨ New RESISTANCE formed at {self.last_resistance:.2f}")

        current_min = self.min_low[-1]
        fractal_low = self.data.Low[-3]
        if fractal_low == current_min:
            self.last_support = fractal_low
            print(f"🌙✨ New SUPPORT formed at {self.last_support:.2f}")

        # Cosmic entry signals 🌌
        if not self.position:
            # Long entry: Break resistance with stellar volume 🌠
            if self.last_resistance and self.data.High[-1] > self.last_resistance:
                if self.data.Volume[-1] > self.volume_multiplier * self.vma[-1]:
                    print(f"🚀🌕 BULLISH BREAKOUT! Resistance: {self.last_resistance:.2f}, Volume: {self.data.Volume[-1]:.2f} (VMA: {self.vma[-1]:.2f})")
                    self.enter_long()

            # Short entry: Crash support with meteor volume ☄️
            elif self.last_support and self.data.Low[-1] < self.last_support:
                if self.data.Volume[-1] > self.volume_multiplier * self.vma[-1]:
                    print(f"🚀🌑 BEARISH BREAKOUT! Support: {self.last_support:.2f}, Volume: {self.data.Volume[-1]:.2f} (VMA: {self.vma[-1]:.2f})")
                    self.enter_short()

        # Galactic position management 🌟
        else:
            if self.position.is_long:
                self.manage_long()
            elif self.position.is_short:
                self.manage_short()

    def enter_long(self):
        entry_price = self.last_resistance
        sl_price = entry_price * (1 - 0.01)  # 1% stop loss 🌙
        risk_amount = self.risk_pct * self.equity
        risk_per_unit = entry_price - sl_price
        
        if risk_per_unit <= 0:
            print("🌑 Black hole scenario detected! Avoiding trade.")
            return
            
        position_size = int(round(risk_amount / risk_per_unit))
        if position_size > 0:
            self.buy(size=position_size, sl=sl_price, tag="Moon Launch 🚀")
            print(f"🌕💫 LONG POSITION: {position_size} units