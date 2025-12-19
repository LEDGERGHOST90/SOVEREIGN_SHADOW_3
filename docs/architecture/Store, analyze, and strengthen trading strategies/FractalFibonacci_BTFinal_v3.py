from backtesting import Backtest, Strategy
import talib
import pandas as pd
import numpy as np

class FractalFibonacci(Strategy):
    def init(self):
        # Calculate indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.macd, self.macdsignal, self.macdhist = self.I(talib.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)
        
        # Fractal detection (using swing highs/lows)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=5)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=5)
        
        # Track last fractal points for Fibonacci levels
        self.last_swing_high = None
        self.last_swing_low = None
        self.fib_levels = None
        
    def next(self):
        price = self.data.Close[-1]
        
        # Detect new swing highs/lows (fractals)
        if self.data.High[-1] == self.swing_high[-1]:
            self.last_swing_high = self.data.High[-1]
            print(f"🌙 New Swing High Detected at {self.last_swing_high}")
            
        if self.data.Low[-1] == self.swing_low[-1]:
            self.last_swing_low = self.data.Low[-1]
            print(f"🌙 New Swing Low Detected at {self.last_swing_low}")
        
        # Calculate Fibonacci levels when we have both swing points
        if self.last_swing_high is not None and self.last_swing_low is not None:
            swing_range = self.last_swing_high - self.last_swing_low
            self.fib_levels = {
                '0': self.last_swing_low,
                '23.6': self.last_swing_low + swing_range * 0.236,
                '38.2': self.last_swing_low + swing_range * 0.382,
                '50': self.last_swing_low + swing_range * 0.5,
                '61.8': self.last_swing_low + swing_range * 0.618,
                '100': self.last_swing_high,
                '127.2': self.last_swing_high + swing_range * 0.272,
                '161.8': self.last_swing_high + swing_range * 0.618
            }
        
        # Check for entries only if we have Fibonacci levels
        if self.fib_levels is not None and len(self.data.Close) > 2:
            # Check for bullish setup (price at support with bullish divergence)
            if (price <= self.fib_levels['38.2'] * 1.005 and 
                price >= self.fib_levels['38.2'] * 0.995 and
                self.rsi[-1] > 30 and 
                self.rsi[-1] > self.rsi[-2] and 
                self.data.Close[-1] > self.data.Open[-1]):
                
                # Calculate position size (1% risk)
                risk_amount = self.equity * 0.01
                stop_loss = self.fib_levels['23.6']
                risk_per_unit = abs(price - stop_loss)
                position_size = int(round(risk_amount / risk_per_unit))
                
                if position_size > 0 and price > stop_loss:
                    print(f"🚀 Moon Dev BUY Signal at {price} | TP: {self.fib_levels['61.8']} | SL: {stop_loss}")
                    self.buy(size=position_size, sl=stop_loss, tp=self.fib_levels['61.8'])
            
            # Check for bearish setup (price at resistance with bearish divergence)
            elif (price <= self.fib_levels['61.8'] * 1.005 and 
                  price >= self.fib_levels['61.8'] * 0.995 and
                  self.rsi[-1] < 70 and 
                  self.rsi[-1] < self.rsi[-2] and 
                  self.data.Close[-1] < self.data.Open[-1]):
                
                # Calculate position size (1% risk)
                risk_amount = self.equity * 0.01
                stop_loss = self.fib_levels['100']
                risk_per_unit = abs(stop_loss - price)
                position_size = int(round(risk_amount / risk_per_unit))
                
                if position_size > 0 and price < stop_loss:
                    print(f"🌑 Moon Dev SELL Signal at {price} | TP: {self.fib_levels['38.2']} | SL: {stop_loss}")
                    self.sell(size=position_size, sl=stop_loss, tp=self.fib_levels['38.2'])

# Load and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Datetime'
})
data = data.set_index(pd.to_datetime(data['Datetime']))

# Run backtest with increased initial cash
print("🌙 Moon Dev Backtest Initializing...")
print("✨ Preparing Fractal Fibonacci Strategy...")
print("🚀 Increasing initial cash to handle BTC prices...")
bt = Backtest(data, FractalFibonacci, commission=.002, exclusive_orders=True, cash=1000000)
stats = bt.run()
print("🌑 Backtest Complete! Moon Dev Results:")
print(stats)
print(stats._strategy)