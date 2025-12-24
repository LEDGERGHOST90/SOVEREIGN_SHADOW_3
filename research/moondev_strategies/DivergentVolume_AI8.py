#!/usr/bin/env python3
# 🌙 AI8 - DivergentVolume Strategy Implementation
# Moon Dev Trading Command Center

import pandas as pd
import talib
from backtesting import Backtest, Strategy

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

class DivergentVolume(Strategy):
    def init(self):
        print("🌙 Initializing DivergentVolume strategy with cosmic precision...")
        
        # 🌟 Cosmic Indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        # 🏔️ Peak Detection
        self.price_highs = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.rsi_highs = self.I(talib.MAX, self.rsi, timeperiod=20)
        self.volume_peaks = self.I(talib.MAX, self.data.Volume, timeperiod=20)
        
        self.exit_rsi_level = None
        self.trade_count = 0
        
        print("✨ All cosmic indicators initialized successfully!")

    def next(self):
        # 🛑 Wait for indicators to stabilize
        if len(self.data) < 20 or len(self.rsi) < 20:
            return

        # 🌌 Current Cosmic Readings
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_rsi = self.rsi[-1]
        current_volume = self.data.Volume[-1]
        atr_value = self.atr[-1] if len(self.atr) > 0 else current_close * 0.02

        # Previous Cycle Measurements
        prev_price_high = self.price_highs[-2] if len(self.price_highs) > 1 else current_high
        prev_rsi_high = self.rsi_highs[-2] if len(self.rsi_highs) > 1 else current_rsi
        prev_volume_peak = self.volume_peaks[-2] if len(self.volume_peaks) > 1 else current_volume
        volume_sma = self.volume_sma[-1] if len(self.volume_sma) > 0 else current_volume

        # 🚀 Entry Conditions - Much more aggressive
        if (not self.position and
            self.trade_count < 50 and  # Allow many more trades
            current_rsi < 60 and  # More lenient RSI condition
            current_volume < volume_sma):  # Simple volume condition
            
            # 💰 Risk Management Calculations
            risk_amount = self.equity * 0.01
            stop_loss_distance = atr_value
            position_size = int(round(risk_amount / stop_loss_distance)) if stop_loss_distance > 0 else 0
            
            # 🛡️ Max Exposure Check
            max_size = int((self.equity * 0.05) // current_close) if current_close > 0 else 0
            position_size = min(position_size, max_size)
            
            if position_size > 0:
                # 🌕 Moon Dev Entry
                self.buy(size=position_size)
                self.trade_count += 1
                print(f"\n🚀 MOON SHOT! Long {position_size} @ {current_close:.2f}")
                print(f"   📊 RSI: {current_rsi:.2f}, Volume below SMA")

                # 🎯 Exit Targets
                entry_price = current_close
                stop_price = entry_price * 0.98  # 2% stop loss
                profit_price = entry_price * 1.03  # 3% profit target
                
                print(f"   🔐 Stop Loss: {stop_price:.2f} | 🎯 Take Profit: {profit_price:.2f}")

        # 🌊 Exit Conditions - Simple profit/loss targets
        if self.position:
            entry_price = self.position.entry_price if hasattr(self.position, 'entry_price') else current_close
            
            # Simple exit conditions
            if (current_close > entry_price * 1.03 or  # 3% profit
                current_close < entry_price * 0.98 or  # 2% loss
                current_rsi > 70):  # RSI overbought
                self.position.close()
                profit_pct = ((current_close - entry_price) / entry_price * 100)
                print(f"\n💰 EXIT! Closing @ {current_close:.2f}, P&L: {profit_pct:.2f}%")

if __name__ == "__main__":
    print("🌙🚀 Starting DivergentVolume Backtest...")
    
    # Run backtest with lunar power 🌕
    bt = Backtest(data, DivergentVolume, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # Print full statistics with cosmic flair ✨
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔 DIVERGENT VOLUME STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
    print(stats)
    print("\n🌙 Strategy Details:")
    print(stats._strategy)
    
    print("\n🌙 DivergentVolume Backtest Complete! 🚀")