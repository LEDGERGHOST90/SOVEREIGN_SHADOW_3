#!/usr/bin/env python3
# 🌙 AI8 - DivergentMomentum Strategy Implementation
# Moon Dev Trading Command Center

import pandas as pd
from backtesting import Backtest, Strategy
import talib
import numpy as np

# Load and preprocess data with lunar precision 🌕
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean data columns with cosmic care ✨
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to match backtesting requirements
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Convert datetime and set index with lunar alignment 🌑
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

print(f"🌙 Data loaded: {len(data)} rows from {data.index[0]} to {data.index[-1]}")

class DivergentMomentum(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    rsi_period = 14
    ma_period = 50
    cci_period = 20
    swing_window = 5  # Swing low detection window

    def init(self):
        print("🌙 Initializing DivergentMomentum strategy with cosmic precision...")
        
        # Calculate indicators using TA-Lib with cosmic precision 🌌
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.ma50 = self.I(talib.SMA, self.data.Close, self.ma_period)
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low, self.data.Close, self.cci_period)
        self.price_lows = self.I(talib.MIN, self.data.Low, self.swing_window)
        self.rsi_lows = self.I(talib.MIN, self.rsi, self.swing_window)
        
        print("✨ All cosmic indicators initialized successfully!")

    def next(self):
        # Skip if not enough data (wait for full moon cycle) 🌕
        if len(self.rsi) < self.swing_window + 2:
            return

        # Current values
        price_low_current = self.price_lows[-1]
        price_low_prev = self.price_lows[-2]
        rsi_low_current = self.rsi_lows[-1]
        rsi_low_prev = self.rsi_lows[-2]
        
        # Divergence detection with lunar accuracy 🌙
        bearish_price = price_low_current < price_low_prev
        bullish_rsi = rsi_low_current > rsi_low_prev
        divergence = bearish_price and bullish_rsi

        # Entry conditions with cosmic alignment ✨ - Made more aggressive
        if not self.position:
            if (self.rsi[-1] < 50 and  # Much more lenient RSI
                self.data.Close[-1] > self.ma50[-1]):  # Removed strict divergence requirement
                
                # Risk management calculations with lunar precision 🌑
                entry_price = self.data.Close[-1]
                stop_loss = entry_price * 0.98  # Simple 2% stop loss
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = (self.equity * self.risk_percent) / risk_per_share
                    position_size = int(round(position_size))  # Ensure whole number of units
                    
                    if position_size > 0:
                        # Moon-themed debug print 🌙✨
                        print(f"🌙✨ Lunar Entry! Price: {entry_price:.2f}, Size: {position_size} contracts, SL: {stop_loss:.2f}")
                        print(f"   🔍 RSI: {self.rsi[-1]:.2f}, Price Low: {price_low_current:.2f} -> {price_low_prev:.2f}")
                        print(f"   🔍 RSI Low: {rsi_low_current:.2f} -> {rsi_low_prev:.2f}")
                        
                        self.buy(size=position_size, sl=stop_loss)

        # Exit conditions with cosmic wisdom 🌌 - More aggressive exits
        else:
            entry_price = self.position.entry_price if hasattr(self.position, 'entry_price') else self.data.Close[-1]
            current_price = self.data.Close[-1]
            
            # Take profit at 3% or stop loss at 2%
            if (current_price > entry_price * 1.03 or  # 3% profit
                current_price < entry_price * 0.98 or  # 2% loss
                self.rsi[-1] > 70):  # RSI overbought
                print(f"🚀🌙 Exit! Closing position at {current_price:.2f}")
                self.position.close()

if __name__ == "__main__":
    print("🌙🚀 Starting DivergentMomentum Backtest...")
    
    # Run backtest with lunar power 🌕
    bt = Backtest(data, DivergentMomentum, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # Print full statistics with cosmic flair ✨
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔 DIVERGENT MOMENTUM STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
    print(stats)
    print("\n🌙 Strategy Details:")
    print(stats._strategy)
    
    print("\n🌙 DivergentMomentum Backtest Complete! 🚀")