# 🌙 Moon Dev's DeltaSentiment Backtest - AI5 Implementation
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy

# Data Preparation
print("🌙 Loading BTC-USD 15m data for DeltaSentiment strategy...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

print(f"🚀 Data loaded: {len(data)} bars from {data.index[0]} to {data.index[-1]}")

def sma(series, period):
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
    return series.rolling(period).mean().values

def sub(series1, series2):
    if isinstance(series1, np.ndarray):
        series1 = pd.Series(series1)
    if isinstance(series2, np.ndarray):
        series2 = pd.Series(series2)
    return (series1 - series2).values

class DeltaSentiment(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    stop_loss_pct = 0.02   # 2% stop loss
    take_profit_pct = 0.03 # 3% take profit
    
    def init(self):
        # Calculate indicators with proper integration
        self.sma20 = self.I(sma, self.data.Close, 20)
        self.sma50 = self.I(sma, self.data.Close, 50)
        self.spread = self.I(sub, self.sma20, self.sma50)
        self.volume_ma = self.I(sma, self.data.Volume, 20)
        
        print("🌙 DeltaSentiment Strategy Initialized! ✨")
        print("SMA20, SMA50, Spread (SMA20-SMA50), Volume MA(20)")

    def next(self):
        # Ensure we have enough data
        if len(self.spread) < 2 or len(self.volume_ma) < 1:
            return

        # Current indicator values
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        volume_ma = self.volume_ma[-1]
        spread_now = self.spread[-1]
        spread_prev = self.spread[-2]
        
        # Check for valid indicator values
        if (np.isnan(spread_now) or np.isnan(spread_prev) or np.isnan(volume_ma)):
            return

        # Calculate trading conditions
        high_liquidity = current_volume > volume_ma
        spread_narrowing = spread_now < spread_prev
        spread_widening = spread_now > spread_prev

        # Risk calculations
        equity = self.equity
        
        # Entry/Exit logic
        if not self.position:
            # Long entry logic - Spread narrowing indicates bullish sentiment
            if high_liquidity and spread_narrowing:
                sl_price = current_close * (1 - self.stop_loss_pct)
                risk_per_share = current_close - sl_price
                position_size = (equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                
                if position_size > 0:
                    tp_price = current_close * (1 + self.take_profit_pct)
                    print(f"🚀 BULLISH DELTA: Spread narrowing with high liquidity!")
                    print(f"Entry: {current_close:.2f}, Size: {position_size}, SL: {sl_price:.2f}, TP: {tp_price:.2f}")
                    self.buy(size=position_size, sl=sl_price, tp=tp_price)
            
            # Short entry logic - Spread widening indicates bearish sentiment
            elif high_liquidity and spread_widening:
                sl_price = current_close * (1 + self.stop_loss_pct)
                risk_per_share = sl_price - current_close
                position_size = (equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                
                if position_size > 0:
                    tp_price = current_close * (1 - self.take_profit_pct)
                    print(f"📉 BEARISH DELTA: Spread widening with high liquidity!")
                    print(f"Entry: {current_close:.2f}, Size: {position_size}, SL: {sl_price:.2f}, TP: {tp_price:.2f}")
                    self.sell(size=position_size, sl=sl_price, tp=tp_price)
        else:
            # Exit conditions for existing position based on sentiment change
            if self.position.is_long and (spread_widening or not high_liquidity):
                print(f"🌕 Closing LONG position: Sentiment changed - spread widening or low liquidity at {current_close:.2f}")
                self.position.close()
            elif self.position.is_short and (spread_narrowing or not high_liquidity):
                print(f"🌑 Closing SHORT position: Sentiment changed - spread narrowing or low liquidity at {current_close:.2f}")
                self.position.close()

# 🌙✨ Launch Backtest
print("🚀 Launching DeltaSentiment backtest with $1,000,000 portfolio...")
bt = Backtest(data, DeltaSentiment, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n" + "="*60)
print("🌙 MOON DEV DELTASENTIMENT STRATEGY RESULTS 🌙")
print("="*60)
print(stats)
print("\n🔍 Strategy Details:")
print(stats._strategy)
print("="*60)