I'll debug the code while maintaining the original strategy logic. Here's the fixed version with Moon Dev themed debug prints:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR TERMINUSBREAKOUT STRATEGY 🚀

# ===== REQUIRED IMPORTS =====
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# ===== DATA PREPARATION =====
# Load and clean market data 🌌
data = pd.read_csv(
    '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv',
    parse_dates=['datetime'],
    index_col='datetime'
)

# Clean column names ✨
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map to backtesting.py format 🌕
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# ===== STRATEGY IMPLEMENTATION =====
class TerminusBreakout(Strategy):
    risk_pct = 0.02  # 2% risk per trade 🌗
    band_period = 20
    
    def init(self):
        # 🌗 BOLLINGER BANDS CALCULATION USING TA-LIB
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 
                              timeperiod=self.band_period, nbdevup=2, 
                              nbdevdn=2, matype=0, name='BB_UPPER', which=0)
        self.bb_mid = self.I(talib.BBANDS, self.data.Close,
                            timeperiod=self.band_period, nbdevup=2,
                            nbdevdn=2, matype=0, name='BB_MID', which=1)
        self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                              timeperiod=self.band_period, nbdevup=2,
                              nbdevdn=2, matype=0, name='BB_LOWER', which=2)
        
        # 🌑 VIX TERM STRUCTURE INDICATOR
        self.vix_term = self.I(lambda: self.data['vix_futures'] - self.data['vix_spot'])
        
        self.prev_term = None  # Track previous term structure

    def next(self):
        # 🌓 MOON DEV SIGNAL VALIDATION CHECK
        if len(self.data.Close) < 2:
            print("🌑 Moon Dev Warning: Not enough data points for analysis")
            return

        current_close = self.data.Close[-1]
        prev_close = self.data.Close[-2]
        current_term = self.vix_term[-1]
        prev_term = self.vix_term[-2] if len(self.vix_term) > 1 else None

        # 🌗 BOLLINGER BAND BREAKOUT DETECTION (MANUAL CROSSOVER)
        long_break = (prev_close > self.bb_lower[-2]) and (current_close < self.bb_lower[-1])
        short_break = (prev_close < self.bb_upper[-2]) and (current_close > self.bb_upper[-1])

        # 🌑 VIX TERM STRUCTURE FLIP DETECTION (MANUAL CROSSUNDER)
        term_bullish = (prev_term is not None and prev_term >= 0) and (current_term < 0)
        term_bearish = (prev_term is not None and prev_term <= 0) and (current_term > 0)

        # 🌕 MOON DEV ENTRY LOGIC
        if not self.position:
            # Long entry: Lower band breakout + VIX backwardation
            if long_break and term_bullish:
                print("🌕 Moon Dev Signal: LONG entry triggered!")
                self.enter_long()
            
            # Short entry: Upper band breakout + VIX contango
            elif short_break and term_bearish:
                print("🌑 Moon Dev Signal: SHORT entry triggered!")
                self.enter_short()

        # 🌑 POSITION MANAGEMENT
        else:
            self.manage_positions(current_close)

    def enter_long(self):
        # 🌓 RISK CALCULATION
        entry_price = self.data.Close[-1]
        stop_price = self.bb_upper[-1]  # Opposite band
        risk_amount = self.risk_pct * self.equity
        risk_per_share = abs(entry_price - stop_price)