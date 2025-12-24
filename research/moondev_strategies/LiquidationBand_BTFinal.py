I'll fix the incomplete code while maintaining the original strategy logic. Here's the complete, debugged version with Moon Dev themed improvements:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Define helper functions for Bollinger Bands calculations
def calculate_bb_upper(close, timeperiod, nbdev):
    upper, _, _ = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
    return upper

def calculate_bb_middle(close, timeperiod, nbdev):
    _, middle, _ = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
    return middle

def calculate_bb_lower(close, timeperiod, nbdev):
    _, _, lower = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev)
    return lower

# Strategy implementation
class LiquidationBand(Strategy):
    bb_period = 20
    bb_dev = 2
    risk_per_trade = 0.01
    contraction_threshold = 0.2
    tp_multiplier = 1.5
    time_exit_multiplier = 1.5
    
    def init(self):
        # Calculate indicators using TA-Lib with self.I()
        self.bb_upper = self.I(calculate_bb_upper, self.data.Close, self.bb_period, self.bb_dev, name='BB_Upper')
        self.bb_middle = self.I(calculate_bb_middle, self.data.Close, self.bb_period, self.bb_dev, name='BB_Middle')
        self.bb_lower = self.I(calculate_bb_lower, self.data.Close, self.bb_period, self.bb_dev, name='BB_Lower')
        
        # Calculate Bollinger Band Width
        self.bb_width = self.I(lambda u, l, m: (u - l)/m, self.bb_upper, self.bb_lower, self.bb_middle, name='BB_Width')
        self.bb_width_avg = self.I(talib.SMA, self.bb_width, self.bb_period, name='BB_Width_Avg')
        
        # Track maximum equity for drawdown calculation
        self.max_equity = self._broker.starting_cash
        self.current_drawdown = 0
        
        print("🌙 Moon Dev Strategy Initialized! ✨")
        print(f"⚙️ Parameters: BB Period={self.bb_period}, BB Dev={self.bb_dev}")
        print(f"⚙️ Risk/Trade={self.risk_per_trade*100}%, TP Multiplier={self.tp_multiplier}x")
        
    def next(self):
        # Update equity tracking
        current_equity = self.equity
        self.max_equity = max(self.max_equity, current_equity)
        self.current_drawdown = (self.max_equity - current_equity) / self.max_equity
        
        # Trade entry logic
        if not self.position:
            # Long entry conditions
            if (self.bb_width[-1] < self.contraction_threshold * self.bb_width_avg[-1] and
                self.data.BidAskRatio[-1] > 2 and
                self.data.LiquidationClustering[-1] == 1 and
                self.data.Close[-1] > self.bb_upper[-1]):
                
                risk_amount = self.equity * self.risk_per_trade
                entry_price = self.data.Close[-1]
                stop_loss = self.bb_lower[-1]
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    take_profit = entry_price + self.bb_width[-1] * self.tp_multiplier
                    self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                    print(f"🌙✨ LONG ENTRY! ✨ Entry: {entry_price:.2f}, Size: {position_size}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    print(f"🌌 BB Width: {self.bb_width[-1]:.4f}, Avg Width: {self.bb_width_avg[-1]:.4f}")
            
            # Short entry conditions
            if (self.bb_width[-1] < self.contraction_threshold * self.bb_width_avg[-1] and