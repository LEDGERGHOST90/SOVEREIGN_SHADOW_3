#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - Decision Tracer

Full tracing and visualization for multi-agent trading decisions.
Extends ReflectionAgent with comprehensive debugging capabilities.

Traces captured:
1. Regime Detection - inputs, calculations, output
2. Swarm Votes - each agent's vote with reasoning
3. Trade Decisions - final decision with all context
4. Outcomes - what actually happened

Usage:
    from doe_engine.core.intelligence.decision_tracer import get_tracer

    tracer = get_tracer()

    # Record a decision trace
    trace_id = tracer.start_trace("BTC/USD")
    tracer.record_regime(trace_id, regime_data)
    tracer.record_swarm_vote(trace_id, "whale_watcher", vote_data)
    tracer.record_decision(trace_id, decision_data)
    tracer.end_trace(trace_id, outcome_data)

    # View traces
    tracer.show_trace(trace_id)
    tracer.show_recent(limit=10)
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent


@dataclass
class RegimeTrace:
    """Regime detection trace"""
    trace_id: str
    regime: str
    confidence: float
    volatility_percentile: float
    trend_strength: float
    rsi: float
    atr: float
    candle_count: int
    inputs_summary: str
    timestamp: str


@dataclass
class SwarmVote:
    """Individual agent vote"""
    trace_id: str
    agent_id: str
    agent_type: str  # whale_watcher, manus_researcher, sentiment_scanner, etc.
    decision: str  # buy, sell, hold
    confidence: float
    reasoning: str
    data_sources: str  # JSON list of sources used
    timestamp: str


@dataclass
class DecisionTrace:
    """Final trade decision"""
    trace_id: str
    symbol: str
    decision: str  # buy, sell, hold
    confidence: float
    consensus_reached: bool
    vote_breakdown: str  # JSON: {"buy": 2, "sell": 1, "hold": 0}
    strategy_selected: str
    position_size_multiplier: float
    reflection_adjustment: float
    reflection_approach: str  # aggressive, balanced, conservative
    final_reasoning: str
    timestamp: str


@dataclass
class TraceOutcome:
    """What actually happened"""
    trace_id: str
    executed: bool
    entry_price: Optional[float]
    exit_price: Optional[float]
    pnl: Optional[float]
    pnl_percent: Optional[float]
    exit_reason: Optional[str]
    duration_minutes: Optional[int]
    timestamp: str


