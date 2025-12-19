I'll help fix the code by removing all `backtesting.lib` dependencies and ensuring proper indicator usage. Here's the corrected version:

```python
# 🌙 Moon Dev's CoTrendalNeutral Backtest 🌙
from backtesting import Backtest, Strategy
import pandas as pd
import talib

# Data Preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
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

class CoTrendalNeutral(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Trend Indicators
        self.sma50 = self.I(talib.SMA, self.data.Close, timeperiod=50, name='SMA50')
        self.sma200 = self.I(talib.SMA, self.data.Close, timeperiod=200, name='SMA200')
        
        # Volatility Indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR')
        self.atr_ma = self.I(talib.SMA, self.atr, timeperiod=14, name='ATR_MA')
        
        # Swing Levels
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='Swing High')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='Swing Low')
        
        print("✨ Moon Dev Indicators Initialized! Ready for Launch 🚀")

    def next(self):
        price = self.data.Close[-1]
        
        # Trend Conditions
        uptrend = price > self.sma50[-1] and self.sma50[-1] > self.sma200[-1]
        downtrend = price < self.sma50[-1] and self.sma50[-1] < self.sma200[-1]
        
        # Volatility Conditions
        vol_decreasing = self.atr[-1] < self.atr_ma[-1]
        vol_increasing = self.atr[-1] > self.atr_ma[-1]
        
        if not self.position:
            # Long Entry Logic
            if uptrend and vol_decreasing:
                sl = self.swing_low[-1]
                risk_per_share = price - sl
                if risk_per_share > 0:
                    tp = price + 3*risk_per_share
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl, tp=tp)
                        print(f"🌙🚀 MOON SHOT LONG! Entry: {price:.2f}, Size: {position_size}, SL: {sl:.2f}, TP: {tp:.2f}")

            # Short Entry Logic        
            elif downtrend and vol_increasing:
                sl = self.swing_high[-1]
                risk_per_share = sl - price
                if risk_per_share > 0:
                    tp = price - 3*risk_per_share
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=sl, tp=tp)
                        print(f"🌙📉 BLACK HOLE SHORT! Entry: {price:.2f}, Size: {position_size}, SL: {sl:.2f}, TP: {tp:.2f}")

        else:
            # Moon Gravity Exit Check 🌕
            if self.position.is_long and ((self.sma50[-2] > self.data.Close[-2] and self.sma50[-1] < self.data.Close[-1]) or vol_increasing):
                self.position.close()
                print(f"🌕🌌 LONG GRAVITY EXIT at {price:.2f}")
            elif self.position.is_short and ((self.data.Close[-2] > self.sma50[-2] and self