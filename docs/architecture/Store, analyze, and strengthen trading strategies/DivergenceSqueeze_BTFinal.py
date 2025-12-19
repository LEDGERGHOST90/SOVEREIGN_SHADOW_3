I'll debug the code while maintaining the original strategy logic. Here's the fixed version with Moon Dev improvements:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np  # 🌙 Added for array operations
from backtesting.lib import crossover  # 🌙 Added proper import

# 🌙 MOON DEV DATA PREPARATION 🌙
def prepare_data(path):
    data = pd.read_csv(path, parse_dates=['datetime'], index_col='datetime')
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    # Proper column case mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    return data

class DivergenceSqueeze(Strategy):
    risk_percent = 0.01  # 🌙 1% risk per trade
    
    def init(self):
        # 🌟 INDICATOR CALCULATIONS 🌟
        self.macd_hist = self.I(self._calculate_macd_hist)
        self.bbw = self.I(self._calculate_bbw)
        self.bbw_low = self.I(talib.MIN, self.bbw, 10)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        self.entry_trigger = False
        self.trigger_price = None
        self.swing_low = None

    def _calculate_macd_hist(self):
        macd, signal, hist = talib.MACD(self.data.Close, 12, 26, 9)
        return hist
    
    def _calculate_bbw(self):
        upper, middle, lower = talib.BBANDS(self.data.Close, 20, 2)
        return (upper - lower) / middle

    def next(self):
        # 🌙 STRATEGY CORE LOGIC 🌙
        if len(self.data) < 34:  # Ensure sufficient data
            return
            
        price = self.data.Close[-1]
        lows = self.data.Low
        hist = self.macd_hist
        
        # 🚀 DIVERGENCE DETECTION 🚀
        price_divergence = (lows[-3] < lows[-2] < lows[-1]) and \
                          (hist[-3] > hist[-2] > hist[-1])
        
        # 📉 BOLLINGER SQUEEZE CONFIRMATION 📉
        bbw_squeeze = self.bbw[-1] <= self.bbw_low[-1]
        
        # 🌙 ENTRY CONDITIONS 🌙
        if price_divergence and bbw_squeeze and not self.position:
            self.entry_trigger = True
            self.swing_low = lows[-1]
            self.trigger_price = self.data.High[-1]
            print(f"🌙✨ DOUBLE DIVERGENCE DETECTED! Swing Low: {self.swing_low:.2f}")
            
        if self.entry_trigger and self.data.Close[-1] > self.trigger_price:
            # 💰 RISK MANAGEMENT CALCULATIONS 💰
            risk_amount = self.equity * self.risk_percent
            entry_price = self.data.Close[-1]
            atr_value = self.atr[-1]
            
            stop_loss = self.swing_low - 0.05*atr_value  # 🛑 DYNAMIC STOP
            take_profit = entry_price + 1.5*atr_value    # 🎯 PROFIT TARGET
            
            risk_per_share = entry_price - stop_loss
            position_size = int(round(risk_amount / risk_per_share))
            
            if position_size > 0:
                self.buy(size=position_size)
                print(f"🚀🌕 BLAST OFF! Long {position_size} @ {entry_price:.2f}")
                print(f"   🌙 TP: {take_profit:.2f} | 🛑 SL: {stop_loss:.2f}")
                
                # SET ORDER TARGETS
                self.sell(size=position_size, limit=take_profit)
                self.sell(size=position_size, stop=stop_loss)
                
            self.entry_trigger = False

# 🌙 BACKTEST EXECUTION 🌙
if __name__ == "__main__":
    data = prepare_data('your_data.csv')  # 🌙 Replace with your actual data path
    bt = Backtest(data, Diverg