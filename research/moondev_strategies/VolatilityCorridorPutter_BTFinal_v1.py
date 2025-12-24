from backtesting import Backtest, Strategy
import talib
import pandas as pd
import numpy as np

class VolatilityCorridorPutter(Strategy):
    def init(self):
        # Moon Dev debug prints
        print("🌙 Moon Dev Volatility Corridor Putter Strategy Initialized! ✨")
        
        # Calculate 20-day VIX-SPX correlation
        self.vix_spx_corr = self.I(talib.CORREL, self.data.df['vix'], self.data.df['spx'], timeperiod=20)
        
        # Calculate daily highs/lows
        self.daily_high = self.I(talib.MAX, self.data.High, timeperiod=24)
        self.daily_low = self.I(talib.MIN, self.data.Low, timeperiod=24)
        
        # Track position info
        self.position_size = 0
        self.entry_price = 0
        self.entry_day = 0

    def next(self):
        # Check if it's expiration day (Friday)
        is_expiration_day = self.data.index[-1].weekday() == 4
        
        # Get current correlation value
        current_corr = self.vix_spx_corr[-1] if len(self.vix_spx_corr) > 0 else 0
        
        # Check volatility filter (VIX <= 30)
        current_vix = self.data.df['vix'][-1]
        vix_ok = current_vix <= 30
        
        # Correlation band check (-0.05 to +0.05)
        corr_ok = -0.05 <= current_corr <= 0.05
        
        # Emergency exit condition
        emergency_exit = abs(current_corr) > 0.10
        
        # Moon Dev debug prints
        print(f"🌙 Current VIX-SPX Correlation: {current_corr:.4f} | VIX: {current_vix:.2f} | Exp Day: {is_expiration_day}")
        
        # Emergency exit logic
        if emergency_exit and self.position:
            print("🚨 EMERGENCY EXIT! Correlation band broken! 🚨")
            self.position.close()
            return
        
        # Entry conditions
        if not self.position and is_expiration_day and vix_ok and corr_ok:
            # Check price breaks above prior day's high
            if self.data.Close[-1] > self.daily_high[-2]:
                # Calculate position size (5% of equity)
                risk_amount = self.equity * 0.05
                position_size = int(round(risk_amount / self.data.Close[-1]))
                
                # Enter short put position (sell)
                self.sell(size=position_size)
                self.entry_price = self.data.Close[-1]
                self.entry_day = len(self.data)
                print(f"✨ ENTRY SIGNAL! Selling puts at {self.entry_price:.2f} | Size: {position_size} ✨")
        
        # Exit conditions
        if self.position:
            # Profit target (next day's low)
            profit_target = self.daily_low[-1]
            
            # Time exit (end of expiration day)
            time_exit = len(self.data) - self.entry_day >= 1
            
            # Check exit conditions
            if self.data.Close[-1] <= profit_target or time_exit:
                print(f"🌙 EXIT SIGNAL! Price: {self.data.Close[-1]:.2f} | Target: {profit_target:.2f} | Time Exit: {time_exit}")
                self.position.close()

# Load and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Ensure proper column mapping
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Set datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# Add mock VIX and SPX data for testing (replace with real data)
data['vix'] = np.random.uniform(10, 40, len(data))
data['spx'] = np.random.normal(4000, 100, len(data))

# Run backtest with sufficient initial cash
bt = Backtest(data, VolatilityCorridorPutter, commission=.002, margin=1, trade_on_close=True, cash=100000)
stats = bt.run()
print(stats)
print(stats._strategy)