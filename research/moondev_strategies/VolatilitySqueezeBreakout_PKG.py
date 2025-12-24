Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed indicators:

```python
# 🌙 Moon Dev's Volatility Squeeze Breakout Backtest 🌙
import numpy as np
import pandas as pd
import talib
from backtesting import Strategy, Backtest

# Clean and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class VolatilitySqueezeBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌙
    
    def init(self):
        # 🌙 Calculate indicators with TA-Lib
        close = self.data.Close
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, close, timeperiod=20, nbdevup=2, nbdevdn=2)
        bb_width = self.upper - self.lower
        self.bb_width = self.I(lambda: bb_width, name='BB_Width')
        
        # 🌙 Historical BB Width Percentile (20th percentile over 100 periods)
        def calc_percentile(arr):
            result = np.full_like(arr, np.nan)
            for i in range(100, len(arr)):
                result[i] = np.percentile(arr[i-100:i], 20)
            return result
        self.bb_width_pct = self.I(calc_percentile, bb_width, name='BB_Width_Pct')
        
        # 🌙 Volume indicators
        self.vol_median = self.I(talib.MEDIAN, self.data.Volume, timeperiod=20, name='Vol_Median')
        
        print("🌙✨ Strategy Initialized with Moon Power! ✨🌙")

    def next(self):
        price = self.data.Close[-1]
        
        # 🌙 Entry Conditions
        long_cond = (price > self.upper[-1] and 
                    self.bb_width[-1] < self.bb_width_pct[-1] and 
                    self.data.Volume[-1] > self.vol_median[-1])
        
        short_cond = (price < self.lower[-1] and 
                     self.bb_width[-1] < self.bb_width_pct[-1] and 
                     self.data.Volume[-1] > self.vol_median[-1])

        # 🌙 Position Sizing & Risk Management
        if not self.position:
            if long_cond:
                stop_loss = self.data.Low[-1]
                risk_amount = self.risk_per_trade * self.equity
                risk_per_share = price - stop_loss
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_loss)
                    print(f"🚀🌙 MOON BLASTOFF! LONG {position_size} @ {price:.2f} | SL: {stop_loss:.2f}")
            
            elif short_cond:
                stop_loss = self.data.High[-1]
                risk_amount = self.risk_per_trade * self.equity
                risk_per_share = stop_loss - price
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_loss)
                    print(f"🌧️🌙 SHORT SURGE! {position_size} @ {price:.2f} | SL: {stop_loss:.2f}")
        
        # 🌙 Trailing Stop Logic
        else:
            if self.position.is_long:
                new_sl = max(self.position.sl, self.data.High[-1] - (self.upper[-1] - self.lower[-1]))
                self.position.sl = new_sl
            elif self.position.is_short:
                new_sl = min(self.position.sl, self.data.Low[-1] + (self.upper[-1] - self.lower[-1]))
                self.position.sl = new_sl

# 🌙 Launch Backtest
bt = Backtest(data, VolatilitySqueezeBreakout, cash=1_000_000, commission=.002)
stats