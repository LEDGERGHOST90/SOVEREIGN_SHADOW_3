Here's the fixed and complete code with all necessary improvements and Moon Dev themed debug prints 🌙✨:

```python
import pandas as pd
import pandas_ta as ta
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to proper case
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Convert to datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Calculate 4H Heikin-Ashi using resampling
def calculate_ha(df):
    return df.ta.ha(append=True)

resampled_4h = data.resample('4H').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
})
resampled_4h = resampled_4h.ta.ha(append=True)
ha_columns = ['HA_open', 'HA_high', 'HA_low', 'HA_close']
data = data.join(resampled_4h[ha_columns].resample('15T').ffill())

class ClusterReversal(Strategy):
    def init(self):
        # Moon Dev Indicator Initialization 🌙
        self.ha_close = self.I(lambda: self.data.HA_close)
        self.ha_open = self.I(lambda: self.data.HA_open)
        
        # Volatility indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.atr_sma = self.I(talib.SMA, self.atr, timeperiod=14)
        
        # Swing levels
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        print("🌙 Lunar indicators initialized! Ready for launch 🚀")

    def next(self):
        if len(self.data) < 20:
            return

        # Current market conditions 🌌
        current_close = self.data.Close[-1]
        ha_bearish = self.ha_close[-1] < self.ha_open[-1]
        ha_bullish = self.ha_close[-1] > self.ha_open[-1]
        prev_ha_bearish = self.ha_close[-2] < self.ha_open[-2]
        
        # Volatility check 🌪️
        volatility_ok = self.atr[-1] < self.atr_sma[-1]
        
        # Swing levels 🎯
        swing_high = self.swing_high[-1]
        swing_low = self.swing_low[-1]

        # Entry logic 🌗
        if not self.position:
            # Short signal constellation 🌑
            if ha_bearish and not prev_ha_bearish and volatility_ok:
                if current_close >= swing_high * 0.995:
                    risk_amount = self.equity * 0.01
                    stop_loss = swing_high + 0.0001
                    risk_per_share = stop_loss - current_close
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss, tp=current_close - 2*(stop_loss-current_close))
                        print(f"🌑 BEARISH REVERSAL! Short {position_size} @ {current_close:.2f}")
                        print(f"   🛑 SL: {stop_loss:.2f} | 🎯 TP: {current_close - 2*(stop_loss-current_close):.2f}")

            # Long signal constellation 🌕
            elif ha_bullish and not prev_ha_bullish and volatility_ok:
                if current_close <= swing_low * 1.005:
                    risk_amount = self.equity * 0.01
                    stop_loss = swing_low - 0.0001
                    risk_per_share = current_close - stop_loss
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size