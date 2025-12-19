Here's the complete backtesting implementation for the ChikouVolatility strategy:

```python
# 🌙 MOON DEV BACKTESTING SCRIPT FOR CHIKOU VOLATILITY STRATEGY 🚀

import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# ====================
# DATA PREPARATION
# ====================
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and prepare data 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Proper column mapping ✨
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Date'
})

# Set datetime index
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# ====================
# STRATEGY IMPLEMENTATION
# ====================
class ChikouVolatility(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌕
    bb_period = 20
    bb_dev = 2
    chikou_lookback = 26  # Ichimoku lag period 🌗

    def init(self):
        # 🌙 BOLLINGER BANDS CALCULATION
        def bb_upper(close):
            upper, _, _ = talib.BBANDS(close, 
                                      timeperiod=self.bb_period,
                                      nbdevup=self.bb_dev,
                                      nbdevdn=self.bb_dev,
                                      matype=0)
            return upper
        
        def bb_lower(close):
            _, _, lower = talib.BBANDS(close,
                                      timeperiod=self.bb_period,
                                      nbdevup=self.bb_dev,
                                      nbdevdn=self.bb_dev,
                                      matype=0)
            return lower
        
        # Add indicators using proper self.I() wrapper 🌌
        self.bb_upper = self.I(bb_upper, self.data.Close)
        self.bb_lower = self.I(bb_lower, self.data.Close)

    def next(self):
        # 🌙 CORE STRATEGY LOGIC
        if len(self.data) < self.chikou_lookback + 2:
            return  # Not enough data for calculations 🌑

        # Chikou Span condition calculation ✨
        current_close = self.data.Close[-1]
        chikou_reference = self.data.Close[-self.chikou_lookback]
        chikou_bullish = current_close > chikou_reference
        chikou_bearish = current_close < chikou_reference

        # Bollinger Band conditions 🌈
        prev_close = self.data.Close[-2]
        current_lower = self.bb_lower[-1]
        prev_lower = self.bb_lower[-2]
        current_upper = self.bb_upper[-1]
        prev_upper = self.bb_upper[-2]

        # 🚀 BULLISH ENTRY CONDITIONS
        bullish_entry = (
            chikou_bullish and
            (prev_close <= prev_lower) and 
            (current_close > current_lower)
        )

        # 🚨 BEARISH ENTRY CONDITIONS
        bearish_entry = (
            chikou_bearish and
            (prev_close >= prev_upper) and 
            (current_close < current_upper)
        )

        # 🌙 POSITION SIZING CALCULATION
        def calculate_size(entry_price, stop_price):
            risk_per_share = abs(entry_price - stop_price)
            if risk_per_share == 0:
                return 0
            risk_amount = self.equity * self.risk_percent
            size = risk_amount / risk_per_share
            return int(round(size))

        # 💫 ENTRY LOGIC
        if not self.position:
            if bullish_entry:
                stop_price = current_lower * 0.999  # 0.1% below lower band 🌑
                size = calculate_size(current_close, stop_price)
                if size > 0:
                    self.buy(size=size, sl=stop_price)
                    print(f"🌙🚀 MOON DEV LONG ENTRY | Price: {current_close:.2f} | Size: {size} | SL: {stop_price:.2f}")

            elif bearish_entry:
                stop_price =