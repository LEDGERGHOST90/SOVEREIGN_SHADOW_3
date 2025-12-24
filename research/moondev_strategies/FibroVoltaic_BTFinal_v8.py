from backtesting import Backtest, Strategy
import talib
import pandas as pd
import numpy as np

class FibroVoltaic(Strategy):
    ema_period = 50
    atr_period = 14
    atr_sma_period = 20
    risk_per_trade = 0.02  # 2% risk per trade
    
    def init(self):
        # Calculate indicators
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.atr_sma = self.I(talib.SMA, self.atr, timeperiod=self.atr_sma_period)
        
        # Track swing highs/lows
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=5)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=5)
        
        # Track volatility contraction
        self.vol_contraction = self.I(lambda x: x < self.atr_sma, self.atr)
        
        # Initialize variables for trade tracking
        self.entry_price = None
        self.entry_atr = None
        self.stop_loss = None
        self.take_profit = None
        
    def next(self):
        # Moon Dev debug prints 🌙
        if len(self.data.Close) < 100:  # Skip early bars
            return
            
        current_close = self.data.Close[-1]
        current_low = self.data.Low[-1]
        current_high = self.data.High[-1]
        
        # Calculate Fibonacci levels from last swing low to high
        last_swing_low = min(self.swing_low[-5:])
        last_swing_high = max(self.swing_high[-5:])
        fib_range = last_swing_high - last_swing_low
        
        fib_382 = last_swing_high - fib_range * 0.382
        fib_50 = last_swing_high - fib_range * 0.5
        fib_618 = last_swing_high - fib_range * 0.618
        fib_1618 = last_swing_low + fib_range * 1.618
        
        # Check uptrend conditions
        uptrend = (current_close > self.ema[-1] and 
                  self.swing_high[-1] > self.swing_high[-2] and 
                  self.swing_low[-1] > self.swing_low[-2])
        
        # Check if we're in golden zone (50-61.8%)
        in_golden_zone = fib_50 >= current_close >= fib_618
        
        # Check volatility contraction
        volatility_ok = self.vol_contraction[-1] and (self.atr[-1] < self.atr[-2])
        
        # Entry conditions
        if not self.position and uptrend and in_golden_zone and volatility_ok and current_close > self.data.Open[-1]:
            
            # Calculate risk management
            risk_amount = self.equity * self.risk_per_trade
            self.stop_loss = last_swing_low
            risk_per_share = current_close - self.stop_loss
            position_size = int(round(risk_amount / risk_per_share))
            
            if position_size > 0:
                self.entry_price = current_close
                self.entry_atr = self.atr[-1]
                self.take_profit = fib_1618
                self.buy(size=position_size, sl=self.stop_loss)
                print(f"🌙 MOON DEV ENTRY SIGNAL 🌙")
                print(f"✨ Price: {current_close:.2f} | Fib Zone: {fib_50:.2f}-{fib_618:.2f}")
                print(f"🚀 ATR: {self.atr[-1]:.2f} (contracting) | Stop: {self.stop_loss:.2f}")
                
        # Exit conditions
        elif self.position:
            # Check for take profit
            if current_high >= self.take_profit:
                self.position.close()
                print(f"🌙 MOON DEV PROFIT TAKEN 🌙")
                print(f"🎯 Target hit at {self.take_profit:.2f} | ATR: {self.atr[-1]:.2f}")
            
            # Check for stop loss
            elif current_low <= self.stop_loss:
                self.position.close()
                print(f"🌙 MOON DEV STOP OUT 🌙")
                print(f"🛑 Stop hit at {self.stop_loss:.2f} | ATR: {self.atr[-1]:.2f}")
            
            # Emergency volatility exit
            elif self.atr[-1] > self.entry_atr * 1.2:
                self.position.close()
                print(f"🌙 MOON DEV VOLATILITY EXIT 🌙")
                print(f"⚡ ATR expanded >20% | Current: {self.atr[-1]:.2f} vs Entry: {self.entry_atr:.2f}")
            
            # Trail stop with 3x ATR
            else:
                new_stop = current_close - (3 * self.atr[-1])
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
                    print(f"🌙 MOON DEV TRAILING STOP 🌙")
                    print(f"📈 New stop: {self.stop_loss:.2f} | ATR: {self.atr[-1]:.2f}")

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

# Run backtest with increased initial cash
bt = Backtest(data, FibroVoltaic, commission=.002, exclusive_orders=True, cash=100000)
stats = bt.run()
print(stats)
print(stats._strategy)