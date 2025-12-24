Here's the fixed code with all backtesting.lib imports and functions removed, and proper Moon Dev themed debug prints added:

```python
# 🌙 Moon Dev's VolatilitySurge Backtest Implementation ✨
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VolatilitySurge(Strategy):
    # Strategy parameters
    atr_period = 14
    swing_period = 20
    atr_multiplier = 1.5
    sma_period = 50
    risk_percent = 0.01  # 1% risk per trade
    take_profit_multiplier = 2
    
    def init(self):
        # Clean data columns
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        
        # Calculate indicators using TA-Lib
        self.atr = self.I(talib.ATR, 
                         self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=self.atr_period, name='ATR')
        self.swing_high = self.I(talib.MAX, self.data.High, 
                                timeperiod=self.swing_period, name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low, 
                               timeperiod=self.swing_period, name='SWING_LOW')
        self.sma = self.I(talib.SMA, self.data.Close, 
                         timeperiod=self.sma_period, name='SMA')
        
        print("🌙 MOON DEV: Indicators initialized successfully! ✨")
        print("🌌 ATR Period:", self.atr_period)
        print("🌠 Swing Period:", self.swing_period)
        print("✨ SMA Period:", self.sma_period)

    def next(self):
        # Skip initial bars without indicator values
        if len(self.data) < self.swing_period + 1:
            return
        
        # Get previous values to avoid lookahead bias
        prev_swing_high = self.swing_high[-2]
        prev_swing_low = self.swing_low[-2]
        prev_atr = self.atr[-2]
        current_close = self.data.Close[-1]
        current_sma = self.sma[-2]  # Use SMA from previous bar
        
        # Calculate dynamic breakout levels
        upper_band = prev_swing_high + (self.atr_multiplier * prev_atr)
        lower_band = prev_swing_low - (self.atr_multiplier * prev_atr)
        
        # Moon Dev Risk Management Calculations 🌙
        equity = self.equity
        atr_value = self.atr[-1]
        
        # Entry Logic
        if not self.position:
            # Long Entry Conditions
            if (current_close > upper_band and 
                current_close > current_sma and 
                self.atr[-1] < (current_close * 0.01)):  # 1% volatility threshold
                
                # Calculate position size
                stop_loss = lower_band
                risk_per_share = current_close - stop_loss
                position_size = int(round((self.risk_percent * equity) / risk_per_share))
                
                # Moon Dev Entry Signal 🌙
                print(f"🚀 MOON DEV LONG SIGNAL @ {current_close:.2f}")
                print(f"✨ Size: {position_size} | SL: {stop_loss:.2f} | TP: {current_close + (self.take_profit_multiplier * atr_value):.2f}")
                self.buy(size=position_size, 
                         sl=stop_loss,
                         tp=current_close + (self.take_profit_multiplier * atr_value))
            
            # Short Entry Conditions    
            elif (current_close < lower_band and 
                  current_close < current_sma and 
                  self.atr[-1] < (current_close * 0.01)):
                
                # Calculate position size
                stop_loss = upper_band
                risk_per_share = stop_loss - current_close
                position_size = int(round((self.risk_percent * equity) / risk_per_share))
                
                # Moon Dev Entry Signal 🌙
                print(f"🌑 MOON DEV SHORT SIGNAL @ {current_close:.2f}")
                print(f"✨ Size: {position_size} | SL: {stop_loss:.2f} | TP: {current_close - (self.take_profit_multiplier * atr_value):.2f}")
                self.sell(size=position_size,
                          sl=stop_loss,
                          tp=current_close - (self.take_profit_multiplier * atr_value))
        
        # Moon Dev Trailing Stop Logic 🌙