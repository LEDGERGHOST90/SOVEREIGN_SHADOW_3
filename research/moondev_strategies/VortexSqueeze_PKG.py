I'll fix the code by removing all `backtesting.lib` imports and replacing the crossover function with the proper implementation. Here's the corrected version with Moon Dev themed debug prints:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy

# Data preparation
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class VortexSqueeze(Strategy):
    entry_bbw = None  # To track BBW at entry
    
    def init(self):
        # 🌙 Vortex Indicator Calculations
        vi = ta.vi(high=self.data.High, low=self.data.Low, close=self.data.Close, length=14)
        self.vi_plus = self.I(lambda: vi['VIP_14'], name='VI+')
        self.vi_minus = self.I(lambda: vi['VIM_14'], name='VI-')
        
        # ✨ Choppiness Index Filter
        self.ci = self.I(ta.chop, self.data.High, self.data.Low, self.data.Close, length=14, name='CI')
        
        # 🌀 Bollinger Band Width Calculation
        upper, middle, lower = talib.BBANDS(self.data.Close, timeperiod=20)
        bb_width = (upper - lower) / middle
        self.bbw = self.I(lambda: bb_width, name='BBW')
        self.bbw_low = self.I(talib.MIN, bb_width, timeperiod=10, name='BBW_Low')
        
        # 🛡️ Swing High/Low for Stop Loss
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='Swing_High')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='Swing_Low')
        
    def next(self):
        if len(self.data) < 20:  # Ensure enough data
            return
        
        # 🌙 Current indicator values
        vi_plus = self.vi_plus[-1]
        vi_minus = self.vi_minus[-1]
        ci = self.ci[-1]
        bbw = self.bbw[-1]
        bbw_low = self.bbw_low[-1]
        
        # 🚀 Entry/Exit Conditions
        if not self.position:
            # Long Entry Conditions
            if (self.vi_plus[-2] < self.vi_minus[-2] and vi_plus > vi_minus) and ci < 38 and bbw <= bbw_low:
                risk_amount = self.equity * 0.01  # 1% risk
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_low[-1]
                
                if entry_price > stop_loss:
                    position_size = int(round(risk_amount / (entry_price - stop_loss)))
                    self.buy(size=position_size, sl=stop_loss)
                    self.entry_bbw = bbw
                    print(f"🚀🌙 MOONSHOT LONG! | Size: {position_size} | Entry: {entry_price:.2f} | SL: {stop_loss:.2f}")
            
            # Short Entry Conditions
            elif (self.vi_minus[-2] > self.vi_plus[-2] and vi_minus < vi_plus) and ci < 38 and bbw <= bbw_low:
                risk_amount = self.equity * 0.01  # 1% risk
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_high[-1]
                
                if stop_loss > entry_price:
                    position_size = int(round(risk_amount / (stop_loss - entry_price)))
                    self.sell(size=position_size, sl=stop_loss)
                    self.entry_bbw = bbw
                    print(f"🌑🌙 DARK SIDE SHORT! | Size: {position_size} | Entry: {entry_price:.2f} | SL: {stop_loss:.2f}")
        else