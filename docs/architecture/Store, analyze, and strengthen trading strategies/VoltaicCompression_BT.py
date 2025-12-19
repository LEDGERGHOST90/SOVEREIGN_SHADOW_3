```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Data preparation
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

class VoltaicCompression(Strategy):
    def init(self):
        # Core indicators
        self.ema20 = self.I(talib.EMA, self.data.Close, 20)
        self.atr20 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20)
        self.vol_ma = self.I(talib.SMA, self.data.Volume, 20)
        self.vol_std = self.I(talib.STDDEV, self.data.Volume, 20)
        self.atr14 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        # Trackers for position management
        self.entry_bar = None
        self.highest_close = None
        self.lowest_close = None

    def next(self):
        # Skip early bars without sufficient data
        if len(self.data) < 40: return
        
        # Current market conditions
        close = self.data.Close[-1]
        volume = self.data.Volume[-1]
        ema = self.ema20[-1]
        atr20 = self.atr20[-1]
        upper_keltner = ema + 1.5*atr20
        lower_keltner = ema - 1.5*atr20
        
        # Volatility contraction check
        keltner_width = 3 * atr20
        median_width = np.median([3*x for x in self.atr20[-20:]])
        contraction = keltner_width < median_width
        
        # Volume thresholds
        vol_threshold_high = self.vol_ma[-1] + self.vol_std[-1]
        vol_threshold_low = self.vol_ma[-1] - self.vol_std[-1]
        
        if not self.position:
            # 🌙 Long Entry Logic 🌙
            if (contraction and close > upper_keltner and volume > vol_threshold_high):
                risk_amount = self.equity * 0.01
                atr14 = self.atr14[-1]
                stop_loss = close - 2*atr14
                risk_per_share = close - stop_loss
                
                if risk_per_share > 0:
                    size = int(round(risk_amount / risk_per_share))
                    print(f"🌙✨🚀 MOON ROCKET LONG LAUNCH! Entry: {close:.2f} | Size: {size}")
                    self.buy(size=size, sl=stop_loss)
                    self.entry_bar = len(self.data)-1
                    self.highest_close = close

            # 🌑 Short Entry Logic 🌑
            elif (contraction and close < lower_keltner and volume < vol_threshold_low):
                risk_amount = self.equity * 0.01
                atr14 = self.atr14[-1]
                stop_loss = close + 2*atr14
                risk_per_share = stop_loss - close
                
                if risk_per_share > 0:
                    size = int(round(risk_amount / risk_per_share))
                    print(f"🌑💫☄️ MOON COMET SHORT BLAST! Entry: {close:.2f} | Size: {size}")
                    self.sell(size=size, sl=stop_loss)
                    self.entry_bar = len(self.data)-1
                    self.lowest_close = close
        
        else:
            # 🌕 Position Management 🌕
            if self.position.is_long:
                self.highest_close = max(self.highest_close, close)
                trail_stop = self.highest_close - 3*self.atr14[-1]
                self.position.sl = max(trail_stop, self.position.sl)
                
                # Time-based exit check
                if len(self.data)-1 - self.entry_bar >=