# 🌙 Moon Dev's VolumeSurgeEMA Backtest Implementation
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class VolumeSurgeEMA(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    ema_period_short = 50
    ema_period_long = 200
    rsi_period = 14
    volume_ma_period = 20
    swing_period = 20

    def init(self):
        # 🌙 Moon Dev Indicators Setup
        self.ema50 = self.I(talib.EMA, self.data.Close, self.ema_period_short, name='EMA50')
        self.ema200 = self.I(talib.EMA, self.data.Close, self.ema_period_long, name='EMA200')
        self.volume_sma = self.I(talib.SMA, self.data.Volume, self.volume_ma_period, name='Volume SMA')
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period, name='RSI')
        self.swing_low = self.I(talib.MIN, self.data.Low, self.swing_period, name='Swing Low')

    def next(self):
        # 🌙 Moon Dev Core Strategy Logic
        if self.position:
            # RSI Exit Condition
            if len(self.rsi) >= 2 and self.rsi[-2] >= 70 and self.rsi[-1] < 70:
                self.position.close(tag="RSI Exit 🌙")
                print(f"🌙✨ Moon Dev Exit Signal! RSI {self.rsi[-1]:.1f} dropping below 70")

        else:
            # Entry Conditions
            if len(self.ema50) >= 2 and len(self.ema200) >= 2:
                ema_cross = (self.ema50[-2] < self.ema200[-2]) and (self.ema50[-1] > self.ema200[-1])
                volume_spike = self.data.Volume[-1] > 2 * self.volume_sma[-1]

                if ema_cross and volume_spike and len(self.swing_low) > 0:
                    stop_price = self.swing_low[-1]
                    entry_price = self.data.Open[-1]  # Next candle's open
                    
                    if entry_price > stop_price:
                        risk_per_share = entry_price - stop_price
                        position_size = int(round((self.equity * self.risk_pct) / risk_per_share))
                        
                        if position_size > 0:
                            tp_price = entry_price + 2 * risk_per_share
                            self.buy(
                                size=position_size,
                                sl=stop_price,
                                tp=tp_price,
                                tag=f"Moon Surge Entry 🚀"
                            )
                            print(f"🌙🚀 MOON DEV ALERT! Buying {position_size} shares")
                            print(f"   Entry: {entry_price:.2f}, SL: {stop_price:.2f}, TP: {tp_price:.2f}")

# 🌙 Data Preparation Ritual
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path)

# 🌌 Cosmic Data Cleansing
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# 🚀 Launching Moon Dev Backtest
bt = Backtest(data, VolumeSurgeEMA, cash=1_000_000, commission=.002)
stats = bt.run()

# 🌕 Displaying Cosmic Results
print("\n🌙✨ Moon Dev Final Report ✨🌙")
print(stats)
print(stats._strategy)