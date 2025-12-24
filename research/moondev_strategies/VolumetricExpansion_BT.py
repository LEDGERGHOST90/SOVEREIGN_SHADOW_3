```python
# 🌙 Moon Dev's VolumetricExpansion Backtest 🌙
import pandas as pd
import numpy as np
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Data preparation function
def prepare_data(path):
    # Load and clean data
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Column mapping with proper case
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    # Convert datetime and set index
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data

class VolumetricExpansion(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    atr_multiplier = 3
    obv_period = 10
    
    def init(self):
        # 🌙 Calculate Indicators using TA-Lib
        # Bollinger Bands
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, 
                                                    self.data.Close, 
                                                    timeperiod=20, 
                                                    nbdevup=2, nbdevdn=2, matype=0)
        
        # BB Width calculations
        bb_width = (self.upper - self.lower) / self.middle
        self.bb_width_avg = self.I(talib.SMA, bb_width, timeperiod=20)
        self.bb_width_std = self.I(talib.STDDEV, bb_width, timeperiod=20)
        self.bb_width_threshold = self.bb_width_avg + 2*self.bb_width_std
        
        # On-Balance Volume
        self.obv = self.I(ta.obv, self.data.Close, self.data.Volume)
        self.obv_high = self.I(talib.MAX, self.obv, timeperiod=self.obv_period)
        
        # ATR for trailing stop
        self.atr = self.I(talib.ATR, 
                         self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=14)
        
        # Track trade parameters
        self.trailing_stop = None
        self.peak_price = None

    def next(self):
        current_price = self.data.Close[-1]
        
        # 🌟 Moon Dev Debug Prints 🌟
        print(f"\n🌕 Moon Dev Status: Bar {len(self.data)-1}")
        print(f"   Close: {current_price:.2f} | BB Width: {(self.upper[-1]-self.lower[-1])/self.middle[-1]:.4f}")
        print(f"   OBV: {self.obv[-1]:.2f} vs High: {self.obv_high[-1]:.2f}")
        print(f"   ATR: {self.atr[-1]:.2f} | Equity: {self.equity:,.2f}")

        # Exit logic
        if self.position:
            self.peak_price = max(self.peak_price, self.data.High[-1])
            self.trailing_stop = self.peak_price - self.atr_multiplier * self.atr[-1]
            
            if self.data.Close[-1] < self.trailing_stop:
                print(f"🚨 MOON EXIT SIGNAL 🚨 | Price: {current_price:.2f} < Trailing Stop: {self.trailing_stop:.2f}")
                self.position.close()
                self.trailing_stop = None
                self.peak_price = None

        # Entry conditions
        else:
            bb_current_width = (self.upper[-1] - self.lower[-1]) / self.middle[-1]
            bb_condition = bb_current_width > self.bb_width_threshold[-1]
            obv_condition = self.obv[-1] > self.obv_high[-2]  # New 10-period high
            
            if bb_condition and obv_condition:
                print(f"\n🚀 MOON ENTRY SIGNAL 🚀")
                print(f"   BB Width: {bb_current_width:.4f} > Threshold: {self.bb_width_threshold[-1]:.4f}")
                print(f"   OBV: {self.obv[-1]:.2f} > Previous High: {self