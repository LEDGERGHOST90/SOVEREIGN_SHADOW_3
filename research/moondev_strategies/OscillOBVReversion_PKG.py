Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed indicators:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR OSCILLOBV REVERSION STRATEGY 🚀

import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# 🌌 DATA PREPARATION
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Cleanse and align cosmic data energies 🌠
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class OscillOBVReversion(Strategy):
    def init(self):
        # 🌗 COSMIC INDICATORS
        # Bollinger Bands with %B calculation
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0, name='BB_upper', index=0)
        self.bb_middle = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0, name='BB_middle', index=1)
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0, name='BB_lower', index=2)
        
        # 🌊 On-Balance Volume
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume, name='OBV')
        
        # 🌀 Volume-Weighted Moving Averages
        close_volume = self.data.Close * self.data.Volume
        self.vwma_short = self.I(lambda: talib.SMA(close_volume, 5)/talib.SMA(self.data.Volume, 5), name='VWMA_5')
        self.vwma_long = self.I(lambda: talib.SMA(close_volume, 20)/talib.SMA(self.data.Volume, 20), name='VWMA_20')
        
        # ⚡ Volatility Measure
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR_14')
        
        # 🌑 Swing Highs/Lows
        self.swing_low = self.I(talib.MIN, self.data.Low, 14, name='Swing_Low_14')
        self.swing_high = self.I(talib.MAX, self.data.High, 14, name='Swing_High_14')

    def next(self):
        # 🌓 REQUIRED COSMIC ALIGNMENTS
        if len(self.data.Close) < 20 or len(self.obv) < 2:
            return
            
        # 🌕 CURRENT STAR ALIGNMENTS
        close = self.data.Close[-1]
        bb_upper = self.bb_upper[-1]
        bb_lower = self.bb_lower[-1]
        percent_b = (close - bb_lower)/(bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0
        
        # 🌗 OBV DIVERGENCE DETECTION
        current_low, prev_low = self.data.Low[-1], self.data.Low[-2]
        current_obv, prev_obv = self.obv[-1], self.obv[-2]
        bullish_div = current_low < prev_low and current_obv > prev_obv
        bearish_div = self.data.High[-1] > self.data.High[-2] and current_obv < prev_obv
        
        # 🌀 VOLUME TREND ANALYSIS
        vwma_short_trend = self.vwma_short[-1] > self.vwma_short[-2]

        # 🚀 ENTRY PROTOCOLS
        if not self.position:
            # 🌙 LONG ENTRY CONDITIONS
            if percent_b <= 0.2 and bullish_div and vwma_short_trend:
                sl_price = self.swing_low[-1] - self.atr[-1]
                risk_amount = 0.01 * self.equity
                position_size = int(round(risk_amount / (close - sl_price)))
                
                if position_size > 0: