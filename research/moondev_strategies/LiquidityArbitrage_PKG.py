# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# 🌙 MOON DEV DATA PREPARATION
def load_data(path):
    data = pd.read_csv(path)
    
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
    })
    
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    return data

class LiquidityArbitrage(Strategy):
    risk_pct = 0.01  # 1% risk per trade 🌙
    stop_loss_pct = 0.005  # 0.5% stop loss 🛑
    max_hold_bars = 5  # 5*15m = 75min ⏳
    spread_multiplier = 2  # Entry when spread > 2x avg ✨
    
    def init(self):
        # 🌙 MOON DEV INDICATORS
        self.spread = self.I(lambda: self.data.High - self.data.Low, name='Spread')
        self.avg_spread = self.I(talib.SMA, self.spread, timeperiod=20, name='Avg Spread')
        self.avg_volume = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='Avg Volume')
        self.price_sma = self.I(talib.SMA, self.data.Close, timeperiod=20, name='Price SMA')
        
    def next(self):
        if len(self.data) < 20:
            return  # Skip warmup period
        
        current_close = self.data.Close[-1]
        current_spread = self.spread[-1]
        avg_spread = self.avg_spread[-1]
        current_vol = self.data.Volume[-1]
        avg_vol = self.avg_volume[-1]
        price_sma = self.price_sma[-1]

        # 🌙🚀 ENTRY LOGIC
        if not self.position:
            if (current_spread > self.spread_multiplier * avg_spread and
                current_vol > avg_vol and
                current_close < price_sma):
                
                # Risk management calculations 🌙
                risk_amount = self.equity * self.risk_pct
                stop_price = current_close * (1 - self.stop_loss_pct)
                risk_per_unit = current_close - stop_price
                
                if risk_per_unit > 0:
                    position_size = int(round(risk_amount / risk_per_unit))
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_price)
                        self.entry_bar = len(self.data)-1
                        print(f"🌙✨ MOON DEV LONG ENTRY: {position_size} units at {current_close:.2f} | SL: {stop_price:.2f} 🚀")

        # 🛑 EXIT LOGIC        
        else:
            # Spread narrowing exit
            if current_spread < avg_spread:
                self.position.close()
                print(f"🌙📉 SPREAD NARROWING EXIT at {current_close:.2f} ✨")
            
            # Time-based exit
            elif (len(self.data)-1 - self.entry_bar) >= self.max_hold_bars:
                self.position.close()
                print(f"🌙⏰ TIME EXIT at {current_close:.2f} | Held {self.max_hold_bars} bars ⏳")

# 🌙 LOAD AND RUN BACKTEST
data = load_data('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
bt = Backtest(data, LiquidityArbitrage, cash=1_000_000, commission=.002)

# 🚀 EXECUTE AND PRINT FULL STATS
stats = bt.run()
print("\n🌕🌖🌗🌘🌑🌒🌓🌔🌕")
print("MOON DEV BACKTEST RESULTS:")
print(stats)
print(stats._strategy)
print("🌙 ARBITRAGE MISSION COMPLETE! 🚀")