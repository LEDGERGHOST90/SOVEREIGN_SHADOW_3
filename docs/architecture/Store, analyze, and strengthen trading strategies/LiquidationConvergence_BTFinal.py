Here's the debugged code with all technical issues fixed while preserving the original strategy logic:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Clean and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names and drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Format columns to backtesting.py specifications
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Set datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

class LiquidationConvergence(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌙
    efi_period = 13
    sar_step = 0.02
    sar_max = 0.2
    swing_period = 20  # Liquidation zone lookback
    
    def init(self):
        # Liquidation Zones (Swing Highs/Lows) ✨
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.swing_period)
        
        # Elder Force Index Calculation 🚀
        close = self.data.Close
        volume = self.data.Volume
        force_index = (close - close.shift(1)) * volume
        self.efi = self.I(talib.EMA, force_index, timeperiod=self.efi_period)
        
        # Parabolic SAR for exits 🌙
        self.sar = self.I(talib.SAR, self.data.High, self.data.Low, 
                         acceleration=self.sar_step, maximum=self.sar_max)
        
    def next(self):
        current_price = self.data.Close[-1]
        equity = self.broker.equity
        
        # Entry Logic 🌙✨
        if not self.position:
            # Long Entry: Price breaks swing high + EFI bullish crossover
            if ((self.data.Close[-2] < self.swing_high[-2] and self.data.Close[-1] > self.swing_high[-1]) and 
                (self.efi[-2] < 0 and self.efi[-1] > 0)):
                
                sl = self.swing_low[-1]  # Opposite liquidity boundary
                risk_per_share = current_price - sl
                
                if risk_per_share > 0:
                    position_size = int(round((equity * self.risk_percent) / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl)
                        print(f"🌙 MOON ENTRY LONG ✨ | Price: {current_price:.2f} | Size: {position_size} | SL: {sl:.2f}")
            
            # Short Entry: Price breaks swing low + EFI bearish crossover
            elif ((self.data.Close[-2] > self.swing_low[-2] and self.data.Close[-1] < self.swing_low[-1]) and 
                  (self.efi[-2] > 0 and self.efi[-1] < 0)):
                
                sl = self.swing_high[-1]  # Opposite liquidity boundary
                risk_per_share = sl - current_price
                
                if risk_per_share > 0:
                    position_size = int(round((equity * self.risk_percent) / risk_per_share))
                    if position_size > 0:
                        self.sell(size=position_size, sl=sl)
                        print(f"🌙 MOON ENTRY SHORT ✨ | Price: {current_price:.2f} | Size: {position_size} | SL: {sl:.2f}")
        
        # Exit Logic with Parabolic SAR 🚀
        else:
            if self.position.is_long and current_price < self.sar[-1]:
                self.position.close()
                print(f"🌙 SAR MOON EXIT 🌝 | Closed LONG at {current_price:.2f}")
            elif self.position.is_short and current_price > self.sar[-1]:
                self.position.close()
                print(f"🌙 SAR MOON EXIT 🌚 | Closed SHORT at {current_price:.2f}")

# Run backtest
bt = Backtest