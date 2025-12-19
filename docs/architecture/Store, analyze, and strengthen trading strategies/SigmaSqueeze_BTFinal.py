Here's the fully debugged and Moon Dev themed version of your SigmaSqueeze strategy:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

# Load and preprocess data with Moon Dev magic ✨
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv', 
                   parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class SigmaSqueeze(Strategy):
    def init(self):
        # Volatility components powered by Moon Dev analytics 🌙
        self.mean_close = self.I(talib.SMA, self.data.Close, timeperiod=20, name='20 SMA')
        self.std_dev = self.I(talib.STDDEV, self.data.Close, timeperiod=20, nbdev=1, name='20 STD')
        self.lower_band = self.I(lambda: self.mean_close - 3*self.std_dev, name='3σ Lower')
        
        # Volume spike detection with lunar precision 🌕
        self.vol_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='Vol MA20')
        
        # Bollinger Band contraction analysis
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close, 
                                                              timeperiod=20, nbdevup=2, nbdevdn=2, 
                                                              matype=0, name='BBANDS')
        self.bb_width = self.I(lambda: (self.bb_upper - self.bb_lower)/self.bb_middle, name='BB Width')
        self.bb_width_min = self.I(talib.MIN, self.bb_width, timeperiod=10, name='BB Width Min')
        
        # Exit indicators with cosmic accuracy 🌌
        typical_price = (self.data.High + self.data.Low + self.data.Close)/3
        tpv = typical_price * self.data.Volume
        self.vwap = self.I(lambda: tpv.cumsum()/self.data.Volume.cumsum(), name='VWAP')
        self.vwap_ma = self.I(talib.SMA, self.vwap, timeperiod=20, name='VWAP MA20')
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14, name='RSI14')
        
        # Risk management with Moon Dev safeguards 🛡️
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14, name='ATR14')
        
        print("🌙✨ Moon Dev Sigma Squeeze Strategy Activated! 🚀")
        print("✨ All indicators powered by pure Moon magic! 🌙")

    def next(self):
        price = self.data.Close[-1]
        
        # Entry conditions with lunar precision 🌕
        if not self.position:
            sigma_trigger = price < self.lower_band[-1]
            volume_spike = self.data.Volume[-1] > 2*self.vol_ma[-1]
            bb_squeeze = self.bb_width[-1] < self.bb_width_min[-1]
            
            if sigma_trigger and volume_spike and bb_squeeze:
                # Risk calculations with Moon Dev precision 🎯
                risk_amount = self.equity * 0.01  # 1% risk per trade
                atr_value = self.atr[-1]
                stop_distance = 2 * atr_value
                
                if stop_distance > 0:
                    position_size = int(round(risk_amount / stop_distance))
                    if position_size > 0:
                        stop_price = price - stop_distance
                        self.buy(size=position_size, sl=stop_price)
                        print(f"🚀🌙 MOON SHOT! Long {position_size} units at {price:.2f} | SL: {stop_price:.2f} ✨")
                        print("🌌 Powered by pure Moon Dev signal generation!")
        
        # Exit conditions with cosmic timing 🌠
        else:
            # Manual VWAP crossover detection
            vwap_cross = (self.vwap[-2] < self.vwap_ma[-2]) and (self.vwap[-