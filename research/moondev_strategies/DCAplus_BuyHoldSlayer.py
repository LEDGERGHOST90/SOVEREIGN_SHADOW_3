#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCA Plus Buy & Hold Slayer Strategy
AI6 Implementation for Moon Dev Trading System 🌙
Target: Beat 127.77% buy & hold return with 5+ trades

Strategy: Dollar Cost Averaging PLUS tactical additions
Key insight: Regular DCA + Extra buys on dips = Beat buy & hold
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

class DCAPlusSlayer(Strategy):
    """
    DCA Plus Strategy to Slay Buy & Hold
    
    Strategy: Regular DCA + Extra tactical buys
    """
    
    def init(self):
        # DCA schedule (every ~1000 bars = regular intervals)
        self.dca_intervals = [
            100,    # Start early
            1100,   # Regular DCA
            2100,   # Continue
            3100,   # Keep going
            4100,   # More DCA
            5100,   # Continue
            6100,   # Keep buying
            7100,   # More
            8100,   # Continue
            9100,   # Keep going
            10100,  # More
            11100,  # Continue
            12100,  # Keep buying
            13100,  # More
            14100,  # Continue
            15100,  # Keep going
            16100,  # More
            17100,  # Continue
            18100,  # Keep buying
            19100,  # More
            20100,  # Continue
        ]
        self.dca_made = 0
        
        # Simple moving average for dip detection
        def calc_sma(data, period):
            return pd.Series(data).rolling(window=period).mean().values
            
        self.ma50 = self.I(calc_sma, self.data.Close, 50)

    def next(self):
        current_bar = len(self.data)
        
        # Execute DCA schedule
        if (self.dca_made < len(self.dca_intervals) and 
            current_bar >= self.dca_intervals[self.dca_made]):
            
            self.execute_dca_buy()
        
        # Also buy dips (price > 5% below MA50)
        elif (len(self.ma50) > 0 and not np.isnan(self.ma50[-1]) and
              self.data.Close[-1] < self.ma50[-1] * 0.95 and
              current_bar % 500 == 0):  # Every 500 bars if dip
            
            self.execute_dip_buy()

    def execute_dca_buy(self):
        """Execute regular DCA purchase"""
        current_price = self.data.Close[-1]
        
        # Progressive DCA - start small, get bigger
        if self.dca_made < 5:
            dca_amount = 45000  # $45k each
        elif self.dca_made < 10:
            dca_amount = 55000  # $55k each
        else:
            dca_amount = 65000  # $65k each
        
        position_size = int(dca_amount / current_price)
        
        if position_size > 0:
            self.dca_made += 1
            self.buy(size=position_size)
            
            print(f'💰 DCA BUY #{self.dca_made}: Size={position_size} @ {current_price:.2f}')
            print(f'   Amount: ${dca_amount} | Bar: {len(self.data)}')

    def execute_dip_buy(self):
        """Execute tactical dip purchase"""
        current_price = self.data.Close[-1]
        ma_level = self.ma50[-1]
        
        # Bigger dip = bigger buy
        dip_percent = (ma_level - current_price) / ma_level
        if dip_percent > 0.10:  # 10%+ dip
            dip_amount = 100000
        elif dip_percent > 0.07:  # 7%+ dip
            dip_amount = 75000
        else:  # 5%+ dip
            dip_amount = 50000
        
        position_size = int(dip_amount / current_price)
        
        if position_size > 0:
            self.buy(size=position_size)
            
            print(f'📉 DIP BUY: Size={position_size} @ {current_price:.2f}')
            print(f'   Dip: {dip_percent:.1%} below MA | Amount: ${dip_amount}')

# Run backtest
print("🌙 Starting DCA Plus Buy & Hold Slayer...")
print("Strategy: DCA + Tactical Dip Buying")
print("=" * 60)

bt = Backtest(data, DCAPlusSlayer, cash=1000000, commission=.002)
stats = bt.run()

print("\n🌙 DCA Plus Slayer Results:")
print("=" * 60)
print(stats)

# Key metrics
print(f"\n⭐ DCA Plus Performance:")
print(f"💰 Total Return: {stats['Return [%]']:.2f}%")
print(f"🎯 Buy & Hold Benchmark: 127.77%")
print(f"📈 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"🎯 Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"📊 Total Trades: {stats['# Trades']}")

# Success check
if stats['Return [%]'] > 127.77 and stats['# Trades'] >= 5:
    print(f"\n🏆 SUCCESS! DCA Plus SLAYS buy & hold!")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Outperformance: {stats['Return [%]'] - 127.77:.2f}%")
    print(f"   🔥 DCA PLUS VICTORY! 🔥")
elif stats['# Trades'] >= 5:
    print(f"\n✅ TRADE COUNT MET but return insufficient")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Underperformance: {stats['Return [%]'] - 127.77:.2f}%")
else:
    print(f"\n❌ Requirements not met")
    print(f"   Return: {stats['Return [%]']:.2f}% (Target: >127.77%)")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")

print("\n🌙 DCA Plus Slayer completed! ✨")