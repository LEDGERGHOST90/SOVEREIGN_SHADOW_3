I'll fix the code by removing all `backtesting.lib` imports and replacing any usage of `crossover` or `crossunder` with manual implementations. Here's the corrected version with Moon Dev themed debug prints:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR VOLDELTABREAKOUT STRATEGY 🚀✨

import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# DATA PREPARATION 🌙✨
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Convert and set datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolDeltaBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌙
    consecutive_losses = 0
    entry_bar = None
    
    def init(self):
        # 🌙 VWAP Calculation (Cumulative)
        typical_price = (self.data.High + self.data.Low + self.data.Close) / 3
        tpv = typical_price * self.data.Volume
        cumulative_tpv = tpv.cumsum()
        cumulative_vol = self.data.Volume.cumsum()
        self.vwap = self.I(lambda: cumulative_tpv / cumulative_vol, name='VWAP')
        
        # 🚀 ATR Calculation
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR')
        
        # 🌊 Volume Delta Calculation
        volume_delta = np.where(self.data.Close > self.data.Open, self.data.Volume,
                               np.where(self.data.Close < self.data.Open, -self.data.Volume, 0))
        self.volume_delta = self.I(lambda: volume_delta, name='VolumeDelta')
        self.volume_delta_ma = self.I(talib.SMA, self.volume_delta, 20, name='VolumeDelta_MA')
        
    def next(self):
        # 🌑 Risk Management: Check consecutive losses
        if self.consecutive_losses >= 3:
            print("🌑🌙 MOON DEV RISK ALERT: 3 consecutive losses - pausing trades")
            return
            
        # 🚀 Entry Logic
        if not self.position:
            # Previous period values
            prev_vwap = self.vwap[-2]
            prev_atr = self.atr[-2]
            upper_band = prev_vwap + 2 * prev_atr
            lower_band = prev_vwap - 2 * prev_atr
            
            # Long Entry Conditions 🌙
            if self.data.Close[-2] > upper_band:
                vol_delta = self.volume_delta[-2]
                vol_delta_ma = self.volume_delta_ma[-2]
                if vol_delta >= vol_delta_ma * 1.25 and vol_delta_ma != 0:
                    self.enter_long()
                    print(f"🚀🌙 MOON DEV LONG ENTRY | Price: {self.data.Close[-1]:.2f}")
            
            # Short Entry Conditions 🌑
            elif self.data.Close[-2] < lower_band:
                vol_delta = self.volume_delta[-2]
                vol_delta_ma = self.volume_delta_ma[-2]
                if vol_delta <= vol_delta_ma * 0.75 and vol_delta_ma != 0:
                    self.enter_short()
                    print(f"🌑🌙 MOON DEV SHORT ENTRY | Price: {self.data.Close[-1]:.2f}")
        
        # ✨ Exit Logic
        else:
            current_vwap = self.vwap[-1]
            current_atr = self.atr[-1]
            
            # Long Exit
            if self.position.is_long:
                lower_band = current_vwap - 2 * current_atr
                if (self.data.Close[-1] < current_vwap) or (self.data.Low[-1] <= lower_band):
                    self.position.close()
                    print(f"🌑🌙 MOON DEV LONG EXIT | Price: {self.data.Close[-1]: