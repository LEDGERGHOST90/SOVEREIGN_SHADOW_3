```python
# 🌙 Moon Dev's Volatility Liquidity Backtest 🌙
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta
from datetime import datetime, time

# 🚀 Data Preparation Rocket Boosters Ignite!
data = pd.read_csv(
    '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv',
    parse_dates=['datetime'],
    index_col='datetime'
)

# 🌌 Cosmic Data Cleaning
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolatilityLiquidity(Strategy):
    # 🌗 Lunar Strategy Parameters
    donchian_period = 20
    atr_period = 14
    vol_multiplier = 0.5
    volume_ema_period = 14
    risk_pct = 0.01  # 1% risk per trade
    rr_ratio = 2     # Moon Mission Reward/Risk Ratio
    
    # 🌑 Low-Liquidity Hours Configuration (UTC)
    trade_start = time(0, 0)  # Midnight UTC
    trade_end = time(4, 0)    # 4 AM UTC

    def init(self):
        # 🌠 Cosmic Indicators Initialization
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        # 🌀 Volatility-Adjusted Donchian Channel
        self.upper_band = self.I(talib.MAX, self.data.High, self.donchian_period) + (self.atr * self.vol_multiplier)
        self.lower_band = self.I(talib.MIN, self.data.Low, self.donchian_period) - (self.atr * self.vol_multiplier)
        
        # 📈 Volume Momentum Engine
        self.volume_ema = self.I(talib.EMA, self.data.Volume, self.volume_ema_period)
        
        # 🕰️ Trade Duration Tracking
        self.trade_entry_time = None

    def next(self):
        current_time = self.data.index[-1].time()
        in_trading_hours = self.trade_start <= current_time <= self.trade_end
        
        # 🌗 Lunar Cycle Exit Protocol
        if self.position and not in_trading_hours:
            self.position.close()
            print(f"🌙 Lunar Exit: Trading hours ended | Price: {self.data.Close[-1]:.2f}")
            return

        if not in_trading_hours:
            return  # Only trade during moon phase hours

        # 🚀 Core Trading Logic
        price = self.data.Close[-1]
        upper = self.upper_band[-1]
        lower = self.lower_band[-1]
        vol_trend = self.volume_ema[-1] < self.volume_ema[-2]

        # 🛰️ Signal Detection System
        long_signal = price > upper and vol_trend
        short_signal = price < lower and vol_trend

        # 💰 Risk Management Constellation
        if not self.position:
            risk_amount = self.risk_pct * self.equity
            atr_value = self.atr[-1]
            
            if long_signal:
                sl = price - (atr_value * 1.5)
                tp = price + (atr_value * self.rr_ratio * 1.5)
                position_size = int(round(risk_amount / (price - sl)))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=sl, tp=tp)
                    print(f"🚀 BLAST OFF LONG! | Size: {position_size} | Entry: {price:.2f}")
                    self.trade_entry_time = self.data.index[-1]

            elif short_signal:
                sl = price + (atr_value * 1.5)
                tp = price - (atr_value * self.rr_ratio * 1.5)
                position_size = int(round(risk_amount / (sl - price)))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=sl, tp=tp)
                    print(f"🌑 BLACK HOLE SHORT! | Size: {position_size} | Entry: {