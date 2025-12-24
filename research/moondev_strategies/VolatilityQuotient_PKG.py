Here's the fixed code with all backtesting.lib imports removed and crossover conditions properly replaced:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Define data path and load data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path)

# Clean and prepare data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Date'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class VolatilityQuotient(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    max_exposure = 0.2  # 20% portfolio limit
    trailing_stop_pct = 0.02  # 2% trailing stop
    
    def init(self):
        super().init()
        
        # Calculate indicators
        self.log_ret = self.I(self._log_returns, self.data.Close, name='Log_Returns')
        self.hv_10 = self.I(talib.STDDEV, self.log_ret, 10, name='HV_10')
        self.hv_ma = self.I(talib.SMA, self.hv_10, 20, name='HV_MA_20')
        self.rsi = self.I(talib.RSI, self.data.Close, 5, name='RSI_5')
        self.sma_200 = self.I(talib.SMA, self.data.Close, 200, name='SMA_200')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='Swing_Low')
        
        self.trail_active = False
        self.trail_peak = 0

    @staticmethod
    def _log_returns(close):
        lr = np.zeros_like(close)
        for i in range(1, len(close)):
            lr[i] = np.log(close[i] / close[i-1])
        return lr
    
    def next(self):
        price = self.data.Close[-1]
        
        # Exit conditions
        if self.position:
            # Trailing stop check
            if self.trail_active:
                self.trail_peak = max(self.trail_peak, self.data.High[-1])
                if price < self.trail_peak * (1 - self.trailing_stop_pct):
                    self.position.close()
                    print(f"🌙✨ Trailing stop hit at {price:.2f}!")
                    self.trail_active = False
                    return
                
            # RSI exit - replaced crossover with direct comparison
            if self.rsi[-2] < 70 and self.rsi[-1] > 70:
                self.position.close()
                print(f"🌙🚨 RSI Exit at {price:.2f}")
                self.trail_active = False
            
            # Volatility expansion exit - replaced crossover with direct comparison
            if self.hv_10[-2] < self.hv_ma[-2] and self.hv_10[-1] > self.hv_ma[-1]:
                self.position.close()
                print(f"🌙⚡ HV Exit at {price:.2f}")
                self.trail_active = False
        
        # Entry conditions
        if not self.position and len(self.data) > 200:
            # Volatility contraction - already using direct comparison
            hv_cross = (self.hv_10[-2] > self.hv_ma[-2]) and (self.hv_10[-1] < self.hv_ma[-1])
            trend_filter = price > self.sma_200[-1]
            
            if hv_cross and trend_filter:
                sl_price = self.swing_low[-1]
                risk_per_share = price - sl_price
                
                if risk_per_share <= 0:
                    print("🌙⚠️ Invalid SL, skip entry")
                    return
                
                # Position sizing
                risk_amount = self.equity * self.risk_pct
                size_by_risk = risk_amount / risk_per_share
                size_by_exposure = (self.equity * self.max_exposure) / price
                size = int(round(min(size_by_risk, size_by_exposure)))
                
                if size