I'll analyze and fix the code while maintaining the original strategy logic. Here's the debugged version with Moon Dev improvements:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
from pathlib import Path

# =====================
# 🌙 MOON DEV DATA PREP
# =====================
print("🌙 Initializing Moon Dev Data Preparation...")
data_path = Path("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and prepare data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# =====================
# 🌟 STRATEGY CLASS
# =====================
class DeltaBandBreakout(Strategy):
    # Strategy parameters
    bb_period = 20
    bb_stddev = 2
    contraction_periods = 5
    contraction_threshold = 0.02  # 2%
    volume_surge_multiplier = 1.5  # 50% above average
    exit_bandwidth_ratio = 0.5
    exit_consecutive_bars = 3
    risk_per_trade = 0.02  # 2% of equity
    stop_loss_pct = 0.01  # 1%
    
    def init(self):
        print("🌙 Initializing Moon Dev Indicators...")
        # Bollinger Bands Calculation
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_stddev,
            nbdevdn=self.bb_stddev,
            matype=0
        )

        # Delta Volume (OBV)
        self.delta_volume = self.I(
            talib.OBV,
            self.data.Close,
            self.data.Volume
        )
        
        # Volume MA
        self.volume_ma = self.I(
            talib.SMA,
            self.data.Volume,
            timeperiod=20
        )
        
        # Track entry bandwidth
        self.entry_bandwidth = None

    def _check_contraction(self):
        """🌙 Check for volatility contraction"""
        current_bw = self.bb_upper[-1] - self.bb_lower[-1]
        avg_bw = sum(self.bb_upper[-self.contraction_periods-1:-1] - 
                   self.bb_lower[-self.contraction_periods-1:-1]) / self.contraction_periods
        return current_bw < avg_bw * (1 - self.contraction_threshold)

    def _negative_divergence(self):
        """🌙 Check for negative divergence between price and OBV"""
        if len(self.data.Close) < 5 or len(self.delta_volume) < 5:
            return False
            
        # Price makes higher high while OBV makes lower high
        price_hh = (self.data.Close[-3] < self.data.Close[-1] and 
                   self.data.Close[-2] < self.data.Close[-1])
        obv_lh = (self.delta_volume[-3] > self.delta_volume[-1] and 
                 self.delta_volume[-2] > self.delta_volume[-1])
        return price_hh and obv_lh

    def next(self):
        # 🌙 Risk Management Check
        if len(self.trades) >= 3:
            last_three = [t for t in self.trades[-3:] if t.exit_price]
            if len(last_three) >= 3 and all(t.pnl < 0 for t in last_three):
                print("🌙💔 MOON DEV ALERT: 3 consecutive losses - trading paused!")
                return

        if not self.position:
            # 🌟 Long Entry Conditions
            if (self._check_contraction() and 
                self._negative_divergence() and 
                self.data.Close[-1] > self.bb_upper[-1] and 
                self.data.Volume[-1] > self.volume_ma[-1] * self.volume_surge_multiplier):
                
                # Calculate position size based on risk
                stop_price = self.data.Close[-1] *