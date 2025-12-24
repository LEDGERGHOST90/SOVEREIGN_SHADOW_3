from backtesting import Backtest, Strategy
import talib
import pandas as pd

class VolatilityBreakout(Strategy):
    bb_period = 20
    bb_dev = 2
    rsi_period = 14
    risk_per_trade = 0.01  # 1% risk per trade

    def init(self):
        close = self.data.Close
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, close, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev, matype=0)
        self.bb_width = self.I(lambda: (self.upper - self.lower), name='BB Width')
        self.bb_width_ma = self.I(talib.SMA, self.bb_width, timeperiod=self.bb_period)
        self.rsi = self.I(talib.RSI, close, timeperiod=self.rsi_period)
        
    def next(self):
        if len(self.data.Close) < self.bb_period * 2:  # Need enough data for indicators
            return

        price = self.data.Close[-1]
        
        if not self.position:
            # Check for low volatility condition
            low_volatility = self.bb_width[-1] < self.bb_width_ma[-1]
            
            # Check for breakout signal
            breakout_signal = price < self.lower[-1]
            
            # Additional confirmation with RSI
            rsi_confirmation = self.rsi[-1] < 50
            
            if low_volatility and breakout_signal and rsi_confirmation:
                # Calculate position size based on 1% risk
                risk_amount = self.equity * self.risk_per_trade
                stop_loss = self.upper[-1]  # Upper band as stop loss
                risk_per_unit = abs(price - stop_loss)
                
                if risk_per_unit > 0:
                    position_size = int(round(risk_amount / risk_per_unit))
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss)
                        print(f"🌙 MOON DEV SHORT SIGNAL! ✨ Price: {price:.2f}, Size: {position_size}, RSI: {self.rsi[-1]:.2f}")
        
        elif self.position.is_short:
            # Exit condition - price touches upper band
            if price >= self.upper[-1]:
                self.position.close()
                print(f"🌙 MOON DEV EXIT SIGNAL! 🚀 Price: {price:.2f}, Profit: {self.position.pl:.2f}")

# Data preparation
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()], errors='ignore')
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'datetime': 'Datetime'
})
data = data.set_index(pd.to_datetime(data['Datetime']))

# Run backtest
bt = Backtest(data, VolatilityBreakout, commission=.002, margin=1.0, trade_on_close=True)
stats = bt.run()
print(stats)
print(stats._strategy)