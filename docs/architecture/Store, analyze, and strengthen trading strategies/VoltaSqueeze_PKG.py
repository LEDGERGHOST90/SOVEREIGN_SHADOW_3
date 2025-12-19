The code you've provided is already well-structured and doesn't contain any `backtesting.lib` imports or functions. However, I'll ensure that all indicators are correctly implemented and that the code adheres to Moon Dev's standards. Here's the verified and slightly enhanced version of your code:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import pandas_ta as pta
import numpy as np
from backtesting import Strategy, Backtest

# Moon Dev Data Preparation Ritual 🌙✨
def prepare_data(filepath):
    # Load and cleanse data
    data = pd.read_csv(filepath, parse_dates=['datetime'])
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Proper column mapping
    data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    data.set_index('datetime', inplace=True)
    return data

class VoltaSqueeze(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    lookback_period = 100
    
    def init(self):
        # Moon Dev Indicator Ceremony 🌙📊
        # Bollinger Bands
        close = self.data.Close
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, close, 
                                                   timeperiod=20, nbdevup=2, nbdevdn=2, 
                                                   matype=0, name='BBANDS')
        
        # BB Width Calculation
        bb_width = (self.upper - self.lower) / self.middle
        self.bb_width = self.I(lambda x: x, bb_width, name='BB_Width')
        
        # Width Percentile (Pandas_TA implementation)
        self.width_pct = self.I(pta.percentile, self.bb_width, length=self.lookback_period, 
                              name='Width_Pct')
        
        # Volume Confirmation
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='Vol_SMA')
        
        # ATR for Exit Signals
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                        timeperiod=20, name='ATR_20')
        
        print("🌙 VoltaSqueeze Strategy Activated! May the squeeze be with you! 🚀")

    def next(self):
        current_close = self.data.Close[-1]
        current_upper = self.upper[-1]
        current_width_pct = self.width_pct[-1]
        current_vol = self.data.Volume[-1]
        vol_sma = self.vol_sma[-1]

        # Moon Dev Entry Protocol 🌙💎
        if not self.position:
            squeeze_condition = (current_width_pct <= 10)
            volume_condition = (current_vol < vol_sma)
            breakout_condition = (current_close > current_upper) and (self.data.Close[-2] <= self.upper[-2])

            if all([squeeze_condition, volume_condition, breakout_condition]):
                # Risk Management Calculation
                stop_price = self.lower[-1]
                risk_per_share = current_close - stop_price
                
                if risk_per_share <= 0:
                    print("⚠️ Cosmic Anomaly! Negative risk detected. Aborting launch! 🚨")
                    return
                
                position_size = (self.equity * self.risk_percent) / risk_per_share
                position_size = int(round(position_size))
                
                # Stellar Entry Signal 🌠
                self.buy(size=position_size, sl=stop_price, 
                        tag={'atr_entry': self.atr[-1], 'entry_price': current_close})
                print(f"🚀 LIFTOFF! Long {position_size} units at {current_close:.2f}")
                print(f"🔭 Tracking stop at {stop_price:.2f} | ATR Shield: {self.atr[-1]:.2f}")

        # Moon Dev Exit Protocol 🌙🎯
        for trade in self.trades:
            if trade.is_long:
                atr_entry = trade.tag['atr_entry']
                tp_level = trade.entry_price + atr_entry
                
                if current_close >= tp_level:
                    trade.close()
                    print(f"🌕 LUNAR LANDING! TP reached at {tp_level:.2f} | Profit: {trade.pl:.2f}")