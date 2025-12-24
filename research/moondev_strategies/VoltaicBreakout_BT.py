```python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import talib
from backtesting import Strategy, Backtest

class VoltaicBreakout(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌙
    
    def init(self):
        # Clean data columns already handled in data preparation
        
        # Bollinger Bandwidth calculation ✨
        def bb_bandwidth(close, timeperiod=20, nbdev=2):
            upper, middle, lower = talib.BBANDS(close, timeperiod=timeperiod, 
                                              nbdevup=nbdev, nbdevdn=nbdev)
            return (upper - lower) / middle
        
        # Historical percentile calculation 🌗
        def calc_percentile(series, window=100, percentile=20):
            return np.array([np.percentile(series[max(0,i-window):i], percentile) 
                           for i in range(len(series))])
        
        # Indicator initialization 🚀
        self.bb_width = self.I(bb_bandwidth, self.data.Close, 20, 2)
        self.bb_percentile = self.I(calc_percentile, self.bb_width, 100, 20)
        self.volume_ma20 = self.I(talib.SMA, self.data.Volume, 20)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, 14)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        print("🌙 Voltaic Breakout Strategy Initialized! ✨")

    def next(self):
        # Wait for sufficient data 🌊
        if len(self.data) < 100:
            return
            
        # Core Strategy Logic ⚡
        current_idx = len(self.data) - 1
        
        # Volatility contraction signal 🌌
        volatility_signal = (
            self.bb_width[-1] < self.bb_percentile[-1] and 
            self.bb_width[-2] >= self.bb_percentile[-2]
        )
        
        # Volume surge confirmation 🔊
        volume_ratio = self.data.Volume[-1] / self.volume_ma20[-1]
        volume_signal = volume_ratio > 1.5
        
        if volatility_signal and volume_signal:
            print(f"🌋 BREAKOUT DETECTED! Bandwidth {self.bb_width[-1]:.4f} < {self.bb_percentile[-1]:.4f}")
            print(f"📈 Volume Surge {volume_ratio:.2f}x MA | ATR: {self.atr[-1]:.2f}")
            
            # Entry price levels 🎯
            entry_high = self.data.High[-1]
            entry_low = self.data.Low[-1]
            atr_value = self.atr[-1]
            
            # Risk calculations 🧮
            equity = self.equity
            risk_amount = equity * self.risk_percent
            
            # Long entry setup 🚀
            long_sl = entry_high - 0.75 * atr_value
            long_risk = entry_high - long_sl
            if long_risk > 0:
                long_size = int(round(risk_amount / long_risk))
                self.buy(stop=entry_high, 
                        sl=long_sl, 
                        size=long_size,
                        tag={'type': 'long', 
                            'adx_window': 3,
                            'atr_entry': atr_value})
                print(f"🚀 LONG Entry Signal: {entry_high:.2f}")
                print(f"   Size: {long_size} | SL: {long_sl:.2f} (-{0.75*atr_value:.2f})")
            
            # Short entry setup 🌧️
            short_sl = entry_low + 0.75 * atr_value
            short_risk = short_sl - entry_low
            if short_risk > 0:
                short_size = int(round(risk_amount / short_risk))
                self.sell(stop=entry_low, 
                         sl=short_sl, 
                         size=short_size,
                         tag={'type': 'short',
                             'adx_window': 3,
                             'atr_entry': atr_value})
                print(f"🌧️ SHORT Entry Signal: {entry_low:.2f}")
                print(f"   Size: {short_size} | SL: {short_sl:.2f} (+{0.75*