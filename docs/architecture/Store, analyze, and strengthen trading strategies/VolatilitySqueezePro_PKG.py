Here's the fixed code with all `backtesting.lib` imports and functions removed, and replaced with appropriate alternatives:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR VOLATILITYSQUEEZEPRO STRATEGY 🚀

import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VolatilitySqueezePro(Strategy):
    # Strategy parameters 🌐
    bb_period = 20
    bb_dev = 2
    keltner_period = 20
    atr_multiplier = 1.5
    atr_period = 14
    risk_pct = 0.01  # 1% risk per trade 🌕
    rr_ratio = 2  # Risk:Reward 1:2 ✨

    def init(self):
        # Clean data columns 🌙
        self.data.columns = [col.strip().lower() for col in self.data.columns]
        
        # Calculate indicators using TA-Lib 📊
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        # Bollinger Bands 📈
        self.bb_upper, self.bb_middle, self.bb_lower = talib.BBANDS(
            close, self.bb_period, self.bb_dev, self.bb_dev
        )
        self.I(lambda: self.bb_upper, name='Upper BB')
        self.I(lambda: self.bb_lower, name='Lower BB')

        # Keltner Channels 🌗
        ema = talib.EMA(close, self.keltner_period)
        atr = talib.ATR(high, low, close, self.atr_period)
        self.upper_keltner = ema + atr * self.atr_multiplier
        self.lower_keltner = ema - atr * self.atr_multiplier
        self.I(lambda: self.upper_keltner, name='Upper Keltner')
        self.I(lambda: self.lower_keltner, name='Lower Keltner')

        # Volatility Squeeze Detection 🌪️
        self.bb_width = self.bb_upper - self.bb_lower
        self.bb_width_ma = talib.SMA(self.bb_width, self.bb_period)
        self.bb_width_std = talib.STDDEV(self.bb_width, self.bb_period)
        self.squeeze_threshold = self.bb_width_ma - self.bb_width_std
        self.I(lambda: self.squeeze_threshold, name='Squeeze Threshold')

    def next(self):
        # Moon Dev Position Management Logic 🌑🌕
        if self.position:
            return  # Hold existing position

        # Current indicator values 📌
        price = self.data.Close[-1]
        upper_kelt = self.upper_keltner[-1]
        lower_kelt = self.lower_keltner[-1]
        bb_width = self.bb_width[-1]
        threshold = self.squeeze_threshold[-1]

        # Volatility Squeeze Condition 🌪️
        squeeze_active = bb_width < threshold

        # Entry Signals 🚦
        long_trigger = price > upper_kelt
        short_trigger = price < lower_kelt

        # Moon Dev Risk Calculations 🔒
        equity = self.equity
        risk_amount = equity * self.risk_pct
        
        if squeeze_active and long_trigger:
            # Long Entry Setup 🚀
            entry_price = self.data.Open[-1]
            sl_price = self.lower_keltner[-1]
            risk_per_share = entry_price - sl_price
            
            if risk_per_share > 0:
                position_size = int(round(risk_amount / risk_per_share))
                tp_price = entry_price + (risk_per_share * self.rr_ratio)
                
                self.buy(size=position_size, sl=sl_price, tp=tp_price)
                print(f"🚀 MOON DEV LONG ENTRY 🚀 Size: {position_size} | Entry: {entry_price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f} 🌕")

        elif squeeze_active and short_trigger:
            # Short Entry Setup 🌑
            entry_price = self.data.Open[-1]
            sl_price = self.upper_keltner[-1]
            risk_per_share = sl_price - entry_price
            
            if risk_per_share > 0:
                position_size = int(round(risk_amount / risk_per_share))
                tp_price = entry_price - (risk_per_share * self.rr_ratio)
                
                self.sell(size