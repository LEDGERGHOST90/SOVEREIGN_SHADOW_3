# 🌙 Moon Dev's Volatility Cluster Breakout Backtest 🌙
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class VolatilityClusterBreakout(Strategy):
    risk_per_trade = 0.01  # 1% of equity per trade
    
    def init(self):
        # 🌈 Calculate Bollinger Bands components using TA-Lib
        self.middle_bb = self.I(talib.SMA, self.data.Close, 20)
        self.stddev = self.I(talib.STDDEV, self.data.Close, 20)
        self.upper_bb = self.I(lambda: self.middle_bb + 2*self.stddev)
        self.lower_bb = self.I(lambda: self.middle_bb - 2*self.stddev)
        
        # 📊 Calculate Bollinger Bandwidth Percentile
        self.bw = self.I(lambda: (self.upper_bb - self.lower_bb)/self.middle_bb)
        self.bw_percentile = self.I(self._calculate_percentile, self.bw, 100)
        
    def _calculate_percentile(self, series, window):
        """✨ Calculate rolling percentile rank for bandwidth"""
        return np.array([np.sum(series[i-window:i] < series[i])/window*100 
                        if i >= window else np.nan for i in range(len(series))]

    def next(self):
        # 🌙 Strategy Core Logic
        price = self.data.Close[-1]
        mid_bb = self.middle_bb[-1]
        
        # 📉 Exit conditions for open positions
        if self.position:
            if (self.position.is_long and crossover(-1, price - mid_bb)) or \
               (self.position.is_short and crossover(price - mid_bb, 1)):
                self.position.close()
                print(f"🌙 Mean Reversion Exit at {price:.2f} ✨")

        # 📈 Entry conditions
        elif self.bw_percentile[-1] < 10:
            if price > self.upper_bb[-1]:
                self._enter_trade('long', price, self.lower_bb[-1])
            elif price < self.lower_bb[-1]:
                self._enter_trade('short', price, self.upper_bb[-1])

    def _enter_trade(self, direction, entry_price, sl_price):
        """🚀 Execute trade with proper risk management"""
        risk = abs(entry_price - sl_price)
        if risk == 0:
            return
            
        # 🔒 Calculate position size
        risk_amount = self.risk_per_trade * self.equity
        position_size = int(round(risk_amount / risk))
        
        if position_size == 0:
            return
            
        # 🎯 Set TP at 2:1 risk-reward
        tp_price = entry_price + 2*(entry_price - sl_price) if direction == 'long' \
                   else entry_price - 2*(sl_price - entry_price)
        
        if direction == 'long':
            self.buy(size=position_size, sl=sl_price, tp=tp_price)
            print(f"🚀 LONG: {position_size} units | Entry: {entry_price:.2f}")
        else:
            self.sell(size=position_size, sl=sl_price, tp=tp_price)
            print(f"🚨 SHORT: {position_size} units | Entry: {entry_price:.2f}")

# 🌍 Data Preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# 🧹 Clean and format data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# 🚀 Run Backtest
bt = Backtest(data, VolatilityClusterBreakout, cash=1_000_000, commission=.002)
stats = bt.run()

# 🌕 Print Full Results
print("="*55 + "\n🌙 MOON DEV BACKTEST RESULTS 🚀")
print(stats)
print(stats._strategy)
print("="*55)