```python
# 🌙 MOON DEV BACKTESTING AI - SQUEEZE MOMENTUM STRATEGY IMPLEMENTATION 🚀

from backtesting import Backtest, Strategy
import pandas as pd
import talib

class SqueezeMomentum(Strategy):
    risk_per_trade = 0.01  # 1% of equity per trade 🌕
    max_consecutive_losses = 3  # Max allowed consecutive losses 🌑
    
    def init(self):
        # 🌙 CALCULATE ALL INDICATORS USING TALIB THROUGH I() WRAPPER
        self.bb_upper = self.I(lambda c: talib.BBANDS(c, 20, 2, 2)[0], self.data.Close)
        self.bb_lower = self.I(lambda c: talib.BBANDS(c, 20, 2, 2)[2], self.data.Close)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, 14)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 30)
        self.macd = self.I(lambda c: talib.MACD(c, 12, 26, 9)[0], self.data.Close)
        self.signal = self.I(lambda c: talib.MACD(c, 12, 26, 9)[1], self.data.Close)
        
        self.consecutive_losses = 0  # 🌑 Track bad moon streaks
        print("🌙✨ MOON INDICATORS INITIALIZED! Ready for lunar launch! 🚀")

    def next(self):
        # 🌙 MOON TRADE LOGIC ORBITAL CHECK
        if self.position:
            return  # 🛑 Active position - no new entries
            
        if self.consecutive_losses >= self.max_consecutive_losses:
            print("🌑☄️ THREE LOSSES! Moon base shutdown - no new entries!")
            return

        # 🌙 INDICATOR CONDITION CHECKS
        squeeze = (self.bb_upper[-1] - self.bb_lower[-1])/self.bb_lower[-1] <= 0.05
        adx_weak = self.adx[-1] < 25 and self.adx[-1] < self.adx[-2]
        volume_low = self.data.Volume[-1] < self.volume_ma[-1]
        
        if not (squeeze and adx_weak and volume_low):
            return  # ❌ Conditions not met
            
        # 🌙 MACD CROSSOVER CHECK
        macd_bullish = self.macd[-1] > self.signal[-1] and self.macd[-2] <= self.signal[-2]
        macd_bearish = self.macd[-1] < self.signal[-1] and self.macd[-2] >= self.signal[-2]
        
        # 🚀 LONG ENTRY CONDITIONS
        if self.data.Close[-1] > self.bb_upper[-1] and macd_bullish:
            entry_price = self.data.Close[-1]
            sl_price = max(self.bb_lower[-1], entry_price*0.98)
            risk = entry_price - sl_price
            
            if risk <= 0: return  # 🛑 Invalid risk calculation
            
            position_size = int(round((self.equity * self.risk_per_trade) / risk))
            self.buy(size=position_size, sl=sl_price, tp=self.bb_upper[-1])
            print(f"🌕🚀 BLAST OFF! LONG {position_size} @ {entry_price:.2f} | SL: {sl_price:.2f} | TP: {self.bb_upper[-1]:.2f}")

        # 🌑 SHORT ENTRY CONDITIONS    
        elif self.data.Close[-1] < self.bb_lower[-1] and macd_bearish:
            entry_price = self.data.Close[-1]
            sl_price = min(self.bb_upper[-1], entry_price*1.02)
            risk = sl_price - entry_price
            
            if risk <= 0: return  # 🛑 Invalid risk calculation
            
            position_size = int(round((self.equity * self.risk_per_trade) / risk))
            self.sell(size=position_size, sl=sl_price, tp=self.bb_lower[-1])
            print(f"🌑☄️ DARK SIDE ENTRY! SHORT {position_size} @ {entry_price:.2f} | SL: {sl_price:.2f} | TP: {self