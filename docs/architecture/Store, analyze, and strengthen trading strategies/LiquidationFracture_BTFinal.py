I'll fix the incomplete code while maintaining the original strategy logic. Here's the complete, debugged version with Moon Dev themed prints:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# =====================
# DATA PREPARATION 🌙📊
# =====================
print("🌙 Initializing Lunar Data Processing...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean and prepare data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])

# Column mapping for backtesting.py
column_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}
data = data.rename(columns=column_mapping)
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# =====================
# STRATEGY CORE 🌙🚀
# =====================
class LiquidationFracture(Strategy):
    initial_capital = 1_000_000
    
    def init(self):
        # Ichimoku Cloud Configuration 🌙☁️
        print("🌙 Configuring Ichimoku Cloud Indicators...")
        self.tenkan = self.I(lambda high, low: 
            (talib.MAX(high, 9) + talib.MIN(low, 9)) / 2,
            self.data.High, self.data.Low, name='Tenkan')
            
        self.kijun = self.I(lambda high, low: 
            (talib.MAX(high, 26) + talib.MIN(low, 26)) / 2,
            self.data.High, self.data.Low, name='Kijun')
            
        self.senkou_a = self.I(lambda ts, ks: 
            (ts + ks) / 2, self.tenkan, self.kijun, name='Senkou A')
            
        self.senkou_b = self.I(lambda high, low: 
            (talib.MAX(high, 52) + talib.MIN(low, 52)) / 2,
            self.data.High, self.data.Low, name='Senkou B')

        # Risk Management Indicators 🌙🛡️
        print("🌙 Initializing Risk Management Systems...")
        self.atr = self.I(talib.ATR, 
            self.data.High, self.data.Low, self.data.Close, 14, name='ATR')
            
        self.swing_high = self.I(talib.MAX, 
            self.data.High, 20, name='Swing High')

        # Liquidation Metrics 🌙💧
        print("🌙 Calibrating Liquidation Detection Sensors...")
        self.liq_ma = self.I(talib.SMA, 
            self.data['liquidations'], 672, name='Liquidation MA')
        
        self.entry_bar = None

    def next(self):
        # Moon Dev Debug Prints 🌙📝
        print(f"🌙 Lunar Pulse Check | Bar: {len(self.data)} | Close: {self.data.Close[-1]:.2f}")

        if self.position:
            # Emergency Exit Condition 🌙🚨
            current_liq = self.data['liquidations'][-1]
            if current_liq < 2 * self.liq_ma[-1]:
                print(f"🌙🚨 LIQUIDATION COLLAPSE! Closing position at {self.data.Close[-1]}")
                self.position.close()
            
            # Time-based Exit 🌙⏳
            elif len(self.data) - self.entry_bar >= 16:  # 4 hours
                print(f"🌙⏳ TIME VORTEX EXPIRED! Closing position")
                self.position.close()
        else:
            # Entry Conditions Check 🌙🔍
            if len(self.data) < 672 + 26:  # Ensure warmup period
                return

            # Cloud Break Check 🌩️
            cloud_top = max(self.senkou_a[-26], self.senkou_b[-26])
            cloud_bottom = min(self.senkou_a[-26], self.senkou_b[-26])
            price_in_bear_zone = self.data.Close[-1] < cloud_bottom

            # Liquidation Spike 🌊
            liq_spike = self.data['liquidations'][-1] >= 3 * self.liq_ma[-1]

            if price_in_bear_zone and li