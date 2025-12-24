#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - BACKTEST RUNNER
Quick backtest runner with basic strategies

Usage:
    python3 backtesting/run_backtest.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting.backtest_engine import BacktestEngine, save_backtest_results
from backtesting.data_loader import DataLoader, calculate_technical_indicators


class MACrossoverStrategy:
    """Simple Moving Average Crossover"""
    name = "ma_crossover_50_200"

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        df = calculate_technical_indicators(data)
        signals = pd.Series(0, index=data.index)

        # Long when 50 SMA > 200 SMA
        signals[df['sma_50'] > df['sma_200']] = 1
        # Short when 50 SMA < 200 SMA
        signals[df['sma_50'] < df['sma_200']] = -1

        return signals


class RSIMeanReversionStrategy:
    """RSI Mean Reversion - buy oversold, sell overbought"""
    name = "rsi_mean_reversion"

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        df = calculate_technical_indicators(data)
        signals = pd.Series(0, index=data.index)

        # Long when RSI < 30 (oversold)
        signals[df['rsi'] < 30] = 1
        # Exit when RSI > 50
        signals[(df['rsi'] > 50) & (signals.shift(1) == 1)] = 0
        # Short when RSI > 70 (overbought)
        signals[df['rsi'] > 70] = -1
        # Exit when RSI < 50
        signals[(df['rsi'] < 50) & (signals.shift(1) == -1)] = 0

        return signals


class MACDMomentumStrategy:
    """MACD Momentum Strategy"""
    name = "macd_momentum"

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        df = calculate_technical_indicators(data)
        signals = pd.Series(0, index=data.index)

        # Long when MACD crosses above signal
        signals[(df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))] = 1
        # Keep long while MACD > signal
        signals[df['macd'] > df['macd_signal']] = 1
        # Short when MACD crosses below signal
        signals[(df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))] = -1
        signals[df['macd'] < df['macd_signal']] = -1

        return signals


class BollingerBandStrategy:
    """Bollinger Band Mean Reversion"""
    name = "bollinger_bands"

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        df = calculate_technical_indicators(data)
        signals = pd.Series(0, index=data.index)

        # Long when price touches lower band
        signals[df['close'] < df['bb_lower']] = 1
        # Exit at middle band
        signals[(df['close'] > df['bb_middle']) & (signals.shift(1) == 1)] = 0
        # Short when price touches upper band
        signals[df['close'] > df['bb_upper']] = -1
        # Exit at middle band
        signals[(df['close'] < df['bb_middle']) & (signals.shift(1) == -1)] = 0

        return signals


def run_all_backtests():
    """Run backtests on all strategies"""
    print("\n" + "="*80)
    print("🧪 SOVEREIGN SHADOW II - BACKTEST RUNNER")
    print("="*80)

    # Initialize
    engine = BacktestEngine(initial_capital=10000)
    loader = DataLoader(data_dir="backtest_data")

    # Load datasets (use shorter period to avoid overflow)
    datasets = loader.load_all_datasets(
        assets=['BTC', 'ETH', 'SOL', 'XRP'],
        timeframes=['4h', '1d'],  # Skip 15m due to overflow issues
        use_synthetic=True
    )

    # Define strategies to test
    strategies = [
        MACrossoverStrategy(),
        RSIMeanReversionStrategy(),
        MACDMomentumStrategy(),
        BollingerBandStrategy(),
    ]

    all_results = []

    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Testing: {strategy.name}")
        print('='*60)

        results = engine.run_multi_dataset_backtest(strategy, datasets)
        all_results.extend(results)

        # Evaluate
        evaluation = engine.evaluate_strategy(results)

        print(f"\n📊 EVALUATION: {strategy.name}")
        print(f"   Approved: {'✅ YES' if evaluation['approved'] else '❌ NO'}")
        print(f"   Reason: {evaluation['reason']}")
        print(f"   Profitable: {evaluation['profitable_datasets']}/{evaluation['total_datasets']} datasets")
        print(f"   Avg Return: {evaluation['avg_return']*100:+.2f}%")
        print(f"   Avg Sharpe: {evaluation['avg_sharpe']:.2f}")
        print(f"   Avg Win Rate: {evaluation['avg_win_rate']*100:.1f}%")
        print(f"   Total Trades: {evaluation['total_trades']}")

    # Save results
    save_backtest_results(all_results, output_dir="backtest_results")

    # Summary
    print("\n" + "="*80)
    print("📈 BACKTEST SUMMARY")
    print("="*80)

    for strategy in strategies:
        strategy_results = [r for r in all_results if r.strategy_name == strategy.name]
        if strategy_results:
            avg_return = np.mean([r.total_return for r in strategy_results])
            win_count = len([r for r in strategy_results if r.total_return > 0])
            print(f"{strategy.name}: {avg_return*100:+.2f}% avg return, {win_count}/{len(strategy_results)} profitable")

    print("="*80)
    print("✅ Results saved to backtest_results/")
    print("="*80 + "\n")

    return all_results


if __name__ == "__main__":
    run_all_backtests()
