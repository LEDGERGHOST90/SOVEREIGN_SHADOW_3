```python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest

# Moon Dev Data Preparation 🌙
def prepare_data(path):
    data = pd.read_csv(path)
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    # Drop unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    # Ensure proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    data.index = pd.to_datetime(data['datetime'])
    return data

class VortexSqueeze(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌟 Calculate Indicators using TA-Lib
        # Vortex Indicator
        self.vi_plus, self.vi_minus = self.I(talib.VORTEX, 
                                            self.data.High, 
                                            self.data.Low, 
                                            self.data.Close)
        
        # Keltner Channel Components
        self.ema_period = 20
        self.atr_period = 20
        self.multiplier = 2
        
        self.ema_middle = self.I(talib.EMA, self.data.Close, self.ema_period)
        self.atr = self.I(talib.ATR, 
                         self.data.High, 
                         self.data.Low, 
                         self.data.Close, 
                         self.atr_period)
        
        # Calculate channel bands
        self.keltner_upper = self.ema_middle + (self.atr * self.multiplier)
        self.keltner_lower = self.ema_middle - (self.atr * self.multiplier)
        
        # Channel width analysis
        self.channel_width = (self.keltner_upper - self.keltner_lower)/self.ema_middle
        self.width_ma = self.I(talib.SMA, self.channel_width, 20)
        
        # RSI for exits
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        
        # Swing low for stop loss
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)
        
        print("✨ Moon Dev Indicators Activated! 🌙")

    def next(self):
        current_close = self.data.Close[-1]
        current_rsi = self.rsi[-1]
        
        # 🚀 Entry Conditions
        if not self.position:
            # Vortex crossover
            vortex_crossover = (self.vi_plus[-1] > self.vi_minus[-1]) and \
                              (self.vi_plus[-2] <= self.vi_minus[-2])
            
            # Keltner squeeze condition (width < moving average)
            squeeze_active = self.channel_width[-1] < self.width_ma[-1]
            
            # Price above middle line
            price_above_ema = current_close > self.ema_middle[-1]
            
            if vortex_crossover and squeeze_active and price_above_ema:
                # Calculate stop loss
                stop_loss_level = max(self.swing_low[-1], self.keltner_lower[-1])
                risk_per_share = current_close - stop_loss_level
                
                if risk_per_share <= 0:
                    print("🌑 Risk calculation invalid - trade skipped")
                    return
                
                # Position sizing
                risk_amount = self.equity * self.risk_per_trade
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.buy(size=position_size, 
                            sl=stop_loss_level,
                            tag="VortexSqueeze Entry")
                    print(f"🚀 LONG ENTRY | Size: {position_size} | Price: {current_close:.2f} | SL: {stop_loss_level:.2f}")
        
        # 💰 Exit Conditions
        elif self.position.is_long:
            # RSI-based exit
            if current_rsi > 70:
                self.position.close()
                print(f"🏆 RSI EXIT | RSI: {current_rsi:.2f}")
            
            # Update trailing stop (lower of swing low or Keltner lower)
            new_sl = max(self.swing_low[-1], self.keltner_lower[-1])
            self.position.sl = max(new_sl, self.position.sl)  # Trail upwards

# Load and prepare Moon Dev data 🌙
data