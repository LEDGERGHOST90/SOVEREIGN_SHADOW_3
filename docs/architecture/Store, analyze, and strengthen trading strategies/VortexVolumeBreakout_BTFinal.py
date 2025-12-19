```python
# 🌙 Moon Dev's VortexVolumeBreakout Strategy 🌙
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
import numpy as np

# Data preprocessing moon magic ✨
def prepare_data(path):
    data = pd.read_csv(path)
    # Cleanse column names
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Cosmic column alignment 🌌
    column_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    data = data.rename(columns=column_map)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    return data

# Load lunar data 🚀
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = prepare_data(data_path)

class VortexVolumeBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌗 Vortex Indicator Configuration
        self.vi_plus = self.I(talib.VORTEX, self.data.High, self.data.Low, self.data.Close, 
                             timeperiod=14, name='VI+', which=0)
        self.vi_minus = self.I(talib.VORTEX, self.data.High, self.data.Low, self.data.Close,
                              timeperiod=14, name='VI-', which=1)
        
        # 📈 Elder's Volume Force Calculation
        mom = self.I(talib.MOM, self.data.Close, timeperiod=1, name='MOM1')
        self.volume_force = self.I(lambda: mom * self.data.Volume, name='VolumeForce')
        self.vf_ema = self.I(talib.EMA, self.volume_force, timeperiod=20, name='VF_EMA')
        
        # 🔍 Volatility and Price Levels
        self.avg_volume = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='AvgVolume')
        self.recent_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='RecentHigh')
        self.recent_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='RecentLow')
        
        # 🌀 KST Momentum Configuration
        kst = ta.kst(self.data.Close, roc1=10, roc2=15, roc3=20, roc4=30,
                    ema1=10, ema2=10, ema3=10, ema4=15, signal=288)
        self.kst_line = self.I(lambda: kst.iloc[:,0], name='KST')
        self.kst_ema = self.I(lambda: kst.iloc[:,1], name='KST_EMA')
        
    def next(self):
        # 🌑 Moon-powered debug console
        print(f"🌙 Current Price: {self.data.Close[-1]:.2f} | VI+:{self.vi_plus[-1]:.2f} VI-:{self.vi_minus[-1]:.2f}")
        
        # 🚨 Entry Conditions
        if not self.position:
            # Long Entry Constellation 🌠
            if (self.vi_plus[-2] < self.vi_minus[-2] and self.vi_plus[-1] > self.vi_minus[-1]) and \
               (self.volume_force[-1] > self.vf_ema[-1]) and \
               (self.data.Volume[-1] > 2 * self.avg_volume[-1]) and \
               (self.data.Close[-1] > self.recent_high[-1]):
                
                sl_price = self.recent_low[-1]
                risk_per_share = self.data.Close[-1] - sl_price
                if risk_per_share <= 0: return
                
                position_size = int(round((self.equity * self.risk_per_trade) / risk_per_share))
                if position_size > 0:
                    self.buy(size=position_size, sl=sl_price)
                    print(f"🚀🌕 BULLISH BREAKOUT! Entry: {self.data.Close[-1]:.2f} | Size: {position_size} | SL: {sl_price:.2f}")