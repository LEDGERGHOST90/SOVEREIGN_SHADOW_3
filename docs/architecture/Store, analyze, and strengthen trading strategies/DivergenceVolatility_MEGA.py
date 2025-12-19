#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DivergenceVolatility MEGA Strategy - Beat Buy & Hold
AI6 Implementation for Moon Dev Trading System 🌙
Target: Beat 127.77% buy & hold return with 5+ trades
"""

import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High', 
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class DivergenceVolatilityMEGA(Strategy):
    """
    DivergenceVolatility MEGA Strategy: Beat Buy & Hold 🌙
    
    Approach: Simplified trend following with aggressive position sizing
    """
    
    # MEGA Parameters - Much Simpler Approach
    risk_per_trade = 0.25  # 25% risk per trade (very aggressive)
    trend_period = 50      # Simple trend following
    rsi_period = 14        # RSI for timing
    volume_threshold = 1.2 # Volume confirmation
    
    def init(self):
        # Simple moving average for trend
        def calc_sma(data, period):
            return pd.Series(data).rolling(window=period).mean().values
            
        self.trend_sma = self.I(calc_sma, self.data.Close, self.trend_period)
        
        # Simple RSI
        def calc_rsi(close, period=14):
            close_series = pd.Series(close)
            delta = close_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.values
        
        self.rsi = self.I(calc_rsi, self.data.Close, self.rsi_period)
        
        # Volume SMA
        self.volume_sma = self.I(calc_sma, self.data.Volume, 20)
        
        # Trade tracking
        self.entry_price = None
        self.entry_time = None
        self.trades_taken = 0

    def next(self):
        if len(self.data) < self.trend_period + 1:
            return
            
        # Exit first
        if self.position:
            self.check_mega_exits()
            return
        
        # Only take a few high-conviction trades
        if self.trades_taken >= 8:  # Limit to 8 trades max
            return
            
        # MEGA Entry Logic - Very Simple
        current_price = self.data.Close[-1]
        trend_level = self.trend_sma[-1]
        current_rsi = self.rsi[-1]
        current_volume = self.data.Volume[-1]
        avg_volume = self.volume_sma[-1]
        
        # Strong uptrend conditions
        uptrend = current_price > trend_level * 1.02  # 2% above trend
        rsi_ok = current_rsi < 80  # Not overbought
        volume_ok = current_volume > avg_volume * self.volume_threshold
        momentum_ok = len(self.data.Close) > 5 and self.data.Close[-1] > self.data.Close[-5]
        
        # Entry condition - all must be true for high conviction
        if uptrend and rsi_ok and volume_ok and momentum_ok:
            self.execute_mega_entry()

    def execute_mega_entry(self):
        """MEGA Entry with huge position size"""
        # Very aggressive position sizing
        risk_amount = self.equity * self.risk_per_trade
        
        # Simple stop loss at trend line
        stop_loss = self.trend_sma[-1] * 0.98  # 2% below trend
        risk_per_unit = self.data.Close[-1] - stop_loss
        
        if risk_per_unit <= 0:
            return
            
        position_size = risk_amount / risk_per_unit
        position_size = int(round(position_size))
        
        if position_size > 0:
            self.entry_price = self.data.Close[-1]
            self.entry_time = len(self.data)
            self.trades_taken += 1
            
            self.buy(size=position_size)
            
            print(f'🚀 MEGA ENTRY #{self.trades_taken}: Size={position_size} @ {self.entry_price:.2f}')
            print(f'   Trend: {self.trend_sma[-1]:.2f} | RSI: {self.rsi[-1]:.1f}')
            print(f'   Risk: ${risk_amount:.0f} (25% of equity)')

    def check_mega_exits(self):
        """Simple exit logic"""
        current_price = self.data.Close[-1]
        current_time = len(self.data)
        
        # Stop loss at trend line
        if current_price < self.trend_sma[-1] * 0.98:
            self.position.close()
            print(f'🛑 MEGA STOP @ {current_price:.2f}')
            self.reset_params()
            return
            
        # Take profit at 50% gain
        if self.entry_price and current_price > self.entry_price * 1.5:
            self.position.close()
            print(f'🎯 MEGA PROFIT @ {current_price:.2f} (50% gain!)')
            self.reset_params()
            return
            
        # Time exit after 2000 bars (hold longer)
        if self.entry_time and (current_time - self.entry_time) > 2000:
            self.position.close()
            print(f'⏰ MEGA TIME EXIT @ {current_price:.2f}')
            self.reset_params()
            return

    def reset_params(self):
        self.entry_price = None
        self.entry_time = None

# Run backtest
print("🌙 Starting DivergenceVolatility MEGA Backtest...")
print("Target: Beat 127.77% Buy & Hold Return with 5+ trades")
print("=" * 60)

bt = Backtest(data, DivergenceVolatilityMEGA, cash=1000000, commission=.002)
stats = bt.run()

print("\n🌙 DivergenceVolatility MEGA Strategy Results:")
print("=" * 60)
print(stats)

# Key metrics
print(f"\n⭐ MEGA Performance Metrics:")
print(f"💰 Total Return: {stats['Return [%]']:.2f}%")
print(f"🎯 Buy & Hold Target: 127.77%")
print(f"📈 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"🎯 Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"📊 Total Trades: {stats['# Trades']}")

# Success check
if stats['Return [%]'] > 127.77 and stats['# Trades'] >= 5:
    print(f"\n🏆 SUCCESS! Strategy beats buy & hold!")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
else:
    print(f"\n❌ Need more optimization...")
    print(f"   Return: {stats['Return [%]']:.2f}% (Target: >127.77%)")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")

print("\n🌙 MEGA backtest completed! ✨")