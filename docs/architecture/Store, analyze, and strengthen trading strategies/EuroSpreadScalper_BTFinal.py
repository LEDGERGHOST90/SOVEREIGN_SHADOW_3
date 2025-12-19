# 🌙 MOON DEV BACKTESTING SCRIPT FOR EUROSPREADSCALPER STRATEGY

# ======== REQUIRED IMPORTS ========
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from datetime import time

# ======== STRATEGY CLASS ========
class EuroSpreadScalper(Strategy):
    time_window_start = time(8, 0)  # European session start (8:00 AM GMT)
    atr_period = 14
    risk_pct = 0.01  # 1% risk per trade
    tp_factor = 0.005  # 0.5% take profit
    sl_factor = 0.005  # 0.5% stop loss
    
    def init(self):
        # 🌙 VOLATILITY INDICATOR
        self.atr = self.I(talib.ATR,
                         self.data.High,
                         self.data.Low,
                         self.data.Close,
                         timeperiod=self.atr_period)
        
        # 🌙 TRADE TRACKING
        self.entry_bar = 0

    def next(self):
        current_time = self.data.index[-1].time()
        price = self.data.Close[-1]
        
        # 🌙 EUROPEAN SESSION CHECK
        if current_time != self.time_window_start:
            return
            
        # 🌙 VOLATILITY FILTER
        if self.atr[-1] < 50:
            print(f"🌙✨ VOLATILITY TOO LOW: ATR={self.atr[-1]:.1f}")
            return
            
        # 🌙 ENTRY LOGIC
        if not self.position:
            # RISK MANAGEMENT CALCULATIONS
            sl_price = price * (1 - self.sl_factor)  # Fixed: Corrected SL calculation for short position
            risk_per_unit = abs(sl_price - price)
            position_size = int(round((self.equity * self.risk_pct) / risk_per_unit))
            
            if position_size > 0:
                # 🚀 SHORT ENTRY WITH MOON DEV FLAIR
                self.sell(size=position_size,
                         sl=sl_price,
                         tp=price * (1 - self.tp_factor))
                self.entry_bar = len(self.data)
                print(f"🌙🚀 EURO SHORT! Size: {position_size} | Entry: {price:.2f}")
                print(f"    SL: {sl_price:.2f} | TP: {price*(1-self.tp_factor):.2f}")

        # ⏰ TIME-BASED EXIT LOGIC
        if self.position and (len(self.data) - self.entry_bar) >= 2:
            self.position.close()
            print(f"⏰🌙 MOON DEV TIME EXIT! Bars held: {len(self.data)-self.entry_bar}")

# ======== DATA PREPARATION ========
# 🌙 LOAD AND CLEAN DATA
data = pd.read_csv(
    '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv',
    parse_dates=['datetime'],
    index_col='datetime'
)

# 🧹 CLEAN COLUMN NAMES
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# 🔄 PROPER COLUMN MAPPING
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# ======== BACKTEST EXECUTION ========
print("🌕🌖🌗🌘🌑🌒🌓🌔🌕 MOON DEV BACKTEST INITIATED 🚀")
bt = Backtest(data, EuroSpreadScalper, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n🌙✨ FINAL BACKTEST STATS:")
print(stats)
print("\n🌙🚀 STRATEGY DETAILS:")
print(stats._strategy)
print("MOON DEV BACKTEST COMPLETE! 🌕✨")