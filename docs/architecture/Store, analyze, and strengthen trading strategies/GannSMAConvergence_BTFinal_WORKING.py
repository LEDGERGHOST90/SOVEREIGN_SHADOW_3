import pandas as pd
import numpy as np
from backtesting import Strategy, Backtest
import talib

class GannSMAConvergence(Strategy):
    def init(self):
        # Calculate indicators directly from self.data
        self.sma5 = self.I(talib.SMA, self.data.Close, timeperiod=5)
        self.atr14 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # Gann angle calculations (simplified)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        print("🌙 Moon Dev Strategy Initialized: GannSMAConvergence Ready for Launch! 🚀")

    def next(self):
        price = self.data.Close[-1]
        sma = self.sma5[-1]
        atr = self.atr14[-1]
        
        # Simplified Gann angle interaction logic
        gann_up_angle = price > self.swing_low[-1] * 1.01  # 1x1 angle approximation
        gann_down_angle = price < self.swing_high[-1] * 0.99  # 1x1 angle approximation
        
        # Risk management
        risk_per_trade = 0.01 * self.equity  # 1% risk per trade
        stop_distance = 1.5 * atr
        position_size = int(round(risk_per_trade / stop_distance))
        
        # Long entry conditions
        if (price > sma and 
            gann_up_angle and 
            not self.position.is_long):
            
            stop_price = self.data.Low[-1] - stop_distance
            target_price = price + (2 * stop_distance)
            
            print(f"🌙 Moon Dev Long Signal! 🚀 Price: {price:.2f}, SMA5: {sma:.2f}")
            print(f"✨ Entry: {price:.2f}, Stop: {stop_price:.2f}, Target: {target_price:.2f}")
            
            self.buy(size=position_size, sl=stop_price, tp=target_price)
        
        # Short entry conditions
        elif (price < sma and 
              gann_down_angle and 
              not self.position.is_short):
            
            stop_price = self.data.High[-1] + stop_distance
            target_price = price - (2 * stop_distance)
            
            print(f"🌙 Moon Dev Short Signal! 🌑 Price: {price:.2f}, SMA5: {sma:.2f}")
            print(f"✨ Entry: {price:.2f}, Stop: {stop_price:.2f}, Target: {target_price:.2f}")
            
            self.sell(size=position_size, sl=stop_price, tp=target_price)
        
        # Trailing stop for open positions
        if self.position.is_long:
            if (self.data.Close[-2] < self.sma5[-2] and self.data.Close[-1] > self.sma5[-1]):
                print("🌙 Moon Dev Trailing Stop Hit! ✨ Closing Long Position")
                self.position.close()
        
        if self.position.is_short:
            if (self.sma5[-2] < self.data.Close[-2] and self.sma5[-1] > self.data.Close[-1]):
                print("🌙 Moon Dev Trailing Stop Hit! ✨ Closing Short Position")
                self.position.close()

# Load and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['Datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('Datetime')

print("🌙 Moon Dev Data Preparation Complete! ✨ Cleaned and formatted data ready for backtesting")

# Run backtest with increased initial cash
bt = Backtest(data, GannSMAConvergence, commission=.002, margin=1.0, trade_on_close=True, cash=100000)
stats = bt.run()
print(stats)
print(stats._strategy)