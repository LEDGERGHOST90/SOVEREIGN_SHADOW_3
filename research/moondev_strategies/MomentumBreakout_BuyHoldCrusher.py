#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Momentum Breakout Buy & Hold Crusher Strategy
AI6 Implementation for Moon Dev Trading System 🌙
Target: Beat 127.77% buy & hold return with 5+ trades

Strategy: Pyramiding momentum strategy that scales into winners
Key insight: In strong bull markets, the best strategy is to ride the trend with increasing position sizes
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

class MomentumBreakoutCrusher(Strategy):
    """
    Momentum Breakout Strategy to Crush Buy & Hold
    
    Key Strategy Elements:
    1. Identify major momentum breakouts using multiple timeframes
    2. Scale into positions as momentum accelerates
    3. Use trailing stops to lock in gains
    4. Reinvest profits for compound growth
    """
    
    # Momentum parameters
    lookback_short = 10   # Short-term momentum
    lookback_medium = 50  # Medium-term trend
    lookback_long = 100   # Long-term trend
    volume_threshold = 1.5  # Volume surge requirement
    breakout_threshold = 0.03  # 3% breakout above resistance
    
    def init(self):
        # Multiple timeframe moving averages
        def calc_sma(data, period):
            return pd.Series(data).rolling(window=period).mean().values
            
        self.sma_short = self.I(calc_sma, self.data.Close, self.lookback_short)
        self.sma_medium = self.I(calc_sma, self.data.Close, self.lookback_medium)
        self.sma_long = self.I(calc_sma, self.data.Close, self.lookback_long)
        
        # Volume analysis
        self.volume_sma = self.I(calc_sma, self.data.Volume, 20)
        
        # Resistance levels (rolling highs)
        def calc_rolling_max(data, period):
            return pd.Series(data).rolling(window=period).max().values
            
        self.resistance = self.I(calc_rolling_max, self.data.High, 50)
        
        # Momentum indicators
        def calc_roc(close, period=10):
            close_series = pd.Series(close)
            return ((close_series - close_series.shift(period)) / close_series.shift(period) * 100).values
        
        self.roc_short = self.I(calc_roc, self.data.Close, 10)
        self.roc_medium = self.I(calc_roc, self.data.Close, 20)
        
        # Position tracking
        self.positions_taken = 0
        self.last_entry_price = None
        self.trailing_stop = None
        self.pyramid_levels = []  # Track multiple entries

    def next(self):
        if len(self.data) < max(self.lookback_long, 50) + 1:
            return
            
        # Exit management first
        if self.position:
            self.manage_exits()
            return
        
        # Entry logic - look for momentum breakouts
        if self.positions_taken < 12:  # Limit total entries for concentration
            self.check_momentum_breakout()

    def check_momentum_breakout(self):
        """Identify high-probability momentum breakouts"""
        current_price = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        avg_volume = self.volume_sma[-1]
        
        # Multi-timeframe trend alignment
        trend_alignment = (current_price > self.sma_short[-1] > self.sma_medium[-1] > self.sma_long[-1])
        
        # Momentum surge
        momentum_surge = (self.roc_short[-1] > 2 and self.roc_medium[-1] > 1)  # Strong momentum
        
        # Volume confirmation
        volume_surge = current_volume > avg_volume * self.volume_threshold
        
        # Breakout above resistance
        resistance_level = self.resistance[-1]
        breakout = current_price > resistance_level * (1 + self.breakout_threshold)
        
        # All-time high breakout (even stronger signal)
        ath_breakout = current_price > max(self.data.Close[:len(self.data)])
        
        # Entry conditions - need strong confluence
        strong_signal = (trend_alignment and momentum_surge and volume_surge and 
                        (breakout or ath_breakout))
        
        if strong_signal:
            self.execute_momentum_entry()

    def execute_momentum_entry(self):
        """Execute momentum-based entry with position scaling"""
        current_price = self.data.Close[-1]
        
        # Progressive position sizing - get more aggressive as we prove the trend
        if self.positions_taken == 0:
            position_fraction = 0.2  # Start with 20%
        elif self.positions_taken <= 3:
            position_fraction = 0.3  # Scale up to 30%
        elif self.positions_taken <= 6:
            position_fraction = 0.4  # Get more aggressive
        else:
            position_fraction = 0.5  # Maximum aggression
        
        # Calculate position size
        available_cash = self.equity * position_fraction
        position_size = int(available_cash / current_price)
        
        if position_size > 0:
            self.last_entry_price = current_price
            self.positions_taken += 1
            
            # Set initial trailing stop
            if self.sma_medium[-1] > 0:
                self.trailing_stop = max(self.sma_medium[-1], current_price * 0.92)  # 8% or medium MA
            else:
                self.trailing_stop = current_price * 0.92
            
            # Track this entry
            self.pyramid_levels.append({
                'price': current_price,
                'size': position_size,
                'time': len(self.data)
            })
            
            self.buy(size=position_size)
            
            print(f'🚀 MOMENTUM ENTRY #{self.positions_taken}: Size={position_size} @ {current_price:.2f}')
            print(f'   ROC Short: {self.roc_short[-1]:.1f}% | ROC Medium: {self.roc_medium[-1]:.1f}%')
            print(f'   Position Fraction: {position_fraction:.0%} | Trailing Stop: {self.trailing_stop:.2f}')
            print(f'   Volume Surge: {self.data.Volume[-1]/self.volume_sma[-1]:.1f}x')

    def manage_exits(self):
        """Advanced exit management with trailing stops"""
        current_price = self.data.Close[-1]
        
        # Update trailing stop - let winners run
        if current_price > self.last_entry_price * 1.05:  # 5% profit
            # Aggressive trailing for momentum
            new_stop = max(self.trailing_stop, current_price * 0.95)  # 5% trailing
            if new_stop > self.trailing_stop:
                self.trailing_stop = new_stop
                print(f'📈 TRAILING STOP UPDATED: {self.trailing_stop:.2f} (5% trail)')
        
        elif current_price > self.last_entry_price * 1.02:  # 2% profit
            # Conservative trailing
            new_stop = max(self.trailing_stop, current_price * 0.97)  # 3% trailing
            if new_stop > self.trailing_stop:
                self.trailing_stop = new_stop
                print(f'📈 TRAILING STOP UPDATED: {self.trailing_stop:.2f} (3% trail)')
        
        # Exit on trailing stop hit
        if current_price <= self.trailing_stop:
            profit_pct = ((current_price - self.last_entry_price) / self.last_entry_price) * 100
            self.position.close()
            print(f'🛑 TRAILING STOP EXIT @ {current_price:.2f} | Profit: {profit_pct:.1f}%')
            self.reset_position()
            return
        
        # Exit on momentum failure
        if (len(self.roc_short) > 5 and 
            self.roc_short[-1] < -2 and  # Negative momentum
            current_price < self.sma_short[-1] and  # Below short MA
            current_price > self.last_entry_price):  # Only if profitable
            
            profit_pct = ((current_price - self.last_entry_price) / self.last_entry_price) * 100
            self.position.close()
            print(f'📉 MOMENTUM FAILURE EXIT @ {current_price:.2f} | Profit: {profit_pct:.1f}%')
            self.reset_position()
            return

    def reset_position(self):
        """Reset position tracking"""
        self.last_entry_price = None
        self.trailing_stop = None
        # Don't reset positions_taken - we want to track total entries

