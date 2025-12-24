Here's the fully debugged and Moon Dev themed version of your backtest code with all technical issues fixed:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np

# Load and preprocess data with Moon Dev magic ✨
print("🌙 MOON DEV DATA LOADER ACTIVATED...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data columns with cosmic precision 🌌
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)
print("🌕 DATA CLEANSING COMPLETE! READY FOR LIFTOFF 🚀")

class ForceSqueeze(Strategy):
    risk_percent = 0.01  # 1% risk per trade - Moon Dev approved risk level 🌙
    
    def init(self):
        # Calculate indicators with TA-Lib cosmic energy
        print("🌌 INITIALIZING COSMIC INDICATORS...")
        self.efi = self.I(talib.FORCEINDEX, self.data.Close, self.data.Volume, 13, name='EFI 🌊')
        
        # Bollinger Bands components - Moon's gravitational pull indicators
        self.bb_upper, self.bb_mid, self.bb_lower = self.I(
            lambda close: talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0),
            self.data.Close,
            name=['BB_UP 🌕', 'BB_MID 🌓', 'BB_LO 🌑']
        )
        
        # Calculate BB width and SMA - Moon phase measurements
        self.bb_width = self.I(lambda u, l, m: (u-l)/m, 
                              self.bb_upper, self.bb_lower, self.bb_mid,
                              name='BB_WIDTH 📏')
        self.bb_width_sma10 = self.I(talib.SMA, self.bb_width, 10,
                                    name='BB_WIDTH_SMA10 📈')
        
        self.stop_loss_level = None  # Trailing stop tracker
        print("🌠 INDICATOR INITIALIZATION COMPLETE! READY FOR TRADING")

    def next(self):
        # Skip early bars without indicator values - Moon's dark phase
        if len(self.efi) < 2 or len(self.bb_width) < 2:
            return

        current_efi = self.efi[-1]
        prev_efi = self.efi[-2]
        current_width = self.bb_width[-1]
        prev_width = self.bb_width[-2]
        width_sma = self.bb_width_sma10[-1]

        # Moon Dev Entry Logic 🚀
        if not self.position:
            # Manual crossover check with lunar precision
            if (prev_efi < 0 and current_efi > 0) and (current_width < prev_width):
                entry_price = self.data.Close[-1]
                sl_price = self.bb_lower[-1]
                
                # Calculate position size with cosmic accuracy
                risk_amount = self.equity * self.risk_percent
                risk_per_share = entry_price - sl_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl_price)
                        self.stop_loss_level = sl_price
                        print(f"🌕 MOON DEV ALERT: LONG ENTRY SIGNAL ACTIVATED 🚀")
                        print(f"📊 Position Size: {position_size} units (rounded to nearest whole moon rock)")
                        print(f"💰 Entry Price: {entry_price:.2f}")
                        print(f"🛡️ Stop Loss: {sl_price:.2f} (lower bollinger band)")
                        print("="*40)

        # Moon Dev Exit Logic 🌙
        else:
            # Update trailing stop with lunar gravity
            current_lower_bb = self.bb_lower[-1]
            self.stop_loss_level = max(self.stop_loss_level, current_lower_bb)
            
            # Check volatility expansion exit - cosmic expansion detected!
            if