#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - BACKTESTING ENGINE
Professional backtesting system for RBI methodology

Tests strategies across multiple:
- Assets (BTC, ETH, SOL, XRP)
- Timeframes (1h, 4h, 1d, 1w)
- Market conditions (bull, bear, sideways)

Philosophy: "Test on 20+ datasets. Look for consistency, not outliers."

Author: SovereignShadow Trading System
Created: 2025-11-24
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class BacktestResult:
    """Results from a single backtest run"""
    strategy_name: str
    asset: str
    timeframe: str

    # Performance metrics
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float

    # Exposure
    exposure_time: float  # % of time in trades

    # Risk metrics
    expectancy: float  # Expected value per trade

    # Comparison
    buy_hold_return: float

    # Metadata
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float


class BacktestEngine:
    """
    Professional backtesting engine

    Follows Munddev's approach:
    - Test on multiple datasets
    - Calculate professional metrics
    - Identify robust strategies
    """

    def __init__(self, initial_capital: float = 10000):
        """
        Initialize backtest engine

        Args:
            initial_capital: Starting capital for backtests
        """
        self.initial_capital = initial_capital

        print("🧪 BACKTEST ENGINE initialized")
        print(f"   Initial Capital: ${initial_capital:,.2f}")

    def run_backtest(
        self,
        strategy,
        data: pd.DataFrame,
        asset: str,
        timeframe: str
    ) -> BacktestResult:
        """
        Run backtest for a strategy on given data

        Args:
            strategy: Strategy object with generate_signals() method
            data: OHLCV DataFrame
            asset: Asset name (BTC, ETH, etc.)
            timeframe: Timeframe (1h, 4h, 1d, 1w)

        Returns:
            BacktestResult object
        """
        # Generate signals
        signals = strategy.generate_signals(data)

        # Simulate trading
        trades = self._simulate_trading(data, signals)

        # Calculate metrics
        metrics = self._calculate_metrics(trades, data)

        # Create result
        result = BacktestResult(
            strategy_name=strategy.name,
            asset=asset,
            timeframe=timeframe,
            total_return=metrics['total_return'],
            sharpe_ratio=metrics['sharpe_ratio'],
            max_drawdown=metrics['max_drawdown'],
            win_rate=metrics['win_rate'],
            profit_factor=metrics['profit_factor'],
            total_trades=metrics['total_trades'],
            winning_trades=metrics['winning_trades'],
            losing_trades=metrics['losing_trades'],
            avg_win=metrics['avg_win'],
            avg_loss=metrics['avg_loss'],
            exposure_time=metrics['exposure_time'],
            expectancy=metrics['expectancy'],
            buy_hold_return=metrics['buy_hold_return'],
            start_date=data.index[0].isoformat(),
            end_date=data.index[-1].isoformat(),
            initial_capital=self.initial_capital,
            final_capital=metrics['final_capital']
        )

        return result

    def _simulate_trading(
        self,
        data: pd.DataFrame,
        signals: pd.Series
    ) -> List[Dict[str, Any]]:
        """
        Simulate trading based on signals

        Args:
            data: OHLCV DataFrame
            signals: Series with 1 (long), -1 (short), 0 (neutral)

        Returns:
            List of trade dictionaries
        """
        trades = []
        position = None
        capital = self.initial_capital

        for i in range(len(data)):
            current_signal = signals.iloc[i]
            current_price = data['close'].iloc[i]

            # Entry logic
            if position is None and current_signal != 0:
                # Enter position
                position = {
                    'entry_price': current_price,
                    'entry_date': data.index[i],
                    'direction': 'long' if current_signal == 1 else 'short',
                    'size': capital * 0.95  # Use 95% of capital
                }

            # Exit logic
            elif position is not None and current_signal == 0:
                # Exit position
                exit_price = current_price

                if position['direction'] == 'long':
                    pnl = (exit_price - position['entry_price']) / position['entry_price']
                else:  # short
                    pnl = (position['entry_price'] - exit_price) / position['entry_price']

                pnl_dollars = position['size'] * pnl
                capital += pnl_dollars

                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': data.index[i],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'direction': position['direction'],
                    'pnl_pct': pnl,
                    'pnl_dollars': pnl_dollars,
                    'capital_after': capital
                })

                position = None

        # Close any open position at end
        if position is not None:
            exit_price = data['close'].iloc[-1]

            if position['direction'] == 'long':
                pnl = (exit_price - position['entry_price']) / position['entry_price']
            else:
                pnl = (position['entry_price'] - exit_price) / position['entry_price']

            pnl_dollars = position['size'] * pnl
            capital += pnl_dollars

            trades.append({
                'entry_date': position['entry_date'],
                'exit_date': data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'direction': position['direction'],
                'pnl_pct': pnl,
                'pnl_dollars': pnl_dollars,
                'capital_after': capital
            })

        return trades

    def _calculate_metrics(
        self,
        trades: List[Dict[str, Any]],
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate performance metrics

        Args:
            trades: List of completed trades
            data: OHLCV DataFrame

        Returns:
            Dict of metrics
        """
        if not trades:
            return self._empty_metrics(data)

        # Basic stats
        total_trades = len(trades)
        winners = [t for t in trades if t['pnl_dollars'] > 0]
        losers = [t for t in trades if t['pnl_dollars'] <= 0]

        winning_trades = len(winners)
        losing_trades = len(losers)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # P&L
        total_pnl = sum(t['pnl_dollars'] for t in trades)
        final_capital = self.initial_capital + total_pnl
        total_return = (final_capital - self.initial_capital) / self.initial_capital

        # Win/Loss averages
        avg_win = np.mean([t['pnl_dollars'] for t in winners]) if winners else 0
        avg_loss = np.mean([t['pnl_dollars'] for t in losers]) if losers else 0

        # Profit factor
        total_wins = sum(t['pnl_dollars'] for t in winners)
        total_losses = abs(sum(t['pnl_dollars'] for t in losers))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Expectancy
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        # Exposure time
        total_time = len(data)
        time_in_trades = sum((t['exit_date'] - t['entry_date']).total_seconds() for t in trades)
        total_time_seconds = (data.index[-1] - data.index[0]).total_seconds()
        exposure_time = (time_in_trades / total_time_seconds) if total_time_seconds > 0 else 0

        # Sharpe ratio (simplified)
        if len(trades) >= 2:
            returns = [t['pnl_pct'] for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # Max drawdown
        equity_curve = [self.initial_capital]
        for trade in trades:
            equity_curve.append(trade['capital_after'])

        max_drawdown = self._calculate_max_drawdown(equity_curve)

        # Buy and hold return
        buy_hold_return = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'final_capital': final_capital,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'exposure_time': exposure_time,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'buy_hold_return': buy_hold_return
        }

    def _empty_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Return empty metrics when no trades"""
        buy_hold_return = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]

        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_return': 0.0,
            'final_capital': self.initial_capital,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
            'expectancy': 0.0,
            'exposure_time': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'buy_hold_return': buy_hold_return
        }

    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(equity_curve) < 2:
            return 0.0

        peak = equity_curve[0]
        max_dd = 0.0

        for value in equity_curve:
            if value > peak:
                peak = value

            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def run_multi_dataset_backtest(
        self,
        strategy,
        datasets: Dict[str, pd.DataFrame]
    ) -> List[BacktestResult]:
        """
        Run backtest across multiple datasets

        Args:
            strategy: Strategy object
            datasets: Dict of {(asset, timeframe): DataFrame}

        Returns:
            List of BacktestResult objects
        """
        results = []

        print(f"\n🧪 Running multi-dataset backtest: {strategy.name}")
        print(f"   Testing on {len(datasets)} datasets...")

        for (asset, timeframe), data in datasets.items():
            try:
                result = self.run_backtest(strategy, data, asset, timeframe)
                results.append(result)

                # Print progress
                status = "✅" if result.total_return > 0 else "❌"
                print(f"   {status} {asset}-{timeframe}: {result.total_return*100:+.1f}% ({result.total_trades} trades)")

            except Exception as e:
                print(f"   ❌ {asset}-{timeframe}: Error - {str(e)}")

        return results

    def evaluate_strategy(
        self,
        results: List[BacktestResult],
        min_positive_rate: float = 0.60  # 60% of datasets should be profitable
    ) -> Dict[str, Any]:
        """
        Evaluate strategy across all results

        Args:
            results: List of BacktestResult objects
            min_positive_rate: Minimum % of profitable datasets

        Returns:
            Dict with evaluation
        """
        if not results:
            return {'approved': False, 'reason': 'No results'}

        # Count positive results
        positive = [r for r in results if r.total_return > 0]
        positive_rate = len(positive) / len(results)

        # Average metrics
        avg_return = np.mean([r.total_return for r in results])
        avg_sharpe = np.mean([r.sharpe_ratio for r in results])
        avg_win_rate = np.mean([r.win_rate for r in results])
        avg_expectancy = np.mean([r.expectancy for r in results])

        # Check if trades happened
        total_trades = sum(r.total_trades for r in results)
        avg_trades_per_dataset = total_trades / len(results)

        # Evaluation criteria
        approved = (
            positive_rate >= min_positive_rate and
            avg_expectancy > 0 and
            avg_trades_per_dataset >= 5 and  # At least 5 trades per dataset
            avg_win_rate > 0.35  # At least 35% win rate
        )

        # Determine reason
        if not approved:
            if positive_rate < min_positive_rate:
                reason = f"Only {positive_rate*100:.0f}% profitable (need {min_positive_rate*100:.0f}%)"
            elif avg_expectancy <= 0:
                reason = f"Negative expectancy: {avg_expectancy:.4f}"
            elif avg_trades_per_dataset < 5:
                reason = f"Too few trades: {avg_trades_per_dataset:.1f} per dataset"
            elif avg_win_rate <= 0.35:
                reason = f"Low win rate: {avg_win_rate*100:.1f}%"
            else:
                reason = "Did not meet criteria"
        else:
            reason = f"✅ Approved: {positive_rate*100:.0f}% profitable, expectancy={avg_expectancy:.4f}"

        return {
            'approved': approved,
            'reason': reason,
            'positive_rate': positive_rate,
            'avg_return': avg_return,
            'avg_sharpe': avg_sharpe,
            'avg_win_rate': avg_win_rate,
            'avg_expectancy': avg_expectancy,
            'total_datasets': len(results),
            'profitable_datasets': len(positive),
            'total_trades': total_trades
        }


def save_backtest_results(
    results: List[BacktestResult],
    output_dir: str = "backtest_results"
):
    """Save backtest results to JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group by strategy
    by_strategy = {}
    for result in results:
        if result.strategy_name not in by_strategy:
            by_strategy[result.strategy_name] = []
        by_strategy[result.strategy_name].append(asdict(result))

    # Save each strategy
    for strategy_name, strategy_results in by_strategy.items():
        filename = output_path / f"{strategy_name}_results.json"
        with open(filename, 'w') as f:
            json.dump(strategy_results, f, indent=2)

        print(f"✅ Saved {len(strategy_results)} results to {filename}")


if __name__ == "__main__":
    print("🧪 Backtest Engine - Ready for RBI System")
    print("Use this engine to test strategies across multiple datasets")
