import pandas as pd
from backtesting import Backtest, Strategy
import numpy as np

# Data preprocessing
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'datetime': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class BandDivergence(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 Moon Dev Indicators Setup
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # Bollinger Bands
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        
        self.bb_mid = self.I(lambda: sma20)
        self.bb_upper = self.I(lambda: sma20 + 2*std20)
        self.bb_lower = self.I(lambda: sma20 - 2*std20)
        
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        self.macd = self.I(lambda: ema12 - ema26)
        
        # ATR
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.atr = self.I(lambda: tr.rolling(14).mean())
        
        # Swing points
        self.swing_high = self.I(lambda: high.rolling(20).max())
        self.swing_low = self.I(lambda: low.rolling(20).min())
        
        print("🌙✨ Moon Dev Indicators Activated! BB|MACD|SWING|ATR Ready 🚀")

    def next(self):
        # Wait for sufficient data
        if len(self.data) < 30:
            return

        # 🌙 Current Market Conditions
        price = self.data.Close[-1]
        
        # Safe indicator access with NaN handling
        macd_val = self.macd[-1] if not np.isnan(self.macd[-1]) else 0
        atr_val = self.atr[-1] if not np.isnan(self.atr[-1]) else 100
        bb_mid_current = self.bb_mid[-1] if not np.isnan(self.bb_mid[-1]) else price
        bb_mid_prev = self.bb_mid[-2] if len(self.data) > 1 and not np.isnan(self.bb_mid[-2]) else bb_mid_current

        # 🚀 Long Entry Logic
        if not self.position and atr_val > 0:
            # Trend confirmation
            if len(self.data) >= 22:  # Ensure we have enough data for swing calculations
                higher_high = self.swing_high[-1] > self.swing_high[-2]
                higher_low = self.swing_low[-1] > self.swing_low[-2]
                uptrend = higher_high and higher_low
                
                if (bb_mid_current > bb_mid_prev and
                    macd_val > 0 and
                    uptrend):
                    
                    # 🌙 Risk Management
                    stop_loss = price - 1.5*atr_val
                    risk_amount = self.equity * self.risk_pct
                    risk_per_share = price - stop_loss
                    
                    if risk_per_share > 0:
                        position_size = int(round(risk_amount / risk_per_share))
                        
                        if position_size > 0:
                            self.buy(size=position_size, sl=stop_loss)
                            print(f"🚀🌙 MOON DEV LONG: {self.data.index[-1]} | Size: {position_size} | SL: {stop_loss:.2f}")

        # 🌑 Short Entry Logic
        if not self.position and atr_val > 0:
            # Volatility contraction
            bb_width = self.bb_upper[-1] - self.bb_lower[-1] if not np.isnan(self.bb_upper[-1]) and not np.isnan(self.bb_lower[-1]) else 0
            bb_width_prev = self.bb_upper[-2] - self.bb_lower[-2] if len(self.data) > 1 and not np.isnan(self.bb_upper[-2]) and not np.isnan(self.bb_lower[-2]) else bb_width
            
            # Trend confirmation
            if len(self.data) >= 22:  # Ensure we have enough data for swing calculations
                lower_high = self.swing_high[-1] < self.swing_high[-2]
                lower_low = self.swing_low[-1] < self.swing_low[-2]
                downtrend = lower_high and lower_low
                
                if (bb_width < bb_width_prev and
                    macd_val < 0 and
                    downtrend):
                    
                    # 🌙 Risk Management
                    stop_loss = price + 1.5*atr_val
                    risk_amount = self.equity * self.risk_pct
                    risk_per_share = stop_loss - price
                    
                    if risk_per_share > 0:
                        position_size = int(round(risk_amount / risk_per_share))
                        
                        if position_size > 0:
                            self.sell(size=position_size, sl=stop_loss)
                            print(f"🌑🌙 MOON DEV SHORT: {self.data.index[-1]} | Size: {position_size} | SL: {stop_loss:.2f}")

        # Exit Logic
        if self.position:
            # Take profit conditions
            if (self.position.is_long and not np.isnan(self.bb_upper[-1]) and 
                price >= self.bb_upper[-1]):
                self.position.close()
                print(f"💰🌙 MOON DEV PROFIT - Long Exit: {price:.2f}")
            elif (self.position.is_short and not np.isnan(self.bb_lower[-1]) and 
                  price <= self.bb_lower[-1]):
                self.position.close()
                print(f"💰🌙 MOON DEV PROFIT - Short Exit: {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting BandDivergence Backtest...")
bt = Backtest(data, BandDivergence, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ BAND DIVERGENCE STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)