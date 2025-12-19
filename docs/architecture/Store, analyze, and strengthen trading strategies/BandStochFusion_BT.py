from backtesting import Strategy, Backtest
import talib
import pandas as pd

class BandStochFusion(Strategy):
    def init(self):
        # Clean and prepare data
        self.data.columns = self.data.columns.str.strip().str.lower()
        self.data = self.data.drop(columns=[col for col in self.data.columns if 'unnamed' in col.lower()])
        self.data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        
        # Indicators
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, 
                                                             self.data.close, 
                                                             timeperiod=20, 
                                                             nbdevup=2, 
                                                             nbdevdn=2, 
                                                             matype=0)
        self.stoch_k, self.stoch_d = self.I(talib.STOCH, 
                                          self.data.high, 
                                          self.data.low, 
                                          self.data.close, 
                                          fastk_period=14, 
                                          slowk_period=3, 
                                          slowk_matype=0, 
                                          slowd_period=3, 
                                          slowd_matype=0)
        
    def next(self):
        # Long Entry
        if self.data.close[-1] <= self.bb_lower[-1]:
            if self.stoch_k[-1] < 20 and (self.stoch_k[-2] < self.stoch_d[-2] and self.stoch_k[-1] > self.stoch_d[-1]):
                position_size = int(round(1000000 / self.data.close[-1]))
                self.buy(size=position_size)
                print(f"🌙 Moon Dev Alert: LONG activated at {self.data.close[-1]:.2f} | Size: {position_size} units 🚀")
        
        # Short Entry
        if self.data.close[-1] >= self.bb_upper[-1]:
            if self.stoch_k[-1] > 80 and (self.stoch_d[-2] < self.stoch_k[-2] and self.stoch_d[-1] > self.stoch_k[-1]):
                position_size = int(round(1000000 / self.data.close[-1]))
                self.sell(size=position_size)
                print(f"🌙 Moon Dev Alert: SHORT activated at {self.data.close[-1]:.2f} | Size: {position_size} units 🌒")
        
        # Long Exit
        if self.position.is_long:
            if self.data.close[-1] >= self.bb_middle[-1] or self.stoch_k[-1] > 80:
                self.position.close()
                print(f"✨ Moon Dev Exit: LONG closed at {self.data.close[-1]:.2f} | Profit: {self.position.pl:.2f} 🌟")
        
        # Short Exit
        if self.position.is_short:
            if self.data.close[-1] <= self.bb_middle[-1] or self.stoch_k[-1] < 20:
                self.position.close()
                print(f"✨ Moon Dev Exit: SHORT closed at {self.data.close[-1]:.2f} | Profit: {self.position.pl:.2f} 🌟")

# Data loading with proper error handling
try:
    data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
    data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
    print("🌙 Moon Dev: Data loaded successfully! Starting backtest... ✨")
    
    # Run backtest
    bt = Backtest(data, BandStochFusion, cash=1000000, commission=0.002)
    stats = bt.run()
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔🌕")
    print("🌙 Moon Dev Backtest Complete!")
    print("✨ Strategy Performance Summary:")
    print(stats)
    
except FileNotFoundError:
    print("🌙 Moon Dev Error: Data file not found! Please check the path.")
except Exception as e:
    print(f"🌙 Moon Dev Error: {str(e)}")