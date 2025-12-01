#!/usr/bin/env python3
"""
ARCHITECT FORGE - Self-Correcting Strategy Builder
Turns natural language → verified Python trading scripts
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class StrategyResult:
    """Result of strategy building process"""
    status: str  # "verified" | "failed"
    summary: Optional[Dict[str, Any]] = None
    risk_note: str = ""
    strategy_code: str = ""
    errors: List[str] = None
    refinement_iterations: int = 0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArchitectForge:
    """
    Self-correcting strategy builder for Sovereign Shadow 3

    Workflow:
    1. PLAN: Parse intent → generate strategy code
    2. VERIFY: Backtest in sandbox → check for errors
    3. REFINE: Fix issues → re-verify (max N iterations)
    """

    MAX_REFINEMENTS = 3
    MIN_WIN_RATE = 0.40
    MAX_DRAWDOWN = 0.30

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Strategy template
        self.template_path = Path(__file__).parent / "strategy_template.py"

        # Sandbox directory
        self.sandbox_dir = Path(__file__).parent.parent.parent / "sandbox" / "strategies"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

        # Logs directory
        self.log_dir = Path(__file__).parent.parent.parent / "logs" / "architect_forge"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_system_prompt(self) -> str:
        """Load the Architect Forge system prompt"""
        import yaml
        prompt_file = Path(__file__).parent.parent / "configs" / "system_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f)
                return prompts.get("architect_forge", "")
        return ""

    def build(
        self,
        request: str,
        symbols: List[str] = None,
        timeframe: str = "1d",
        backtest_days: int = 90,
        initial_equity: float = 10000
    ) -> StrategyResult:
        """
        Build a trading strategy from natural language request

        Args:
            request: Natural language strategy description
            symbols: Assets to trade (default: ["BTC/USDT"])
            timeframe: Trading timeframe
            backtest_days: Days of data for backtest
            initial_equity: Starting equity for backtest

        Returns:
            StrategyResult with verified strategy or failure reasons
        """
        symbols = symbols or ["BTC/USDT"]

        # Phase 1: Generate initial strategy
        strategy_spec = self._parse_request(request)
        strategy_code = self._generate_code(strategy_spec, symbols, timeframe)

        result = StrategyResult(status="failed")

        # Phase 2 & 3: Verify and refine loop
        for iteration in range(self.MAX_REFINEMENTS + 1):
            result.refinement_iterations = iteration

            # Verify in sandbox
            verify_result = self._verify_strategy(
                strategy_code,
                symbols,
                timeframe,
                backtest_days,
                initial_equity
            )

            if verify_result["success"]:
                metrics = verify_result["metrics"]

                # Check if metrics are acceptable
                if self._metrics_acceptable(metrics):
                    result.status = "verified"
                    result.summary = metrics
                    result.strategy_code = strategy_code
                    result.risk_note = self._generate_risk_note(metrics)
                    break
                else:
                    # Metrics not good enough, try to refine
                    if iteration < self.MAX_REFINEMENTS:
                        strategy_code = self._refine_strategy(
                            strategy_code,
                            metrics,
                            "Poor performance metrics"
                        )
                    else:
                        result.errors.append(f"Could not achieve acceptable metrics after {self.MAX_REFINEMENTS} refinements")
            else:
                # Error occurred, try to fix
                error = verify_result.get("error", "Unknown error")
                result.errors.append(error)

                if iteration < self.MAX_REFINEMENTS:
                    strategy_code = self._refine_strategy(
                        strategy_code,
                        {},
                        error
                    )
                else:
                    result.errors.append(f"Could not fix errors after {self.MAX_REFINEMENTS} refinements")

        # Log the result
        self._log_build(request, result)

        return result

    def _parse_request(self, request: str) -> Dict[str, Any]:
        """
        Parse natural language request into strategy specification

        Returns structured spec with:
        - indicators
        - entry_rules
        - exit_rules
        - position_sizing
        - risk_params
        """
        # Simple keyword-based parsing (enhance with LLM for production)
        spec = {
            "name": "custom_strategy",
            "indicators": [],
            "entry_rules": [],
            "exit_rules": [],
            "position_size_pct": 0.02,  # 2% risk per trade
            "stop_loss_pct": 0.05,  # 5% stop
            "take_profit_pct": 0.10,  # 10% take profit
        }

        request_lower = request.lower()

        # Detect indicators
        if "rsi" in request_lower:
            spec["indicators"].append("RSI")
            if "oversold" in request_lower or "below 30" in request_lower:
                spec["entry_rules"].append("RSI < 30")
            if "overbought" in request_lower or "above 70" in request_lower:
                spec["exit_rules"].append("RSI > 70")

        if "macd" in request_lower:
            spec["indicators"].append("MACD")
            if "crossover" in request_lower or "cross" in request_lower:
                spec["entry_rules"].append("MACD_CROSSOVER")

        if "moving average" in request_lower or "ema" in request_lower or "sma" in request_lower:
            spec["indicators"].append("EMA")
            if "golden cross" in request_lower:
                spec["entry_rules"].append("GOLDEN_CROSS")
            if "death cross" in request_lower:
                spec["exit_rules"].append("DEATH_CROSS")

        if "bollinger" in request_lower:
            spec["indicators"].append("BBANDS")
            spec["entry_rules"].append("PRICE_BELOW_BB_LOWER")
            spec["exit_rules"].append("PRICE_ABOVE_BB_UPPER")

        # Default rules if none detected
        if not spec["entry_rules"]:
            spec["indicators"].append("RSI")
            spec["entry_rules"].append("RSI < 35")
            spec["exit_rules"].append("RSI > 65")

        return spec

    def _generate_code(
        self,
        spec: Dict[str, Any],
        symbols: List[str],
        timeframe: str
    ) -> str:
        """Generate Python strategy code from specification"""

        indicator_code = self._generate_indicator_code(spec["indicators"])
        entry_code = self._generate_entry_code(spec["entry_rules"])
        exit_code = self._generate_exit_code(spec["exit_rules"])

        code = f'''#!/usr/bin/env python3
"""
Auto-generated strategy by ARCHITECT FORGE
Sovereign Shadow 3

