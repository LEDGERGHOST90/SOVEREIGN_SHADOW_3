import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Clean and prepare data with Moon Dev precision 🌙
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolatilityInversion(Strategy):
    risk_percent = 0.01  # 1% risk per trade (fixed as fraction)
    
    def init(self):
        # Calculate logarithmic returns with lunar precision 🌕
        close = self.data.Close
        self.log_ret = np.log(close / close.shift(1))
        
        # Calculate volatility indicators using TA-Lib
        self.realized_vol_10 = self.I(talib.STDDEV, self.log_ret, 960, name='RV_10D')
        self.realized_vol_20 = self.I(talib.STDDEV, self.log_ret, 1920, name='RV_20D')
        self.implied_vol = self.I(talib.SMA, self.realized_vol_10, 10, name='Implied_Vol')
        
        self.entry_vol = None  # Track volatility at entry

    def next(self):
        current_price = self.data.Close[-1]
        
        if not self.position:
            # Entry conditions 🌙
            if (self.realized_vol_10[-1] > self.realized_vol_20[-1] and   # Term structure inversion
                self.realized_vol_10[-1] < self.implied_vol[-1]):         # RV < IV
                
                # Moon Dev position sizing rules 🚀
                risk_amount = self.equity * self.risk_percent
                position_size = int(round(risk_amount / current_price))  # Fixed rounding to whole units
                
                if position_size > 0:
                    self.sell(size=position_size)  # Short volatility position
                    self.entry_vol = self.realized_vol_10[-1]
                    print(f"🌙✨ MOON DEV ENTRY: Short Vol at ${current_price:.2f} | Size: {position_size:,} | RV10: {self.realized_vol_10[-1]:.4f} ✨")
        else:
            # Exit conditions 🌙
            current_rv10 = self.realized_vol_10[-1]
            current_rv20 = self.realized_vol_20[-1]
            contango = ((current_rv20 - current_rv10)/current_rv10)*100 if current_rv10 != 0 else 0
            
            # Contango threshold exit 🚀
            if contango >= 5:
                self.position.close()
                print(f"🌙🚀 MOON DEV EXIT: Contango {contango:.1f}% | Price: ${current_price:.2f} ✨")
            
            # Volatility spike exit 🚨
            elif current_rv10 >= 1.2 * self.entry_vol:
                self.position.close()
                print(f"🌙⚠️ STOP LOSS: RV10 +20% ({current_rv10:.4f} vs {self.entry_vol:.4f}) | Price: ${current_price:.2f} 🚨")
            
            # IV crossover exit 📉
            elif current_rv10 > self.implied_vol[-1]:
                self.position.close()
                print(f"🌙📉 EXIT: RV10 > IV ({current_rv10:.4f} vs {self.implied_vol[-1]:.4f}) | Price: ${current_price:.2f}")

# Run backtest with Moon Dev settings 🌕
bt = Backtest(data, VolatilityInversion, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n🌙✨ MOON DEV BACKTEST RESULTS ✨🌙")
print("="*40)
print(stats)
print("\n🌙🚀 STRATEGY DETAILS 🚀🌙")
print("="*40)
print(stats._strategy)