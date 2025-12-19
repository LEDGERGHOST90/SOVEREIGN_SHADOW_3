Here's the complete fixed code with all technical issues resolved while preserving the original strategy logic:

```python
# 🌙 Moon Dev's DualMomentumFisher Backtest 🌙
from backtesting import Backtest, Strategy
import pandas as pd
import pandas_ta as ta
import talib
import numpy as np

class DualMomentumFisher(Strategy):
    # Risk parameters
    risk_per_trade = 0.01  # 1% risk per trade
    max_daily_loss = 0.03  # 3% max daily loss
    cvi_threshold = 50     # Volatility threshold
    time_exit_bars = 192   # 48 hours in 15m intervals
    
    def init(self):
        # 🌈 Heikin-Ashi Calculation
        ha_df = ta.heikin_ashi(self.data.Open, self.data.High, self.data.Low, self.data.Close)
        self.ha_open = self.I(lambda x: ha_df['HA_open'].values, name='HA_Open')
        self.ha_close = self.I(lambda x: ha_df['HA_close'].values, name='HA_Close')
        
        # 🎣 Fisher Transform
        fisher = ta.fisher(self.data.High, self.data.Low, length=14)
        self.fisher = self.I(lambda x: fisher['FISHER_14_1'].values, name='Fisher')
        self.signal = self.I(lambda x: fisher['FISHERs_14_1'].values, name='Signal')
        
        # 🌪️ Chande's Volatility Index
        self.cvi = self.I(ta.cvi, self.data.High, self.data.Low, length=9, name='CVI')
        
        # 📈 Trend Filter
        self.ema20 = self.I(talib.EMA, self.data.Close, timeperiod=20, name='EMA20')
        
        # 📅 Daily tracking
        self.daily_equity_start = self.equity
        self.last_date = None
        
    def next(self):
        # 🌙 Moon Dev Debug Prints
        current_bar = len(self.data)-1
        print(f"\n🌙 Bar {current_bar} | Price: {self.data.Close[-1]:.2f} | Equity: {self.equity:,.2f} ✨")
        
        # 🛑 Risk Management Checks
        if self._check_daily_loss():
            print("🌙🛑 DAILY LOSS LIMIT HIT! No new trades today")
            return
            
        if self.cvi[-1] > self.cvi_threshold:
            print(f"🌙⚠️ High Volatility (CVI {self.cvi[-1]:.1f}) - No new entries")
            return
            
        # 📉 Exit Conditions
        if self.position:
            self._check_exits()
            
        # 🚀 Entry Conditions
        if not self.position:
            self._check_entries()
            
    def _check_daily_loss(self):
        current_date = self.data.index[-1].date()
        if current_date != self.last_date:
            self.daily_equity_start = self.equity
            self.last_date = current_date
            
        daily_pnl = (self.equity - self.daily_equity_start) / self.daily_equity_start
        return daily_pnl <= -self.max_daily_loss
        
    def _check_entries(self):
        # Long Conditions 🌈
        ha_uptrend = all(self.ha_close[-i] > self.ha_open[-i] for i in range(1,4))
        fisher_buy = (self.fisher[-2] < self.signal[-2] and self.fisher[-1] > self.signal[-1])
        price_above_ema = self.data.Close[-1] > self.ema20[-1]
        
        if ha_uptrend and fisher_buy and price_above_ema:
            self._enter_trade('long')
            
        # Short Conditions 🌧️
        ha_downtrend = all(self.ha_close[-i] < self.ha_open[-i] for i in range(1,4))
        fisher_sell = (self.fisher[-2] > self.signal[-2] and self.fisher[-1] < self.signal[-1])
        price_below_ema = self.data.Close[-1] < self.ema20[-1]
        
        if ha_downtrend and fisher_sell and price_below_ema:
            self._enter_trade('short')
            
    def _enter_trade(self, direction):
        entry_price = self.data.Close[-1]
        current_cvi = self.cvi[-1]
        risk_amount = self.equity * self.risk