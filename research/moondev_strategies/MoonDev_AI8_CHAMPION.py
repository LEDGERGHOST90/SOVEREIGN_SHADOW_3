#!/usr/bin/env python3
# 🌙 AI8 - MoonDev CHAMPION Strategy - The FINAL CHAMPION
# Moon Dev Trading Command Center - ABSOLUTE CHAMPION

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

class MoonDevChampion(Strategy):
    def init(self):
        print("🌙 Initializing MoonDev CHAMPION strategy...")
        
        # Champion indicators for maximum gains 🚀
        self.sma20 = self.I(talib.SMA, self.data.Close, 20)
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close)
        
        self.trade_count = 0
        self.last_trade_bar = 0
        
        print("✨ Champion system activated!")

    def next(self):
        if len(self.data) < 100:
            return
            
        current_bar = len(self.data) - 1
        current_price = self.data.Close[-1]
        
        # CHAMPION STRATEGY: Buy EARLY and hold through the ENTIRE bull run 🎯
        if not self.position and self.trade_count < 6:  # Only 6 strategic entries maximum
            
            # Space trades by 4000+ bars (about 6 weeks)
            if current_bar - self.last_trade_bar < 4000:
                return
            
            # Entry conditions - focus on EARLY trend detection
            price_above_sma = current_price > self.sma20[-1]
            rsi_bullish = 40 < self.rsi[-1] < 65  # Not oversold, not overbought
            macd_positive = self.macd[-1] > self.macd_signal[-1]
            
            # Look for early momentum
            price_momentum = current_price > self.data.Close[-10] * 1.01  # 1% gain in 10 bars
            
            if price_above_sma and rsi_bullish and macd_positive and price_momentum:
                # CHAMPION position sizing - go ALL IN for massive gains 💪
                position_size = int(self.equity / current_price)  # Use ALL equity
                
                if position_size > 0:
                    # Very wide stop loss - never get stopped out during normal volatility
                    stop_loss = current_price * 0.75  # 25% stop loss
                    
                    self.buy(size=position_size, sl=stop_loss)
                    self.trade_count += 1
                    self.last_trade_bar = current_bar
                    
                    print(f"🚀👑 CHAMPION ENTRY #{self.trade_count}!")
                    print(f"   💎 Size: {position_size} @ {current_price:.2f} (ALL IN)")
                    print(f"   📊 SMA20: {self.sma20[-1]:.0f}, RSI: {self.rsi[-1]:.1f}")
                    print(f"   📈 MACD: {self.macd[-1]:.3f}")
                    print(f"   🛡️ Stop: {stop_loss:.2f}")

        # CHAMPION HOLDING STRATEGY - Ride the ENTIRE trend 🌊
        else:
            if self.position:
                entry_price = self.position.entry_price if hasattr(self.position, 'entry_price') else current_price
                profit_pct = (current_price - entry_price) / entry_price
                
                # Only exit on MASSIVE profits or clear bear market
                # Exit conditions are very strict - we want to capture the full bull run
                
                # 1. Massive profit target - let's aim for the moon
                mega_profit = profit_pct > 3.0  # 300% profit!
                
                # 2. Clear bear market with multiple confirmations
                clear_bear = (current_price < self.sma20[-1] * 0.90 and  # 10% below SMA20
                             self.rsi[-1] < 30 and  # RSI oversold
                             self.macd[-1] < self.macd_signal[-1] and  # MACD bearish
                             self.macd[-1] < -50)  # MACD very negative
                
                # 3. Time-based exit only if losing money
                bars_held = current_bar - self.last_trade_bar
                time_exit_losing = bars_held > 8000 and profit_pct < 0  # Exit if losing after long time
                
                if mega_profit or clear_bear or time_exit_losing:
                    self.position.close()
                    exit_reason = ("MEGA PROFIT" if mega_profit else
                                 ("CLEAR BEAR" if clear_bear else "TIME EXIT LOSING"))
                    print(f"💰👑 CHAMPION EXIT! {exit_reason}")
                    print(f"   🎯 EPIC P&L: {profit_pct*100:.1f}% @ {current_price:.2f}")
                    print(f"   📊 Bars held: {bars_held}")

if __name__ == "__main__":
    print("🌙🚀 Starting MoonDev CHAMPION Backtest...")
    
    # Run backtest with lunar power 🌕
    bt = Backtest(data, MoonDevChampion, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # Print full statistics with cosmic flair ✨
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔 CHAMPION MOONDEV STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
    print(stats)
    print(f"\n🎯 Target: Beat Buy & Hold {stats['Buy & Hold Return [%]']:.1f}%")
    print(f"🚀 Strategy Return: {stats['Return [%]']:.1f}%")
    print(f"📊 Number of Trades: {stats['# Trades']}")
    
    if stats['# Trades'] > 0:
        print(f"🏆 Win Rate: {stats['Win Rate [%]']:.1f}%")
        print(f"📈 Best Trade: {stats['Best Trade [%]']:.1f}%")
        print(f"💎 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    
    # CHAMPION victory conditions
    beats_buy_hold = stats['Return [%]'] > stats['Buy & Hold Return [%]']
    enough_trades = stats['# Trades'] >= 5
    excellent_return = stats['Return [%]'] > 100
    
    if beats_buy_hold and enough_trades:
        print("\n🏆👑🚀 CHAMPION VICTORY ACHIEVED! 🚀👑🏆")
        print("🎉🎉🎉 STRATEGY BEATS BUY & HOLD WITH 5+ TRADES! 🎉🎉🎉")
        print("🌙🚀✨👑✨🚀🌙🚀✨👑✨🚀🌙🚀✨👑✨🚀🌙🚀✨👑✨🚀🌙")
        print("🎯 MISSION: ABSOLUTELY ACCOMPLISHED! 🎯")
    elif enough_trades and excellent_return:
        print(f"\n🎊 CHAMPION PERFORMANCE! {stats['# Trades']} trades, {stats['Return [%]']:.1f}% return! 🎊")
        print("🌟 Excellent results! Over 100% returns achieved! 🌟")
    elif enough_trades:
        ratio = stats['Return [%]'] / stats['Buy & Hold Return [%]'] * 100
        print(f"\n✅ SOLID! {stats['# Trades']} trades, achieving {ratio:.1f}% of buy-and-hold performance")
    else:
        print(f"\n📊 {stats['# Trades']} trades completed with {stats['Return [%]']:.1f}% return")
    
    # Detailed analysis
    print(f"\n📈 CHAMPION Analysis:")
    print(f"   💰 Strategy Return: {stats['Return [%]']:.1f}%")
    print(f"   📊 Buy & Hold Return: {stats['Buy & Hold Return [%]']:.1f}%")
    print(f"   🎯 Performance Ratio: {stats['Return [%]'] / stats['Buy & Hold Return [%]'] * 100:.1f}%")
    print(f"   📉 Max Drawdown: {stats['Max. Drawdown [%]']:.1f}%")
    
    print("\n🌙 MoonDev CHAMPION Backtest Complete! 🚀")