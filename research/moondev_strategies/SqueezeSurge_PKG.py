Here's the fixed code with all backtesting.lib imports removed and replaced with proper Moon Dev implementations:

```python
# 🌙 Moon Dev's SqueezeSurge Backtest Implementation ✨
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

class SqueezeSurge(Strategy):
    def init(self):
        # 🌟 Calculate Indicators using TA-Lib
        close = self.data.Close
        volume = self.data.Volume
        
        # Bollinger Bands (20-period, 2 std)
        self.bb_upper, self.bb_middle, self.bb_lower = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        self.I(lambda: self.bb_upper, name='BB_upper')
        self.I(lambda: self.bb_middle, name='BB_middle')
        self.I(lambda: self.bb_lower, name='BB_lower')
        
        # Bollinger Band Width & Percentile
        bb_width = self.bb_upper - self.bb_lower
        self.bb_width_series = pd.Series(bb_width)
        self.bb_width_percentile = self.bb_width_series.rolling(100).quantile(0.2)
        self.I(lambda: self.bb_width_percentile, name='BB_width_pct')
        
        # Volume SMA (10-period)
        self.volume_sma = talib.SMA(volume, timeperiod=10)
        self.I(lambda: self.volume_sma, name='Volume_SMA')
        
        print("🌙 Indicators initialized! Ready to catch those surges! 🚀")

    def next(self):
        current_close = self.data.Close[-1]
        bb_upper = self.data.BB_upper[-1]
        bb_lower = self.data.BB_lower[-1]
        bb_width = self.bb_width_series[-1]
        bb_width_pct = self.bb_width_percentile[-1]
        volume = self.data.Volume[-1]
        vol_sma = self.data.Volume_SMA[-1]

        # 🌙 Entry Conditions
        if not self.position:
            # Long Entry (Breakout with volume surge)
            if (bb_width < bb_width_pct) and (volume > vol_sma * 1.2) and (current_close > bb_upper):
                self.enter_long()
                
            # Short Entry (Breakdown with volume surge)
            elif (bb_width < bb_width_pct) and (volume > vol_sma * 1.2) and (current_close < bb_lower):
                self.enter_short()

    def enter_long(self):
        entry_price = self.data.Close[-1]
        bb_width = self.bb_width_series[-1]
        
        # 🎯 Risk Management
        stop_loss = entry_price - bb_width
        take_profit = entry_price + (bb_width * 1.5)
        risk_per_share = entry_price - stop_loss
        
        # 💰 Position Sizing (1% risk)
        position_size = int(round((0.01 * self.equity) / risk_per_share))
        
        if position_size > 0:
            self.buy(size=position_size, sl=stop_loss, tp=take_profit)
            print(f"🌙✨ LONG ENTRY! Price: {entry_price:.2f}, Size: {position_size} 🚀 SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

    def enter_short(self):
        entry_price = self.data.Close[-1]
        bb_width = self.bb_width_series[-1]
        
        # 🎯 Risk Management
        stop_loss = entry_price + bb_width
        take_profit = entry_price - (bb_width * 1.5)
        risk_per_share = stop_loss - entry_price
        
        # 💰 Position Sizing (1% risk)
        position_size = int(round((0.01 * self.equity) / risk_per_share))
        
        if position_size > 0:
            self.sell(size=position_size, sl=stop_loss, tp=take_profit)
            print(f"🌙✨ SHORT ENTRY! Price: {entry_price:.2f}, Size: {position_size} 🚀 SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

# 🚀 Data Preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data =