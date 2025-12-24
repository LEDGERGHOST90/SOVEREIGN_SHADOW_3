import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Moon Dev Data Preparation 🌙
def prepare_data(path):
    data = pd.read_csv(path, parse_dates=['datetime'])
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    # Drop unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Column mapping with case conversion
    column_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'liquiditydelta': 'LiquidityDelta'  # Critical orderbook metric 🌊
    }
    data = data.rename(columns=column_map)
    return data

class VelocityDivergence(Strategy):
    zscore_window = 2  # 30-min baseline (2*15m)
    atr_period = 14
    risk_pct = 0.01
    liquidity_threshold = 0.7
    
    def init(self):
        # Calculate velocity momentum ✨
        mom = self.I(talib.MOM, self.data.Close, 1)
        vol = self.data.Volume
        self.price_velocity = self.I(lambda m,v: m*v, mom, vol, name='Velocity')
        
        # Z-Score calculations 🧮
        mean = self.I(talib.SMA, self.price_velocity, self.zscore_window)
        std = self.I(talib.STDDEV, self.price_velocity, self.zscore_window)
        self.zscore = self.I(lambda pv,m,s: (pv-m)/s, 
                           self.price_velocity, mean, std, name='Z-Score')
        
        # Liquidity & Risk Indicators 🌊
        self.liquidity = self.data.LiquidityDelta
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                        self.data.Close, self.atr_period)
        
        print("🌙 Moon Dev Engine Initialized! Ready for cosmic analysis 🌌")

    def next(self):
        current_z = self.zscore[-1]
        liquidity = self.liquidity[-1]
        atr = self.atr[-1]
        close = self.data.Close[-1]
        
        # Risk Management Calculations 🛡️
        risk_amount = self.equity * self.risk_pct
        if atr > 0:
            position_size = int(round(risk_amount / (atr * close)))
            max_size = int(self.equity // close)
            position_size = min(position_size, max_size)
        else:
            return
        
        # Entry Logic 🚀
        if not self.position:
            if current_z > 2 and liquidity > self.liquidity_threshold:
                sl = close - atr * 1.5
                tp = close + atr * 3
                self.buy(size=position_size, sl=sl, tp=tp)
                print(f"🚀 LONG ACTIVATED! Size: {position_size} | Cosmic Momentum Detected 🌠")
                
            elif current_z < -2 and liquidity < -self.liquidity_threshold:
                sl = close + atr * 1.5
                tp = close - atr * 3
                self.sell(size=position_size, sl=sl, tp=tp)
                print(f"🌑 SHORT ENGAGED! Size: {position_size} | Black Hole Liquidation Detected 🕳️")

        # Exit Logic 💫
        else:
            if (self.position.is_long and current_z < 1) or \
               (self.position.is_short and current_z > -1):
                self.position.close()
                print(f"🌙 Position Closed | Z-Score Stabilized at {current_z:.1f} σ")
                
            if (self.position.is_long and current_z > 3) or \
               (self.position.is_short and current_z < -3):
                self.position.close()
                print(f"🌪️  Emergency Exit! Extreme Z-Score {current_z:.1f} σ")

# Cosmic Backtest Execution 🌌
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = prepare_data(data_path)

bt = Backtest(data, VelocityDivergence, cash=1_000_000, commission=.002)
stats = bt.run()
print(stats)
print(stats._strategy)