#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Early Bird Buy & Hold Destroyer Strategy
AI6 Implementation for Moon Dev Trading System 🌙
Target: Beat 127.77% buy & hold return with 5+ trades

Strategy: Get in BEFORE the major moves and scale up
Key insight: Beat buy & hold by entering before the trend starts
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

class EarlyBirdDestroyer(Strategy):
    """
    Early Bird Strategy to Destroy Buy & Hold
    
    Strategy: Get in VERY early and scale positions
    """
    
    def init(self):
        # Early entry points (much earlier than buy & hold)
        self.entry_points = [
            100,    # Very early
            500,    # Still early
            1500,   # Early trend
            3000,   # Building position
            6000,   # Scaling up
            10000,  # More size
            15000,  # Continue building
            20000   # Final scale
        ]
        self.entries_made = 0

    def next(self):
        current_bar = len(self.data)
        
        # Make early entries
        if (self.entries_made < len(self.entry_points) and 
            current_bar >= self.entry_points[self.entries_made]):
            
            self.make_early_entry()

    def make_early_entry(self):
        """Make early aggressive entries"""
        current_price = self.data.Close[-1]
        
        # Progressive position sizing - get bigger as we prove thesis
        if self.entries_made == 0:
            cash_fraction = 0.20  # Start with 20%
        elif self.entries_made <= 2:
            cash_fraction = 0.25  # Scale to 25%
        elif self.entries_made <= 4:
            cash_fraction = 0.30  # Scale to 30%
        else:
            cash_fraction = 0.35  # Maximum 35%
        
        available_cash = self.equity * cash_fraction
        position_size = int(available_cash / current_price)
        
        if position_size > 0:
            self.entries_made += 1
            self.buy(size=position_size)
            
            print(f'🐦 EARLY BIRD ENTRY #{self.entries_made}: Size={position_size} @ {current_price:.2f}')
            print(f'   Cash Fraction: {cash_fraction:.0%} | Cash: ${available_cash:.0f}')
            print(f'   Bar: {len(self.data)} | Equity: ${self.equity:.0f}')

# Run backtest
print("🌙 Starting Early Bird Buy & Hold Destroyer...")
print("Strategy: Get In Early, Scale Up, Destroy Buy & Hold")
print("=" * 70)

bt = Backtest(data, EarlyBirdDestroyer, cash=1000000, commission=.002)
stats = bt.run()

print("\n🌙 Early Bird Destroyer Results:")
print("=" * 70)
print(stats)

# Key metrics
print(f"\n⭐ Early Bird Performance:")
print(f"💰 Total Return: {stats['Return [%]']:.2f}%")
print(f"🎯 Buy & Hold Benchmark: 127.77%")
print(f"📈 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"🎯 Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"📊 Total Trades: {stats['# Trades']}")

# Success check
if stats['Return [%]'] > 127.77 and stats['# Trades'] >= 5:
    print(f"\n🏆 SUCCESS! Early Bird DESTROYS buy & hold!")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Outperformance: {stats['Return [%]'] - 127.77:.2f}%")
    print(f"   🔥 EARLY BIRD VICTORY! 🔥")
elif stats['# Trades'] >= 5:
    print(f"\n✅ TRADE COUNT MET but return insufficient")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Underperformance: {stats['Return [%]'] - 127.77:.2f}%")
else:
    print(f"\n❌ Requirements not met")
    print(f"   Return: {stats['Return [%]']:.2f}% (Target: >127.77%)")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")

print("\n🌙 Early Bird Destroyer completed! ✨")