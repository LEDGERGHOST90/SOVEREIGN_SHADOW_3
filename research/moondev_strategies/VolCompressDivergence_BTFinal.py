Here's the fully debugged and Moon Dev optimized backtest code with all technical issues fixed while preserving the original strategy logic:

```python
# 🌙 Moon Dev Backtest AI Implementation 🌙
import pandas as pd
from backtesting import Backtest, Strategy
import talib
import numpy as np

# ---------------------------
# DATA PREPARATION
# ---------------------------
def load_data(path):
    # Load and clean data
    data = pd.read_csv(
        path,
        parse_dates=['datetime'],
        index_col='datetime'
    )
    
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Ensure proper column mapping
    column_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    data = data.rename(columns=column_map)
    
    return data

# ---------------------------
# STRATEGY IMPLEMENTATION
# ---------------------------
class VolCompressDivergence(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    stop_loss_pct = 0.02   # 2% fixed stop loss
    
    def init(self):
        # 🌙 Calculate indicators using TA-Lib
        self.vix = self.data['vix']
        self.vvix = self.data['vvix']
        
        # Volatility indicators
        self.vix_sma20 = self.I(talib.SMA, self.vix, timeperiod=20, name='VIX 20SMA')
        self.vvix_sma5 = self.I(talib.SMA, self.vvix, timeperiod=5, name='VVIX 5SMA')
        
        # Volatility-based stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14, name='ATR14')
        
        print("🌙✨ Strategy Initialized with Moon Dev Volatility Framework!")
    
    def next(self):
        # Wait for sufficient data
        if len(self.data) < 20:
            return
        
        # 🌙 Current indicator values
        current_vix = self.vix[-1]
        current_vvix = self.vvix[-1]
        vix_above_sma = current_vix > self.vix_sma20[-1]
        vvix_below_sma = current_vvix < self.vvix_sma5[-1]
        
        # Entry Logic
        if not self.position:
            if vix_above_sma and vvix_below_sma:
                # 🌙✨ Risk management calculations
                entry_price = self.data.Close[-1]
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                risk_amount = self.equity * self.risk_per_trade
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = risk_amount / risk_per_share
                    position_size = int(round(position_size))  # 🌙 Fixed: Round to whole units
                    
                    if position_size > 0:
                        self.buy(
                            size=position_size,
                            sl=stop_loss,
                            tag='MoonDev_Long'
                        )
                        print(f"🌙✨🚀 LONG ENTRY | Price: {entry_price:.2f} | Size: {position_size} | SL: {stop_loss:.2f}")
        
        # Exit Logic
        else:
            # VIX crosses below its SMA20 - proper crossover implementation
            if (self.vix[-2] > self.vix_sma20[-2]) and (self.vix[-1] < self.vix_sma20[-1]):
                self.position.close()
                print(f"🌙✨🌑 EXIT SIGNAL | VIX Cross Under | Price: {self.data.Close[-1]:.2f}")

# ---------------------------
# BACKTEST EXECUTION
# ---------------------------
if __name__ == '__main__':
    # Load and prepare data
    data = load_data('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    
    # Initialize backtest
    bt = Backtest(
        data,
        VolCompressDivergence,
        cash=1_000_000,
        exclusive_orders=True,
        trade_on_close=True
    )
    
    # Run backtest and print results
    stats = bt.run()
    print("\n🌕🌖🌗🌘🌑