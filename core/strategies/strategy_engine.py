#!/usr/bin/env python3
"""
STRATEGY ENGINE - Unified strategy selection and memory system for SS_III

Integrates:
- Market Regime Detection (ADX + ATR)
- AI Strategy Selection (451 strategies)
- Self-Annealing Loop (persistent memory)
- Performance Tracking (SQLite)

Based on Manus AI analysis of Moon Dev's trading framework.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# SS_III paths
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
BRAIN_PATH = SS3_ROOT / "BRAIN.json"
STRATEGY_DB = SS3_ROOT / "data" / "strategy_performance.db"
STRATEGY_LIBRARY = SS3_ROOT / "core" / "strategies" / "strategy_library.json"

# Ensure data directory exists
(SS3_ROOT / "data").mkdir(exist_ok=True)


class MarketRegimeDetector:
    """
    Detects market regime based on ADX and ATR percentile.

    Regimes:
    - High Volatility Trend: ADX > 25, ATR Percentile > 70%
    - Low Volatility Trend: ADX > 25, ATR Percentile < 30%
    - High Volatility Range: ADX < 20, ATR Percentile > 70%
    - Low Volatility Range: ADX < 20, ATR Percentile < 30%
    - Transitioning Market: ADX 20-25, ATR Percentile 30-70%
    """

    def __init__(self, adx_period: int = 14, atr_period: int = 14, atr_lookback: int = 100):
        self.adx_period = adx_period
        self.atr_period = atr_period
        self.atr_lookback = atr_lookback

        # Regime to strategy type mapping
        self.regime_map = {
            "High Volatility Trend": ["Trend Following", "Breakout", "Volatility", "Momentum"],
            "Low Volatility Trend": ["Trend Following", "Pullback", "Momentum"],
            "High Volatility Range": ["Mean Reversion", "Volatility", "Scalping", "Arbitrage"],
            "Low Volatility Range": ["Mean Reversion", "Volatility Squeeze", "Accumulation"],
            "Transitioning Market": ["Divergence", "Adaptive", "Harmonic"]
        }

    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()
        return atr

    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Average Directional Index"""
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        atr = self.calculate_atr(high, low, close)

        plus_di = 100 * (plus_dm.rolling(window=self.adx_period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.adx_period).mean() / atr)

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
        adx = dx.rolling(window=self.adx_period).mean()

        return adx

    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """Detect current market regime from OHLCV data"""
        # Normalize column names
        df_norm = df.copy()
        df_norm.columns = df_norm.columns.str.capitalize()

        if len(df_norm) < self.atr_lookback:
            return {
                "regime": "Insufficient Data",
                "adx": 0,
                "atr_percentile": 50,
                "recommended_types": []
            }

        # Calculate indicators
        atr = self.calculate_atr(df_norm['High'], df_norm['Low'], df_norm['Close'])
        adx = self.calculate_adx(df_norm['High'], df_norm['Low'], df_norm['Close'])

        # ATR percentile
        atr_pct = (atr.rank(pct=True) * 100).iloc[-1]

        current_adx = adx.iloc[-1]
        current_atr_pct = atr_pct if not pd.isna(atr_pct) else 50

        # Determine regime
        if pd.isna(current_adx):
            regime = "Transitioning Market"
        elif current_adx > 25:
            if current_atr_pct > 70:
                regime = "High Volatility Trend"
            elif current_atr_pct < 30:
                regime = "Low Volatility Trend"
            else:
                regime = "Transitioning Market"
        elif current_adx < 20:
            if current_atr_pct > 70:
                regime = "High Volatility Range"
            elif current_atr_pct < 30:
                regime = "Low Volatility Range"
            else:
                regime = "Transitioning Market"
        else:
            regime = "Transitioning Market"

        return {
            "regime": regime,
            "adx": round(float(current_adx) if not pd.isna(current_adx) else 0, 2),
            "atr_percentile": round(float(current_atr_pct), 2),
            "recommended_types": self.regime_map.get(regime, [])
        }


