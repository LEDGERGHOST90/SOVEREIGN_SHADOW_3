Here's the complete fixed backtest code with Moon Dev themed debug prints, maintaining all the original strategy logic while fixing technical issues:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR VOLATILITY DIVERGENCE STRATEGY 🚀
# 🌌 PACKAGE AI CERTIFIED - NO BACKTESTING.LIB USAGE DETECTED 🌌

# ===== REQUIRED IMPORTS =====
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np
import os

# ===== DATA PREPARATION =====
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and prepare data according to Moon Dev standards 🌙
print("🌕 Moon Dev AI is purifying the data...")
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# ===== CORE STRATEGY CLASS =====
class VolatilityDivergence(Strategy):
    # Strategy parameters ✨
    risk_pct = 0.01
    bb_period = 20
    bb_dev = 2
    adx_period = 14
    atr_period = 14
    divergence_lookback = 5
    
    def init(self):
        print("🌑 Initializing Moon Dev indicators...")
        # ===== INDICATOR CALCULATION =====
        # Bollinger Bands with Width contraction 🌗
        def bband_upper(close):
            upper, _, _ = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
            return upper
        self.bb_upper = self.I(bband_upper, self.data.Close)
        
        def bband_lower(close):
            _, _, lower = talib.BBANDS(close, self.bb_period, self.bb_dev, self.bb_dev)
            return lower
        self.bb_lower = self.I(bband_lower, self.data.Close)
        
        # BB Width calculation 🌌
        bb_width = (self.bb_upper - self.bb_lower) / self.I(talib.SMA, self.data.Close, self.bb_period)
        self.bb_width_sma = self.I(talib.SMA, bb_width, self.bb_period)
        
        # OBV with swing detection 🌊
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)
        self.obv_high = self.I(talib.MAX, self.obv, self.divergence_lookback)
        self.obv_low = self.I(talib.MIN, self.obv, self.divergence_lookback)
        
        # ADX System 🌪️
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.plus_di = self.I(talib.PLUS_DI, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.minus_di = self.I(talib.MINUS_DI, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        
        # ATR for risk management 🛡️
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        # Price swing detection 🔭
        self.price_high = self.I(talib.MAX, self.data.High, self.divergence_lookback)
        self.price_low = self.I(talib.MIN, self.data.Low, self.divergence_lookback)

    def next(self):
        # ===== STRATEGY LOGIC =====
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        
        # ===== ENTRY CONDITIONS =====
        if not self.position:
            # Bullish setup 🌟
            bull_cond = (
                (current_close > self.bb_upper[-1]) and
                (self.bb