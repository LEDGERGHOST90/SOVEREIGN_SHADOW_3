```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR LIQUIDITY SQUEEZE STRATEGY 🚀

import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply

class LiquiditySqueeze(Strategy):
    # Risk per trade (1% of equity)
    risk_percent = 0.01
    
    def init(self):
        # 🌙 STEP 1: Calculate Indicators using TA-Lib
        # Donchian Channel (20-period)
        self.donchian_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='Donchian High')
        self.donchian_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='Donchian Low')
        
        # Donchian Width & Historical Narrowing
        self.donchian_width = self.I(lambda h, l: h - l, self.donchian_high, self.donchian_low, name='Donchian Width')
        self.min_width = self.I(talib.MIN, self.donchian_width, timeperiod=100, name='Min Width (100)')
        
        # Swing High/Low for TP targets
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20, name='Swing High (20)')
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20, name='Swing Low (20)')
        
        # 🌙 Funding Rate Data (must exist in CSV)
        self.funding_rate = self.data.df['fundingrate']  # After column cleaning

    def next(self):
        # 🌙 MOON DEV DEBUG: Print key values
        if len(self.data) % 500 == 0:
            print(f"\n🌙 MOON DEV STATUS UPDATE 🌙\n"
                  f"Current Close: {self.data.Close[-1]:.2f}\n"
                  f"Donchian Width: {self.donchian_width[-1]:.2f} vs Min {self.min_width[-1]:.2f}\n"
                  f"Funding Rate: {self.funding_rate[-1]*100:.4f}%\n"
                  f"Equity: {self.equity:.2f} ✨\n")

        # 🚀 ENTRY LOGIC
        if not self.position:
            # Long Entry Conditions
            if (self.donchian_width[-1] <= self.min_width[-1] and
                self.funding_rate[-1] < -0.0001 and
                self.data.Close[-1] > self.donchian_high[-1]):
                
                # Risk Management Calculations
                sl_price = (self.donchian_high[-1] + self.donchian_low[-1]) / 2
                tp_price = self.swing_high[-1] + 1.5 * self.donchian_width[-1]
                
                # Position Sizing
                risk_amount = self.equity * self.risk_percent
                risk_per_share = self.data.Close[-1] - sl_price
                position_size = int(round(risk_amount / risk_per_share)) if risk_per_share > 0 else 0
                
                if position_size > 0:
                    self.buy(size=position_size, sl=sl_price, tp=tp_price)
                    print(f"🚀🌙 MOON DEV LONG SIGNAL 🚀\n"
                          f"Entry: {self.data.Close[-1]:.2f} | "
                          f"SL: {sl_price:.2f} | "
                          f"TP: {tp_price:.2f} | "
                          f"Size: {position_size} units ✨")

            # Short Entry Conditions    
            elif (self.donchian_width[-1] <= self.min_width[-1] and
                  self.funding_rate[-1] < -0.0001 and
                  self.data.Close[-1] < self.donchian_low[-1]):
                
                sl_price = (self.donchian_high[-1] + self.donchian_low[-1]) / 2
                tp_price = self.swing_low[-1] - 1.5 * self.donchian_width[-1]
                
                risk_amount = self.equity * self.risk_percent
                risk_per_share = sl_price - self.data.Close[-1]
                position_size = int(round(risk_amount / risk_per_share)) if risk_per_share > 0