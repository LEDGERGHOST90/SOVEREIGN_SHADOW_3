Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed indicators:

```python
# 🌙 Moon Dev's VolumetricCross Backtest Script 🚀✨

import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

class VolumetricCross(Strategy):
    ema50_period = 50
    ema200_period = 200
    rsi_period = 14
    volume_avg_period = 20
    swing_low_period = 20
    atr_period = 14
    risk_percent = 0.01  # 1% risk per trade
    volume_spike_multiplier = 1.5

    def init(self):
        # 🌙 Calculate indicators using TA-Lib (Moon-Approved Indicators Only)
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema50_period)
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema200_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.volume_avg = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_avg_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_low_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)

    def next(self):
        # ✨ Moon Dev Debugging Tools
        price = self.data.Close[-1]
        # print(f"🌙 Current Price: {price} | EMA50: {self.ema50[-1]:.2f} | EMA200: {self.ema200[-1]:.2f} | RSI: {self.rsi[-1]:.2f}")

        if not self.position:
            # 🌙 Check for Golden Cross entry conditions (No backtesting.lib allowed!)
            golden_cross = (self.ema50[-2] < self.ema200[-2]) and (self.ema50[-1] > self.ema200[-1])
            volume_spike = self.data.Volume[-1] > (self.volume_avg[-1] * self.volume_spike_multiplier)
            
            if golden_cross and volume_spike:
                # 🚀 Calculate position sizing with Moon Risk Management
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_low[-1]
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share <= 0:
                    print(f"🌙✨ Aborting entry - Negative risk detected! Entry: {entry_price} | SL: {stop_loss}")
                    return
                
                risk_amount = self.risk_percent * self.equity
                position_size = int(round(risk_amount / risk_per_share))
                atr_trailing = self.atr[-1] * 2
                
                if position_size > 0:
                    self.buy(
                        size=position_size,
                        sl=entry_price - atr_trailing,  # 🌙 Manual trailing stop implementation
                        tag="MoonDev_VolCross"
                    )
                    print(f"🚀🌕 MOON ENTRY! Size: {position_size} @ {entry_price} | SL: {stop_loss} | Trailing ATR: {atr_trailing:.2f} 🌊")

        else:
            # 🌙 Check RSI exit condition
            if self.rsi[-1] < 70 and self.rsi[-2] >= 70:
                self.position.close()
                print(f"🌙✨ RSI EXIT! Closing @ {price} | Profit: {self.position.pl_pct:.2%} 🌗")

# 🌙 Data Preparation Ritual
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# 🌙 Launch Backtest
bt = Backtest(
    data,
    VolumetricCross