class DecisionTracer:
    """
    Full decision tracing for debugging multi-agent trading.

    Captures the complete decision tree:

    Trace #1247
    ├─ REGIME: trending_bullish (73%)
    │   └─ Inputs: RSI=62, ATR=450, 100 candles
    ├─ SWARM VOTES:
    │   ├─ whale_watcher: BUY (72%) "Large accumulation"
    │   ├─ manus_researcher: BUY (65%) "Positive news"
    │   └─ sentiment_scanner: HOLD (45%) "Mixed signals"
    ├─ REFLECTION: aggressive (1.1x confidence)
    ├─ DECISION: BUY @ $94,500 (68% confidence)
    └─ OUTCOME: +2.3% in 45 min (TAKE_PROFIT)
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(BASE_DIR / "data" / "decision_traces.db")
        self._init_db()
        self._active_traces: Dict[str, dict] = {}
        logger.info(f"DecisionTracer initialized: {self.db_path}")

    def _init_db(self):
        """Initialize trace database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Regime traces
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regime_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT,
                regime TEXT,
                confidence REAL,
                volatility_percentile REAL,
                trend_strength REAL,
                rsi REAL,
                atr REAL,
                candle_count INTEGER,
                inputs_summary TEXT,
                timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Swarm votes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS swarm_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT,
                agent_id TEXT,
                agent_type TEXT,
                decision TEXT,
                confidence REAL,
                reasoning TEXT,
                data_sources TEXT,
                timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Decision traces
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT UNIQUE,
                symbol TEXT,
                decision TEXT,
                confidence REAL,
                consensus_reached INTEGER,
                vote_breakdown TEXT,
                strategy_selected TEXT,
                position_size_multiplier REAL,
                reflection_adjustment REAL,
                reflection_approach TEXT,
                final_reasoning TEXT,
                timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Trace outcomes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trace_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT UNIQUE,
                executed INTEGER,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                pnl_percent REAL,
                exit_reason TEXT,
                duration_minutes INTEGER,
                timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Index for fast lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_id ON swarm_votes(trace_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision_timestamp ON decision_traces(timestamp)')

        conn.commit()
        conn.close()

    def start_trace(self, symbol: str) -> str:
        """Start a new decision trace, returns trace_id"""
        trace_id = f"T{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        self._active_traces[trace_id] = {
            "symbol": symbol,
            "started_at": datetime.utcnow().isoformat(),
            "regime": None,
            "votes": [],
            "decision": None
        }

        logger.debug(f"Started trace: {trace_id} for {symbol}")
        return trace_id

    def record_regime(
        self,
        trace_id: str,
        regime: str,
        confidence: float,
        volatility_percentile: float = 0,
        trend_strength: float = 0,
        rsi: float = 50,
        atr: float = 0,
        candle_count: int = 0,
        inputs_summary: str = ""
    ):
        """Record regime detection for this trace"""
        trace = RegimeTrace(
            trace_id=trace_id,
            regime=regime,
            confidence=confidence,
            volatility_percentile=volatility_percentile,
            trend_strength=trend_strength,
            rsi=rsi,
            atr=atr,
            candle_count=candle_count,
            inputs_summary=inputs_summary,
            timestamp=datetime.utcnow().isoformat()
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO regime_traces
            (trace_id, regime, confidence, volatility_percentile, trend_strength,
             rsi, atr, candle_count, inputs_summary, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trace.trace_id, trace.regime, trace.confidence,
            trace.volatility_percentile, trace.trend_strength,
            trace.rsi, trace.atr, trace.candle_count,
            trace.inputs_summary, trace.timestamp
        ))
        conn.commit()
        conn.close()

        if trace_id in self._active_traces:
            self._active_traces[trace_id]["regime"] = asdict(trace)

        logger.debug(f"Recorded regime: {regime} ({confidence:.1f}%)")

    def record_swarm_vote(
        self,
        trace_id: str,
        agent_id: str,
        agent_type: str,
        decision: str,
        confidence: float,
        reasoning: str = "",
        data_sources: List[str] = None
    ):
        """Record an individual agent's vote"""
        vote = SwarmVote(
            trace_id=trace_id,
            agent_id=agent_id,
            agent_type=agent_type,
            decision=decision.lower(),
            confidence=confidence,
            reasoning=reasoning,
            data_sources=json.dumps(data_sources or []),
            timestamp=datetime.utcnow().isoformat()
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO swarm_votes
            (trace_id, agent_id, agent_type, decision, confidence, reasoning, data_sources, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vote.trace_id, vote.agent_id, vote.agent_type,
            vote.decision, vote.confidence, vote.reasoning,
            vote.data_sources, vote.timestamp
        ))
        conn.commit()
        conn.close()

        if trace_id in self._active_traces:
            self._active_traces[trace_id]["votes"].append(asdict(vote))

        logger.debug(f"Recorded vote: {agent_id} -> {decision} ({confidence:.1f}%)")

    def record_decision(
        self,
        trace_id: str,
        symbol: str,
        decision: str,
        confidence: float,
        consensus_reached: bool,
        vote_breakdown: Dict[str, int],
        strategy_selected: str = "",
        position_size_multiplier: float = 1.0,
        reflection_adjustment: float = 1.0,
        reflection_approach: str = "balanced",
        final_reasoning: str = ""
    ):
        """Record the final trade decision"""
        trace = DecisionTrace(
            trace_id=trace_id,
            symbol=symbol,
            decision=decision.lower(),
            confidence=confidence,
            consensus_reached=consensus_reached,
            vote_breakdown=json.dumps(vote_breakdown),
            strategy_selected=strategy_selected,
            position_size_multiplier=position_size_multiplier,
            reflection_adjustment=reflection_adjustment,
            reflection_approach=reflection_approach,
            final_reasoning=final_reasoning,
            timestamp=datetime.utcnow().isoformat()
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO decision_traces
            (trace_id, symbol, decision, confidence, consensus_reached, vote_breakdown,
             strategy_selected, position_size_multiplier, reflection_adjustment,
             reflection_approach, final_reasoning, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trace.trace_id, trace.symbol, trace.decision, trace.confidence,
            1 if trace.consensus_reached else 0, trace.vote_breakdown,
            trace.strategy_selected, trace.position_size_multiplier,
            trace.reflection_adjustment, trace.reflection_approach,
            trace.final_reasoning, trace.timestamp
        ))
        conn.commit()
        conn.close()

        if trace_id in self._active_traces:
            self._active_traces[trace_id]["decision"] = asdict(trace)

        logger.info(f"Decision recorded: {trace_id} -> {decision.upper()} ({confidence:.1f}%)")

    def record_outcome(
        self,
        trace_id: str,
        executed: bool,
        entry_price: float = None,
        exit_price: float = None,
        pnl: float = None,
        pnl_percent: float = None,
        exit_reason: str = None,
        duration_minutes: int = None
    ):
        """Record what actually happened after the decision"""
        outcome = TraceOutcome(
            trace_id=trace_id,
            executed=executed,
            entry_price=entry_price,
            exit_price=exit_price,
            pnl=pnl,
            pnl_percent=pnl_percent,
            exit_reason=exit_reason,
            duration_minutes=duration_minutes,
            timestamp=datetime.utcnow().isoformat()
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO trace_outcomes
            (trace_id, executed, entry_price, exit_price, pnl, pnl_percent,
             exit_reason, duration_minutes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            outcome.trace_id, 1 if outcome.executed else 0,
            outcome.entry_price, outcome.exit_price, outcome.pnl,
            outcome.pnl_percent, outcome.exit_reason, outcome.duration_minutes,
            outcome.timestamp
        ))
        conn.commit()
        conn.close()

        # Remove from active traces
        if trace_id in self._active_traces:
            del self._active_traces[trace_id]

        logger.info(f"Outcome recorded: {trace_id} -> {'EXECUTED' if executed else 'SKIPPED'}")

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Get complete trace by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get decision
        cursor.execute('SELECT * FROM decision_traces WHERE trace_id = ?', (trace_id,))
        decision_row = cursor.fetchone()

        if not decision_row:
            conn.close()
            return None

        decision = dict(decision_row)

        # Get regime
        cursor.execute('SELECT * FROM regime_traces WHERE trace_id = ?', (trace_id,))
        regime_row = cursor.fetchone()
        regime = dict(regime_row) if regime_row else None

        # Get votes
        cursor.execute('SELECT * FROM swarm_votes WHERE trace_id = ? ORDER BY timestamp', (trace_id,))
        votes = [dict(row) for row in cursor.fetchall()]

        # Get outcome
        cursor.execute('SELECT * FROM trace_outcomes WHERE trace_id = ?', (trace_id,))
        outcome_row = cursor.fetchone()
        outcome = dict(outcome_row) if outcome_row else None

        conn.close()

        return {
            "trace_id": trace_id,
            "decision": decision,
            "regime": regime,
            "votes": votes,
            "outcome": outcome
        }

    def get_recent_traces(self, limit: int = 20) -> List[Dict]:
        """Get recent decision traces"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT d.*, o.executed, o.pnl_percent, o.exit_reason
            FROM decision_traces d
            LEFT JOIN trace_outcomes o ON d.trace_id = o.trace_id
            ORDER BY d.timestamp DESC
            LIMIT ?
        ''', (limit,))

        traces = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return traces

    def show_trace(self, trace_id: str) -> str:
        """Generate human-readable trace visualization"""
        trace = self.get_trace(trace_id)

        if not trace:
            return f"Trace {trace_id} not found"

        d = trace["decision"]
        r = trace["regime"]
        votes = trace["votes"]
        o = trace["outcome"]

        # Build tree visualization
        lines = [
            f"",
            f"{'='*60}",
            f"TRACE: {trace_id}",
            f"{'='*60}",
            f"Symbol: {d['symbol']}",
            f"Time: {d['timestamp']}",
            f""
        ]

        # Regime
        if r:
            lines.append(f"├─ REGIME: {r['regime']} ({r['confidence']:.1f}% confidence)")
            lines.append(f"│   ├─ RSI: {r['rsi']:.1f}")
            lines.append(f"│   ├─ ATR: {r['atr']:.2f}")
            lines.append(f"│   ├─ Trend Strength: {r['trend_strength']:.2f}")
            lines.append(f"│   └─ Volatility: {r['volatility_percentile']:.1f}%")

        # Votes
        if votes:
            lines.append(f"│")
            lines.append(f"├─ SWARM VOTES ({len(votes)} agents):")
            for i, v in enumerate(votes):
                prefix = "│   └─" if i == len(votes) - 1 else "│   ├─"
                emoji = "🟢" if v['decision'] == 'buy' else "🔴" if v['decision'] == 'sell' else "⚪"
                lines.append(f"{prefix} {emoji} {v['agent_type']}: {v['decision'].upper()} ({v['confidence']*100:.0f}%)")
                if v['reasoning']:
                    lines.append(f"│       \"{v['reasoning'][:50]}...\"" if len(v['reasoning']) > 50 else f"│       \"{v['reasoning']}\"")

        # Reflection
        lines.append(f"│")
        lines.append(f"├─ REFLECTION: {d['reflection_approach']} ({d['reflection_adjustment']:.2f}x)")

        # Decision
        vote_breakdown = json.loads(d['vote_breakdown'])
        consensus = "✅" if d['consensus_reached'] else "❌"
        decision_emoji = "🟢" if d['decision'] == 'buy' else "🔴" if d['decision'] == 'sell' else "⚪"

        lines.append(f"│")
        lines.append(f"├─ DECISION: {decision_emoji} {d['decision'].upper()}")
        lines.append(f"│   ├─ Confidence: {d['confidence']:.1f}%")
        lines.append(f"│   ├─ Consensus: {consensus} ({vote_breakdown})")
        lines.append(f"│   ├─ Strategy: {d['strategy_selected'] or 'N/A'}")
        lines.append(f"│   └─ Size Multiplier: {d['position_size_multiplier']:.2f}x")

        # Outcome
        if o:
            lines.append(f"│")
            if o['executed']:
                pnl_emoji = "📈" if (o['pnl_percent'] or 0) > 0 else "📉"
                lines.append(f"└─ OUTCOME: {pnl_emoji} {o['pnl_percent']:+.2f}%")
                lines.append(f"    ├─ Entry: ${o['entry_price']:,.2f}")
                lines.append(f"    ├─ Exit: ${o['exit_price']:,.2f}")
                lines.append(f"    ├─ P&L: ${o['pnl']:+,.2f}")
                lines.append(f"    ├─ Reason: {o['exit_reason']}")
                lines.append(f"    └─ Duration: {o['duration_minutes']} min")
            else:
                lines.append(f"└─ OUTCOME: ⏸️  NOT EXECUTED")
        else:
            lines.append(f"│")
            lines.append(f"└─ OUTCOME: ⏳ PENDING")

        lines.append(f"{'='*60}")

        return "\n".join(lines)

    def show_recent(self, limit: int = 10) -> str:
        """Show recent traces summary"""
        traces = self.get_recent_traces(limit)

        if not traces:
            return "No traces found"

        lines = [
            "",
            "=" * 80,
            f"RECENT DECISION TRACES (last {len(traces)})",
            "=" * 80,
            f"{'TRACE ID':<25} {'SYMBOL':<10} {'DECISION':<8} {'CONF':<6} {'P&L':<10} {'REASON':<15}",
            "-" * 80
        ]

        for t in traces:
            pnl = f"{t['pnl_percent']:+.2f}%" if t['pnl_percent'] else "pending"
            reason = (t['exit_reason'] or "")[:12]
            lines.append(
                f"{t['trace_id']:<25} {t['symbol']:<10} {t['decision'].upper():<8} "
                f"{t['confidence']:.0f}%   {pnl:<10} {reason:<15}"
            )

        lines.append("=" * 80)

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get tracing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM decision_traces')
        total_traces = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM trace_outcomes WHERE executed = 1')
        executed = cursor.fetchone()[0]

        cursor.execute('SELECT AVG(pnl_percent) FROM trace_outcomes WHERE executed = 1 AND pnl_percent IS NOT NULL')
        avg_pnl = cursor.fetchone()[0] or 0

        cursor.execute('SELECT COUNT(*) FROM trace_outcomes WHERE executed = 1 AND pnl_percent > 0')
        winners = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT agent_type) FROM swarm_votes')
        agent_types = cursor.fetchone()[0]

        conn.close()

        win_rate = (winners / executed * 100) if executed > 0 else 0

        return {
            "total_traces": total_traces,
            "executed_trades": executed,
            "win_rate": win_rate,
            "avg_pnl_percent": avg_pnl,
            "agent_types": agent_types,
            "active_traces": len(self._active_traces)
        }


# Singleton
_tracer: Optional[DecisionTracer] = None


def get_tracer() -> DecisionTracer:
    """Get or create the global DecisionTracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = DecisionTracer()
    return _tracer


