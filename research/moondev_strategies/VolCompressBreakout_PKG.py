Here's the fixed code with all backtesting.lib references removed and proper Moon Dev themed debug prints added:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

def bb_upper(close, timeperiod=20, nbdevup=2):
    upper, _, _ = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevup)
    return upper

def bb_lower(close, timeperiod=20, nbdevdn=2):
    _, _, lower = talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevdn, nbdevdn=nbdevdn)
    return lower

class VolCompressBreakout(Strategy):
    risk_percent = 0.01
    max_exposure = 0.05
    
    def init(self):
        # Bollinger Bands components
        self.upper = self.I(bb_upper, self.data.Close, 20, 2)
        self.middle = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.lower = self.I(bb_lower, self.data.Close, 20, 2)
        
        # Volatility compression indicator
        self.bb_width = self.I(lambda u, l, m: (u - l)/m*100, 
                              self.upper, self.lower, self.middle)
        self.bb_width_min = self.I(talib.MIN, self.bb_width, timeperiod=17280)  # 6 months 15m data
        
        # Volume confirmation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        print("🌙✨ Moon Dev Strategy Activated! Ready for Cosmic Breakouts! 🚀")

    def next(self):
        current_width = self.bb_width[-1]
        min_width = self.bb_width_min[-1]
        close = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Moon-themed debug prints
        print(f"🌙 BB Width: {current_width:.4f} | 6M Min: {min_width:.4f}")
        print(f"📈 Close: {close:.2f} vs Upper: {self.upper[-1]:.2f} | Lower: {self.lower[-1]:.2f}")
        print(f"📊 Volume: {volume:.2f} vs SMA20: {self.volume_sma[-1]:.2f}")

        if not self.position:
            # Long entry logic
            if (current_width <= min_width and 
                close > self.upper[-1] and 
                volume > self.volume_sma[-1]):
                
                risk_amount = self.equity * self.risk_percent
                entry_price = close
                stop_price = self.middle[-1]
                risk_per_share = entry_price - stop_price
                
                if risk_per_share > 0:
                    size = min(risk_amount/risk_per_share, 
                             (self.equity*self.max_exposure)/entry_price)
                    size = int(round(size))
                    self.buy(size=size, tag={'stop': stop_price})
                    print(f"🚀🌙 LONG ENTRY! Size: {size} @ {entry_price:.2f} | Cosmic Boom Detected!")
            
            # Short entry logic
            elif (current_width <= min_width and 
                  close < self.lower[-1] and 
                  volume > self.volume_sma[-1]):
                
                risk_amount = self.equity * self.risk_percent
                entry_price = close
                stop_price = self.middle[-1]
                risk_per_share = stop_price - entry_price
                
                if risk_per_share > 0:
                    size = min(risk_amount/risk_per_share, 
                             (self.equity*self.max_exposure)/entry_price)
                    size = int(round(size))
                    self.sell(size=size, tag={'stop': stop_price})
                    print(f"🌙📉 SHORT ENTRY! Size: {size} @ {entry_price:.2f} | Gravitational Collapse Detected!")

        # Exit logic for long positions
        elif self.position.is_long:
            current_stop = max(self.position.tag['stop'], self.lower[-1])
            if self.data.Low[-1] < current_stop:
                self.position.close()
                print(f"🌙🔻 EXIT LONG @ {self.data.Close[-1]:.2f} | Moon Shield Activated!")

        # Exit logic for short positions        
        elif self.position.is_short:
            current_stop = min(self.position.tag['stop'],