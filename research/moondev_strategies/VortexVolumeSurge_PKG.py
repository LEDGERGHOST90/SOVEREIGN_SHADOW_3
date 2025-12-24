Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed debug prints added:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np

class VortexVolumeSurge(Strategy):
    risk_per_trade = 0.01  # 1% of equity per trade
    
    def init(self):
        # Calculate indicators using TA-Lib with self.I()
        self.vi_plus, self.vi_minus = self.I(talib.VORTEX, 
                                            self.data.High, 
                                            self.data.Low, 
                                            self.data.Close, 
                                            timeperiod=14, 
                                            name='Vortex')
        
        self.volume_sma = self.I(talib.SMA, 
                                self.data.Volume, 
                                timeperiod=20, 
                                name='Volume SMA')
        
        self.atr = self.I(talib.ATR, 
                         self.data.High, 
                         self.data.Low, 
                         self.data.Close, 
                         timeperiod=14, 
                         name='ATR')
        
        # Track trade parameters
        self.trailing_stop = None
        self.highest_high = None

    def next(self):
        current_close = self.data.Close[-1]
        
        # Moon Dev Debug Prints 🌙
        print(f"🌙 Current Close: {current_close:.2f} | VI+ {self.vi_plus[-1]:.2f} vs VI- {self.vi_minus[-1]:.2f}")
        print(f"📈 Volume: {self.data.Volume[-1]:.2f} vs SMA {self.volume_sma[-1]:.2f}")
        
        # Entry Logic 🌕
        if not self.position:
            # Vortex crossover confirmation
            vi_bullish = (self.vi_plus[-1] > self.vi_minus[-1] and 
                          self.vi_plus[-2] <= self.vi_minus[-2])
            
            # Volume surge filter
            volume_surge = self.data.Volume[-1] > 1.5 * self.volume_sma[-1]
            
            if vi_bullish and volume_surge:
                # Risk management calculations
                atr_value = self.atr[-1]
                entry_price = current_close
                stop_loss = entry_price - 3 * atr_value
                risk_amount = self.risk_per_trade * self.equity
                risk_per_share = entry_price - stop_loss
                
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trailing_stop = stop_loss
                    self.highest_high = entry_price
                    print(f"🌕 MOON DEV ALERT: Long Entry at {entry_price:.2f}")
                    print(f"🔒 Initial Stop: {stop_loss:.2f} | Size: {position_size}")

        # Exit Logic 🌗
        elif self.position.is_long:
            # Update trailing stop
            current_high = self.data.High[-1]
            atr_value = self.atr[-1]
            
            if current_high > self.highest_high:
                self.highest_high = current_high
                self.trailing_stop = self.highest_high - 3 * atr_value
                print(f"🎯 New Trail Stop: {self.trailing_stop:.2f}")

            # Check for exits
            if (self.vi_minus[-2] < self.vi_plus[-2] and 
                self.vi_minus[-1] > self.vi_plus[-1]):  # Replaced crossover
                self.position.close()
                print(f"🌗 MOON DEV EXIT: VI- crossed VI+ at {current_close:.2f}")
                
            elif self.data.Low[-1] < self.trailing_stop:
                self.position.close()
                print(f"🚨 STOP HIT: Closed at {current_close:.2f} | Max Profit: {(self.highest_high - self.position.entry_price):.2f}")

# Data handling
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path)

# Clean columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])

# Ensure proper column mapping
data = data.rename(columns={
    'open': 'Open