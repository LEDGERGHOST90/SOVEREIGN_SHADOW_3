Here's the fixed code with all backtesting.lib imports removed and replaced with proper implementations, along with Moon Dev themed debug prints:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])

# Format columns for backtesting.py
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Convert index to datetime
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class LiquiClusterSqueeze(Strategy):
    risk_per_trade = 0.01  # 1% of equity per trade
    max_concurrent_trades = 3
    
    def init(self):
        # Bollinger Band components
        self.bb_middle = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.bb_stddev = self.I(talib.STDDEV, self.data.Close, timeperiod=20, nbdev=1)
        
        # Volume indicators
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        # Liquidation clusters (swing levels)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=50)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=50)
        
        # Track bandwidth history
        self.bandwidth_history = []
        
        # Trade tracking
        self.active_trades = 0
        self.entry_volume = 0
        self.consecutive_low_volume = 0

    def next(self):
        current_close = self.data.Close[-1]
        print(f"🌙 Moon Dev Debug: Processing {self.data.index[-1]} | Close: {current_close:.2f} ✨")
        
        # Manage existing positions
        if self.position:
            # Emergency volume exit check
            current_volume = self.data.Volume[-1]
            if current_volume < 0.5 * self.entry_volume:
                self.consecutive_low_volume += 1
                print(f"🚨 Volume Alert: {self.consecutive_low_volume}/3 low volume bars 🌧️")
                if self.consecutive_low_volume >= 3:
                    print(f"💥 EMERGENCY EXIT: Volume collapse detected! 🚫")
                    self.position.close()
            else:
                self.consecutive_low_volume = 0

        # Skip if not enough data
        if len(self.data) < 50 or len(self.bandwidth_history) < 20:
            return

        # Calculate Bollinger Bandwidth
        current_upper = self.bb_middle[-1] + 2 * self.bb_stddev[-1]
        current_lower = self.bb_middle[-1] - 2 * self.bb_stddev[-1]
        bandwidth = (current_upper - current_lower) / self.bb_middle[-1]
        self.bandwidth_history.append(bandwidth)
        
        # Squeeze detection
        min_bandwidth = min(self.bandwidth_history[-20:])
        squeeze_active = bandwidth <= 1.2 * min_bandwidth
        print(f"🔍 Squeeze Status: {squeeze_active} | Current BW: {bandwidth:.4f} vs Min BW: {min_bandwidth:.4f} 🌀")

        # Get cluster levels
        cluster_high = self.swing_high[-1]
        cluster_low = self.swing_low[-1]

        # Long entry logic
        if not self.position and self.active_trades < self.max_concurrent_trades:
            if (0.005 <= (cluster_high - current_close)/cluster_high <= 0.015 and
                self.data.High[-1] > cluster_high and
                self.data.Volume[-1] > self.volume_ma[-1] and
                squeeze_active):
                
                print(f"🚀 LONG Signal: Breaking cluster high at {cluster_high:.2f} 📈")
                sl_price = cluster_low * 0.995
                risk_per_share