```python
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

# Data Handling
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and prepare columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class VortexChaikinFlow(Strategy):
    cmf_period = 20
    kc_ema_period = 20
    kc_atr_period = 20
    kc_multiplier = 2
    swing_period = 20
    risk_pct = 0.01  # 1% risk per trade
    
    def init(self):
        # Vortex Indicator
        self.vi_plus, self.vi_minus = self.I(talib.VORTEX, 
                                            self.data.High, 
                                            self.data.Low, 
                                            self.data.Close, 
                                            timeperiod=14, 
                                            name=['VI+', 'VI-'])
        
        # Chaikin Money Flow
        self.cmf = self.I(talib.CMF, 
                         self.data.High, 
                         self.data.Low, 
                         self.data.Close, 
                         self.data.Volume,
                         timeperiod=self.cmf_period,
                         name='CMF')
        
        # Keltner Channel Components
        self.ema20 = self.I(talib.EMA, self.data.Close, self.kc_ema_period, name='EMA20')
        self.atr20 = self.I(talib.ATR, 
                           self.data.High, 
                           self.data.Low, 
                           self.data.Close,
                           self.kc_atr_period,
                           name='ATR20')
        self.upper_kc = self.I(lambda: self.ema20 + self.kc_multiplier * self.atr20,
                              name='Upper KC')
        self.lower_kc = self.I(lambda: self.ema20 - self.kc_multiplier * self.atr20,
                              name='Lower KC')
        
        # Swing High/Low for Stop Loss
        self.swing_high = self.I(talib.MAX, 
                                self.data.High, 
                                self.swing_period,
                                name='Swing High')
        self.swing_low = self.I(talib.MIN,
                               self.data.Low,
                               self.swing_period,
                               name='Swing Low')
        
        print("🌙✨ VortexChaikinFlow Strategy Activated with Lunar Precision! 🚀")

    def next(self):
        equity = self.equity()
        price = self.data.Close[-1]
        
        # Long Entry Logic
        if not self.position and crossover(self.vi_plus, self.vi_minus) and self.cmf[-1] > 0.05:
            sl_price = self.swing_low[-1]
            risk_per_share = price - sl_price
            if risk_per_share > 0:
                size = int(round((equity * self.risk_pct) / risk_per_share))
                self.buy(size=size, sl=sl_price, tag='🌙 Long Entry')
                print(f"🚀 BUY SIGNAL: {size} units at {price:.2f} | SL: {sl_price:.2f}")
        
        # Short Entry Logic
        if not self.position and crossover(self.vi_minus, self.vi_plus) and self.cmf[-1] < -0.05:
            sl_price = self.swing_high[-1]
            risk_per_share = sl_price - price
            if risk_per_share > 0:
                size = int(round((equity * self.risk_pct) / risk_per_share))
                self.sell(size=size, sl=sl_price, tag='🌑 Short Entry')
                print(f"🌒 SELL SIGNAL: {size} units at {price:.2f} | SL: {sl_price:.2f}")
                
        # Exit Logic
        if self.position:
            if self.position.is_long:
                if self.data.High[-1] >= self.upper_kc[-1]:
                    self.position.close()
                    print(f"🌕 EXIT LONG: Price touched Upper KC {self.upper_kc[-1]:.2f}")
                elif