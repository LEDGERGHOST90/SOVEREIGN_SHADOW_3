Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed debug prints added:

```python
# -*- coding: utf-8 -*-
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import pandas_ta as ta
import numpy as np

class LiquidityBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    rr_ratio = 2  # Risk:Reward ratio
    
    def init(self):
        # Calculate indicators using TA-Lib through self.I()
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='🌙 SWING HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='🌑 SWING LOW')
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='📊 VOL SMA')
        self.sma50 = self.I(talib.SMA, self.data.Close, timeperiod=50, name='📈 SMA50')
        
    def next(self):
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Moon Dev debug prints ✨
        print(f"\n🌕 Moon Dev Debug | Close: {current_close:.2f} | Volume: {current_volume:.2f}")
        print(f"✨ Swing High: {self.swing_high[-1]:.2f} | Swing Low: {self.swing_low[-1]:.2f}")
        print(f"📈 Trend Filter SMA50: {self.sma50[-1]:.2f}")

        if not self.position:
            # Long entry condition 🌙
            if (current_close > self.swing_high[-1] 
                and current_volume > self.volume_sma[-1]
                and current_close > self.sma50[-1]):
                
                sl_price = self.swing_low[-1]
                risk_per_share = current_close - sl_price
                
                if risk_per_share > 0:
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        tp_price = current_close + self.rr_ratio * risk_per_share
                        self.buy(size=position_size, 
                                sl=sl_price,
                                tp=tp_price,
                                tag="🌙 LONG BREAKOUT")
                        print(f"🚀 MOON LAUNCH! LONG {position_size} units")
                        print(f"🎯 TP: {tp_price:.2f} | 🛑 SL: {sl_price:.2f}")

            # Short entry condition 🌑
            elif (current_close < self.swing_low[-1]
                  and current_volume > self.volume_sma[-1]
                  and current_close < self.sma50[-1]):
                
                sl_price = self.swing_high[-1]
                risk_per_share = sl_price - current_close
                
                if risk_per_share > 0:
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        tp_price = current_close - self.rr_ratio * risk_per_share
                        self.sell(size=position_size,
                                 sl=sl_price,
                                 tp=tp_price,
                                 tag="🌑 SHORT BREAKOUT")
                        print(f"🌒 DARK SIDE ENTRY! SHORT {position_size} units")
                        print(f"🎯 TP: {tp_price:.2f} | 🛑 SL: {sl_price:.2f}")

# Data preparation 🌙
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Run backtest 🚀
bt = Backtest(data, LiquidityBreakout, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n🌕🌖🌗