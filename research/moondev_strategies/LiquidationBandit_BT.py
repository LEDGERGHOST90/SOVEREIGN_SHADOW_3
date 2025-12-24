```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION 🌙
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

# ======================== DATA PREPARATION ========================
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and format columns according to Moon Dev standards 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map to backtesting.py format with proper case
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Convert index to datetime
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# ======================== LIQUIDATION BANDIT STRATEGY ========================
class LiquidationBandit(Strategy):
    risk_pct = 0.01  # 1% per trade 🌕
    max_daily_trades = 3  # 🚀 Moon Mission Limit
    atr_period = 14
    bb_period = 20
    
    def init(self):
        # 🌗 CORE INDICATORS USING TA-LIB
        close = self.data.Close
        self.upper_bb, self.middle_bb, _ = self.I(talib.BBANDS, close, 
                                                  timeperiod=self.bb_period, 
                                                  nbdevup=2, nbdevdn=2, 
                                                  name='BBANDS')
        
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, close,
                         timeperiod=self.atr_period, name='ATR')
        
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 20, name='VolMA')
        
        # 🌌 Liquidation Zone Detection
        self.oi_cluster = self.I(talib.MAX, self.data.High, 50, name='OI_Cluster')
        
        # 🌠 Trade Tracking
        self.daily_trades = {}
        self.entry_atr = None

    def next(self):
        current_time = self.data.index[-1]
        hour = current_time.hour
        
        # 🌑 Night Mode: Only trade during high liquidity hours
        if not (12 <= hour < 16):
            return
            
        # 🌕 Moon Position Management
        if self.position:
            price = self.data.Close[-1]
            
            # 🎯 Profit Target Hit
            if price >= self.entry_target:
                self.position.close()
                print(f"🌕 TARGET REACHED! Cosmic profits achieved! 🚀")
            
            # 🛑 Stop Loss Check
            elif self.data.Low[-1] <= self.position.sl:
                self.position.close()
                print(f"🌑 STOP LOSS ACTIVATED! Returning to lunar base 💔")
            
            # 🌪️ Emergency Exit Conditions
            elif (self.data.Volume[-1] < self.volume_ma[-1] and 
                  self.atr[-1] < self.entry_atr * 0.5):
                self.position.close()
                print(f"🚨 VOLATILITY COLLAPSE! Emergency evacuation! 🌪️")
                
        else:
            # 🌟 Entry Signal Conditions
            today = current_time.date()
            trades_today = self.daily_trades.get(today, 0)
            
            if trades_today >= self.max_daily_trades:
                return
                
            if (self.data.Close[-1] > self.upper_bb[-1] and 
                self.data['funding_rate'][-1] <= -0.0001):
                
                # 🧮 Risk Calculation
                atr_value = self.atr[-1]
                stop_loss = self.data.Close[-1] - 1.5 * atr_value
                risk_amount = self.equity * self.risk_pct
                position_size = risk_amount / (1.5 * atr_value)
                position_size = int(round(position_size))
                
                if position_size > 0:
                    target = self.oi_cluster[-1]
                    self.buy(size=position_size, 
                            sl=stop_loss,
                            tp=target)
                    
                    self.entry_atr = atr_value
                    self.entry_target = target
                    self.daily_trades[today] = trades_today + 1
                    print(f