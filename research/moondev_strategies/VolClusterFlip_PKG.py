# 🌙 Moon Dev's VolClusterFlip Backtest Implementation 🚀
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Clean and prepare data 🌕
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

class VolClusterFlip(Strategy):
    risk_pct = 0.02  # 🌑 2% risk per trade
    atr_period = 14
    rsi_period = 14
    
    def init(self):
        # Core Indicators 🌙
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 30)
        
        # Liquidity Zones ✨
        self.swing_high = self.I(talib.MAX, self.data.High, 20)
        self.swing_low = self.I(talib.MIN, self.data.Low, 20)
        
        # Placeholder for VIX structure (requires external data)
        # self.vix_front = self.data['vix_front']  # Would need actual data columns
        # self.vix_second = self.data['vix_second']
        
    def next(self):
        price = self.data.Close[-1]
        
        # 🌕 Moon Dev Entry Logic Cluster
        if (not self.position and
            # Basic price/volume conditions
            price >= self.swing_high[-1] and
            self.data.Volume[-1] > self.volume_ma[-1] and
            self.rsi[-1] > 60):
            
            # Risk Management Calculations 🌑
            atr_value = self.atr[-1] or 1  # Prevent zero division
            risk_amount = self.equity * self.risk_pct
            position_size = int(round(risk_amount / atr_value))
            
            # ✨ Moon-sized Entry!
            self.buy(size=position_size)
            print(f"🚀 MOON DEV ENTRY: {position_size} units at {price:.2f}")
            print(f"   📈 RSI: {self.rsi[-1]:.2f} | 📊 Volume: {self.data.Volume[-1]:.2f}")
            
        # 🌑 Exit Logic Constellation
        if self.position:
            entry_price = self.position.entry_price
            if (price >= entry_price + 1.5 * self.atr[-1] or
                price <= entry_price - 1 * self.atr[-1]):
                
                self.position.close()
                print(f"🌕 MOON DEV EXIT: Closed at {price:.2f}")
                print(f"   🎯 Profit: {(price/entry_price-1)*100:.2f}%")

# Launch Backtest 🌙🚀
bt = Backtest(data, VolClusterFlip, cash=1_000_000, commission=.002)
stats = bt.run()

# Print Full Moon Stats 🌕✨
print("\n🌙🌙🌙 MOON DEV FINAL STATS 🌙🌙🌙")
print(stats)
print(stats._strategy)
print("🌑 Backtest Complete - To the Moon! 🚀")