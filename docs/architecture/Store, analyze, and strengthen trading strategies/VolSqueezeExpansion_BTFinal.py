I've completed debugging the code while maintaining the original strategy logic. Here's the fixed version with Moon Dev themed debug prints and all necessary technical corrections:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np

class VolSqueezeExpansion(Strategy):
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        
        # Calculate Bollinger Bands
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        self.I(lambda x: x, upper, name='BB_UPPER')
        self.I(lambda x: x, middle, name='BB_MIDDLE')
        self.I(lambda x: x, lower, name='BB_LOWER')
        
        # Calculate Bollinger Band Width
        bb_width = upper - lower
        self.I(lambda x: x, bb_width, name='BB_WIDTH')
        
        # Historical percentile calculation (5th percentile over 2000 periods)
        lookback_percentile = 2000
        bb_low_percentile = bb_width.rolling(lookback_percentile).quantile(0.05)
        self.I(lambda x: x, bb_low_percentile, name='BB_LOW_PERCENTILE')
        
        # Moving Average and StdDev of BB Width
        ma_width = talib.SMA(bb_width, timeperiod=20)
        std_width = talib.STDDEV(bb_width, timeperiod=20)
        self.I(lambda x: x, ma_width, name='MA_WIDTH')
        self.I(lambda x: x, std_width, name='STD_WIDTH')
        
        # ATR for trailing stop
        atr = talib.ATR(high, low, close, timeperiod=14)
        self.I(lambda x: x, atr, name='ATR')
        
        # Initialize trade tracking variables
        self.bars_in_trade = 0
        self.trailing_high = None
        self.trailing_stop = None

    def next(self):
        # Moon Dev debug prints 🌙
        print(f"🌙 Moon Dev Debug - Bar: {len(self.data)-1} Close: {self.data.Close[-1]} ✨")
        
        if not self.position:
            self._check_entry()
        else:
            self._manage_trade()

    def _check_entry(self):
        current_width = self.data.BB_WIDTH[-1]
        current_percentile = self.data.BB_LOW_PERCENTILE[-1]
        bb_middle = self.data.BB_MIDDLE[-1]
        
        if (current_width <= current_percentile and 
            self.data.Close[-1] > bb_middle and 
            not np.isnan(current_percentile)):
            
            self._enter_long()

    def _enter_long(self):
        entry_price = self.data.Close[-1]
        stop_loss = self.data.BB_LOWER[-1]
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            print("🌙 MOON DEV WARNING: Invalid risk calculation ⚠️")
            return
        
        # Calculate position size with moon-sized risk management 🌝
        risk_pct = 0.01  # 1% risk per trade
        risk_amount = self.equity * risk_pct
        position_size = int(round(risk_amount / risk_per_share))
        
        if position_size > 0:
            self.buy(size=position_size, sl=stop_loss)
            self.trailing_high = entry_price
            self.trailing_stop = entry_price - 1.5 * self.data.ATR[-1]
            print(f"🌙 MOON DEV ALERT: Long entry at {entry_price}, Size: {position_size} 🚀")
            print(f"✨ Initial Stop: {stop_loss}, Trailing Stop: {self.trailing_stop} ✨")

    def _manage_trade(self):
        self.bars_in_trade += 1
        
        # Update trailing stop
        current_high = self.data.High[-1]
        if current_high > self.trailing_high:
            self.trailing_high = current_high
            self.trailing_stop = self.trailing_high - 1.5 * self.data.ATR[-1]