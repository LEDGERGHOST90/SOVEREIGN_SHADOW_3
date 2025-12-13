"""SQLite performance tracker for Sovereign Shadow II.

Stores:
- regime observations
- strategy decisions/signals
- executed trades (real or simulated)
- aggregated per-strategy stats

This is intentionally lightweight (sqlite3 + json).
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class StrategyStats:
    strategy_name: str
    regime: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_pnl_percent: float


class PerformanceTracker:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv(
            "SS2_DB_PATH", str(Path("/workspace") / "SovereignShadow_II" / "state" / "performance.db")
        )
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS regimes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    regime TEXT NOT NULL,
                    features_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    regime TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price REAL,
                    reasoning TEXT,
                    extras_json TEXT
                );

                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts_entry TEXT NOT NULL,
                    ts_exit TEXT,
                    exchange TEXT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    regime TEXT NOT NULL,
                    qty REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    pnl_usd REAL,
                    pnl_percent REAL,
                    exit_reason TEXT,
                    meta_json TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_trades_strategy_regime ON trades(strategy_name, regime);
                """
            )

    def log_regime(self, *, symbol: str, timeframe: str, regime: str, features: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO regimes(ts, symbol, timeframe, regime, features_json) VALUES(?,?,?,?,?)",
                (datetime.utcnow().isoformat(), symbol, timeframe, regime, json.dumps(features, default=str)),
            )

    def log_signal(
        self,
        *,
        symbol: str,
        timeframe: str,
        strategy_name: str,
        regime: str,
        signal: str,
        confidence: float,
        price: Optional[float] = None,
        reasoning: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO signals(ts, symbol, timeframe, strategy_name, regime, signal, confidence, price, reasoning, extras_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.utcnow().isoformat(),
                    symbol,
                    timeframe,
                    strategy_name,
                    regime,
                    signal,
                    float(confidence),
                    float(price) if price is not None else None,
                    reasoning,
                    json.dumps(extras or {}, default=str),
                ),
            )

    def log_trade_entry(
        self,
        *,
        exchange: str,
        symbol: str,
        side: str,
        strategy_name: str,
        regime: str,
        qty: float,
        entry_price: float,
        meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO trades(ts_entry, exchange, symbol, side, strategy_name, regime, qty, entry_price, meta_json)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    datetime.utcnow().isoformat(),
                    exchange,
                    symbol,
                    side,
                    strategy_name,
                    regime,
                    float(qty),
                    float(entry_price),
                    json.dumps(meta or {}, default=str),
                ),
            )
            return int(cur.lastrowid)

    def log_trade_exit(
        self,
        *,
        trade_id: int,
        exit_price: float,
        exit_reason: str,
    ) -> None:
        with self._connect() as conn:
            row = conn.execute("SELECT qty, entry_price FROM trades WHERE id=?", (trade_id,)).fetchone()
            if not row:
                return
            qty = float(row["qty"])
            entry_price = float(row["entry_price"])
            pnl_usd = (float(exit_price) - entry_price) * qty
            pnl_percent = ((float(exit_price) - entry_price) / entry_price) * 100.0

            conn.execute(
                """UPDATE trades
                   SET ts_exit=?, exit_price=?, pnl_usd=?, pnl_percent=?, exit_reason=?
                   WHERE id=?""",
                (datetime.utcnow().isoformat(), float(exit_price), pnl_usd, pnl_percent, exit_reason, int(trade_id)),
            )

    def get_strategy_stats(self, *, strategy_name: str, regime: str) -> StrategyStats:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT pnl_percent
                FROM trades
                WHERE strategy_name=? AND regime=? AND pnl_percent IS NOT NULL
                """,
                (strategy_name, regime),
            ).fetchall()

        pnl = [float(r["pnl_percent"]) for r in rows]
        total = len(pnl)
        wins = len([x for x in pnl if x > 0])
        losses = total - wins
        win_rate = (wins / total) if total else 0.0
        avg_pnl = (sum(pnl) / total) if total else 0.0
        return StrategyStats(
            strategy_name=strategy_name,
            regime=regime,
            total_trades=total,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_pnl_percent=avg_pnl,
        )

    def rank_strategies_for_regime(
        self,
        *,
        regime: str,
        strategy_names: List[str],
        limit: int = 10,
    ) -> List[Tuple[str, float, StrategyStats]]:
        """Return (strategy_name, score, stats) sorted desc.

        Score is simple and intentionally robust with sparse data:
        - if no trades: score=0
        - else: score = win_rate * max(avg_pnl_percent, 0)
        """
        ranked: List[Tuple[str, float, StrategyStats]] = []
        for name in strategy_names:
            stats = self.get_strategy_stats(strategy_name=name, regime=regime)
            score = 0.0
            if stats.total_trades:
                score = stats.win_rate * max(stats.avg_pnl_percent, 0.0)
            ranked.append((name, score, stats))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:limit]
