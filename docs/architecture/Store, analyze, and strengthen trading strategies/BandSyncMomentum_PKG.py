I've reviewed the code and made the necessary fixes to remove any `backtesting.lib` dependencies. Here's the corrected version with Moon Dev themed debug prints and proper indicator handling:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

def bollinger_bands(price, timeperiod=20, nbdev=2, which='upper'):
    upper, middle, lower = talib.BBANDS(price, timeperiod=timeperiod, 
                                      nbdevup=nbdev, nbdevdn=nbdev, matype=0)
    return {'upper': upper, 'middle': middle, 'lower': lower}[which]

class BandSyncMomentum(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    bb_period = 20
    bb_dev = 2
    
    def init(self):
        # Bollinger Bands indicators 🌙
        self.bb_upper = self.I(bollinger_bands, self.data.Close, self.bb_period, 
                             self.bb_dev, 'upper', name='BB_UPPER')
        self.bb_middle = self.I(bollinger_bands, self.data.Close, self.bb_period,
                              self.bb_dev, 'middle', name='BB_MID')
        self.bb_lower = self.I(bollinger_bands, self.data.Close, self.bb_period,
                             self.bb_dev, 'lower', name='BB_LOWER')
        
        # Engulfing pattern detection ✨
        self.bullish_engulf = self.I(talib.CDLENGULFING, self.data.Open, 
                                   self.data.High, self.data.Low, self.data.Close,
                                   name='BULL_ENGULF')
        self.bearish_engulf = self.I(talib.CDLENGULFING, self.data.Open,
                                   self.data.High, self.data.Low, self.data.Close,
                                   name='BEAR_ENGULF')

    def next(self):
        # Wait for minimum data period 🕒
        if len(self.data.Close) < self.bb_period + 1:
            return
            
        current_close = self.data.Close[-1]
        current_low = self.data.Low[-1]
        current_high = self.data.High[-1]
        
        # Bollinger values 📊
        bb_upper = self.bb_upper[-1]
        bb_mid = self.bb_middle[-1]
        bb_lower = self.bb_lower[-1]
        
        # Midpoint trend calculation 📈
        mid_trend_up = bb_mid > self.bb_middle[-2]
        mid_trend_down = bb_mid < self.bb_middle[-2]

        # Risk management calculations 🔒
        equity = self.equity
        position_size = 0
        
        # Long entry constellation 🌌
        if not self.position and current_low <= bb_lower and mid_trend_up:
            if self.bullish_engulf[-1] > 0:  # Bullish engulfing confirmation
                stop_loss = bb_lower * 0.995
                risk_amount = equity * self.risk_percent
                risk_per_share = current_close - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_loss, tp=bb_upper)
                        print(f"🌙🚀 LUNAR LIFT-OFF! Long {position_size} @ {current_close:.2f}")
                        print(f"   🛡️SL: {stop_loss:.2f} | 🎯TP: {bb_upper:.2f}")

        # Short entry constellation 🌠
        elif not self.position and current_high >= bb_upper and mid_trend_down:
            if self.bearish_engulf[-1] < 0:  # Bearish engulfing confirmation
                stop_loss = bb_upper * 1.005
                risk_amount = equity * self.risk_percent
                risk_per_share = stop_loss - current_close
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss, tp=bb_lower)
                        print(f"🌙📉 COSMIC CORRECTION! Short {position_size} @ {current_close:.2f}")
                        print(f"   🛡️SL: {stop_loss:.2f} | 🎯TP: