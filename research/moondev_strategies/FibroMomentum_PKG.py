I'll help you fix the code by removing the `backtesting.lib` import and replacing the crossover logic. Here's the corrected version with Moon Dev themed debug prints:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# Load and clean data
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

class FibroMomentum(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    atr_multiplier = 1.5
    rsi_period = 14
    swing_period = 50

    def init(self):
        # Core indicators 🌙
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period, name='SWING HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period, name='SWING LOW')
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period, name='RSI')
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9, name='MACD')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR')
        self.hammer = self.I(talib.CDLHAMMER, self.data.Open, self.data.High, self.data.Low, self.data.Close, name='HAMMER')
        
        # Trend confirmation ✨
        self.sma50 = self.I(talib.SMA, self.data.Close, 50, name='SMA50')
        self.sma200 = self.I(talib.SMA, self.data.Close, 200, name='SMA200')

    def next(self):
        # Skip early bars with incomplete data 🌙
        if len(self.data.Close) < 200 or len(self.swing_high) < 2:
            return

        # Calculate Fibonacci levels from latest swing points 🔭
        swing_high = self.swing_high[-1]
        swing_low = self.swing_low[-1]
        fib_diff = swing_high - swing_low
        fib_levels = np.array([0.382, 0.5, 0.618]) * fib_diff + swing_low

        # Current market conditions 🌡️
        price = self.data.Close[-1]
        in_downtrend = self.sma50[-1] < self.sma200[-1]
        near_fib = any(abs(price - level)/level < 0.005 for level in fib_levels)
        
        # Entry checklist conditions ✅
        bearish_momentum = (self.rsi[-1] < 50) and (self.macd[-1] < self.macd_signal[-1])
        reversal_signal = self.hammer[-1] > 0

        # Moon Dev Entry Signal 🌕🚀
        if not self.position and in_downtrend and near_fib and bearish_momentum and reversal_signal:
            atr_value = self.atr[-1]
            stop_loss = price - self.atr_multiplier * atr_value
            risk_amount = self.equity * self.risk_pct
            position_size = risk_amount / (self.atr_multiplier * atr_value)
            
            self.buy(
                size=int(round(position_size)),
                sl=stop_loss,
                tag=f"🌙 FIBRO ENTRY | SL: {stop_loss:.1f}"
            )
            print(f"🚀 MOON SHOT! Entry: {price:.1f} | Size: {int(position_size)} | ATR: {atr_value:.1f}")

        # Exit management 🌘
        if self.position:
            # Check RSI divergence 📉
            if len(self.rsi) > 5:
                current_low = min(self.data.Low[-3:])
                current_rsi = min(self.rsi[-3:])
                prev_low = min(self.data.Low[-6:-3])