# Run backtest
print("🌙 Starting Momentum Breakout Buy & Hold Crusher...")
print("Target: Beat 127.77% Buy & Hold Return with Momentum Scaling")
print("=" * 70)

bt = Backtest(data, MomentumBreakoutCrusher, cash=1000000, commission=.002)
stats = bt.run()

print("\n🌙 Momentum Breakout Crusher Results:")
print("=" * 70)
print(stats)

# Key metrics
print(f"\n⭐ Momentum Strategy Performance:")
print(f"💰 Total Return: {stats['Return [%]']:.2f}%")
print(f"🎯 Buy & Hold Benchmark: 127.77%")
print(f"📈 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"🎯 Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"📊 Total Trades: {stats['# Trades']}")

# Success check
if stats['Return [%]'] > 127.77 and stats['# Trades'] >= 5:
    print(f"\n🏆 SUCCESS! Momentum strategy CRUSHES buy & hold!")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Outperformance: {stats['Return [%]'] - 127.77:.2f}%")
    print(f"   🔥 MISSION ACCOMPLISHED! 🔥")
elif stats['# Trades'] >= 5:
    print(f"\n✅ TRADE COUNT MET but return insufficient")
    print(f"   Strategy: {stats['Return [%]']:.2f}% vs Buy & Hold: 127.77%")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")
    print(f"   Underperformance: {stats['Return [%]'] - 127.77:.2f}%")
else:
    print(f"\n❌ Requirements not met")
    print(f"   Return: {stats['Return [%]']:.2f}% (Target: >127.77%)")
    print(f"   Trades: {stats['# Trades']} (Required: 5+)")

print("\n🌙 Momentum Crusher completed! ✨")