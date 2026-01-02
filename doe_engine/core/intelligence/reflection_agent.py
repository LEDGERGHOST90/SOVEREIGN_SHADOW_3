#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - Reflection Agent (Learning Layer)

Based on CryptoTrade EMNLP 2024 paper findings:
- Reflection mechanism adds +11% to returns
- Reviews past week's trades, identifies patterns
- Provides feedback to Trading Agent for future decisions

The Reflection Agent analyzes:
1. Past prompts/context given
2. Decisions made (buy/sell/hold)
3. Actual returns achieved
4. What information was most impactful
5. Why certain strategies succeeded/failed
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

# Base directory for D.O.E. engine
BASE_DIR = Path(__file__).parent.parent.parent


@dataclass
class TradeReflection:
    """Single trade reflection entry"""
    trade_id: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    entry_price: float
    exit_price: Optional[float]
    return_pct: float
    regime_at_trade: str
    strategy_used: str
    news_sentiment: str  # bullish, bearish, neutral
    on_chain_signal: str  # bullish, bearish, neutral
    reasoning: str
    outcome: str  # profitable, loss, breakeven
    lesson_learned: str
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class WeeklyReflection:
    """Weekly aggregate reflection"""
    week_start: str
    week_end: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_return_pct: float
    best_trade: Optional[TradeReflection]
    worst_trade: Optional[TradeReflection]

    # Pattern analysis
    effective_strategies: List[str] = field(default_factory=list)
    ineffective_strategies: List[str] = field(default_factory=list)
    effective_signals: List[str] = field(default_factory=list)
    ineffective_signals: List[str] = field(default_factory=list)

    # Recommendations
    recommended_approach: str = "balanced"  # aggressive, conservative, balanced
    key_insights: List[str] = field(default_factory=list)
    avoid_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.best_trade:
            result['best_trade'] = self.best_trade.to_dict()
        if self.worst_trade:
            result['worst_trade'] = self.worst_trade.to_dict()
        return result


