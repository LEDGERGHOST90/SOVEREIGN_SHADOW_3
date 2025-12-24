I'll fix the backtesting.lib imports and replace them with proper implementations. Here's the corrected code:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT 🌙
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# Clean and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class LiquidationRejection(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    rsi_period = 14
    swing_period = 20
    fib_levels = (0.382, 0.618)
    
    def init(self):
        # 🌙 INDICATORS 🌙
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.swing_high = self.I(talib.MAX, self.data.High, self.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, self.swing_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 20)
        
        # 🌙 SWING TRACKERS 🌙
        self.last_swing_high = {'price': None, 'rsi': None}
        self.last_swing_low = {'price': None, 'rsi': None}

    def next(self):
        # 🌙 MOON DEV TRADE FILTER 🌙
        if self.position:
            return  # Only one position at a time
            
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        volume = self.data.Volume[-1]
        
        # 🌙 DETECT SWING POINTS 🌙
        current_swing_high = self.swing_high[-1]
        current_swing_low = self.swing_low[-1]
        
        # Bearish setup detection
        if high == current_swing_high:
            self._update_swing_high(high, self.rsi[-1])
            bearish_divergence = self._check_bearish_divergence(high, self.rsi[-1])
            rejection = self._bearish_rejection_candle()
            volume_ok = volume < self.volume_ma[-1]
            
            if bearish_divergence and rejection and volume_ok:
                self._enter_short(price, current_swing_high, current_swing_low)

        # Bullish setup detection
        if low == current_swing_low:
            self._update_swing_low(low, self.rsi[-1])
            bullish_divergence = self._check_bullish_divergence(low, self.rsi[-1])
            rejection = self._bullish_rejection_candle()
            volume_ok = volume < self.volume_ma[-1]
            
            if bullish_divergence and rejection and volume_ok:
                self._enter_long(price, current_swing_high, current_swing_low)

    def _enter_short(self, entry_price, swing_high, swing_low):
        # 🌙 RISK CALCULATIONS 🌙
        stop_loss = swing_high * 1.005  # 0.5% buffer
        risk_amount = self.risk_percent * self.equity
        risk_per_unit = entry_price - stop_loss
        position_size = int(round(risk_amount / abs(risk_per_unit)))
        
        # 🌙 FIB TARGETS 🌙
        fib_range = swing_high - swing_low
        tp1 = entry_price - fib_range * self.fib_levels[0]
        tp2 = entry_price - fib_range * self.fib_levels[1]
        
        # 🌙 MOON ENTRY MESSAGE 🌙
        print(f"🌙 SHORT SIGNAL 🌙 Price: {entry_price:.2f} | Size: {position_size} ✨")
        print(f"   SL: {stop_loss:.2f} | TP1: {tp1:.2f} | TP2: {tp2:.2f} 🚀")
        self.sell(size=position_size, sl=