class PerformanceTracker:
    """SQLite-based performance tracking for strategy memory"""

    def __init__(self, db_path: Path = STRATEGY_DB):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Performance log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                action TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                pnl_percent REAL,
                success INTEGER,
                context TEXT
            )
        """)

        # Strategy statistics per regime
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_stats (
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                avg_pnl REAL DEFAULT 0.0,
                confidence_score REAL DEFAULT 0.5,
                last_updated TEXT,
                PRIMARY KEY (strategy_name, regime)
            )
        """)

        # Improvement log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvement_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                issue TEXT NOT NULL,
                proposed_fix TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)

        conn.commit()
        conn.close()

    def log_trade(self, strategy_name: str, regime: str, action: str,
                  entry_price: float, exit_price: float = None,
                  success: bool = True, context: Dict = None):
        """Log a trade and update statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        pnl = None
        if exit_price and entry_price:
            if action.upper() in ["LONG", "BUY"]:
                pnl = ((exit_price - entry_price) / entry_price) * 100
            else:
                pnl = ((entry_price - exit_price) / entry_price) * 100

        cursor.execute("""
            INSERT INTO performance_log
            (timestamp, strategy_name, regime, action, entry_price, exit_price, pnl_percent, success, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            strategy_name, regime, action,
            entry_price, exit_price, pnl,
            1 if success else 0,
            json.dumps(context) if context else None
        ))

        conn.commit()
        conn.close()

        # Update stats
        self._update_stats(strategy_name, regime, success, pnl)

    def _update_stats(self, strategy_name: str, regime: str, success: bool, pnl: float):
        """Update running statistics for a strategy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT total_trades, successful_trades, avg_pnl
            FROM strategy_stats WHERE strategy_name = ? AND regime = ?
        """, (strategy_name, regime))

        result = cursor.fetchone()

        if result:
            total, successful, avg = result
            total += 1
            if success:
                successful += 1
            if pnl is not None:
                avg = ((avg * (total - 1)) + pnl) / total

            confidence = (successful / total) * 0.7 + 0.3

            cursor.execute("""
                UPDATE strategy_stats
                SET total_trades = ?, successful_trades = ?, avg_pnl = ?,
                    confidence_score = ?, last_updated = ?
                WHERE strategy_name = ? AND regime = ?
            """, (total, successful, avg, confidence, datetime.now().isoformat(),
                  strategy_name, regime))
        else:
            cursor.execute("""
                INSERT INTO strategy_stats
                (strategy_name, regime, total_trades, successful_trades, avg_pnl, confidence_score, last_updated)
                VALUES (?, ?, 1, ?, ?, 0.5, ?)
            """, (strategy_name, regime, 1 if success else 0, pnl or 0, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_confidence(self, strategy_name: str, regime: str) -> float:
        """Get confidence score for strategy in regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT confidence_score FROM strategy_stats
            WHERE strategy_name = ? AND regime = ?
        """, (strategy_name, regime))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0.5

    def get_underperforming(self, threshold: float = 0.4) -> List[Dict]:
        """Get strategies needing improvement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT strategy_name, regime, total_trades, successful_trades, avg_pnl, confidence_score
            FROM strategy_stats
            WHERE confidence_score < ? AND total_trades >= 5
            ORDER BY confidence_score ASC
        """, (threshold,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'strategy': r[0], 'regime': r[1], 'trades': r[2],
            'wins': r[3], 'avg_pnl': r[4], 'confidence': r[5]
        } for r in results]

    def get_top_performers(self, regime: str, limit: int = 5) -> List[Dict]:
        """Get top performing strategies for a regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT strategy_name, confidence_score, avg_pnl, total_trades
            FROM strategy_stats
            WHERE regime = ? AND total_trades >= 3
            ORDER BY confidence_score DESC, avg_pnl DESC
            LIMIT ?
        """, (regime, limit))

        results = cursor.fetchall()
        conn.close()

        return [{
            'strategy': r[0], 'confidence': r[1], 'avg_pnl': r[2], 'trades': r[3]
        } for r in results]