class ReflectionAgent:
    """
    Learns from past trading decisions to improve future performance.

    Based on CryptoTrade paper's reflection mechanism that achieved +11% improvement.

    Key functions:
    1. Record trade outcomes with full context
    2. Analyze weekly performance patterns
    3. Identify effective vs ineffective strategies
    4. Generate actionable insights for Trading Agent
    5. Adjust risk tolerance based on recent performance
    """

    def __init__(self, db_path: str = None):
        """Initialize the Reflection Agent"""
        self.db_path = db_path or str(BASE_DIR / "data" / "reflections.db")
        self._init_db()

        # Reflection parameters
        self.lookback_days = 7  # Analyze past week
        self.min_trades_for_pattern = 3  # Minimum trades to identify pattern

        # Current state
        self.current_reflection: Optional[WeeklyReflection] = None
        self.trade_history: List[TradeReflection] = []

        logger.info(f"ReflectionAgent initialized with db: {self.db_path}")

    def _init_db(self):
        """Initialize SQLite database for reflections"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trade reflections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                symbol TEXT,
                action TEXT,
                entry_price REAL,
                exit_price REAL,
                return_pct REAL,
                regime_at_trade TEXT,
                strategy_used TEXT,
                news_sentiment TEXT,
                on_chain_signal TEXT,
                reasoning TEXT,
                outcome TEXT,
                lesson_learned TEXT,
                timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Weekly reflections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start TEXT,
                week_end TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_return_pct REAL,
                effective_strategies TEXT,
                ineffective_strategies TEXT,
                effective_signals TEXT,
                ineffective_signals TEXT,
                recommended_approach TEXT,
                key_insights TEXT,
                avoid_patterns TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def record_trade(
        self,
        trade_id: str,
        symbol: str,
        action: str,
        entry_price: float,
        exit_price: Optional[float],
        return_pct: float,
        regime: str,
        strategy: str,
        news_sentiment: str = "neutral",
        on_chain_signal: str = "neutral",
        reasoning: str = ""
    ) -> TradeReflection:
        """
        Record a completed trade for reflection analysis.

        Args:
            trade_id: Unique identifier for the trade
            symbol: Trading pair (e.g., LINK/USDC)
            action: BUY, SELL, or HOLD
            entry_price: Entry price
            exit_price: Exit price (None if still open)
            return_pct: Return percentage
            regime: Market regime at time of trade
            strategy: Strategy that generated the signal
            news_sentiment: Manus news sentiment
            on_chain_signal: On-chain data signal
            reasoning: Why this trade was made

        Returns:
            TradeReflection object
        """
        # Determine outcome
        if return_pct > 0.5:
            outcome = "profitable"
        elif return_pct < -0.5:
            outcome = "loss"
        else:
            outcome = "breakeven"

        # Generate lesson learned based on outcome
        lesson = self._generate_lesson(
            action, return_pct, regime, strategy, news_sentiment, on_chain_signal
        )

        reflection = TradeReflection(
            trade_id=trade_id,
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            exit_price=exit_price,
            return_pct=return_pct,
            regime_at_trade=regime,
            strategy_used=strategy,
            news_sentiment=news_sentiment,
            on_chain_signal=on_chain_signal,
            reasoning=reasoning,
            outcome=outcome,
            lesson_learned=lesson,
            timestamp=datetime.utcnow().isoformat()
        )

        # Save to database
        self._save_trade_reflection(reflection)
        self.trade_history.append(reflection)

        logger.info(f"Recorded trade reflection: {trade_id} -> {outcome} ({return_pct:.2f}%)")

        return reflection

    def _generate_lesson(
        self,
        action: str,
        return_pct: float,
        regime: str,
        strategy: str,
        news_sentiment: str,
        on_chain_signal: str
    ) -> str:
        """Generate a lesson learned from the trade outcome"""
        lessons = []

        if return_pct > 5:
            lessons.append(f"{strategy} strategy effective in {regime} regime")
            if news_sentiment == "bullish" and action == "BUY":
                lessons.append("News sentiment aligned with buy decision")
            if on_chain_signal == "bullish" and action == "BUY":
                lessons.append("On-chain signals confirmed entry")
        elif return_pct < -5:
            lessons.append(f"{strategy} strategy underperformed in {regime} regime")
            if news_sentiment != "bullish" and action == "BUY":
                lessons.append("Should have waited for bullish news confirmation")
            if on_chain_signal != "bullish" and action == "BUY":
                lessons.append("On-chain data did not support entry")
        else:
            lessons.append("Marginal trade - consider tighter entry criteria")

        return "; ".join(lessons) if lessons else "No clear lesson"

    def _save_trade_reflection(self, reflection: TradeReflection):
        """Save trade reflection to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO trade_reflections
                (trade_id, symbol, action, entry_price, exit_price, return_pct,
                 regime_at_trade, strategy_used, news_sentiment, on_chain_signal,
                 reasoning, outcome, lesson_learned, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reflection.trade_id, reflection.symbol, reflection.action,
                reflection.entry_price, reflection.exit_price, reflection.return_pct,
                reflection.regime_at_trade, reflection.strategy_used,
                reflection.news_sentiment, reflection.on_chain_signal,
                reflection.reasoning, reflection.outcome, reflection.lesson_learned,
                reflection.timestamp
            ))
            conn.commit()
        finally:
            conn.close()

    def generate_weekly_reflection(self) -> WeeklyReflection:
        """
        Generate a comprehensive weekly reflection.

        This is the core function that analyzes past performance
        and provides actionable insights for the Trading Agent.
        """
        # Get trades from past week
        week_ago = datetime.utcnow() - timedelta(days=self.lookback_days)
        recent_trades = self._get_trades_since(week_ago)

        if not recent_trades:
            logger.info("No trades in past week to reflect on")
            return WeeklyReflection(
                week_start=week_ago.isoformat(),
                week_end=datetime.utcnow().isoformat(),
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_return_pct=0,
                best_trade=None,
                worst_trade=None,
                key_insights=["No trades to analyze - consider more active positioning"]
            )

        # Calculate statistics
        winning = [t for t in recent_trades if t.outcome == "profitable"]
        losing = [t for t in recent_trades if t.outcome == "loss"]
        total_return = sum(t.return_pct for t in recent_trades)

        # Find best and worst trades
        best_trade = max(recent_trades, key=lambda t: t.return_pct)
        worst_trade = min(recent_trades, key=lambda t: t.return_pct)

        # Analyze patterns
        effective_strategies, ineffective_strategies = self._analyze_strategy_performance(recent_trades)
        effective_signals, ineffective_signals = self._analyze_signal_performance(recent_trades)

        # Determine recommended approach
        win_rate = len(winning) / len(recent_trades) if recent_trades else 0
        if win_rate > 0.6 and total_return > 5:
            recommended = "aggressive"
        elif win_rate < 0.4 or total_return < -5:
            recommended = "conservative"
        else:
            recommended = "balanced"

        # Generate insights
        insights = self._generate_insights(
            recent_trades, effective_strategies, ineffective_strategies,
            effective_signals, ineffective_signals
        )

        # Identify patterns to avoid
        avoid = self._identify_avoid_patterns(losing)

        reflection = WeeklyReflection(
            week_start=week_ago.isoformat(),
            week_end=datetime.utcnow().isoformat(),
            total_trades=len(recent_trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            total_return_pct=total_return,
            best_trade=best_trade,
            worst_trade=worst_trade,
            effective_strategies=effective_strategies,
            ineffective_strategies=ineffective_strategies,
            effective_signals=effective_signals,
            ineffective_signals=ineffective_signals,
            recommended_approach=recommended,
            key_insights=insights,
            avoid_patterns=avoid
        )

        # Save to database
        self._save_weekly_reflection(reflection)
        self.current_reflection = reflection

        logger.info(f"Generated weekly reflection: {len(recent_trades)} trades, {total_return:.2f}% return")

        return reflection

    def _get_trades_since(self, since: datetime) -> List[TradeReflection]:
        """Get trades from database since a given date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT trade_id, symbol, action, entry_price, exit_price, return_pct,
                   regime_at_trade, strategy_used, news_sentiment, on_chain_signal,
                   reasoning, outcome, lesson_learned, timestamp
            FROM trade_reflections
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (since.isoformat(),))

        trades = []
        for row in cursor.fetchall():
            trades.append(TradeReflection(
                trade_id=row[0], symbol=row[1], action=row[2],
                entry_price=row[3], exit_price=row[4], return_pct=row[5],
                regime_at_trade=row[6], strategy_used=row[7],
                news_sentiment=row[8], on_chain_signal=row[9],
                reasoning=row[10], outcome=row[11],
                lesson_learned=row[12], timestamp=row[13]
            ))

        conn.close()
        return trades

    def _analyze_strategy_performance(
        self, trades: List[TradeReflection]
    ) -> Tuple[List[str], List[str]]:
        """Analyze which strategies performed well vs poorly"""
        strategy_returns = {}

        for trade in trades:
            strategy = trade.strategy_used
            if strategy not in strategy_returns:
                strategy_returns[strategy] = []
            strategy_returns[strategy].append(trade.return_pct)

        effective = []
        ineffective = []

        for strategy, returns in strategy_returns.items():
            if len(returns) >= self.min_trades_for_pattern:
                avg_return = sum(returns) / len(returns)
                if avg_return > 1:
                    effective.append(f"{strategy} (avg: {avg_return:.1f}%)")
                elif avg_return < -1:
                    ineffective.append(f"{strategy} (avg: {avg_return:.1f}%)")

        return effective, ineffective

    def _analyze_signal_performance(
        self, trades: List[TradeReflection]
    ) -> Tuple[List[str], List[str]]:
        """Analyze which signal combinations worked well"""
        signal_returns = {}

        for trade in trades:
            # Create signal combo key
            combo = f"{trade.news_sentiment}+{trade.on_chain_signal}"
            if combo not in signal_returns:
                signal_returns[combo] = []
            signal_returns[combo].append(trade.return_pct)

        effective = []
        ineffective = []

        for combo, returns in signal_returns.items():
            if len(returns) >= 2:  # Lower threshold for signal combos
                avg_return = sum(returns) / len(returns)
                if avg_return > 1:
                    effective.append(f"{combo} signals (avg: {avg_return:.1f}%)")
                elif avg_return < -1:
                    ineffective.append(f"{combo} signals (avg: {avg_return:.1f}%)")

        return effective, ineffective

    def _generate_insights(
        self,
        trades: List[TradeReflection],
        effective_strategies: List[str],
        ineffective_strategies: List[str],
        effective_signals: List[str],
        ineffective_signals: List[str]
    ) -> List[str]:
        """Generate actionable insights from the analysis"""
        insights = []

        # Strategy insights
        if effective_strategies:
            insights.append(f"Continue using: {', '.join(effective_strategies)}")
        if ineffective_strategies:
            insights.append(f"Reduce reliance on: {', '.join(ineffective_strategies)}")

        # Signal insights
        if effective_signals:
            insights.append(f"Trust signal combos: {', '.join(effective_signals)}")
        if ineffective_signals:
            insights.append(f"Be cautious with: {', '.join(ineffective_signals)}")

        # Regime insights
        regime_performance = {}
        for trade in trades:
            regime = trade.regime_at_trade
            if regime not in regime_performance:
                regime_performance[regime] = []
            regime_performance[regime].append(trade.return_pct)

        for regime, returns in regime_performance.items():
            avg = sum(returns) / len(returns)
            if avg > 2:
                insights.append(f"Performed well in {regime} regime (+{avg:.1f}%)")
            elif avg < -2:
                insights.append(f"Struggled in {regime} regime ({avg:.1f}%)")

        # News vs on-chain comparison
        news_aligned = [t for t in trades if t.news_sentiment == "bullish" and t.action == "BUY"]
        onchain_aligned = [t for t in trades if t.on_chain_signal == "bullish" and t.action == "BUY"]

        if news_aligned:
            news_avg = sum(t.return_pct for t in news_aligned) / len(news_aligned)
            insights.append(f"News-aligned trades avg: {news_avg:.1f}%")

        if onchain_aligned:
            onchain_avg = sum(t.return_pct for t in onchain_aligned) / len(onchain_aligned)
            insights.append(f"On-chain-aligned trades avg: {onchain_avg:.1f}%")

        return insights[:10]  # Limit to top 10 insights

    def _identify_avoid_patterns(self, losing_trades: List[TradeReflection]) -> List[str]:
        """Identify patterns that led to losses"""
        avoid = []

        if not losing_trades:
            return avoid

        # Check for common patterns in losses
        regime_counts = {}
        strategy_counts = {}

        for trade in losing_trades:
            regime_counts[trade.regime_at_trade] = regime_counts.get(trade.regime_at_trade, 0) + 1
            strategy_counts[trade.strategy_used] = strategy_counts.get(trade.strategy_used, 0) + 1

        # Flag regimes with multiple losses
        for regime, count in regime_counts.items():
            if count >= 2:
                avoid.append(f"Avoid aggressive entries in {regime} regime")

        # Flag strategies with multiple losses
        for strategy, count in strategy_counts.items():
            if count >= 2:
                avoid.append(f"Re-evaluate {strategy} strategy parameters")

        # Check for contra-signal trades
        contra_trades = [t for t in losing_trades
                        if (t.news_sentiment == "bearish" and t.action == "BUY") or
                           (t.on_chain_signal == "bearish" and t.action == "BUY")]
        if contra_trades:
            avoid.append("Avoid buying against bearish news/on-chain signals")

        return avoid

    def _save_weekly_reflection(self, reflection: WeeklyReflection):
        """Save weekly reflection to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO weekly_reflections
                (week_start, week_end, total_trades, winning_trades, losing_trades,
                 total_return_pct, effective_strategies, ineffective_strategies,
                 effective_signals, ineffective_signals, recommended_approach,
                 key_insights, avoid_patterns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reflection.week_start, reflection.week_end,
                reflection.total_trades, reflection.winning_trades,
                reflection.losing_trades, reflection.total_return_pct,
                json.dumps(reflection.effective_strategies),
                json.dumps(reflection.ineffective_strategies),
                json.dumps(reflection.effective_signals),
                json.dumps(reflection.ineffective_signals),
                reflection.recommended_approach,
                json.dumps(reflection.key_insights),
                json.dumps(reflection.avoid_patterns)
            ))
            conn.commit()
        finally:
            conn.close()

    def get_trading_guidance(self) -> Dict[str, Any]:
        """
        Get current trading guidance based on reflections.

        This is called by the Trading Agent before making decisions.

        Returns:
            Dict with guidance including:
            - recommended_approach: aggressive/conservative/balanced
            - preferred_strategies: list of effective strategies
            - avoid_strategies: list to avoid
            - signal_weights: how much to weight each signal type
            - key_warnings: important cautions
        """
        if not self.current_reflection:
            self.generate_weekly_reflection()

        reflection = self.current_reflection

        if not reflection or reflection.total_trades == 0:
            return {
                "recommended_approach": "balanced",
                "preferred_strategies": [],
                "avoid_strategies": [],
                "signal_weights": {
                    "technical": 0.4,
                    "news": 0.3,
                    "on_chain": 0.3
                },
                "key_warnings": [],
                "confidence_adjustment": 1.0
            }

        # Calculate signal weights based on performance
        signal_weights = {"technical": 0.4, "news": 0.3, "on_chain": 0.3}

        # Adjust based on what worked
        if any("on-chain" in s.lower() for s in reflection.effective_signals):
            signal_weights["on_chain"] = 0.4
            signal_weights["technical"] = 0.3
        if any("news" in s.lower() for s in reflection.effective_signals):
            signal_weights["news"] = 0.35

        # Calculate confidence adjustment
        win_rate = reflection.winning_trades / reflection.total_trades if reflection.total_trades > 0 else 0.5
        if win_rate > 0.6:
            confidence_adj = 1.1  # Slightly increase position sizes
        elif win_rate < 0.4:
            confidence_adj = 0.8  # Reduce position sizes
        else:
            confidence_adj = 1.0

        return {
            "recommended_approach": reflection.recommended_approach,
            "preferred_strategies": reflection.effective_strategies,
            "avoid_strategies": reflection.ineffective_strategies,
            "signal_weights": signal_weights,
            "key_warnings": reflection.avoid_patterns,
            "key_insights": reflection.key_insights,
            "confidence_adjustment": confidence_adj,
            "win_rate": win_rate,
            "total_return": reflection.total_return_pct
        }

    def get_reflection_summary(self) -> str:
        """Get a human-readable summary of current reflection state"""
        guidance = self.get_trading_guidance()

        summary = f"""
=== REFLECTION AGENT SUMMARY ===
Recommended Approach: {guidance['recommended_approach'].upper()}
Win Rate: {guidance['win_rate']*100:.1f}%
Total Return: {guidance['total_return']:.2f}%
Confidence Adjustment: {guidance['confidence_adjustment']:.2f}x

Signal Weights:
  Technical: {guidance['signal_weights']['technical']*100:.0f}%
  News:      {guidance['signal_weights']['news']*100:.0f}%
  On-chain:  {guidance['signal_weights']['on_chain']*100:.0f}%

Preferred Strategies: {', '.join(guidance['preferred_strategies']) or 'None identified'}
Avoid Strategies: {', '.join(guidance['avoid_strategies']) or 'None identified'}

Key Insights:
{chr(10).join('  - ' + i for i in guidance.get('key_insights', [])) or '  None yet'}

Warnings:
{chr(10).join('  - ' + w for w in guidance['key_warnings']) or '  None'}
================================
"""
        return summary


