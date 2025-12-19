I'll fix the incomplete code while maintaining the original strategy logic. Here's the complete debugged version with Moon Dev enhancements:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class VolSurgeReversion(Strategy):
    vix_threshold = 12
    risk_percent = 0.02
    atr_multiplier = 1.5
    
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        
        # Calculate indicators with TA-Lib
        self.log_returns = self.I(lambda close: np.log(close / close.shift(1)), 
                             self.data.Close, name='LogReturns')
        self.realized_vol = self.I(talib.STDDEV, self.log_returns, 
                                  timeperiod=20, name='RealizedVol20')
        self.volume_sma20 = self.I(talib.SMA, self.data.Volume, 
                                 timeperiod=20, name='VolumeSMA20')
        self.spread = self.I(lambda vix, rv: vix - rv, 
                           self.data.Vix, self.realized_vol, name='Spread')
        self.spread_mean = self.I(talib.SMA, self.spread, 
                                timeperiod=252, name='SpreadMean1yr')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                        self.data.Close, 14, name='ATR14')
        
        print("🌙 Lunar Indicators Activated: Volatility Matrix Online ✨")
        print("⚡ TA-Lib Powered Indicators Running at Light Speed ⚡")

    def next(self):
        price = self.data.Close[-1]
        vix = self.data.Vix[-1]
        
        # Volatility circuit breaker
        if vix < self.vix_threshold:
            print(f"🌑 VIX {vix:.1f} < {self.vix_threshold} - Cosmic Calm Detected")
            return
            
        if not self.position:
            # Entry conditions
            vol_spread = self.realized_vol[-1] < self.data.Vix[-1]
            volume_surge = self.data.Volume[-1] > 1.5 * self.volume_sma20[-1]
            
            if vol_spread and volume_surge:
                risk_amount = self.equity * self.risk_percent
                atr_value = self.atr[-1]
                stop_price = price + self.atr_multiplier * atr_value
                risk_per_share = stop_price - price
                
                position_size = int(round(risk_amount / risk_per_share))
                position_size = min(position_size, int(self.equity//price))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_price)
                    print(f"🚀 SHORT LAUNCH: {price:.2f} | Size: {position_size} ✨")
                    print(f"🛡️ Cosmic Shield Activated: Stop {stop_price:.2f} 🌌")
        else:
            # Trailing stop update
            current_trade = self.trades[-1]
            new_stop = self.data.Low[-1] + self.atr[-1] * self.atr_multiplier
            current_trade.sl = max(new_stop, current_trade.sl)
            
            # Spread reversion exit
            if self.spread[-1] <= self.spread_mean[-1]:
                self.position.close()
                print(f"🌕 SPREAD COLLAPSE: Profit {current_trade.pl:.2f} 🌠")
                print("🌊 Returning to Lunar Orbit for Next Opportunity...")

# Data preparation
data = pd.read_csv("BTC-USD-15m.csv",
                   parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data = data[['open', 'high', 'low', 'close', 'volume']].rename(columns={
    'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'
})

# Insert mock VIX data for demonstration (real implementation requires actual VIX data)
data['Vix'] = data['Close'].rolling(20).mean() + np.random.normal(0, 2, len(data))

# Execute lunar backtest 🌙
print("🌌 Initializing Moon Dev Backtest Sequence...")
bt = Backtest(data, VolSurgeReversion