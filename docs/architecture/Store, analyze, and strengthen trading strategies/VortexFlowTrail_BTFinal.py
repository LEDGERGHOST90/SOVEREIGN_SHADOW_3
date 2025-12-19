Here's the fully debugged version of your VortexFlowTrail strategy with Moon Dev themed improvements:

```python
import pandas as pd
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta

# Data preprocessing
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path)

# Clean and format columns - Moon Dev precision formatting ✨
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col], errors='ignore')
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Date'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class VortexFlowTrail(Strategy):
    vi_period = 14
    cmf_period = 20
    atr_period = 14
    atr_multiplier = 2
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # Vortex Indicator using pandas_ta - Moon Dev optimized
        vi = ta.vortex(
            high=self.data.High,
            low=self.data.Low,
            close=self.data.Close,
            length=self.vi_period
        )
        self.vi_plus = self.I(lambda x: x, vi[f'VORTIC_{self.vi_period}'], name='VI+')
        self.vi_minus = self.I(lambda x: x, vi[f'VORTICm_{self.vi_period}'], name='VI-')

        # Chaikin Money Flow - Cosmic money flow analysis 🌌
        self.cmf = self.I(ta.cmf,
                         high=self.data.High,
                         low=self.data.Low,
                         close=self.data.Close,
                         volume=self.data.Volume,
                         length=self.cmf_period,
                         name='CMF')

        # ATR for volatility stops - Moon Dev safety nets 🚀
        self.atr = self.I(talib.ATR,
                          high=self.data.High,
                          low=self.data.Low,
                          close=self.data.Close,
                          timeperiod=self.atr_period,
                          name='ATR')

        print("🌙✨ VortexFlowTrail initialized with Moon Dev precision! Parameters:")
        print(f"VI Period: {self.vi_period}, CMF Period: {self.cmf_period}")
        print(f"ATR Multiplier: {self.atr_multiplier}, Risk %: {self.risk_pct*100}%")

    def next(self):
        if len(self.data.Close) < max(self.vi_period, self.cmf_period, self.atr_period) + 1:
            return  # Wait for sufficient data

        if not self.position:
            # Moon Dev entry logic with cosmic alignment 🌑🌕
            vi_cross = (self.vi_plus[-2] < self.vi_minus[-2]) and (self.vi_plus[-1] > self.vi_minus[-1])
            cmf_cross = (self.cmf[-2] < 0) and (self.cmf[-1] > 0)
            
            if vi_cross and cmf_cross:
                atr_value = self.atr[-1]
                if atr_value <= 0:
                    print("🌑 Warning: Invalid ATR value detected - skipping trade")
                    return
                
                # Moon Dev risk management - precise position sizing ✨
                stop_distance = self.atr_multiplier * atr_value
                risk_amount = self.equity * self.risk_pct
                position_size = risk_amount / stop_distance
                position_size = int(round(position_size))  # Ensure whole units
                
                if position_size > 0:
                    entry_price = self.data.Close[-1]
                    stop_price = entry_price - stop_distance
                    self.buy(size=position_size, sl=stop_price)
                    self.trailing_stop = stop_price
                    
                    print(f"🌕 BUY Signal! Size: {position_size} units 🚀")
                    print(f"Entry: {entry_price:.2f}, Initial Stop: {stop_price:.2f}")
                    print(f"ATR: {atr_value:.2f}, Stop Distance: {stop_distance:.2f}")

        elif self.position:
            # Moon Dev trailing stop logic 🌙
            current_stop = self.data.Close[-1] -