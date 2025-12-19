import pandas as pd
from backtesting import Backtest, Strategy
import talib

# Load and preprocess data with lunar precision 🌕
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names with cosmic care 🌌
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

class MomentumCrossADX(Strategy):
    risk_percent = 0.01  # 1% risk per trade 🌙
    ema_short = 50
    ema_long = 200
    adx_period = 14
    rsi_period = 14
    swing_lookback = 20  # For swing low calculation
    
    def init(self):
        # Moon-powered indicators 🌕✨
        self.ema50 = self.I(talib.EMA, self.data.Close, self.ema_short)
        self.ema200 = self.I(talib.EMA, self.data.Close, self.ema_long)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, self.swing_lookback)
        
    def next(self):
        # Skip if not enough data (waiting for moon cycle completion) 🌑
        if len(self.ema50) < 2 or len(self.ema200) < 2 or len(self.adx) < 2:
            return
            
        # Entry constellation alignment 🌌
        if not self.position:
            # Moon-powered crossover detection 🌙✨
            if self.ema50[-2] < self.ema200[-2] and self.ema50[-1] > self.ema200[-1]:
                adx_current = self.adx[-1]
                adx_prev = self.adx[-2]
                
                if adx_current > 25 and adx_current > adx_prev:
                    entry_price = self.data.Close[-1]
                    sl_price = self.swing_low[-1]
                    
                    # Calculate lunar position size 🌘
                    risk_amount = self.equity * self.risk_percent
                    risk_per_share = entry_price - sl_price
                    
                    if risk_per_share > 0:
                        position_size = int(round(risk_amount / risk_per_share))
                        if position_size > 0:
                            self.buy(size=position_size, sl=sl_price)
                            print(f"🌙✨ EMA Crossover CONFIRMED! 🚀 Long entry at {entry_price:.2f} (Size: {position_size})")
        
        # Exit supernova conditions 💫
        else:
            if self.rsi[-1] > 70:
                self.position.close()
                print(f"🚨 RSI OVERHEATING! {self.rsi[-1]:.1f} - Exiting at {self.data.Close[-1]:.2f} 🌡️")
            elif self.adx[-1] < 20:
                self.position.close()
                print(f"🌑 ADX COLLAPSE! {self.adx[-1]:.1f} - Closing at {self.data.Close[-1]:.2f} ⚠️")

    def notify_trade(self, trade):
        if trade.is_closed:
            profit_emoji = "🚀🌕" if trade.pnl > 0 else "💸🌧️"
            print(f"{profit_emoji} Trade closed: {trade.entry_price:.2f} → {trade.exit_price:.2f} | PNL: {trade.pnl:.2f}")

# Launch moon mission 🚀🌙
bt = Backtest(data, MomentumCrossADX, cash=1_000_000, commission=.002)
stats = bt.run()
print("\n🌕✨ Lunar Backtest Results 🌙✨")
print(stats)
print("\n🌌 Final Strategy State:")
print(stats._strategy)