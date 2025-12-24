#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌙 AI7 - OptimalTrend Strategy Backtest
Moon Dev AI Trading Strategy Implementation
Optimized trend following designed to beat buy and hold
"""

import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

# Load and preprocess data
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

class OptimalTrend(Strategy):
    # Optimized parameters based on Bitcoin's characteristics
    ma_fast = 12
    ma_slow = 26
    rsi_period = 14
    position_size_pct = 0.85
    stop_loss_pct = 0.08  # 8% stop loss
    take_profit_pct = 0.25  # 25% take profit
    
    def init(self):
        # Exponential moving averages for faster response
        def _ema(close, period):
            result = ta.ema(pd.Series(close), length=period)
            if result is not None:
                return result.values
            else:
                return pd.Series(close).ewm(span=period).mean().values
        
        self.ema_fast = self.I(_ema, self.data.Close, self.ma_fast, name=f'EMA{self.ma_fast}')
        self.ema_slow = self.I(_ema, self.data.Close, self.ma_slow, name=f'EMA{self.ma_slow}')
        
        # RSI for momentum confirmation
        def _rsi(close, period):
            result = ta.rsi(pd.Series(close), length=period)
            if result is not None:
                return result.values
            else:
                delta = pd.Series(close).diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return (100 - (100 / (1 + rs))).values
        
        self.rsi = self.I(_rsi, self.data.Close, self.rsi_period, name='RSI')
        
        # MACD for trend confirmation
        def _macd(close):
            result = ta.macd(pd.Series(close), fast=12, slow=26, signal=9)
            if result is not None and len(result.columns) > 0:
                return result.iloc[:, 0].values  # MACD line
            else:
                ema_fast = pd.Series(close).ewm(span=12).mean()
                ema_slow = pd.Series(close).ewm(span=26).mean()
                return (ema_fast - ema_slow).values
        
        self.macd = self.I(_macd, self.data.Close, name='MACD')

    def next(self):
        # Skip if not enough data
        if len(self.data.Close) < max(self.ma_slow, self.rsi_period):
            return
        
        price = self.data.Close[-1]
        
        # Trend signals
        bullish_trend = self.ema_fast[-1] > self.ema_slow[-1]
        bearish_trend = self.ema_fast[-1] < self.ema_slow[-1]
        
        # Golden/Death cross signals
        golden_cross = crossover(self.ema_fast, self.ema_slow)
        death_cross = crossover(self.ema_slow, self.ema_fast)
        
        # Momentum conditions
        momentum_bullish = self.rsi[-1] > 50 and self.macd[-1] > 0
        momentum_bearish = self.rsi[-1] < 50 and self.macd[-1] < 0
        
        # Strong momentum conditions for better entries
        strong_bullish = self.rsi[-1] > 60 and self.macd[-1] > self.macd[-2]
        strong_bearish = self.rsi[-1] < 40 and self.macd[-1] < self.macd[-2]
        
        if not self.position:
            # LONG Entry: Golden cross OR strong bullish momentum
            if (golden_cross and momentum_bullish) or (bullish_trend and strong_bullish):
                position_size = int((self.equity * self.position_size_pct) / price)
                
                if position_size > 0:
                    # Calculate stop loss and take profit
                    sl_price = price * (1 - self.stop_loss_pct)
                    tp_price = price * (1 + self.take_profit_pct)
                    
                    self.buy(size=position_size, sl=sl_price, tp=tp_price)
                    
                    if golden_cross:
                        print(f"🚀⚡ GOLDEN CROSS: {price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
                    else:
                        print(f"🚀💪 STRONG BULL: {price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
                        
            # SHORT Entry: Death cross OR strong bearish momentum
            elif (death_cross and momentum_bearish) or (bearish_trend and strong_bearish):
                position_size = int((self.equity * self.position_size_pct) / price)
                
                if position_size > 0:
                    # Calculate stop loss and take profit for short
                    sl_price = price * (1 + self.stop_loss_pct)
                    tp_price = price * (1 - self.take_profit_pct)
                    
                    self.sell(size=position_size, sl=sl_price, tp=tp_price)
                    
                    if death_cross:
                        print(f"🐻⚡ DEATH CROSS: {price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")
                    else:
                        print(f"🐻💪 STRONG BEAR: {price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f}")

# 🌙🚀 Execute Backtest
print("🌙✨ Starting OptimalTrend Backtest...")
bt = Backtest(data, OptimalTrend, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n🌙🎯 BACKTEST RESULTS - OptimalTrend Strategy:")
print("=" * 60)
print(stats)
print(f"\n🌙💎 Buy & Hold Return: {stats['Buy & Hold Return [%]']:.2f}%")
print(f"🌙🚀 Strategy Return: {stats['Return [%]']:.2f}%")
print(f"🌙📊 Number of Trades: {stats['# Trades']}")

if stats['Return [%]'] > stats['Buy & Hold Return [%]'] and stats['# Trades'] > 5:
    print("🌙✅ SUCCESS: Strategy beats buy & hold with sufficient trades!")
    print("DONE")
    print("🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀✨🌙🚀")
else:
    print("🌙❌ Strategy needs more optimization...")
    print(f"🌙🔧 Beat Buy&Hold: {'✅' if stats['Return [%]'] > stats['Buy & Hold Return [%]'] else '❌'}")
    print(f"🌙🔧 Enough Trades: {'✅' if stats['# Trades'] > 5 else '❌'}")

print("\n🌙📊 Strategy Details:")
print(stats._strategy)
print("=" * 60)