Here's the debugged version of your ContangoDivergence backtest with proper Moon Dev theming and all technical fixes:

```python
# 🌙 Moon Dev's ContangoDivergence Backtest 🌙
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class ContangoDivergence(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    ma_period = 5     # Put/Call ratio MA period
    
    def init(self):
        # 🌗 Calculate required indicators using TA-Lib
        self.vix_contango = self.I(lambda: self.data.df['vix_back'] - self.data.df['vix_front'])
        self.putcall_ma = self.I(talib.SMA, self.data.df['put_call_ratio'], timeperiod=self.ma_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        print("✨ Indicators initialized with Moon Magic:")
        print(f"   - VIX Contango Spread 🌉")
        print(f"   - {self.ma_period}-period Put/Call MA 📉")
        print(f"   - 14-period ATR 🌊")

    def next(self):
        price = self.data.Close[-1]
        
        # 🌙 Moon-themed debug prints
        if len(self.data) % 100 == 0:
            print(f"\n🌕 Moon Phase Update [{self.data.index[-1].strftime('%Y-%m-%d %H:%M')}]")
            print(f"   Price: {price:.2f} | Equity: {self.equity:,.2f} 🌌")
            print(f"   Contango Spread: {self.vix_contango[-1]:.2f} 🌉")
            print(f"   Put/Call MA: {self.putcall_ma[-1]:.2f} 📊")

        # Entry Logic
        if not self.position:
            # Contango condition 🌉
            contango = self.data.df['vix_back'][-1] > self.data.df['vix_front'][-1]
            
            # Put/Call ratio declining 📉
            putcall_declining = (self.putcall_ma[-1] < self.putcall_ma[-2] if len(self.putcall_ma) > 2 else False)

            if contango and putcall_declining:
                # 🚀 Risk-managed position sizing
                risk_amount = self.equity * self.risk_pct
                atr_value = self.atr[-1] if len(self.atr) > 0 else 0
                
                if atr_value > 0:
                    position_size = risk_amount / (atr_value * 1.5)  # 1.5x ATR stop
                    position_size = int(round(position_size))  # 🌙 Ensure whole units
                    max_possible = int(self.equity // price)
                    position_size = min(position_size, max_possible)
                    
                    if position_size > 0:
                        print(f"\n🌑 MOONSHOT SHORT ENTRY 🌘")
                        print(f"  Price: {price:.2f} | Size: {position_size} 📉")
                        print(f"  Contango: {self.vix_contango[-1]:.2f} | Put/Call MA: {self.putcall_ma[-1]:.2f}")
                        self.sell(size=position_size, sl=price + atr_value*1.5, tag="Moon Entry")

        # Exit Logic
        else:
            # Backwardation condition 🌗
            backwardation = self.data.df['vix_front'][-1] > self.data.df['vix_back'][-1]
            
            # Put/Call ratio rising 📈
            putcall_rising = (self.putcall_ma[-1] > self.putcall_ma[-2] if len(self.putcall_ma) > 2 else False)

            if backwardation or putcall_rising:
                print(f"\n🌕 FULL MOON EXIT 🌕")
                print(f"  Price: {price:.2f} | P/L: {self.position.pl:.2f} 💰")
                print(f"  Backwardation: {backwardation} | Put/Call Rising: {putcall_rising}")
                self.position.close()

# 🚀 Data Preparation
print("\n🌙 Loading celestial market data...")
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read