# Singleton instance
_reflection_agent: Optional[ReflectionAgent] = None


def get_reflection_agent() -> ReflectionAgent:
    """Get or create the global ReflectionAgent instance"""
    global _reflection_agent
    if _reflection_agent is None:
        _reflection_agent = ReflectionAgent()
    return _reflection_agent


if __name__ == "__main__":
    # Test the reflection agent
    logging.basicConfig(level=logging.INFO)

    agent = ReflectionAgent()

    # Record some test trades
    agent.record_trade(
        trade_id="test_001",
        symbol="LINK/USDC",
        action="BUY",
        entry_price=12.40,
        exit_price=13.50,
        return_pct=8.87,
        regime="trending_bullish",
        strategy="RSIReversion",
        news_sentiment="bullish",
        on_chain_signal="bullish",
        reasoning="Manus RWA thesis + on-chain accumulation"
    )

    agent.record_trade(
        trade_id="test_002",
        symbol="FET/USDC",
        action="BUY",
        entry_price=0.21,
        exit_price=0.19,
        return_pct=-9.52,
        regime="choppy_volatile",
        strategy="TrendFollowEMA",
        news_sentiment="neutral",
        on_chain_signal="bearish",
        reasoning="AI sector momentum play"
    )

    # Generate weekly reflection
    reflection = agent.generate_weekly_reflection()

    # Print summary
    print(agent.get_reflection_summary())
