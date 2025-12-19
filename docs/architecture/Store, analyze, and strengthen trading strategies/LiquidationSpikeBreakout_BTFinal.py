Here's the complete fixed code with Moon Dev themed debug prints and proper position sizing:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class LiquidationSpikeBreakout(Strategy):
    initial_equity = 1_000_000
    risk_per_trade = 0.01  # 1% of equity
    
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col], inplace=True)
        
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume
        
        # Calculate indicators
        # Bollinger Bandwidth (BBW)
        def calc_bbw(close):
            upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            return (upper - lower) / middle
        self.bbw = self.I(calc_bbw, name='BBW')
        self.bbw_sma = self.I(talib.SMA, self.bbw, 10, name='BBW SMA')
        
        # Delta Volume (volume on down candles)
        delta_vol = np.where(self.data.Close < self.data.Open, self.data.Volume, 0)
        self.delta_volume = self.I(lambda: delta_vol, name='Delta Volume')
        self.delta_volume_sma = self.I(talib.SMA, self.delta_volume, 20, name='Delta Volume SMA')
        
        # ATR for volatility checks
        self.atr = self.I(talib.ATR, high, low, close, 20, name='ATR 20')
        
        # Track spike levels and setup state
        self.spike_high = None
        self.spike_low = None
        self.in_spike_setup = False
        
    def next(self):
        if len(self.data) < 21:  # Ensure enough data for indicators
            return
        
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        prev_close = self.data.Close[-2] if len(self.data) > 1 else None
        
        # Detect price spike (2% move from previous close)
        if prev_close and (current_high - current_low)/prev_close >= 0.02:
            # Check indicator conditions
            delta_vol = self.delta_volume[-1]
            delta_sma = self.delta_volume_sma[-1]
            bbw = self.bbw[-1]
            bbw_sma = self.bbw_sma[-1]
            
            if delta_vol >= 3 * delta_sma and bbw < bbw_sma:
                self.spike_high = current_high
                self.spike_low = current_low
                self.in_spike_setup = True
                print(f"🌙✨ MOON DEV ALERT: Liquidation spike detected! {self.data.index[-1]} High: {self.spike_high:.2f}, Low: {self.spike_low:.2f}")
        
        # Check for breakout entries
        if self.in_spike_setup and not self.position:
            # Long entry
            if current_high > self.spike_high:
                entry_price = self.spike_high
                sl_price = self.spike_low
                risk = entry_price - sl_price
                if risk <= 0:
                    return
                
                # Calculate position size with proper rounding
                size = int(round((self.equity * self.risk_per_trade) / risk))
                if size > 0:
                    self.buy(size=size, sl=sl_price, tag="LiquidationBreakoutLong")
                    print(f"🚀🌙 MOON DEV TRADE: LONG ENTRY! Size: {size} @ {entry_price:.2f}, SL: {sl_price:.2f}")
                    self.in_spike_setup = False
            
            # Short entry
            elif current_low < self.spike_low:
                entry_price = self.spike_low
                sl_price = self.spike_high
                risk = sl_price - entry_price
                if risk <= 0:
                    return
                
                # Calculate position size with proper rounding
                size = int(round((self.equity * self.risk_per_trade) / risk))
                if size > 0:
                    self.sell(size=size, sl=sl_price, tag="Liquidation