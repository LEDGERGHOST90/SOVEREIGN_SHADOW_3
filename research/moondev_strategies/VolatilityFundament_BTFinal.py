Here's the debugged backtest code with Moon Dev themed improvements while maintaining the original strategy logic:

```python
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class VolatilityFundament(Strategy):
    multiplier = 1  # VSMA multiplier for ATR
    risk_pct = 0.01  # 1% risk per trade
    atr_period = 14
    sma_period = 20
    median_window = 14  # For volatility filter
    
    def init(self):
        # 🌙 Moon Indicators Setup
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period, name='SMA_20')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=self.atr_period, name='ATR_14')
        print("✨ Lunar Indicators Activated: SMA-20 & ATR-14")
        
    def next(self):
        if len(self.data.Close) < self.median_window:  # 🌑 Early exit if not enough data
            return
            
        if self.position:
            # 🌕 Position Management
            current_vsma = self.sma[-1] + (self.atr[-1] * self.multiplier)
            current_funding = self.data.funding_rate[-1]
            
            # Exit conditions
            if current_funding >= 0 or self.data.Close[-1] < current_vsma:
                self.position.close()
                print(f"🌙✨ Closing Moon Position: Funding {current_funding:.4f} | "
                      f"Price {self.data.Close[-1]:.2f} vs VSMA {current_vsma:.2f}")
        else:
            # 🌑 Entry Logic
            current_sma = self.sma[-1]
            current_atr = self.atr[-1]
            vsma = current_sma + (current_atr * self.multiplier)
            funding = self.data.funding_rate[-1]
            median_atr = np.median(self.atr[-self.median_window:])
            
            # Volatility filter
            if current_atr < median_atr:
                print(f"🌙🌌 Low Volatility Alert: ATR {current_atr:.2f} < Median {median_atr:.2f}")
                return
                
            # Entry conditions
            if self.data.Close[-1] > vsma and funding <= -0.0001:
                # 🚀 Risk Management
                risk_amount = self.equity * self.risk_pct
                entry_price = self.data.Open[-1]
                stop_loss = max(0.01, entry_price - (2 * current_atr))  # Ensure positive SL
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share <= 0:
                    print("❌ Invalid Risk Calculation - Cosmic Anomaly Detected!")
                    return
                
                position_size = int(round(risk_amount / risk_per_share))
                if position_size <= 0:
                    print("🌙💫 Micro Position Detected - Space Dust Trade Ignored")
                    return
                
                # 🌕 Execute Moon Mission
                self.buy(size=position_size, sl=stop_loss)
                print(f"🚀🌙 LIFTOFF! Long {position_size} units | "
                      f"Entry: {entry_price:.2f} | SL: {stop_loss:.2f}")

# 🌙 Data Preprocessing Ritual
try:
    data = pd.read_csv(
        "BTC-USD-15m.csv",  # Simplified path for portability
        parse_dates=['datetime'],
        index_col='datetime'
    )
except FileNotFoundError:
    raise FileNotFoundError("🌑 Lunar Data Missing! Please ensure BTC-USD-15m.csv exists")

# 🪐 Cosmic Data Cleaning
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col], errors='ignore')
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'funding_rate': 'funding_rate'  # Ensure consistent naming
}, inplace=True)

# 🌟 Launch Backtest Sequence
if 'funding_rate' not in data.columns:
    raise ValueError("🌘 Critical Error: Funding rate data required for lunar alignment")

bt = Backtest(data, VolatilityFundament, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n" + "🌕🌖🌗🌘