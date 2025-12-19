Here's the fixed code with all indicators properly implemented without any backtesting.lib usage, along with Moon Dev themed debug prints:

```python
# 🌙 Moon Dev's VoltaBandwidth Backtest Implementation 🚀✨

import pandas as pd
import numpy as np
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy

# Data Preparation 🌍
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean column names 🌟
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Column mapping 🌌
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VoltaBandwidth(Strategy):
    # Strategy Parameters ⚙️
    bb_period = 20
    rsi_period = 14
    vwma_period = 20
    atr_period = 14
    risk_per_trade = 0.01
    
    def init(self):
        # 🌗 Indicator Calculations
        # Bollinger Bands with Band Width 🌈
        upper, middle, lower = talib.BBANDS(
            self.data.Close, 
            timeperiod=self.bb_period, 
            nbdevup=2, 
            nbdevdn=2, 
            matype=0
        )
        self.upper_band = self.I(lambda: upper, name='Upper Band')
        self.middle_band = self.I(lambda: middle, name='Middle Band')
        self.lower_band = self.I(lambda: lower, name='Lower Band')
        
        self.band_width = self.I(
            lambda: (upper - lower) / middle,
            name='Band Width'
        )
        
        # RSI Filter 🔮
        self.rsi = self.I(
            talib.RSI, 
            self.data.Close, 
            timeperiod=self.rsi_period,
            name='RSI'
        )
        
        # Volume Weighted MA 📊
        self.vwma = self.I(
            lambda: ta.vwma(self.data.Close, self.data.Volume, length=self.vwma_period),
            name='VWMA'
        )
        
        # ATR for Risk Management 🛡️
        self.atr = self.I(
            talib.ATR, 
            self.data.High, 
            self.data.Low, 
            self.data.Close,
            timeperiod=self.atr_period,
            name='ATR'
        )
        
        # Volume SMA 📈
        self.volume_sma = self.I(
            talib.SMA, 
            self.data.Volume, 
            timeperiod=20,
            name='Volume SMA'
        )
        
        # Strategy Variables 🌙
        self.consecutive_losses = 0
        self.daily_initial_equity = None
        self.current_date = None

    def next(self):
        # 🌓 New Day Setup
        current_date = self.data.index[-1].date()
        if current_date != self.current_date:
            self.current_date = current_date
            self.daily_initial_equity = self.equity
            print(f"🌄 New Moon Day {current_date} | Starting Equity: {self.equity:,.2f}")

        # 🚫 Risk Management Checks
        if self.consecutive_losses >= 3:
            print("🌘 Three Consecutive Losses! Trading Halted Until Next Win")
            return
            
        if self.daily_initial_equity and self.equity < self.daily_initial_equity * 0.97:
            print(f"🌧️ Daily Loss Limit Hit! Current Equity: {self.equity:,.2f}")
            if self.position:
                self.position.close()
            return

        # 🚀 Entry Logic
        if not self.position:
            # Long Conditions 🌕
            long_cond = (
                self.data.Close[-1] > self.upper_band[-1] and
                self.band_width[-1] > self.band_width[-2] and
                self.data.Volume[-1] > self.volume_sma[-1] and
                self.rsi[-1] < 70
            )
            
            # Short Conditions 🌑
            short_cond = (
                self.data.Close[-1] < self.lower_band[-1] and
                self.b