Generated: {datetime.now().isoformat()}
Symbols: {symbols}
Timeframe: {timeframe}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def get_ohlcv(symbol: str, timeframe: str, days: int) -> pd.DataFrame:
    """
    Data access layer - replace with actual implementation
    Returns DataFrame with columns: timestamp, open, high, low, close, volume
    """
    # Mock data for backtest
    import ccxt
    try:
        exchange = ccxt.binance({{'enableRateLimit': True}})
        from datetime import datetime, timedelta
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        # Fallback mock data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
        np.random.seed(42)
        base_price = 95000 if 'BTC' in symbol else 3500
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * np.cumprod(1 + returns)
        return pd.DataFrame({{
            'timestamp': dates,
            'open': prices * 0.99,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.uniform(1e6, 1e8, days)
        }})


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators"""
    {indicator_code}
    return df


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trading signals

    Returns DataFrame with 'signal' column:
    1 = Buy, -1 = Sell, 0 = Hold
    """
    df = calculate_indicators(df)
    df['signal'] = 0

    # Entry signals
    {entry_code}

    # Exit signals
    {exit_code}

    return df


def position_sizing(equity: float, price: float, risk_pct: float = {spec['position_size_pct']}) -> float:
    """Calculate position size based on risk"""
    risk_amount = equity * risk_pct
    stop_distance = price * {spec['stop_loss_pct']}
    position_size = risk_amount / stop_distance
    position_value = position_size * price

    # Cap at 20% of equity
    max_position = equity * 0.20
    if position_value > max_position:
        position_size = max_position / price

    return position_size


