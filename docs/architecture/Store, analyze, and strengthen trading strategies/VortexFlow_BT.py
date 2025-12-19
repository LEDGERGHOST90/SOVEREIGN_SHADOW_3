import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class VortexFlow(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Calculate Vortex Indicator
        vi = ta.vortex(
            high=self.data.High, 
            low=self.data.Low, 
            close=self.data.Close, 
            length=14
        )
        self.vi_plus = self.I(lambda: vi['VTX_+'], name='VI+ 🌊')
        self.vi_minus = self.I(lambda: vi['VTX_-'], name='VI- 🌊')
        
        # Calculate Chaikin Money Flow
        cmf = ta.cmf(
            high=self.data.High,
            low=self.data.Low,
            close=self.data.Close,
            volume=self.data.Volume,
            length=20
        )
        self.cmf = self.I(lambda: cmf, name='CMF 💰')
        
        # Swing levels for stop loss
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='Swing High 🔺')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='Swing Low 🔻')
        
    def next(self):
        if len(self.data) < 20:  # Ensure enough data points
            return
            
        vi_p, vi_m = self.vi_plus[-1], self.vi_minus[-1]
        prev_vi_p, prev_vi_m = self.vi_plus[-2], self.vi_minus[-2]
        cmf_val = self.cmf[-1]
        
        # Entry signals
        long_cond = crossover(vi_p, vi_m) and cmf_val > 0
        short_cond = crossover(vi_m, vi_p) and cmf_val < 0
        
        # Moon-themed risk calculation 🌙
        if not self.position:
            if long_cond:
                sl_price = self.swing_low[-1]
                risk = self.data.Close[-1] - sl_price
                if risk > 0:
                    size = int(round((self.risk_per_trade * self.equity) / risk))
                    self.buy(size=size, sl=sl_price)
                    print(f"🚀🌕 MOON ROCKET LONG! Size: {size} | Entry: {self.data.Close[-1]:.2f} | SL: {sl_price:.2f}")
                    
            elif short_cond:
                sl_price = self.swing_high[-1]
                risk = sl_price - self.data.Close[-1]
                if risk > 0:
                    size = int(round((self.risk_per_trade * self.equity) / risk))
                    self.sell(size=size, sl=sl_price)
                    print(f"🌑🌗 MOON ECLIPSE SHORT! Size: {size} | Entry: {self.data.Close[-1]:.2f} | SL: {sl_price:.2f}")
        
        # Exit signals
        else:
            if self.position.is_long and crossover(vi_m, vi_p):
                self.position.close()
                print(f"🌙✨ CLOSING LONG: Vortex Reversal Detected!")
            elif self.position.is_short and crossover(vi_p, vi_m):
                self.position.close()
                print(f"🌙✨ CLOSING SHORT: Vortex Reversal Detected!")

# Data preparation
data = pd.read_csv("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Launch Moon Dev Backtest 🚀
bt = Backtest(data, VortexFlow, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)
print(stats._strategy)