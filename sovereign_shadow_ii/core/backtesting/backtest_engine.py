#!/usr/bin/env python3
"""
SOVEREIGN SHADOW II - Backtest Engine (Agent 9)

Comprehensive backtesting framework for modularized strategies.

Features:
- Tests Entry/Exit/Risk modules
- Calculates performance metrics
- Generates detailed reports
- Integrates with Performance Tracker
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """Individual trade result"""
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl_usd: float
    pnl_percent: float
    exit_reason: str
    duration_minutes: int


@dataclass
class BacktestResult:
    """Backtest result summary"""
    strategy_name: str
    regime: str
    timeframe: str
    start_date: str
    end_date: str

    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_pnl_percent: float
    total_pnl_usd: float
    total_pnl_percent: float

    # Risk metrics
    sharpe_ratio: float
    max_drawdown_usd: float
    max_drawdown_percent: float
    profit_factor: float
    avg_trade_duration_minutes: float

    # Additional stats
    best_trade_percent: float
    worst_trade_percent: float
    avg_win_percent: float
    avg_loss_percent: float

    # Trade list
    trades: List[Dict]

    def to_dict(self) -> Dict:
        result = asdict(self)
        return result


class BacktestEngine:
    """
    Backtesting engine for modularized strategies.

    Usage:
        engine = BacktestEngine(historical_data)
        result = engine.backtest_strategy('ElderReversion', 'choppy_volatile')
    """

    def __init__(
        self,
        historical_data: Optional[List[Dict]] = None,
        initial_capital: float = 10000.0
    ):
        """
        Initialize backtest engine.

        Args:
            historical_data: List of OHLCV dicts
            initial_capital: Starting capital for simulation
        """
        self.historical_data = historical_data or []
        self.initial_capital = initial_capital

        # Strategy cache
        self.strategy_cache: Dict[str, Any] = {}

        logger.info(f"BacktestEngine initialized with ${initial_capital:,.2f} capital")

    def load_historical_data(self, file_path: str) -> bool:
        """Load historical data from CSV file"""
        try:
            import csv

            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                self.historical_data = []

                for row in reader:
                    self.historical_data.append({
                        'timestamp': row.get('timestamp', ''),
                        'open': float(row.get('open', 0)),
                        'high': float(row.get('high', 0)),
                        'low': float(row.get('low', 0)),
                        'close': float(row.get('close', 0)),
                        'volume': float(row.get('volume', 0))
                    })

            logger.info(f"Loaded {len(self.historical_data)} candles from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return False

    def generate_synthetic_data(
        self,
        num_candles: int = 1000,
        base_price: float = 95000.0,
        trend: str = "sideways"
    ) -> List[Dict]:
        """Generate synthetic market data for testing"""
        import random

        data = []
        current_price = base_price
        timestamp = datetime.now() - timedelta(minutes=15 * num_candles)

        for i in range(num_candles):
            # Apply trend
            if trend == "bullish":
                drift = random.uniform(-20, 50)
            elif trend == "bearish":
                drift = random.uniform(-50, 20)
            else:
                drift = random.uniform(-30, 30)

            current_price += drift

            # Generate OHLCV
            open_price = current_price + random.uniform(-50, 50)
            high_price = max(open_price, current_price) + random.uniform(0, 200)
            low_price = min(open_price, current_price) - random.uniform(0, 200)
            close_price = current_price
            volume = random.uniform(100, 1000)

            data.append({
                'timestamp': timestamp.isoformat(),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })

            timestamp += timedelta(minutes=15)

        self.historical_data = data
        logger.info(f"Generated {num_candles} synthetic candles ({trend} trend)")
        return data

    def _load_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Load strategy modules"""
        if strategy_name in self.strategy_cache:
            return self.strategy_cache[strategy_name]

        # Try built-in strategies first
        builtin = self._get_builtin_strategy(strategy_name)
        if builtin:
            self.strategy_cache[strategy_name] = builtin
            return builtin

        # Try modularized strategies
        strategy_path = Path(__file__).parent.parent.parent / "strategies" / "modularized"

        for agent_dir in strategy_path.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith("agent_"):
                module_name = strategy_name.lower().replace(" ", "_")
                strategy_dir = agent_dir / module_name

                if strategy_dir.exists():
                    try:
                        # Dynamic import
                        entry_path = strategy_dir / "entry.py"
                        exit_path = strategy_dir / "exit.py"
                        risk_path = strategy_dir / "risk.py"

                        if entry_path.exists() and exit_path.exists() and risk_path.exists():
                            entry_spec = importlib.util.spec_from_file_location("entry", entry_path)
                            entry_module = importlib.util.module_from_spec(entry_spec)
                            entry_spec.loader.exec_module(entry_module)

                            exit_spec = importlib.util.spec_from_file_location("exit", exit_path)
                            exit_module = importlib.util.module_from_spec(exit_spec)
                            exit_spec.loader.exec_module(exit_module)

                            risk_spec = importlib.util.spec_from_file_location("risk", risk_path)
                            risk_module = importlib.util.module_from_spec(risk_spec)
                            risk_spec.loader.exec_module(risk_module)

                            # Get class names
                            class_name = ''.join(word.title() for word in module_name.split('_'))

                            strategy = {
                                'entry': getattr(entry_module, f'{class_name}Entry')(),
                                'exit': getattr(exit_module, f'{class_name}Exit')(),
                                'risk': getattr(risk_module, f'{class_name}Risk')()
                            }

                            self.strategy_cache[strategy_name] = strategy
                            return strategy

                    except Exception as e:
                        logger.error(f"Failed to load strategy {strategy_name}: {e}")

        return None

    def _get_builtin_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Get built-in strategy implementation"""
        try:
            from core.orchestration.builtin_strategies import (
                ElderReversionEntry, ElderReversionExit, ElderReversionRisk,
                RSIReversionEntry, RSIReversionExit, RSIReversionRisk,
                TrendFollowEMAEntry, TrendFollowEMAExit, TrendFollowEMARisk
            )

            builtin = {
                "ElderReversion": {
                    'entry': ElderReversionEntry(),
                    'exit': ElderReversionExit(),
                    'risk': ElderReversionRisk()
                },
                "RSIReversion": {
                    'entry': RSIReversionEntry(),
                    'exit': RSIReversionExit(),
                    'risk': RSIReversionRisk()
                },
                "TrendFollowEMA": {
                    'entry': TrendFollowEMAEntry(),
                    'exit': TrendFollowEMAExit(),
                    'risk': TrendFollowEMARisk()
                }
            }

            return builtin.get(strategy_name)

        except ImportError:
            return None

    def backtest_strategy(
        self,
        strategy_name: str,
        regime: str = "unknown",
        timeframe: str = "15m",
        start_idx: int = 100,
        end_idx: Optional[int] = None
    ) -> BacktestResult:
        """
        Run backtest for a modularized strategy.

        Args:
            strategy_name: Name of strategy to test
            regime: Market regime label
            timeframe: Candle timeframe
            start_idx: Start index (need history for indicators)
            end_idx: End index (None = end of data)

        Returns:
            BacktestResult with performance metrics
        """
        # Load strategy
        strategy = self._load_strategy(strategy_name)

        if strategy is None:
            logger.error(f"Strategy not found: {strategy_name}")
            return self._empty_result(strategy_name, regime, timeframe)

        if len(self.historical_data) < start_idx + 10:
            logger.error("Insufficient historical data")
            return self._empty_result(strategy_name, regime, timeframe)

        end_idx = end_idx or len(self.historical_data)

        # Simulation state
        portfolio_value = self.initial_capital
        position = None
        trades: List[TradeResult] = []

        logger.info(f"Starting backtest: {strategy_name} ({start_idx} to {end_idx})")

        # Run through historical data
        for i in range(start_idx, end_idx):
            # Get data slice for indicators
            current_slice = self.historical_data[max(0, i-100):i]

            if len(current_slice) < 20:
                continue

            current_candle = self.historical_data[i]
            current_price = current_candle['close']
            current_time = current_candle['timestamp']

            # Check exit if in position
            if position is not None:
                exit_signal = strategy['exit'].generate_signal(
                    current_slice,
                    position['entry_price']
                )

                # Check stop loss / take profit manually as well
                pnl_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100

                should_exit = False
                exit_reason = ""

                if exit_signal.get('signal') == 'SELL':
                    should_exit = True
                    exit_reason = exit_signal.get('reason', 'SIGNAL_EXIT')
                elif current_price <= position['stop_loss']:
                    should_exit = True
                    exit_reason = 'STOP_LOSS'
                elif current_price >= position['take_profit']:
                    should_exit = True
                    exit_reason = 'TAKE_PROFIT'

                if should_exit:
                    # Close position
                    pnl_usd = (current_price - position['entry_price']) * position['quantity']
                    portfolio_value += pnl_usd

                    # Calculate duration
                    try:
                        entry_dt = datetime.fromisoformat(position['entry_time'])
                        exit_dt = datetime.fromisoformat(current_time)
                        duration = int((exit_dt - entry_dt).total_seconds() / 60)
                    except:
                        duration = 0

                    trades.append(TradeResult(
                        entry_time=position['entry_time'],
                        exit_time=current_time,
                        entry_price=position['entry_price'],
                        exit_price=current_price,
                        quantity=position['quantity'],
                        pnl_usd=pnl_usd,
                        pnl_percent=pnl_percent,
                        exit_reason=exit_reason,
                        duration_minutes=duration
                    ))

                    position = None

            # Check entry if not in position
            elif position is None:
                entry_signal = strategy['entry'].generate_signal(current_slice)

                if entry_signal.get('signal') == 'BUY':
                    # Calculate position size
                    atr = self._calculate_atr(current_slice)
                    sizing = strategy['risk'].calculate_position_size(
                        portfolio_value,
                        current_price,
                        atr
                    )

                    if sizing['position_value_usd'] >= 10:
                        position = {
                            'entry_price': current_price,
                            'entry_time': current_time,
                            'quantity': sizing['quantity'],
                            'stop_loss': sizing['stop_loss_price'],
                            'take_profit': sizing['take_profit_price']
                        }

        # Close any remaining position at last price
        if position is not None:
            last_price = self.historical_data[-1]['close']
            pnl_usd = (last_price - position['entry_price']) * position['quantity']
            pnl_percent = ((last_price - position['entry_price']) / position['entry_price']) * 100
            portfolio_value += pnl_usd

            trades.append(TradeResult(
                entry_time=position['entry_time'],
                exit_time=self.historical_data[-1]['timestamp'],
                entry_price=position['entry_price'],
                exit_price=last_price,
                quantity=position['quantity'],
                pnl_usd=pnl_usd,
                pnl_percent=pnl_percent,
                exit_reason='END_OF_DATA',
                duration_minutes=0
            ))

        # Calculate metrics
        return self._calculate_metrics(
            strategy_name, regime, timeframe, trades, portfolio_value
        )

    def _calculate_atr(self, data: List[Dict], period: int = 14) -> float:
        """Calculate ATR"""
        if len(data) < 2:
            return 0

        tr_list = []
        for i in range(1, len(data)):
            tr = max(
                data[i]['high'] - data[i]['low'],
                abs(data[i]['high'] - data[i-1]['close']),
                abs(data[i]['low'] - data[i-1]['close'])
            )
            tr_list.append(tr)

        return sum(tr_list[-period:]) / min(len(tr_list), period) if tr_list else 0

    def _calculate_metrics(
        self,
        strategy_name: str,
        regime: str,
        timeframe: str,
        trades: List[TradeResult],
        final_portfolio: float
    ) -> BacktestResult:
        """Calculate comprehensive metrics from trade results"""

        if not trades:
            return self._empty_result(strategy_name, regime, timeframe)

        # Basic stats
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl_usd > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # PnL stats
        pnl_list = [t.pnl_percent for t in trades]
        avg_pnl_percent = sum(pnl_list) / len(pnl_list)
        total_pnl_usd = sum(t.pnl_usd for t in trades)
        total_pnl_percent = ((final_portfolio - self.initial_capital) / self.initial_capital) * 100

        # Sharpe ratio (simplified)
        import statistics
        if len(pnl_list) > 1:
            std_dev = statistics.stdev(pnl_list)
            sharpe_ratio = (avg_pnl_percent / std_dev) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0

        # Max drawdown
        cumulative = 0
        peak = 0
        max_drawdown = 0

        for t in trades:
            cumulative += t.pnl_usd
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        max_drawdown_percent = (max_drawdown / self.initial_capital * 100) if self.initial_capital > 0 else 0

        # Profit factor
        gross_profit = sum(t.pnl_usd for t in trades if t.pnl_usd > 0)
        gross_loss = abs(sum(t.pnl_usd for t in trades if t.pnl_usd < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else gross_profit

        # Duration
        avg_duration = sum(t.duration_minutes for t in trades) / len(trades)

        # Win/loss averages
        wins = [t for t in trades if t.pnl_usd > 0]
        losses = [t for t in trades if t.pnl_usd <= 0]
        avg_win = sum(t.pnl_percent for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl_percent for t in losses) / len(losses) if losses else 0

        # Best/worst
        best_trade = max(pnl_list)
        worst_trade = min(pnl_list)

        # Dates
        start_date = trades[0].entry_time if trades else ""
        end_date = trades[-1].exit_time if trades else ""

        return BacktestResult(
            strategy_name=strategy_name,
            regime=regime,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_pnl_percent=avg_pnl_percent,
            total_pnl_usd=total_pnl_usd,
            total_pnl_percent=total_pnl_percent,
            sharpe_ratio=sharpe_ratio,
            max_drawdown_usd=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            profit_factor=profit_factor,
            avg_trade_duration_minutes=avg_duration,
            best_trade_percent=best_trade,
            worst_trade_percent=worst_trade,
            avg_win_percent=avg_win,
            avg_loss_percent=avg_loss,
            trades=[asdict(t) for t in trades]
        )

    def _empty_result(
        self,
        strategy_name: str,
        regime: str,
        timeframe: str
    ) -> BacktestResult:
        """Return empty result for failed backtests"""
        return BacktestResult(
            strategy_name=strategy_name,
            regime=regime,
            timeframe=timeframe,
            start_date="",
            end_date="",
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            avg_pnl_percent=0,
            total_pnl_usd=0,
            total_pnl_percent=0,
            sharpe_ratio=0,
            max_drawdown_usd=0,
            max_drawdown_percent=0,
            profit_factor=0,
            avg_trade_duration_minutes=0,
            best_trade_percent=0,
            worst_trade_percent=0,
            avg_win_percent=0,
            avg_loss_percent=0,
            trades=[]
        )

    def run_all_backtests(
        self,
        strategies: Optional[List[str]] = None
    ) -> Dict[str, BacktestResult]:
        """Run backtests for multiple strategies"""
        if strategies is None:
            strategies = ["ElderReversion", "RSIReversion", "TrendFollowEMA"]

        results = {}

        for strategy in strategies:
            logger.info(f"Backtesting: {strategy}")
            result = self.backtest_strategy(strategy)
            results[strategy] = result

            # Log summary
            logger.info(
                f"  {strategy}: {result.total_trades} trades, "
                f"Win Rate: {result.win_rate:.1f}%, "
                f"PnL: ${result.total_pnl_usd:.2f}"
            )

        return results

    def generate_report(
        self,
        results: Dict[str, BacktestResult],
        output_path: Optional[str] = None
    ) -> str:
        """Generate backtest report"""
        report_lines = [
            "=" * 80,
            "SOVEREIGN SHADOW II - BACKTEST REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 80,
            ""
        ]

        for strategy, result in results.items():
            report_lines.extend([
                f"\n{'='*40}",
                f"STRATEGY: {strategy}",
                f"{'='*40}",
                f"",
                f"Performance Summary:",
                f"  Total Trades:     {result.total_trades}",
                f"  Win Rate:         {result.win_rate:.1f}%",
                f"  Total PnL:        ${result.total_pnl_usd:,.2f} ({result.total_pnl_percent:.2f}%)",
                f"  Avg Trade PnL:    {result.avg_pnl_percent:.2f}%",
                f"",
                f"Risk Metrics:",
                f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}",
                f"  Max Drawdown:     ${result.max_drawdown_usd:,.2f} ({result.max_drawdown_percent:.2f}%)",
                f"  Profit Factor:    {result.profit_factor:.2f}",
                f"",
                f"Trade Analysis:",
                f"  Winning Trades:   {result.winning_trades}",
                f"  Losing Trades:    {result.losing_trades}",
                f"  Avg Win:          {result.avg_win_percent:.2f}%",
                f"  Avg Loss:         {result.avg_loss_percent:.2f}%",
                f"  Best Trade:       {result.best_trade_percent:.2f}%",
                f"  Worst Trade:      {result.worst_trade_percent:.2f}%",
                f"  Avg Duration:     {result.avg_trade_duration_minutes:.0f} min"
            ])

        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80
        ])

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")

        return report


if __name__ == "__main__":
    # Test the backtest engine
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("SOVEREIGN SHADOW II - BACKTEST ENGINE TEST")
    print("=" * 60)

    # Initialize engine
    engine = BacktestEngine(initial_capital=10000.0)

    # Generate synthetic data
    print("\nGenerating synthetic market data...")
    engine.generate_synthetic_data(num_candles=500, trend="bullish")

    # Run backtests
    print("\nRunning backtests...")
    results = engine.run_all_backtests()

    # Generate report
    print("\n" + "=" * 60)
    report = engine.generate_report(results)
    print(report)

    # Save results
    output_dir = Path(__file__).parent.parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump({k: v.to_dict() for k, v in results.items()}, f, indent=2)

    print(f"\nResults saved to: {results_file}")
    print("\nBacktest engine test complete!")
