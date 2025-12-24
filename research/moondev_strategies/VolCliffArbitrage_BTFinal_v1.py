import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import talib

data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path)
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={'datetime': 'Datetime', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
data = data.set_index(pd.to_datetime(data['Datetime']))

class VolCliffArbitrage(Strategy):
    adx_threshold = 25
    vol_multiplier = 1.5
    risk_percent = 0.02
    atr_multiplier_sl = 2
    vol_drop_threshold = 0.8

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        
        self.bb_width = self.I(lambda u, l: u - l, self.bb_upper, self.bb_lower)
        self.bb_width_sma = self.I(talib.SMA, self.bb_width, timeperiod=100)
        self.recent_vol_max = self.I(talib.MAX, self.bb_width, timeperiod=5)
        
        self.adx = self.I(talib.ADX, high, low, close, timeperiod=14)
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=14)
        self.sma20 = self.I(talib.SMA, close, timeperiod=20)
        
        print("🌙 Moon Dev: Initialized VolCliffArbitrage indicators 🚀")

    def next(self):
        if self.i < 100:
            return
        
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        
        high_vol = self.bb_width[-1] > self.vol_multiplier * self.bb_width_sma[-1]
        range_bound = self.adx[-1] < self.adx_threshold
        
        if high_vol and range_bound and not self.position:
            risk_per_unit = self.atr[-1] * self.atr_multiplier_sl
            risk_amount = self.equity * self.risk_percent
            position_size = int(round(risk_amount / risk_per_unit))
            
            if position_size > 0:
                if current_close > self.bb_upper[-1]:
                    self.sell(size=position_size)
                    print(f"🌙 Moon Dev: Short entry on high vol cliff setup at {current_close}, size {position_size}, risk per unit {risk_per_unit:.2f} 🚀")
                elif current_close < self.bb_lower[-1]:
                    self.buy(size=position_size)
                    print(f"🌙 Moon Dev: Long entry on high vol cliff setup at {current_close}, size {position_size}, risk per unit {risk_per_unit:.2f} 🚀")
        
        if self.position:
            vol_cliff_exit = self.bb_width[-1] < self.vol_drop_threshold * self.recent_vol_max[-1]
            if vol_cliff_exit:
                self.position.close()
                print(f"🌙 Moon Dev: Volatility cliff drop detected, neutral exit at {current_close} 🌙✨")
                return
            
            entry_price = self.position.avg_price
            if self.position.is_long:
                tp_level = self.sma20[-1]
                sl_level = entry_price - self.atr[-1] * self.atr_multiplier_sl
                if current_close >= tp_level:
                    self.position.close()
                    print(f"🌙 Moon Dev: Mean reversion take profit exit long at {current_close} ✨")
                elif current_low <= sl_level:
                    self.position.close()
                    print(f"🌙 Moon Dev: Stop loss hit on long at {current_low} 😞")
            else:  # short
                tp_level = self.sma20[-1]
                sl_level = entry_price + self.atr[-1] * self.atr_multiplier_sl
                if current_close <= tp_level:
                    self.position.close()
                    print(f"🌙 Moon Dev: Mean reversion take profit exit short at {current_close} ✨")
                elif current_high >= sl_level:
                    self.position.close()
                    print(f"🌙 Moon Dev: Stop loss hit on short at {current_high} 😞")
            
            # Additional vol normalization exit
            if self.bb_width[-1] < self.bb_width_sma[-1]:
                self.position.close()
                print(f"🌙 Moon Dev: Volatility normalization exit at {current_close} 🌙")

bt = Backtest(data, VolCliffArbitrage, cash=1000000, commission=0.002, exclusive_orders=True)
stats = bt.run()
print(stats)