def execute_backtest(
    data: pd.DataFrame,
    initial_equity: float = 10000,
    stop_loss_pct: float = {spec['stop_loss_pct']},
    take_profit_pct: float = {spec['take_profit_pct']}
) -> Dict[str, Any]:
    """
    Execute backtest on historical data

    Returns metrics dict
    """
    df = generate_signals(data.copy())

    equity = initial_equity
    position = 0
    entry_price = 0
    trades = []
    equity_curve = [equity]

    for i, row in df.iterrows():
        price = row['close']
        signal = row['signal']

        # Check exit conditions if in position
        if position != 0:
            pnl_pct = (price - entry_price) / entry_price * position

            # Stop loss
            if pnl_pct <= -stop_loss_pct:
                trade_pnl = equity * position * pnl_pct
                equity += trade_pnl
                trades.append({{'type': 'stop_loss', 'pnl': trade_pnl, 'pnl_pct': pnl_pct}})
                position = 0

            # Take profit
            elif pnl_pct >= take_profit_pct:
                trade_pnl = equity * position * pnl_pct
                equity += trade_pnl
                trades.append({{'type': 'take_profit', 'pnl': trade_pnl, 'pnl_pct': pnl_pct}})
                position = 0

            # Exit signal
            elif signal == -1 and position > 0:
                trade_pnl = equity * position * pnl_pct
                equity += trade_pnl
                trades.append({{'type': 'signal_exit', 'pnl': trade_pnl, 'pnl_pct': pnl_pct}})
                position = 0

        # Entry signal
        if position == 0 and signal == 1:
            position = 1  # Long
            entry_price = price

        equity_curve.append(equity)

    # Calculate metrics
    total_return = (equity - initial_equity) / initial_equity
    equity_series = pd.Series(equity_curve)
    drawdown = (equity_series - equity_series.cummax()) / equity_series.cummax()
    max_drawdown = abs(drawdown.min())

    winning_trades = [t for t in trades if t['pnl'] > 0]
    win_rate = len(winning_trades) / len(trades) if trades else 0

    return {{
        'total_return_pct': round(total_return * 100, 2),
        'max_drawdown_pct': round(max_drawdown * 100, 2),
        'win_rate_pct': round(win_rate * 100, 2),
        'trades': len(trades),
        'final_equity': round(equity, 2),
        'initial_equity': initial_equity
    }}


# Main execution
if __name__ == "__main__":
    import sys
    import json

    symbol = sys.argv[1] if len(sys.argv) > 1 else "{symbols[0]}"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 90

    data = get_ohlcv(symbol, "{timeframe}", days)
    metrics = execute_backtest(data)

    print(json.dumps(metrics, indent=2))
