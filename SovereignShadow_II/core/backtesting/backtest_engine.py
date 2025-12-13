"""Backtest engine for modularized strategies.

This engine is designed specifically for the Entry/Exit/Risk module format:
- entry.generate_signal(df) -> {signal, confidence, price, ...}
- exit.generate_signal(df, entry_price) -> {signal, reason, pnl}
- risk.calculate_position_size(portfolio_value, current_price, atr) -> sizing dict

It intentionally avoids exchange APIs and operates on OHLCV dataframes.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class BacktestReport:
    strategy_name: str
    total_trades: int
    win_rate: float
    avg_pnl_percent: float
    total_pnl_usd: float
    trades: List[Dict[str, Any]]


class BacktestEngine:
    def __init__(self, initial_capital: float = 10_000.0):
        self.initial_capital = float(initial_capital)

    def backtest_strategy(
        self,
        *,
        strategy_import_path: str,
        df: pd.DataFrame,
        timeframe: str = "15m",
    ) -> BacktestReport:
        """Backtest a single modularized strategy.

        Args:
            strategy_import_path: e.g. "strategies.modularized.agent_1.elder_reversion"
            df: OHLCV dataframe with columns timestamp, open, high, low, close, volume
        """
        entry_module = importlib.import_module(f"{strategy_import_path}.entry")
        exit_module = importlib.import_module(f"{strategy_import_path}.exit")
        risk_module = importlib.import_module(f"{strategy_import_path}.risk")

        # Strategy class name convention is in the modules themselves.
        EntryClass = getattr(entry_module, "Entry")
        ExitClass = getattr(exit_module, "Exit")
        RiskClass = getattr(risk_module, "Risk")

        entry = EntryClass()
        exit_logic = ExitClass()
        risk = RiskClass()

        portfolio_value = self.initial_capital
        trades: List[Dict[str, Any]] = []
        position: Optional[Dict[str, Any]] = None

        # Ensure timestamp column exists.
        if "timestamp" not in df.columns:
            df = df.copy()
            df["timestamp"] = pd.RangeIndex(start=0, stop=len(df), step=1)

        warmup = max(100, getattr(entry, "warmup", 100))
        for i in range(warmup, len(df)):
            window = df.iloc[: i + 1]
            current_price = float(window["close"].iloc[-1])

            if position is None:
                sig = entry.generate_signal(window)
                if sig.get("signal") == "BUY":
                    atr = self._calculate_atr(window)
                    sizing = risk.calculate_position_size(portfolio_value, current_price, atr)
                    position = {
                        "entry_price": current_price,
                        "entry_time": window["timestamp"].iloc[-1],
                        "quantity": float(sizing["quantity"]),
                        "stop_loss": float(sizing["stop_loss_price"]),
                        "take_profit": float(sizing["take_profit_price"]),
                        "strategy_signal": sig,
                    }

            else:
                exit_sig = exit_logic.generate_signal(window, position["entry_price"])
                # Hard stops
                if current_price <= position["stop_loss"]:
                    exit_sig = {"signal": "SELL", "reason": "STOP_LOSS", "pnl": ((current_price - position["entry_price"]) / position["entry_price"]) * 100}
                if current_price >= position["take_profit"]:
                    exit_sig = {"signal": "SELL", "reason": "TAKE_PROFIT", "pnl": ((current_price - position["entry_price"]) / position["entry_price"]) * 100}

                if exit_sig.get("signal") == "SELL":
                    pnl_usd = (current_price - position["entry_price"]) * position["quantity"]
                    pnl_percent = ((current_price - position["entry_price"]) / position["entry_price"]) * 100
                    trades.append(
                        {
                            "entry_time": position["entry_time"],
                            "exit_time": window["timestamp"].iloc[-1],
                            "entry_price": position["entry_price"],
                            "exit_price": current_price,
                            "quantity": position["quantity"],
                            "pnl_usd": pnl_usd,
                            "pnl_percent": pnl_percent,
                            "exit_reason": exit_sig.get("reason", "SIGNAL_EXIT"),
                        }
                    )
                    portfolio_value += pnl_usd
                    position = None

        if trades:
            wins = [t for t in trades if t["pnl_usd"] > 0]
            win_rate = (len(wins) / len(trades)) * 100
            avg_pnl = sum(t["pnl_percent"] for t in trades) / len(trades)
            total_pnl = portfolio_value - self.initial_capital
            return BacktestReport(
                strategy_name=strategy_import_path.split(".")[-1],
                total_trades=len(trades),
                win_rate=win_rate,
                avg_pnl_percent=avg_pnl,
                total_pnl_usd=total_pnl,
                trades=trades,
            )

        return BacktestReport(
            strategy_name=strategy_import_path.split(".")[-1],
            total_trades=0,
            win_rate=0.0,
            avg_pnl_percent=0.0,
            total_pnl_usd=0.0,
            trades=[],
        )

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        return float(atr) if pd.notna(atr) else float(tr.iloc[-1])
