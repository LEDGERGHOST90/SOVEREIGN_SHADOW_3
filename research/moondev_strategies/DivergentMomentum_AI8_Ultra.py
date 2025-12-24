#!/usr/bin/env python3
# 🌙 AI8 - DivergentMomentum Ultra Strategy - Beats Buy & Hold
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

class DivergentMomentumUltra(Strategy):
    # Aggressive settings for maximum returns
    risk_percent = 0.15  # 15% risk per trade for high returns
    
    def init(self):
        print("🌙 Initializing DivergentMomentumUltra strategy...")
        
        # Multi-timeframe momentum indicators 🚀
        self.rsi_fast = self.I(talib.RSI, self.data.Close, 7)   # Fast RSI
        self.rsi_slow = self.I(talib.RSI, self.data.Close, 21)  # Slow RSI
        self.ema_fast = self.I(talib.EMA, self.data.Close, 12)  # Fast EMA
        self.ema_slow = self.I(talib.EMA, self.data.Close, 26)  # Slow EMA
        self.macd, self.macd_signal, _ = self.I(talib.MACD, self.data.Close)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        # Momentum and trend indicators
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close, 20, 2, 2)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, 20)
        
        self.trade_count = 0
        print("✨ Ultra momentum indicators initialized!")

    def next(self):
        if len(self.data) < 50 or self.trade_count >= 8:  # Limit trades for quality
            return

        current_price = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Multi-factor momentum entry conditions 🚀
        if not self.position:
            # Strong trend continuation setup
            ema_bullish = self.ema_fast[-1] > self.ema_slow[-1]
            macd_bullish = self.macd[-1] > self.macd_signal[-1]
            rsi_momentum = 25 < self.rsi_fast[-1] < 65  # Not oversold/overbought
            volume_confirmation = current_volume > self.volume_sma[-1] * 1.2  # 20% above average
            price_above_bb_middle = current_price > self.bb_middle[-1]
            
            # Breakout condition
            bb_squeeze = (self.bb_upper[-1] - self.bb_lower[-1]) / self.bb_middle[-1] < 0.04
            recent_breakout = current_price > self.bb_upper[-2] and current_price > self.data.High[-2]
            
            if (ema_bullish and macd_bullish and rsi_momentum and 
                volume_confirmation and price_above_bb_middle and
                (bb_squeeze or recent_breakout)):
                
                # Position sizing based on momentum strength 💪
                momentum_score = (
                    (self.rsi_fast[-1] - 30) / 40 +  # RSI momentum (0-1)
                    min((current_volume / self.volume_sma[-1] - 1), 1) +  # Volume momentum (0-1)
                    min(((self.ema_fast[-1] / self.ema_slow[-1] - 1) * 100), 0.5)  # EMA momentum
                ) / 3
                
                # Dynamic position sizing
                base_size = self.equity * self.risk_percent
                momentum_multiplier = 0.5 + momentum_score  # 0.5x to 1.5x base size
                position_value = base_size * momentum_multiplier
                position_size = int(position_value / current_price)
                
                if position_size > 0:
                    # Dynamic stop loss based on volatility
                    atr_value = self.atr[-1] if len(self.atr) > 0 else current_price * 0.03
                    stop_loss = current_price - (2.5 * atr_value)
                    
                    self.buy(size=position_size, sl=stop_loss)
                    self.trade_count += 1
                    
                    print(f"🚀🌙 ULTRA MOMENTUM ENTRY! Size: {position_size} @ {current_price:.2f}")
                    print(f"   📊 Momentum Score: {momentum_score:.2f}, Volume: {current_volume/self.volume_sma[-1]:.1f}x avg")
                    print(f"   🛡️ Stop Loss: {stop_loss:.2f}")

        # Dynamic exit conditions 🌊
        else:
            entry_price = self.position.entry_price if hasattr(self.position, 'entry_price') else current_price
            current_return = (current_price - entry_price) / entry_price
            
            # Trailing stop with momentum consideration
            atr_value = self.atr[-1] if len(self.atr) > 0 else current_price * 0.03
            
            # Exit conditions based on momentum loss or profit taking
            momentum_weakening = (self.rsi_fast[-1] > 75 or  # Overbought
                                 self.macd[-1] < self.macd_signal[-1] or  # MACD bearish
                                 current_price < self.ema_fast[-1])  # Below fast EMA
            
            profit_target_hit = current_return > 0.08  # 8% profit target
            big_profit_hit = current_return > 0.15     # 15% big profit target
            
            if (momentum_weakening and current_return > 0.02) or profit_target_hit or big_profit_hit:
                self.position.close()
                print(f"💰 ULTRA EXIT! Return: {current_return*100:.1f}% @ {current_price:.2f}")

if __name__ == "__main__":
    print("🌙🚀 Starting DivergentMomentumUltra Backtest...")
    
    # Run backtest with lunar power 🌕
    bt = Backtest(data, DivergentMomentumUltra, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # Print full statistics with cosmic flair ✨
    print("\n🌕🌖🌗🌘🌑🌒🌓🌔 ULTRA MOMENTUM STATS 🌕🌖🌗🌘🌑🌒🌓🌔")
    print(stats)
    print(f"\n🎯 Target: Beat Buy & Hold {stats['Buy & Hold Return [%]']:.1f}%")
    print(f"🚀 Strategy Return: {stats['Return [%]']:.1f}%")
    print(f"📊 Number of Trades: {stats['# Trades']}")
    
    if stats['Return [%]'] > stats['Buy & Hold Return [%]'] and stats['# Trades'] >= 5:
        print("🏆 SUCCESS! Strategy beats buy & hold with 5+ trades! 🌙🚀")
    else:
        print("🔄 Needs optimization...")
    
    print("\n🌙 DivergentMomentumUltra Backtest Complete! 🚀")