#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌙 AI7 - MomentumBreakout Strategy Backtest
Moon Dev AI Trading Strategy Implementation
Designed to beat buy and hold with trend following and momentum
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

class MomentumBreakout(Strategy):
    # Optimized parameters for momentum trading
    ma_fast = 10
    ma_slow = 30
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    volume_ma = 20
    risk_percent = 0.02
    
    def init(self):
        # Moving averages for trend detection
        def _sma_fast(close):
            result = ta.sma(pd.Series(close), length=self.ma_fast)
            if result is not None:
                return result.values
            else:
                return pd.Series(close).rolling(self.ma_fast).mean().values
                
        def _sma_slow(close):
            result = ta.sma(pd.Series(close), length=self.ma_slow)
            if result is not None:
                return result.values
            else:
                return pd.Series(close).rolling(self.ma_slow).mean().values
        
        self.ma_fast_line = self.I(_sma_fast, self.data.Close, name=f'SMA{self.ma_fast}')
        self.ma_slow_line = self.I(_sma_slow, self.data.Close, name=f'SMA{self.ma_slow}')
        
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
        
        # Volume moving average for confirmation
        def _volume_sma(volume):
            result = ta.sma(pd.Series(volume), length=self.volume_ma)
            if result is not None:
                return result.values
            else:
                return pd.Series(volume).rolling(self.volume_ma).mean().values
        
        self.volume_ma_line = self.I(_volume_sma, self.data.Volume, name=f'Volume_SMA{self.volume_ma}')
        
        # Price momentum indicators
        def _price_momentum(close, period=5):
            return (pd.Series(close) / pd.Series(close).shift(period) - 1) * 100
        
        self.momentum = self.I(_price_momentum, self.data.Close, 5, name='Momentum_5')

    def next(self):
        # Skip if not enough data
        if len(self.data.Close) < max(self.ma_slow, self.volume_ma, self.rsi_period):
            return
        
        # Current values
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Trend signals
        bullish_ma_cross = crossover(self.ma_fast_line, self.ma_slow_line)
        bearish_ma_cross = crossover(self.ma_slow_line, self.ma_fast_line)
        
        # Trend confirmation
        uptrend = self.ma_fast_line[-1] > self.ma_slow_line[-1]
        downtrend = self.ma_fast_line[-1] < self.ma_slow_line[-1]
        
        # Volume confirmation
        high_volume = volume > self.volume_ma_line[-1] * 1.2
        
        # Momentum confirmation
        strong_momentum = abs(self.momentum[-1]) > 2.0
        
        if not self.position:
            # LONG Entry Conditions:
            # 1. Golden cross (fast MA crosses above slow MA) OR strong uptrend
            # 2. RSI not overbought (< 70)
            # 3. Strong momentum
            # 4. High volume confirmation
            if ((bullish_ma_cross or (uptrend and price > self.ma_fast_line[-1])) and
                self.rsi[-1] < self.rsi_overbought and
                strong_momentum and self.momentum[-1] > 0 and
                high_volume):
                
                # Position sizing based on risk management
                entry_price = price
                sl_price = self.ma_slow_line[-1] * 0.95  # Stop below slow MA
                tp_price = entry_price * 1.15  # 15% profit target
                
                # Ensure valid order structure
                if sl_price >= entry_price:
                    sl_price = entry_price * 0.97  # 3% stop loss
                
                if tp_price <= entry_price:
                    tp_price = entry_price * 1.10  # 10% profit target
                
                risk_amount = self.equity * self.risk_percent
                risk_per_share = entry_price - sl_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl_price, tp=tp_price)
                        print(f"🚀 LONG: {entry_price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f} | Size: {position_size}")
                        
            # SHORT Entry Conditions:
            # 1. Death cross (fast MA crosses below slow MA) OR strong downtrend  
            # 2. RSI not oversold (> 30)
            # 3. Strong negative momentum
            # 4. High volume confirmation
            elif ((bearish_ma_cross or (downtrend and price < self.ma_fast_line[-1])) and
                  self.rsi[-1] > self.rsi_oversold and
                  strong_momentum and self.momentum[-1] < 0 and
                  high_volume):
                
                # Position sizing based on risk management
                entry_price = price
                sl_price = self.ma_slow_line[-1] * 1.05  # Stop above slow MA
                tp_price = entry_price * 0.85  # 15% profit target
                
                # Ensure valid order structure
                if sl_price <= entry_price:
                    sl_price = entry_price * 1.03  # 3% stop loss
                
                if tp_price >= entry_price:
                    tp_price = entry_price * 0.90  # 10% profit target
                
                risk_amount = self.equity * self.risk_percent
                risk_per_share = sl_price - entry_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.sell(size=position_size, sl=sl_price, tp=tp_price)
                        print(f"🐻 SHORT: {entry_price:.2f} | SL: {sl_price:.2f} | TP: {tp_price:.2f} | Size: {position_size}")

# 🌙🚀 Execute Backtest
print("🌙✨ Starting MomentumBreakout Backtest...")
bt = Backtest(data, MomentumBreakout, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n🌙🎯 BACKTEST RESULTS - MomentumBreakout Strategy:")
print("=" * 60)
print(stats)
print(f"\n🌙💎 Buy & Hold Return: {stats['Buy & Hold Return [%]']:.2f}%")
print(f"🌙🚀 Strategy Return: {stats['Return [%]']:.2f}%")
print(f"🌙📊 Number of Trades: {stats['# Trades']}")

if stats['Return [%]'] > stats['Buy & Hold Return [%]'] and stats['# Trades'] > 5:
    print("🌙✅ SUCCESS: Strategy beats buy & hold with sufficient trades!")
else:
    print("🌙❌ Strategy needs optimization...")

print("\n🌙📊 Strategy Details:")
print(stats._strategy)
print("=" * 60)