class StrategyEngine:
    """
    Unified strategy engine combining regime detection, selection, and memory.
    """

    def __init__(self):
        self.regime_detector = MarketRegimeDetector()
        self.tracker = PerformanceTracker()
        self.strategies = self._load_strategy_library()

    def _load_strategy_library(self) -> Dict:
        """Load strategy library from JSON or create default"""
        if STRATEGY_LIBRARY.exists():
            return json.loads(STRATEGY_LIBRARY.read_text())

        # Create default library from top performers
        default = {
            "version": "1.0",
            "strategies": {
                "BandwidthPulse": {"type": "Breakout", "score": 100, "risk": 0.01},
                "ContangoDivergence": {"type": "Arbitrage", "score": 100, "risk": 0.01},
                "DeltaBandBreakout": {"type": "Breakout", "score": 100, "risk": 0.02},
                "DynamicCrossfire": {"type": "Trend Following", "score": 100, "risk": 0.02},
                "FibroVoltaic": {"type": "Volatility", "score": 100, "risk": 0.02},
                "VolatilityDivergence": {"type": "Mean Reversion", "score": 95, "risk": 0.015},
                "VolCliffArbitrage": {"type": "Arbitrage", "score": 95, "risk": 0.01},
                "MomentumBandwidth": {"type": "Momentum", "score": 90, "risk": 0.02},
                "LiquidationSqueeze": {"type": "Volatility", "score": 85, "risk": 0.02},
                "FractalFibonacci": {"type": "Harmonic", "score": 85, "risk": 0.015}
            }
        }

        STRATEGY_LIBRARY.parent.mkdir(parents=True, exist_ok=True)
        STRATEGY_LIBRARY.write_text(json.dumps(default, indent=2))
        return default

    def analyze(self, market_data: pd.DataFrame) -> Dict:
        """
        Full analysis: detect regime, select strategy, return recommendation.

        Args:
            market_data: DataFrame with OHLCV columns

        Returns:
            Complete analysis with regime, strategy, confidence
        """
        # Step 1: Detect regime
        regime_info = self.regime_detector.detect_regime(market_data)
        regime = regime_info['regime']

        # Step 2: Get candidates for this regime
        recommended_types = regime_info['recommended_types']
        candidates = []

        for name, data in self.strategies.get('strategies', {}).items():
            if data['type'] in recommended_types:
                # Adjust score by historical confidence
                confidence = self.tracker.get_confidence(name, regime)
                adjusted_score = data['score'] * confidence

                candidates.append({
                    'name': name,
                    'type': data['type'],
                    'base_score': data['score'],
                    'confidence': confidence,
                    'adjusted_score': adjusted_score,
                    'risk': data.get('risk', 0.02)
                })

        # Sort by adjusted score
        candidates.sort(key=lambda x: x['adjusted_score'], reverse=True)

        # Step 3: Select best
        selected = candidates[0] if candidates else None

        # Step 4: Get historical top performers for this regime
        top_historical = self.tracker.get_top_performers(regime)

        return {
            'timestamp': datetime.now().isoformat(),
            'regime': regime_info,
            'selected_strategy': selected,
            'alternatives': candidates[1:4] if len(candidates) > 1 else [],
            'historical_top': top_historical,
            'total_candidates': len(candidates)
        }

    def log_result(self, strategy_name: str, regime: str, action: str,
                   entry: float, exit: float = None, success: bool = True):
        """Log trade result for learning"""
        self.tracker.log_trade(strategy_name, regime, action, entry, exit, success)

    def get_improvement_suggestions(self) -> List[Dict]:
        """Get strategies needing improvement"""
        underperforming = self.tracker.get_underperforming()

        suggestions = []
        for strat in underperforming:
            fix = "Add tighter stop-loss" if strat['avg_pnl'] < -3 else "Add confirmation filter"
            suggestions.append({
                'strategy': strat['strategy'],
                'regime': strat['regime'],
                'issue': f"Low confidence ({strat['confidence']:.0%})",
                'suggestion': fix
            })

        return suggestions


# Quick test
if __name__ == "__main__":
    print("Testing Strategy Engine...")

    engine = StrategyEngine()

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=200, freq='15min')
    sample_data = pd.DataFrame({
        'Open': np.random.uniform(95000, 105000, 200),
        'High': np.random.uniform(96000, 106000, 200),
        'Low': np.random.uniform(94000, 104000, 200),
        'Close': np.random.uniform(95000, 105000, 200),
        'Volume': np.random.uniform(1000, 5000, 200)
    }, index=dates)

    # Analyze
    result = engine.analyze(sample_data)

    print(f"\nRegime: {result['regime']['regime']}")
    print(f"ADX: {result['regime']['adx']}")
    print(f"ATR %ile: {result['regime']['atr_percentile']}")

    if result['selected_strategy']:
        print(f"\nSelected: {result['selected_strategy']['name']}")
        print(f"Type: {result['selected_strategy']['type']}")
        print(f"Score: {result['selected_strategy']['adjusted_score']:.1f}")

    print("\nStrategy Engine ready!")
