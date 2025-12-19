The code you provided is already free from any `backtesting.lib` imports or functions, which is great! However, I'll ensure that all indicators are properly set up and that the code follows best practices for Moon Dev's trading strategies. Here's the verified and slightly optimized version of your code:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Data preprocessing
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'datetime': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class BandDivergence(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 Moon Dev Indicators Setup
        # Bollinger Bands
        self.bb_mid = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.bb_upper = self.I(lambda c: talib.SMA(c, timeperiod=20) + 2 * talib.STDDEV(c, timeperiod=20), self.data.Close)
        self.bb_lower = self.I(lambda c: talib.SMA(c, timeperiod=20) - 2 * talib.STDDEV(c, timeperiod=20), self.data.Close)
        
        # MACD Line
        def get_macd(close):
            macd, _, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            return macd
        self.macd = self.I(get_macd, self.data.Close)
        
        # Swing Points
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        # Volatility Measure
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        print("🌙✨ Moon Dev Indicators Activated! BB|MACD|SWING|ATR Ready 🚀")

    def next(self):
        # Wait for sufficient data
        if len(self.data) < 20:
            return

        # 🌙 Current Market Conditions
        price = self.data.Close[-1]
        macd_val = self.macd[-1]
        atr_val = self.atr[-1]
        bb_mid_current = self.bb_mid[-1]
        bb_mid_prev = self.bb_mid[-2]

        # 🚀 Long Entry Logic
        if not self.position:
            # Trend confirmation
            higher_high = self.swing_high[-1] > self.swing_high[-2]
            higher_low = self.swing_low[-1] > self.swing_low[-2]
            uptrend = higher_high and higher_low
            
            if (bb_mid_current > bb_mid_prev and
                macd_val > 0 and
                uptrend):
                
                # 🌙 Risk Management
                stop_loss = price - 1.5 * atr_val
                risk_amount = self.equity * self.risk_pct
                position_size = int(round(risk_amount / (price - stop_loss)))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_loss)
                    print(f"🚀🌙 MOON DEV LONG: {self.data.index[-1]} | Size: {position_size} | SL: {stop_loss:.2f}")

        # 🌑 Short Entry Logic
        if not self.position:
            # Volatility contraction
            bb_width = (self.bb_upper[-1] - self.bb_lower[-1])
            bb_width_prev = (self.bb_upper[-2] - self.bb_lower[-2])
            
            # Trend confirmation
            lower_high = self.swing_high[-1] < self.swing_high[-2]
            lower_low = self.swing_low[-1] < self.swing_low[-2]
            downtrend = lower_high and lower_low
            
            if (bb_width < bb_width_prev and