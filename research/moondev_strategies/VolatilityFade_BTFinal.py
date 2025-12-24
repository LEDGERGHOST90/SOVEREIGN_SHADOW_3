import pandas as pd
from backtesting import Backtest, Strategy
import talib
import pandas_ta as ta

# 🌙 Moon Dev Data Loader 🌙
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class VolatilityFade(Strategy):
    adx_period = 14
    chaikin_fast = 3
    chaikin_slow = 10
    atr_period = 14
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # 🌙 Moon Dev Indicators 🌙
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.chaikin = self.I(talib.ADOSC, self.data.High, self.data.Low, self.data.Close,
                            self.data.Volume, self.chaikin_fast, self.chaikin_slow)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.vwap_4h = self.I(ta.vwap, high=self.data.High, low=self.data.Low, close=self.data.Close,
                            volume=self.data.Volume, anchor='4H', name='VWAP_4H')

    def next(self):
        price = self.data.Close[-1]
        high = self.data.High[-1]
        
        # 🌙 Moon Dev Debug Console 🌙
        print(f"🌙 Price: {price:.2f} | ADX: {self.adx[-1]:.2f} | Chaikin: {self.chaikin[-1]:.2f} | ATR: {self.atr[-1]:.2f}")

        if not self.position:
            # 🚀 Entry Conditions 🚀
            if (self.adx[-1] < 20) and (self.chaikin[-2] > 0 and self.chaikin[-1] < 0):
                atr_value = self.atr[-1]
                stop_distance = 1.5 * atr_value
                equity = self._broker.getvalue()
                risk_amount = equity * self.risk_pct
                
                # 🌙 Moon Dev Position Sizing 🌙
                size = int(round(risk_amount / stop_distance))
                if size > 0:
                    self.highest_high = high
                    self.sell(size=size, sl=price + stop_distance,
                            tp=price - (2 * stop_distance),
                            tag="🌙 Moon Dev Short Entry")
                    print(f"🚀🚀 MOON DEV SHORT! {size} units @ {price:.2f}")
                    print(f"🔒 SL: {price + stop_distance:.2f} | Risk: {self.risk_pct*100}%")

        elif self.position.is_short:
            # ✨ Exit Management ✨
            if high > self.highest_high:
                self.highest_high = high
                print(f"🌕 New High! Updating SL...")

            new_sl = self.highest_high + 1.5 * self.atr[-1]
            self.position.sl = new_sl

            # Volume profile exit
            if price <= self.vwap_4h[-1]:
                self.position.close()
                print(f"✨✨ PROFIT TAKEN @ {price:.2f} - VWAP Zone! ✨✨")

            print(f"🌙 Current SL: {new_sl:.2f} | ATR: {self.atr[-1]:.2f}")

# 🌙 Launch Moon Dev Backtest 🌙
bt = Backtest(data, VolatilityFade, cash=1_000_000, exclusive_orders=True)
stats = bt.run()
print(stats)
print(stats._strategy)