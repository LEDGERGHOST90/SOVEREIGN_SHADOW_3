# 🌙 Moon Dev's VoltaicContraction Backtest 🌙
from backtesting import Backtest, Strategy
from talib import ATR, SMA, MAX, MIN
import pandas as pd
import numpy as np

class VoltaicContraction(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade
    time_exit_bars = 40  # 15m * 40 = 10 hours (adjust based on 15m timeframe)
    
    def init(self):
        # 🌌 Moon Dev Indicator Calculation 🌌
        self.atr14 = self.I(ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.atr20_ma = self.I(SMA, self.atr14, timeperiod=20)
        self.atr10_ma = self.I(SMA, self.atr14, timeperiod=10)
        self.volume_ma = self.I(SMA, self.data.Volume, timeperiod=20)
        
        # Track entry ATR for stop loss calculation
        self.entry_atr = None
        self.entry_bar = None

    def next(self):
        current_price = self.data.Close[-1]
        
        # 🚀 Moon Dev Entry Logic 🚀
        if not self.position and len(self.atr14) > 20:
            atr_expanding = self.atr14[-1] > self.atr20_ma[-1]
            volume_declining = self.data.Volume[-1] < self.volume_ma[-1]
            
            if atr_expanding and volume_declining:
                # 🌑 SHORT THE VOLCANO! 🌑
                self.entry_atr = self.atr14[-1]
                self.entry_bar = len(self.data)
                
                # Risk management calculations
                stop_price = current_price + 1.5 * self.entry_atr
                risk_amount = self.equity * self.risk_per_trade
                risk_per_share = stop_price - current_price
                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    print(f"🌋 ENTRY: Short at {current_price:.2f} | Size: {position_size} | Moon Dev Risk Active! 🌋")
                    self.sell(size=position_size, sl=stop_price)

        # ✨ Moon Dev Exit Logic ✨
        elif self.position:
            exit_condition1 = self.atr14[-1] < self.atr10_ma[-1]
            exit_condition2 = self.data.Volume[-1] > self.volume_ma[-1]
            time_exit = (len(self.data) - self.entry_bar) >= self.time_exit_bars
            
            if (exit_condition1 and exit_condition2) or time_exit:
                print(f"🌕 EXIT: Closing at {current_price:.2f} | Moon Dev Profit: {self.position.pl:.2f} 🌕")
                self.position.close()

if __name__ == "__main__":
    # 🌙 Moon Dev Data Preparation 🌙
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    data['Open'] = pd.to_numeric(data['Open'], errors='coerce')
    data['High'] = pd.to_numeric(data['High'], errors='coerce')
    data['Low'] = pd.to_numeric(data['Low'], errors='coerce')
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
    data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
    data = data.dropna()
    
    # 🚀 Launch Moon Dev Backtest 🚀
    bt = Backtest(data, VoltaicContraction, cash=1_000_000, commission=.002)
    stats = bt.run()
    print("\n🌌🌙 MOON DEV FINAL STATS 🌙🌌")
    print(stats)
    print(stats._strategy)