# CLI interface
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    tracer = DecisionTracer()

    if len(sys.argv) < 2:
        print("""
Decision Tracer CLI
-------------------
Usage:
    python decision_tracer.py recent [limit]    Show recent traces
    python decision_tracer.py show <trace_id>   Show specific trace
    python decision_tracer.py stats             Show statistics
    python decision_tracer.py demo              Run demo with sample data
        """)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(tracer.show_recent(limit))

    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: python decision_tracer.py show <trace_id>")
            sys.exit(1)
        print(tracer.show_trace(sys.argv[2]))

    elif cmd == "stats":
        stats = tracer.get_stats()
        print("\n=== TRACER STATISTICS ===")
        print(f"Total Traces: {stats['total_traces']}")
        print(f"Executed Trades: {stats['executed_trades']}")
        print(f"Win Rate: {stats['win_rate']:.1f}%")
        print(f"Avg P&L: {stats['avg_pnl_percent']:.2f}%")
        print(f"Agent Types: {stats['agent_types']}")
        print(f"Active Traces: {stats['active_traces']}")

    elif cmd == "demo":
        print("Running demo trace...")

        # Create a demo trace
        trace_id = tracer.start_trace("BTC/USD")

        # Record regime
        tracer.record_regime(
            trace_id=trace_id,
            regime="trending_bullish",
            confidence=73.5,
            volatility_percentile=45.0,
            trend_strength=0.72,
            rsi=62.3,
            atr=450.0,
            candle_count=100,
            inputs_summary="15m candles, last 100"
        )

        # Record swarm votes
        tracer.record_swarm_vote(
            trace_id=trace_id,
            agent_id="swarm_whale_watcher",
            agent_type="whale_watcher",
            decision="buy",
            confidence=0.72,
            reasoning="Large accumulation detected on Binance",
            data_sources=["binance_flow", "whale_alert"]
        )

        tracer.record_swarm_vote(
            trace_id=trace_id,
            agent_id="swarm_manus",
            agent_type="manus_researcher",
            decision="buy",
            confidence=0.65,
            reasoning="Positive sentiment from institutional news",
            data_sources=["manus_api", "news_feed"]
        )

        tracer.record_swarm_vote(
            trace_id=trace_id,
            agent_id="swarm_sentiment",
            agent_type="sentiment_scanner",
            decision="hold",
            confidence=0.45,
            reasoning="Mixed signals from social media",
            data_sources=["twitter", "reddit"]
        )

        # Record decision
        tracer.record_decision(
            trace_id=trace_id,
            symbol="BTC/USD",
            decision="buy",
            confidence=68.0,
            consensus_reached=True,
            vote_breakdown={"buy": 2, "sell": 0, "hold": 1},
            strategy_selected="TrendFollowEMA",
            position_size_multiplier=0.75,
            reflection_adjustment=1.1,
            reflection_approach="aggressive",
            final_reasoning="Strong bullish consensus with on-chain confirmation"
        )

        # Record outcome
        tracer.record_outcome(
            trace_id=trace_id,
            executed=True,
            entry_price=94500.0,
            exit_price=96700.0,
            pnl=220.0,
            pnl_percent=2.33,
            exit_reason="TAKE_PROFIT",
            duration_minutes=45
        )

        print(tracer.show_trace(trace_id))