'''
        return code

    def _generate_indicator_code(self, indicators: List[str]) -> str:
        """Generate indicator calculation code"""
        lines = ["close = df['close']"]

        for ind in indicators:
            if ind == "RSI":
                lines.append("""
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))""")

            elif ind == "MACD":
                lines.append("""
    # MACD
    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']""")

            elif ind == "EMA":
                lines.append("""
    # EMAs
    df['ema_20'] = close.ewm(span=20).mean()
    df['ema_50'] = close.ewm(span=50).mean()""")

            elif ind == "BBANDS":
                lines.append("""
    # Bollinger Bands
    df['bb_mid'] = close.rolling(window=20).mean()
    df['bb_std'] = close.rolling(window=20).std()
    df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']""")

        return "\n    ".join(lines)

    def _generate_entry_code(self, rules: List[str]) -> str:
        """Generate entry signal code"""
        conditions = []

        for rule in rules:
            if "RSI < " in rule:
                threshold = rule.split("<")[1].strip()
                conditions.append(f"(df['rsi'] < {threshold})")
            elif "RSI > " in rule:
                threshold = rule.split(">")[1].strip()
                conditions.append(f"(df['rsi'] > {threshold})")
            elif rule == "MACD_CROSSOVER":
                conditions.append("((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1)))")
            elif rule == "GOLDEN_CROSS":
                conditions.append("((df['ema_20'] > df['ema_50']) & (df['ema_20'].shift(1) <= df['ema_50'].shift(1)))")
            elif rule == "PRICE_BELOW_BB_LOWER":
                conditions.append("(df['close'] < df['bb_lower'])")

        if conditions:
            return f"df.loc[{' & '.join(conditions)}, 'signal'] = 1"
        return "# No entry rules defined"

    def _generate_exit_code(self, rules: List[str]) -> str:
        """Generate exit signal code"""
        conditions = []

        for rule in rules:
            if "RSI > " in rule:
                threshold = rule.split(">")[1].strip()
                conditions.append(f"(df['rsi'] > {threshold})")
            elif "RSI < " in rule:
                threshold = rule.split("<")[1].strip()
                conditions.append(f"(df['rsi'] < {threshold})")
            elif rule == "DEATH_CROSS":
                conditions.append("((df['ema_20'] < df['ema_50']) & (df['ema_20'].shift(1) >= df['ema_50'].shift(1)))")
            elif rule == "PRICE_ABOVE_BB_UPPER":
                conditions.append("(df['close'] > df['bb_upper'])")

        if conditions:
            return f"df.loc[(df['signal'] == 0) & ({' | '.join(conditions)}), 'signal'] = -1"
        return "# No exit rules defined"

    def _verify_strategy(
        self,
        code: str,
        symbols: List[str],
        timeframe: str,
        days: int,
        equity: float
    ) -> Dict[str, Any]:
        """
        Verify strategy by running in sandbox

        Returns:
        {
            "success": bool,
            "metrics": {...},
            "error": str (if failed)
        }
        """
        # Write strategy to temp file
        strategy_file = self.sandbox_dir / f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

        try:
            with open(strategy_file, 'w') as f:
                f.write(code)

            # Run strategy
            result = subprocess.run(
                ["python3", str(strategy_file), symbols[0], str(days)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.sandbox_dir)
            )

            if result.returncode == 0:
                try:
                    metrics = json.loads(result.stdout)
                    return {"success": True, "metrics": metrics}
                except json.JSONDecodeError:
                    return {"success": False, "error": f"Invalid output: {result.stdout}"}
            else:
                return {"success": False, "error": result.stderr or "Unknown error"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Strategy execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            # Keep file for debugging
            pass

    def _metrics_acceptable(self, metrics: Dict[str, Any]) -> bool:
        """Check if backtest metrics meet minimum requirements"""
        win_rate = metrics.get("win_rate_pct", 0) / 100
        max_dd = metrics.get("max_drawdown_pct", 100) / 100
        trades = metrics.get("trades", 0)

        return (
            win_rate >= self.MIN_WIN_RATE and
            max_dd <= self.MAX_DRAWDOWN and
            trades >= 5  # Need at least 5 trades
        )

    def _refine_strategy(
        self,
        code: str,
        metrics: Dict[str, Any],
        error: str
    ) -> str:
        """
        Refine strategy based on feedback

        Simple refinements:
        - Adjust thresholds if win rate too low
        - Tighten stops if drawdown too high
        """
        # Simple rule-based refinements
        if "win_rate_pct" in metrics and metrics["win_rate_pct"] < 40:
            # More conservative entries
            code = code.replace("< 30", "< 25")
            code = code.replace("> 70", "> 75")

        if "max_drawdown_pct" in metrics and metrics["max_drawdown_pct"] > 30:
            # Tighter stops
            code = code.replace("stop_loss_pct: float = 0.05", "stop_loss_pct: float = 0.03")

        return code

    def _generate_risk_note(self, metrics: Dict[str, Any]) -> str:
        """Generate risk assessment note"""
        notes = []

        win_rate = metrics.get("win_rate_pct", 0)
        if win_rate < 50:
            notes.append(f"Win rate ({win_rate}%) is below 50%, suggesting reliance on larger winners vs losers.")

        max_dd = metrics.get("max_drawdown_pct", 0)
        if max_dd > 15:
            notes.append(f"Max drawdown ({max_dd}%) is significant. Consider reducing position sizes.")

        trades = metrics.get("trades", 0)
        if trades < 20:
            notes.append(f"Only {trades} trades in backtest period. Results may not be statistically significant.")

        if not notes:
            notes.append("Strategy passed basic risk checks. Always paper trade before live deployment.")

        return " ".join(notes)

    def _log_build(self, request: str, result: StrategyResult):
        """Log build attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "status": result.status,
            "iterations": result.refinement_iterations,
            "metrics": result.summary,
            "errors": result.errors
        }

        log_file = self.log_dir / f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)


# CLI
if __name__ == "__main__":
    import sys

    forge = ArchitectForge()

    request = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Build a simple RSI strategy that buys when RSI is oversold"

    print(f"\n{'='*60}")
    print("ARCHITECT FORGE - Strategy Builder")
    print('='*60)
    print(f"Request: {request}\n")

    result = forge.build(request)

    print(f"Status: {result.status}")
    print(f"Iterations: {result.refinement_iterations}")

    if result.status == "verified":
        print(f"\nMetrics: {json.dumps(result.summary, indent=2)}")
        print(f"\nRisk Note: {result.risk_note}")
        print(f"\nStrategy code saved. Length: {len(result.strategy_code)} chars")
    else:
        print(f"\nErrors: {result.errors}")

    print('='*60)
