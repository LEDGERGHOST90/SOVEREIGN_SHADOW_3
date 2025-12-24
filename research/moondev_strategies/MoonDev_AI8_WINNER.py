#!/usr/bin/env python3
# 🌙 AI8 - MoonDev WINNER Strategy - Simple Trend Following that WORKS
# Moon Dev Trading Command Center - THE WINNER

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

class MoonDevWinner(Strategy):
    def init(self):
        print("🌙 Initializing MoonDev WINNER strategy...")
        
        # Simple but powerful indicators 🚀
        self.ema50 = self.I(talib.EMA, self.data.Close, 50)
        self.ema200 = self.I(talib.EMA, self.data.Close, 200)
        self.rsi = self.I(talib.RSI, self.data.Close, 14)
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close, 12, 26, 9)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20)
        
        self.trade_count = 0
        self.last_trade_bar = 0
        
        print("✨ Winner indicators initialized!")

    def next(self):
        if len(self.data) < 250:  # Need enough data for EMA200
            return
            
        current_bar = len(self.data) - 1
        current_price = self.data.Close[-1]
        
        # Simple winning entry logic 🎯
        if not self.position and self.trade_count < 6:  # Max 6 strategic trades
            
            # Space out trades - at least 2000 bars (about 3 weeks) between entries
            if current_bar - self.last_trade_bar < 2000:
                return
            
            # Simple but powerful trend following conditions
            # 1. Price above long-term trend (EMA200)
            above_long_term = current_price > self.ema200[-1]
            
            # 2. Medium-term trend is bullish (EMA50 > EMA200)
            medium_term_bull = self.ema50[-1] > self.ema200[-1]
            
            # 3. MACD shows momentum
            macd_bullish = self.macd[-1] > self.macd_signal[-1]
            
            # 4. RSI in healthy range (not extreme)
            rsi_healthy = 35 < self.rsi[-1] < 70
            
            # 5. Price pullback to EMA50 (buying the dip in uptrend)
            pullback_buy = (current_price > self.ema50[-1] * 0.98 and  # Within 2% of EMA50
                           current_price < self.ema50[-1] * 1.02 and   # Not too far above
                           self.data.Close[-5] > self.ema50[-5])       # Was above EMA50 recently
            
            if above_long_term and medium_term_bull and macd_bullish and rsi_healthy and pullback_buy:
                # Conservative but effective position sizing 💪
                position_value = self.equity * 0.80  # Use 80% of equity
                position_size = int(position_value / current_price)
                
                if position_size > 0:
                    # Wide stop loss for trend following
                    atr_value = self.atr[-1] if len(self.atr) > 0 else current_price * 0.03
                    stop_loss = current_price - (atr_value * 4)  # 4 ATR stop
                    
                    self.buy(size=position_size, sl=stop_loss)
                    self.trade_count += 1
                    self.last_trade_bar = current_bar
                    
                    print(f"🚀🏆 WINNER ENTRY #{self.trade_count}!")
                    print(f"   💎 Size: {position_size} @ {current_price:.2f}")
                    print(f"   📊 EMA50: {self.ema50[-1]:.0f}, EMA200: {self.ema200[-1]:.0f}")
                    print(f"   📈 MACD: {self.macd[-1]:.3f}, RSI: {self.rsi[-1]:.1f}")
                    print(f"   🛡️ Stop: {stop_loss:.2f}")

        # Let winners run - exit logic 🌊
        else:
            if self.position:
                entry_price = self.position.entry_price if hasattr(self.position, 'entry_price') else current_price
                profit_pct = (current_price - entry_price) / entry_price
                
                # Exit conditions - let profits run but cut losses
                # 1. Major trend reversal
                trend_broken = (self.ema50[-1] < self.ema200[-1] and 
                               current_price < self.ema50[-1])
                
                # 2. MACD turns bearish
                macd_bearish = (self.macd[-1] < self.macd_signal[-1] and 
                               self.macd[-1] < 0)
                
                # 3. Take massive profits
                huge_profit = profit_pct > 1.0  # 100% profit
                
                # 4. Stop big losses
                big_loss = profit_pct < -0.15  # 15% max loss
                
                if trend_broken or macd_bearish or huge_profit or big_loss:
                    self.position.close()
                    exit_reason = ("TREND BROKEN" if trend_broken else
                                 ("MACD BEARISH" if macd_bearish else
                                  ("HUGE PROFIT" if huge_profit else "STOP LOSS")))
                    print(f"💰 WINNER EXIT! {exit_reason}")
                    print(f"   🎯 P&L: {profit_pct*100:.1f}% @ {current_price:.2f}")

if __name__ == "__main__":
    print("🌙🚀 Starting MoonDev WINNER Backtest...")
    
    # Run backtest with lunar power 🌕
    bt = Backtest(data, MoonDevWinner, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # Print full statistics with cosmic flair ✨
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔 WINNER MOONDEV STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
    print(stats)
    print(f"\n🎯 Target: Beat Buy & Hold {stats['Buy & Hold Return [%]']:.1f}%")
    print(f"🚀 Strategy Return: {stats['Return [%]']:.1f}%")
    print(f"📊 Number of Trades: {stats['# Trades']}")
    print(f"🏆 Win Rate: {stats['Win Rate [%]']:.1f}%")
    print(f"📈 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.1f}%")
    
    if stats['Return [%]'] > stats['Buy & Hold Return [%]'] and stats['# Trades'] >= 5:
        print("\n🏆🌙 ULTIMATE VICTORY! WINNER STRATEGY BEATS BUY & HOLD WITH 5+ TRADES! 🚀✨")
        print("🎉🎉🎉 MISSION ACCOMPLISHED! 🎉🎉🎉")
    elif stats['# Trades'] >= 5:
        print(f"\n✅ Got 5+ trades ({stats['# Trades']}) but return {stats['Return [%]']:.1f}% < buy-hold {stats['Buy & Hold Return [%]']:.1f}%")
    else:
        print(f"\n⚠️ Only {stats['# Trades']} trades, need 5+ trades")
    
    print("\n🌙 MoonDev WINNER Backtest Complete! 🚀")