# 🌙 Moon Dev's VolumeSurgeReversal Backtest Implementation
import pandas as pd
from backtesting import Backtest, Strategy
import talib

class VolumeSurgeReversal(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌕
    atr_multiplier = 1.5  # Trailing stop multiplier 🚀
    
    def init(self):
        # 🌗 Indicator Calculations using TA-Lib
        self.volume_avg = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.atr5 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=5)
        self.atr20_avg = self.I(talib.SMA, self.atr5, timeperiod=20)
        self.trailing_stop = None

    def next(self):
        # 🌑 Current market conditions
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        atr5 = self.atr5[-1]
        
        # 🌙 Debugging Information
        print(f"🌙 Moon Metrics | Close: {current_close:.2f} | Vol: {current_volume:.2f} vs {self.volume_avg[-1]:.2f} | ATR5: {atr5:.2f} vs {self.atr20_avg[-1]:.2f}")

        # 🚀 Entry Logic: Volume Surge + Volatility Contraction
        if not self.position:
            if (current_volume > self.volume_avg[-1]) and (atr5 < self.atr20_avg[-1]):
                # 🌕 Risk Management Calculation
                risk_amount = self.equity * self.risk_percent
                stop_loss_distance = atr5 * self.atr_multiplier
                position_size = int(round(risk_amount / stop_loss_distance))
                
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trailing_stop = current_close - stop_loss_distance
                    print(f"🚀🌕 LONG ENTRY | Size: {position_size} | Entry: {current_close:.2f} | Stop: {self.trailing_stop:.2f}")
        
        # 🔄 Trailing Stop Logic
        else:
            new_stop = current_close - (atr5 * self.atr_multiplier)
            if new_stop > self.trailing_stop:
                self.trailing_stop = new_stop
                
            if self.data.Close[-1] < self.trailing_stop:
                self.position.close()
                print(f"🌑💫 EXIT | Price: {current_close:.2f} | Stop: {self.trailing_stop:.2f}")

    def notify_trade(self, trade):
        if trade.is_closed:
            print(f"💰🌙 Trade Closed | Profit: {trade.pnl:.2f} | Return: {trade.return_pct:.2%}")

# 🌌 Data Preparation
data = pd.read_csv("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")

# 🧹 Data Cleaning
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data.index = pd.to_datetime(data['datetime'])
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# 🌟 Backtest Execution
bt = Backtest(data, VolumeSurgeReversal, cash=1_000_000)
stats = bt.run()

# 🌙✨ Results Analysis
print("\n" + "="*50)
print("🌕🌖🌗 MOON DEV FINAL STATS 🌘🌑🌒")
print("="*50)
print(stats)
print(stats._strategy)