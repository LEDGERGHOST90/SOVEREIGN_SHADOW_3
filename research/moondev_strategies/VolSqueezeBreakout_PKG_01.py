I'll fix the code by removing all `backtesting.lib` imports and replacing any related functionality. Here's the corrected version with Moon Dev themed improvements:

```python
# moon_dev_vol_squeeze_breakout.py
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VolSqueezeBreakout(Strategy):
    risk_pct = 0.01  # 1% risk per trade 🌙
    bb_period = 20
    bb_dev = 2
    vol_sma_period = 20 * 96  # 20 days in 15m intervals
    squeeze_lookback = 30 * 96  # 30 days in 15m
    atr_period = 14

    def init(self):
        # Clean data already handled externally ✨
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        # Calculate indicators using TA-Lib through self.I() 🌙
        self.upper_bb, self.middle_bb, self.lower_bb = self.I(
            talib.BBANDS, close, 
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev,
            name=['UpperBB', 'MiddleBB', 'LowerBB']
        )
        
        bb_width = self.upper_bb - self.lower_bb
        self.min_bb_width = self.I(
            talib.MIN, bb_width, 
            timeperiod=self.squeeze_lookback,
            name='MinBBWidth'
        )
        
        self.vol_sma = self.I(
            talib.SMA, volume,
            timeperiod=self.vol_sma_period,
            name='VolumeSMA'
        )
        
        self.atr = self.I(
            talib.ATR, high, low, close,
            timeperiod=self.atr_period,
            name='ATR'
        )

        # Trailing price trackers 🚀
        self.max_high = 0
        self.min_low = float('inf')

    def next(self):
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]

        if not self.position:
            # Long entry conditions 🌙✨
            long_cond = (
                (self.upper_bb[-1] - self.lower_bb[-1] <= self.min_bb_width[-1]) and \
                (current_close > self.upper_bb[-1]) and \
                (current_volume > self.vol_sma[-1])
            )
            
            # Short entry conditions 🌙🔻
            short_cond = (
                (self.upper_bb[-1] - self.lower_bb[-1] <= self.min_bb_width[-1]) and \
                (current_close < self.lower_bb[-1]) and \
                (current_volume > self.vol_sma[-1])
            )

            if long_cond:
                risk_per_share = current_close - self.lower_bb[-1]
                if risk_per_share > 0:
                    size = int(round((self.risk_pct * self.equity) / risk_per_share))
                    if size > 0:
                        self.buy(size=size, sl=self.lower_bb[-1])
                        self.max_high = self.data.High[-1]
                        print(f"🚀🌙 LONG ENTRY | Price: {current_close:.2f} | Size: {size} | SL: {self.lower_bb[-1]:.2f}")

            elif short_cond:
                risk_per_share = self.upper_bb[-1] - current_close
                if risk_per_share > 0:
                    size = int(round((self.risk_pct * self.equity) / risk_per_share))
                    if size > 0:
                        self.sell(size=size, sl=self.upper_bb[-1])
                        self.min_low = self.data.Low[-1]
                        print(f"🌙🔻 SHORT ENTRY | Price: {current_close:.2f} | Size: {size} | SL: {self.upper_bb[-1]:.2f}")

        else:
            if self.position.is_long:
                self.max_high = max(self.max_high, self.data.High[-1])
                trailing_stop = self.max_high - 2 * self.atr[-1]
                
                if current_close < self.middle_bb[-1] or current_close < trailing_stop:
                    self.position.close()
                    print(f"🌙✅ LONG EXIT | Price: {current_close:.2f} | Reason: {'Middle BB' if