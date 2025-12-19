# 🌙 Moon Dev's VolSyncBreakout Backtest 🌙
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

class VolSyncBreakout(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌌 Cosmic Indicator Calculation 🌌
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume.values
        
        # Bollinger Bands & BBW
        upper, middle, lower = talib.BBANDS(close, 20, 2, 2)
        self.upper_band = self.I(lambda: upper, name='UPPER_BB')
        self.lower_band = self.I(lambda: lower, name='LOWER_BB')
        bbw = (upper - lower)/middle
        self.bbw = self.I(lambda: bbw, name='BBW')
        self.bbw_ma50 = self.I(lambda: talib.SMA(bbw, 50), name='BBW_MA50')
        
        # OBV System
        obv = talib.OBV(close, volume)
        self.obv = self.I(lambda: obv, name='OBV')
        self.obv_ma20 = self.I(lambda: talib.SMA(obv, 20), name='OBV_MA20')
        
        # ATR for Stops
        self.atr = self.I(lambda: talib.ATR(high, low, close, 14), name='ATR')
        
        self.entry_bbw = None  # Will store BBW at entry

    def next(self):
        # 🌠 Skip first 70 periods for indicator warmup 🌠
        if len(self.data) < 70:
            return
            
        # 🚀 Entry Conditions 🚀
        if not self.position:
            bbw_contraction = (self.bbw[-1] < 0.5*self.bbw_ma50[-1])
            obv_bullish = self.obv[-1] > self.obv_ma20[-1]
            price_breakout = self.data.Close[-1] > self.upper_band[-1]
            
            if bbw_contraction and obv_bullish and price_breakout:
                # 💰 Risk Management Calculations 💰
                equity = self.equity
                risk_amount = equity * self.risk_percent
                atr_value = self.atr[-1]
                stop_loss = self.data.Close[-1] - 2*atr_value
                risk_per_share = self.data.Close[-1] - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.entry_bbw = self.bbw[-1]
                        self.buy(size=position_size, sl=stop_loss)
                        print(f"🌙 MOON DEV ENTRY 🌙 | Price: {self.data.Close[-1]:.2f} | Size: {position_size} | SL: {stop_loss:.2f} | BBW: {self.entry_bbw:.4f}")
        
        # ✨ Exit Conditions ✨
        else:
            if self.bbw[-1] >= 2*self.entry_bbw:
                self.position.close()
                print(f"✨ MOON DEV VOL EXPANSION EXIT ✨ | Price: {self.data.Close[-1]:.2f} | BBW: {self.bbw[-1]:.4f}")

# 🛰️ Data Preprocessing 🛰️
data = pd.read_csv("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open':'Open', 'high':'High',
    'low':'Low', 'close':'Close',
    'volume':'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# 🌖 Launch Backtest 🌖
bt = Backtest(data, VolSyncBreakout, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)
print(stats._strategy)