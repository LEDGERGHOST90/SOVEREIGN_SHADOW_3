import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class BandSqueezeTrend(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # Calculate indicators using TA-Lib with self.I()
        self.upper_band, self.middle_band, _ = [
            self.I(lambda c: talib.BBANDS(c, 20, 2, 2, 0)[i], self.data.Close)
            for i in range(3)
        ]
        
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20)
        self.atr_ma = self.I(talib.SMA, self.atr, 20)
        
        print("🌙✨ Moon Dev Indicators Activated! BBANDS + ATR Systems Online 🚀")

    def next(self):
        current_close = self.data.Close[-1]
        current_atr = self.atr[-1]
        
        # Moon Dev progress tracker
        if len(self.data) % 500 == 0:
            print(f"🌙 Processing Bar {len(self.data)} | Price: {current_close:.2f}")

        if not self.position:
            # Entry conditions
            if (current_close > self.upper_band[-1] and
                current_close < self.atr_ma[-1]):
                
                # Calculate moon-powered position sizing 🌕
                stop_loss = current_close - 0.5 * current_atr
                risk_amount = self.equity * self.risk_percent
                risk_per_share = current_close - stop_loss
                
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    take_profit = current_close + 1.5 * current_atr
                    self.buy(size=position_size,
                            sl=stop_loss,
                            tp=take_profit,
                            tag="MoonRocketEntry🚀")
                    
                    print(f"\n🚀🌕 MOON LAUNCH DETECTED! 🌠"
                          f"\nEntry: {current_close:.2f}"
                          f"\nSize: {position_size} units"
                          f"\nStellar SL: {stop_loss:.2f}"
                          f"\nGalactic TP: {take_profit:.2f}\n")
        else:
            # Exit condition
            if current_close < self.middle_band[-1]:
                self.position.close()
                print(f"🌑🌪️ BLACK HOOMAN EXIT! Closing at {current_close:.2f}")

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['DateTime'] = pd.to_datetime(data['datetime'])
data.set_index('DateTime', inplace=True)

# Launch moon mission 🚀
bt = Backtest(data, BandSqueezeTrend, cash=1_000_000)
stats = bt.run()

print("\n🌕🌖🌗🌘🌑🌒🌓🌔 MOON DEV FINAL REPORT 🌔🌓🌒🌑🌘🌗🌖🌕")
print(stats)
print(stats._strategy)
print("\nMission Complete! Time for moon cheese rewards 🧀🌙")