from backtesting import Backtest, Strategy
import talib
import pandas as pd

class VolumetricBreakout(Strategy):
    def init(self):
        # Calculate indicators
        self.volume_avg = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.ma50 = self.I(talib.SMA, self.data.Close, timeperiod=50)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # Track resistance/support levels
        self.resistance = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.support = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        # Debug prints
        print("🌙 Moon Dev Volumetric Breakout Strategy Initialized! ✨")
        print("📊 Indicators Loaded: Volume MA(20), MA(50), RSI(14), ATR(14)")
        
    def next(self):
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        current_rsi = self.rsi[-1]
        
        # Calculate volume spike condition (1.5x 20-day avg)
        volume_spike = current_volume > (1.5 * self.volume_avg[-1])
        
        # Calculate breakout conditions
        long_breakout = current_close > self.resistance[-1]
        short_breakout = current_close < self.support[-1]
        
        # Trend alignment conditions
        ma_alignment_long = current_close > self.ma50[-1]
        ma_alignment_short = current_close < self.ma50[-1]
        
        # RSI filter (avoid extremes)
        rsi_filter = 30 < current_rsi < 70
        
        # Volatility filter (ATR > 14-day avg)
        volatility_ok = self.atr[-1] > self.I(talib.SMA, self.atr, timeperiod=14)[-1]
        
        # Risk management calculations
        risk_pct = 0.02  # 2% risk per trade
        stop_distance = self.atr[-1] * 1.5
        take_profit = stop_distance * 2  # 2:1 reward:risk
        
        # Position sizing - ensure fractional size between 0 and 1
        risk_amount = self.equity * risk_pct
        position_size = min(risk_amount / stop_distance, 0.99)  # Cap at 99% of equity to avoid margin issues
        
        # Long entry conditions
        if (not self.position and 
            volume_spike and 
            long_breakout and 
            ma_alignment_long and 
            rsi_filter and 
            volatility_ok):
            
            entry_price = current_close
            stop_loss = entry_price - stop_distance
            take_profit_price = entry_price + take_profit
            
            print(f"🚀 MOON DEV LONG SIGNAL! 🌕")
            print(f"📈 Price: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit_price:.2f}")
            print(f"💵 Position Size: {position_size:.4f} of equity")
            
            self.buy(size=position_size, sl=stop_loss, tp=take_profit_price)
        
        # Short entry conditions
        elif (not self.position and 
              volume_spike and 
              short_breakout and 
              ma_alignment_short and 
              rsi_filter and 
              volatility_ok):
            
            entry_price = current_close
            stop_loss = entry_price + stop_distance
            take_profit_price = entry_price - take_profit
            
            print(f"🌑 MOON DEV SHORT SIGNAL! 🌘")
            print(f"📉 Price: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit_price:.2f}")
            print(f"💵 Position Size: {position_size:.4f} of equity")
            
            self.sell(size=position_size, sl=stop_loss, tp=take_profit_price)
        
        # Trailing stop for open positions
        elif self.position:
            if self.position.is_long:
                new_sl = self.data.Close[-1] - (self.atr[-1] * 1.5)
                self.position.close(sl=max(new_sl, self.position.sl or 0))
            else:
                new_sl = self.data.Close[-1] + (self.atr[-1] * 1.5)
                self.position.close(sl=min(new_sl, self.position.sl or float('inf')))
            
            # Exit if volume drops below average
            if current_volume < self.volume_avg[-1]:
                print("🌙 Volume fading - closing position! ✨")
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
    'volume': 'Volume',
    'datetime': 'Datetime'
})
data = data.set_index(pd.to_datetime(data['Datetime']))

# Run backtest with sufficient initial cash
bt = Backtest(data, VolumetricBreakout, commission=.002, margin=1.0, cash=100000)
stats = bt.run()
print(stats)
print(stats._strategy)