```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR LIQUIDITYBREAKOUT STRATEGY 🚀

# ========== IMPORTS ========== #
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib
import numpy as np
from datetime import datetime

# ========== DATA PREP ========== #
def prepare_data(path):
    # 🌙 Read and clean Moon Dev data
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # 🚀 Proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    return data

# ========== STRATEGY CLASS ========== #
class LiquidityBreakout(Strategy):
    # 🌟 Strategy Parameters
    bb_period = 20
    liquidity_lookback = 20
    bbw_lookback = 252 * 4 * 24  # 1yr of 15m data
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 Calculate Liquidity Zones
        self.liquidity_high = self.I(talib.MAX, self.data.High, self.liquidity_lookback)
        self.liquidity_low = self.I(talib.MIN, self.data.Low, self.liquidty_lookback)
        
        # 🚀 Bollinger Bands Calculation
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, self.data.Close, 
                                                     timeperiod=self.bb_period, nbdevup=2, 
                                                     nbdevdn=2, matype=0)
        
        # ✨ Bollinger Band Width (BBW)
        self.bbw = (self.upper - self.lower) / self.middle
        self.bbw_low = self.I(talib.MIN, self.bbw, self.bbw_lookback)
        
    def next(self):
        current_close = self.data.Close[-1]
        entry_price = None
        stop_loss = None
        take_profit = None
        
        # 🌙 Check for volatility contraction
        volatility_contraction = self.bbw[-1] <= self.bbw_low[-1]
        
        # 🚀 Long Entry Logic
        if (current_close > self.liquidity_high[-1] and 
            volatility_contraction and 
            not self.position):
            
            # ✨ Calculate Risk Parameters
            stop_loss = self.liquidity_low[-1]
            risk_per_share = entry_price - stop_loss
            risk_amount = self.equity * self.risk_per_trade
            position_size = int(round(risk_amount / risk_per_share))
            
            # 🌙 Moon Dev Themed Entry
            print(f"🚀🌙 MOON DEV LONG SIGNAL! 🚀🌙")
            print(f"Entry: {entry_price:.2f} | SL: {stop_loss:.2f} | Size: {position_size}")
            
            self.buy(size=position_size, 
                    sl=stop_loss,
                    tag='LiquidityBreakout_Long')
        
        # 🌙 Short Entry Logic
        elif (current_close < self.liquidity_low[-1] and 
              volatility_contraction and 
              not self.position):
            
            # 🚀 Calculate Risk Parameters
            stop_loss = self.liquidity_high[-1]
            risk_per_share = stop_loss - entry_price
            risk_amount = self.equity * self.risk_per_trade
            position_size = int(round(risk_amount / risk_per_share))
            
            # ✨ Moon Dev Themed Entry
            print(f"🌙🚀 MOON DEV SHORT SIGNAL! 🌙🚀")
            print(f"Entry: {entry_price:.2f} | SL: {stop_loss:.2f} | Size: {position_size}")
            
            self.sell(size=position_size,
                     sl=stop_loss,
                     tag='LiquidityBreakout_Short')
        
        # 🌙 Check Exits
        if self.position:
            if len(self.data) == self.position.entry_bar + 3:  # 45min time exit
                self.position.close()
                print(f"🌙✨ MOON DEV TIME