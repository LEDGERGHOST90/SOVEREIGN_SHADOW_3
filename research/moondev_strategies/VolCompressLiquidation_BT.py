```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR VOLCOMPRESSLIQUIDATION STRATEGY 🌙
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

# =====================
# DATA PREPARATION
# =====================
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and prepare columns 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data.set_index(pd.to_datetime(data['datetime']), inplace=True)

# =====================
# STRATEGY IMPLEMENTATION
# =====================
class VolCompressLiquidation(Strategy):
    # Risk parameters ✨
    risk_pct = 0.01
    stop_loss_pct = 0.025
    emergency_stop_pct = 0.03
    max_daily_loss = 0.03
    
    def init(self):
        # 🌗 VOLATILITY INDICATORS
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        self.atr_ma = self.I(talib.SMA, self.atr, 20)
        self.atr_std = self.I(talib.STDDEV, self.atr_ma, 20)
        
        # 🌓 SWING LEVELS USING TALIB
        self.swing_high = self.I(talib.MAX, self.data.High, 20)
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)
        
        # 🌕 VOLUME INDICATORS
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 20)
        
        # Track daily performance 🌙
        self.last_day = None
        self.daily_equity = []

    def next(self):
        # 🌑 DAILY LOSS CHECK
        current_day = self.data.index[-1].date()
        if current_day != self.last_day:
            self.daily_equity.append(self.equity)
            if len(self.daily_equity) > 1:
                daily_return = (self.daily_equity[-1] - self.daily_equity[-2])/self.daily_equity[-2]
                if daily_return < -self.max_daily_loss:
                    print("🌚 MOON ALERT: Max daily loss hit! Ceasing trading.")
                    self.position.close()
            self.last_day = current_day

        # 🌗 ENTRY LOGIC
        if not self.position:
            # Volatility compression check
            vol_compress = self.atr[-1] < self.atr_ma[-1]
            
            # Price near resistance (swing high)
            price_near_resistance = self.data.Close[-1] > 0.985 * self.swing_high[-1]
            
            # Volume confirmation
            volume_ok = self.data.Volume[-1] < self.volume_ma[-1]
            
            if vol_compress and price_near_resistance and volume_ok:
                # 🌙 RISK CALCULATION
                equity = self.equity
                risk_amount = equity * self.risk_pct
                price_diff = self.swing_high[-1] * self.stop_loss_pct
                position_size = risk_amount / price_diff
                
                # 🌕 PROPER POSITION SIZING
                position_size = int(round(position_size))
                if position_size > 0:
                    self.sell(size=position_size, 
                             sl=self.swing_high[-1] * 1.025,
                             tp=self.data.Close[-1] * 0.97)
                    print(f"🌙✨ SHORT ENTRY: {position_size} units at {self.data.Close[-1]} ✨")

        # 🌑 EXIT LOGIC
        else:
            # Dynamic ATR exit
            if self.atr[-1] > self.atr_ma[-1] + self.atr_std[-1]:
                self.position.close()
                print(f"🌗 ATR EXPANSION EXIT: {self.data.Close[-1]}")
                
            # Emergency stop check
            if self.data.High[-1] >= self.position.entry_price