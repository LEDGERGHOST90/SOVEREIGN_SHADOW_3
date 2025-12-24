Here's the fixed and completed backtest code with all technical issues resolved while preserving the original strategy logic:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

class VoltaVwapBreakout(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    
    def init(self):
        # Calculate Bollinger Band components
        def bb_width(close):
            upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            return (upper - lower) / middle
        self.bb_width = self.I(bb_width, self.data.Close)
        
        # Calculate Bollinger Width Percentile
        max_width = self.I(talib.MAX, self.bb_width, timeperiod=100)
        min_width = self.I(talib.MIN, self.bb_width, timeperiod=100)
        
        def percentile_calc(_, mw, mnw):
            width = self.bb_width[-len(mw):]
            percentile = (width - mnw) / (mw - mnw + 1e-9) * 100
            return percentile
        self.percentile = self.I(percentile_calc, max_width, min_width)
        self.percentile_low = self.I(talib.MIN, self.percentile, timeperiod=20)
        
        # Swing high/low detection
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        # Core indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # VWAP tracking variables
        self.vwap_long = self.vwap_short = 0
        self.anchor_idx_long = self.anchor_idx_short = -1
        
    def next(self):
        current_idx = len(self.data) - 1
        close = self.data.Close[-1]
        
        # Detect new swing points
        if self.data.High[-1] == self.swing_high[-1]:
            self.anchor_idx_short = current_idx
            print(f"🌙 New Swing High Detected at {self.data.High[-1]:.2f}")
        if self.data.Low[-1] == self.swing_low[-1]:
            self.anchor_idx_long = current_idx
            print(f"🌙 New Swing Low Detected at {self.data.Low[-1]:.2f}")
        
        # Calculate anchored VWAPs
        if self.anchor_idx_long != -1:
            start = max(0, self.anchor_idx_long)
            typical = (self.data.High[start:] + self.data.Low[start:] + self.data.Close[start:]) / 3
            vwap = (typical * self.data.Volume[start:]).cumsum() / self.data.Volume[start:].cumsum()
            self.vwap_long = vwap[-1] if len(vwap) > 0 else 0
            
        if self.anchor_idx_short != -1:
            start = max(0, self.anchor_idx_short)
            typical = (self.data.High[start:] + self.data.Low[start:] + self.data.Close[start:]) / 3
            vwap = (typical * self.data.Volume[start:]).cumsum() / self.data.Volume[start:].cumsum()
            self.vwap_short = vwap[-1] if len(vwap) > 0 else 0
            
        # Entry conditions
        if not self.position:
            bb_signal = self.percentile[-1] < self.percentile_low[-1]
            
            if bb_signal and close > self.vwap_long:
                # Long entry calculations
                sl_price = self.swing_low[-1] - 1.5 * self.atr[-1]
                risk_share = close - sl_price
                if risk_share > 0:
                    size = int(round((self.equity * self.risk_per_trade) / risk_share))
                    self.buy(size=size, sl=sl_price)
                    print(f"🚀 LONG ENTRY: {close:.2f} | Size: {size} | SL: {sl_price:.2f}")
                    
            elif bb_signal and close < self.vwap_short:
                # Short entry calculations
                sl_price = self.swing_high[-1] + 1.5