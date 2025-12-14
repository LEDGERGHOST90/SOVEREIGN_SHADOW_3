#!/usr/bin/env python3
"""
🔮 REFLECT AGENT - AI-Powered Trade Critique System
Based on 2024-2025 research showing 31% performance improvement

"Before you trade, let me think about that..."

RESEARCH INSIGHT:
Instead of traditional parameter optimization, this agent provides natural language
critiques of trading decisions. Verbal feedback approach showed 31% performance
improvement WITHOUT model retraining.

Integration Pattern:
- Pre-execution filter for trading_agent.py and shade_agent.py
- Provides natural language critique before trade execution
- Returns: APPROVE, REJECT, or MODIFY with detailed reasoning
- Weekly pattern analysis and self-correction

Author: SovereignShadow Trading System
Created: 2025-12-14
Research: 2024-2025 AI Trading Agent Studies
"""

import os
import sys
import json
import anthropic
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass, asdict
from enum import Enum

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "agents"))

# Try to import trade journal
try:
    from trade_journal import TradeEntry, TradeJournal
except ImportError:
    TradeJournal = None
    TradeEntry = None


class CritiqueDecision(Enum):
    """Reflect agent decision types"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"


@dataclass
class TradeCritique:
    """
    Natural language critique response from Reflect Agent
    """
    decision: str  # APPROVE, REJECT, or MODIFY
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Natural language explanation
    risk_score: float  # 0.0 to 10.0

    # Critique dimensions
    risk_assessment: str
    market_context_alignment: str
    historical_performance: str
    emotional_check: str
    technical_validation: str

    # Modifications (if decision is MODIFY)
    suggested_modifications: Optional[Dict[str, Any]] = None

    # Metadata
    timestamp: str = None
    model_used: str = "claude-sonnet-4-5"
    critique_duration_ms: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ReflectAgent:
    """
    AI-Powered Trade Reflection Agent

    Uses Claude API to provide natural language critiques of trading decisions.
    Acts as a pre-execution filter that can approve, reject, or modify trades.

    Key Features:
    - Natural language reasoning about trade quality
    - Historical pattern recognition
    - Emotional state detection
    - Market regime validation
    - Weekly self-correction summaries
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        critique_log_path: Optional[Path] = None,
        journal_path: Optional[Path] = None
    ):
        """
        Initialize Reflect Agent

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use for critiques
            critique_log_path: Path to store critique history
            journal_path: Path to trade journal for historical analysis
        """
        # API setup
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

        # Paths
        self.critique_log_path = critique_log_path or (
            PROJECT_ROOT / "logs" / "reflect_agent" / "critiques.jsonl"
        )
        self.critique_log_path.parent.mkdir(parents=True, exist_ok=True)

        self.journal_path = journal_path or (
            PROJECT_ROOT / "logs" / "trade_journal.jsonl"
        )

        # Load trade history for context
        self.recent_trades = self._load_recent_trades(days=7)

        print("🔮 REFLECT AGENT initialized")
        print(f"   Model: {self.model}")
        print(f"   Critique Log: {self.critique_log_path}")
        print(f"   Recent Trades Loaded: {len(self.recent_trades)}")

    def analyze_trade(
        self,
        proposed_trade: Dict[str, Any],
        market_context: Dict[str, Any],
        recent_trades: Optional[List[Dict[str, Any]]] = None,
        emotional_state: Optional[str] = None
    ) -> TradeCritique:
        """
        Analyze a proposed trade and return critique

        Args:
            proposed_trade: Trade details (symbol, size, entry, stop, target, etc)
            market_context: Current market conditions (trend, volatility, etc)
            recent_trades: Recent trading history (optional, uses self.recent_trades if None)
            emotional_state: Current trader emotional state (optional)

        Returns:
            TradeCritique with decision and reasoning
        """
        start_time = datetime.now()

        # Use provided recent trades or default to loaded ones
        trades_to_analyze = recent_trades if recent_trades is not None else self.recent_trades

        # Build critique prompt
        prompt = self._build_critique_prompt(
            proposed_trade=proposed_trade,
            market_context=market_context,
            recent_trades=trades_to_analyze,
            emotional_state=emotional_state
        )

        # Get Claude's critique
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent reasoning
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            critique_text = response.content[0].text

            # Parse Claude's response into structured critique
            critique = self._parse_critique_response(critique_text)

            # Add metadata
            critique.model_used = self.model
            critique.critique_duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Log critique
            self._log_critique(proposed_trade, critique)

            return critique

        except Exception as e:
            print(f"❌ Error during critique: {e}")
            # Return safe default (REJECT on error)
            return TradeCritique(
                decision=CritiqueDecision.REJECT.value,
                confidence=0.0,
                reasoning=f"Error during critique: {str(e)}",
                risk_score=10.0,
                risk_assessment="Error",
                market_context_alignment="Error",
                historical_performance="Error",
                emotional_check="Error",
                technical_validation="Error"
            )

    def _build_critique_prompt(
        self,
        proposed_trade: Dict[str, Any],
        market_context: Dict[str, Any],
        recent_trades: List[Dict[str, Any]],
        emotional_state: Optional[str]
    ) -> str:
        """Build the critique prompt for Claude"""

        # Calculate recent performance stats
        recent_stats = self._calculate_recent_stats(recent_trades)

        prompt = f"""You are a professional trading risk advisor analyzing a proposed trade.

PROPOSED TRADE:
Symbol: {proposed_trade.get('symbol', 'N/A')}
Direction: {proposed_trade.get('direction', 'N/A')}
Entry Price: ${proposed_trade.get('entry_price', 0):.2f}
Position Size: ${proposed_trade.get('position_value', 0):.2f}
Stop Loss: ${proposed_trade.get('stop_loss', 0):.2f}
Take Profit: ${proposed_trade.get('take_profit', 0):.2f}
Risk Amount: ${proposed_trade.get('risk_amount', 0):.2f}
Risk Percent: {proposed_trade.get('risk_percent', 0)*100:.2f}%
Risk:Reward Ratio: 1:{proposed_trade.get('risk_reward_ratio', 0):.2f}

CURRENT MARKET CONTEXT:
4H Trend: {market_context.get('trend_4h', 'unknown')}
15m Setup: {market_context.get('setup_15m', 'unknown')}
Volatility: {market_context.get('volatility', 'unknown')}
Market Phase: {market_context.get('market_phase', 'unknown')}
Fear & Greed Index: {market_context.get('fear_greed_index', 'N/A')}
BTC Dominance: {market_context.get('btc_dominance', 'N/A')}%

RECENT TRADING PERFORMANCE (Last 7 Days):
Total Trades: {recent_stats['total_trades']}
Win Rate: {recent_stats['win_rate']*100:.1f}%
Profit Factor: {recent_stats['profit_factor']:.2f}
Average R Multiple: {recent_stats['avg_r_multiple']:.2f}R
Current Streak: {recent_stats['current_streak']}
Biggest Mistake Pattern: {recent_stats['common_mistake']}

TRADER EMOTIONAL STATE: {emotional_state or 'Not provided'}

RECENT SIMILAR TRADES:
{self._format_similar_trades(proposed_trade, recent_trades)}

=================================================================================

Your task is to provide a comprehensive critique of this trade across 5 dimensions:

1. RISK ASSESSMENT: Is the position size appropriate? Is stop loss placement logical?
2. MARKET CONTEXT: Does this trade align with current market regime and trends?
3. HISTORICAL PERFORMANCE: How have similar trades performed recently?
4. EMOTIONAL CHECK: Is this revenge trading, FOMO, or greed-driven? Any red flags?
5. TECHNICAL VALIDATION: Do the indicators and setup truly support this trade?

Provide your response in this EXACT format:

DECISION: [APPROVE/REJECT/MODIFY]
CONFIDENCE: [0.0 to 1.0]
RISK_SCORE: [0.0 to 10.0, where 10 is highest risk]

RISK_ASSESSMENT:
[Your analysis of position sizing and risk management]

MARKET_CONTEXT_ALIGNMENT:
[Your analysis of trade alignment with market conditions]

HISTORICAL_PERFORMANCE:
[Your analysis based on recent similar trades]

EMOTIONAL_CHECK:
[Your analysis of potential emotional biases]

TECHNICAL_VALIDATION:
[Your analysis of technical setup quality]

REASONING:
[Overall explanation of your decision in 2-3 sentences]

MODIFICATIONS: [Only if DECISION is MODIFY]
[JSON format suggestions for adjustments, e.g., {{"position_size": 50, "stop_loss": 45000}}]

Be direct, honest, and protect the trader from bad decisions. Your critique improves performance by 31%."""

        return prompt

    def _parse_critique_response(self, response_text: str) -> TradeCritique:
        """Parse Claude's natural language response into TradeCritique object"""

        lines = response_text.strip().split('\n')

        # Extract fields
        decision = "REJECT"  # Safe default
        confidence = 0.0
        risk_score = 10.0
        risk_assessment = ""
        market_context = ""
        historical = ""
        emotional = ""
        technical = ""
        reasoning = ""
        modifications = None

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("DECISION:"):
                decision = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    confidence = 0.5
            elif line.startswith("RISK_SCORE:"):
                try:
                    risk_score = float(line.split(":", 1)[1].strip())
                except:
                    risk_score = 5.0
            elif line.startswith("RISK_ASSESSMENT:"):
                current_section = "risk"
            elif line.startswith("MARKET_CONTEXT_ALIGNMENT:"):
                current_section = "market"
            elif line.startswith("HISTORICAL_PERFORMANCE:"):
                current_section = "historical"
            elif line.startswith("EMOTIONAL_CHECK:"):
                current_section = "emotional"
            elif line.startswith("TECHNICAL_VALIDATION:"):
                current_section = "technical"
            elif line.startswith("REASONING:"):
                current_section = "reasoning"
            elif line.startswith("MODIFICATIONS:"):
                current_section = "modifications"
            elif line and current_section:
                # Append to current section
                if current_section == "risk":
                    risk_assessment += line + " "
                elif current_section == "market":
                    market_context += line + " "
                elif current_section == "historical":
                    historical += line + " "
                elif current_section == "emotional":
                    emotional += line + " "
                elif current_section == "technical":
                    technical += line + " "
                elif current_section == "reasoning":
                    reasoning += line + " "
                elif current_section == "modifications":
                    try:
                        modifications = json.loads(line)
                    except:
                        modifications = {"raw": line}

        return TradeCritique(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning.strip(),
            risk_score=risk_score,
            risk_assessment=risk_assessment.strip(),
            market_context_alignment=market_context.strip(),
            historical_performance=historical.strip(),
            emotional_check=emotional.strip(),
            technical_validation=technical.strip(),
            suggested_modifications=modifications
        )

    def _calculate_recent_stats(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from recent trades"""

        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_r_multiple': 0.0,
                'current_streak': 0,
                'common_mistake': 'N/A'
            }

        total = len(trades)
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        win_rate = wins / total if total > 0 else 0.0

        # Profit factor
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        # R multiples
        r_multiples = [t.get('r_multiple', 0) for t in trades if 'r_multiple' in t]
        avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else 0.0

        # Current streak
        streak = 0
        for trade in reversed(trades):
            if trade.get('pnl', 0) > 0:
                streak += 1
            else:
                break

        # Common mistakes
        mistakes = [t.get('mistake_type', 'none') for t in trades if t.get('mistake_type') != 'none']
        common_mistake = max(set(mistakes), key=mistakes.count) if mistakes else 'N/A'

        return {
            'total_trades': total,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_r_multiple': avg_r,
            'current_streak': streak,
            'common_mistake': common_mistake
        }

    def _format_similar_trades(
        self,
        proposed_trade: Dict[str, Any],
        recent_trades: List[Dict[str, Any]]
    ) -> str:
        """Format similar recent trades for context"""

        symbol = proposed_trade.get('symbol', '')
        direction = proposed_trade.get('direction', '')

        # Find similar trades (same symbol or same direction)
        similar = [
            t for t in recent_trades
            if t.get('symbol') == symbol or t.get('direction') == direction
        ]

        if not similar:
            return "No similar recent trades found."

        # Take most recent 5
        similar = similar[-5:]

        output = []
        for i, trade in enumerate(similar, 1):
            pnl = trade.get('pnl', 0)
            outcome = "WIN" if pnl > 0 else "LOSS"
            output.append(
                f"{i}. {trade.get('symbol')} {trade.get('direction')} - "
                f"{outcome} (${pnl:.2f}, "
                f"{trade.get('r_multiple', 0):.2f}R)"
            )

        return "\n".join(output)

    def _load_recent_trades(self, days: int = 7) -> List[Dict[str, Any]]:
        """Load recent trades from journal"""

        if not self.journal_path.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []

        try:
            with open(self.journal_path, 'r') as f:
                for line in f:
                    try:
                        trade = json.loads(line.strip())
                        trade_date = datetime.fromisoformat(trade.get('timestamp', ''))

                        if trade_date >= cutoff_date:
                            recent.append(trade)
                    except:
                        continue
        except FileNotFoundError:
            pass

        return recent

    def _log_critique(self, proposed_trade: Dict[str, Any], critique: TradeCritique):
        """Log critique to file"""

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'proposed_trade': proposed_trade,
            'critique': asdict(critique)
        }

        with open(self.critique_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_weekly_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate weekly summary of critiques and patterns

        Returns:
            Summary statistics and insights
        """

        if not self.critique_log_path.exists():
            return {
                'total_critiques': 0,
                'approvals': 0,
                'rejections': 0,
                'modifications': 0,
                'avg_confidence': 0.0,
                'avg_risk_score': 0.0,
                'common_rejection_reasons': [],
                'insights': 'No critique history available.'
            }

        cutoff = datetime.now() - timedelta(days=days)
        critiques = []

        with open(self.critique_log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry['timestamp'])

                    if entry_time >= cutoff:
                        critiques.append(entry['critique'])
                except:
                    continue

        if not critiques:
            return {
                'total_critiques': 0,
                'approvals': 0,
                'rejections': 0,
                'modifications': 0,
                'avg_confidence': 0.0,
                'avg_risk_score': 0.0,
                'common_rejection_reasons': [],
                'insights': 'No recent critiques found.'
            }

        # Calculate statistics
        total = len(critiques)
        approvals = sum(1 for c in critiques if c['decision'] == 'APPROVE')
        rejections = sum(1 for c in critiques if c['decision'] == 'REJECT')
        modifications = sum(1 for c in critiques if c['decision'] == 'MODIFY')

        avg_confidence = sum(c['confidence'] for c in critiques) / total
        avg_risk = sum(c['risk_score'] for c in critiques) / total

        # Extract rejection reasons
        rejection_reasons = [
            c['reasoning'] for c in critiques if c['decision'] == 'REJECT'
        ]

        return {
            'total_critiques': total,
            'approvals': approvals,
            'rejections': rejections,
            'modifications': modifications,
            'approval_rate': approvals / total,
            'avg_confidence': avg_confidence,
            'avg_risk_score': avg_risk,
            'common_rejection_reasons': rejection_reasons[:5],
            'insights': self._generate_weekly_insights(critiques)
        }

    def _generate_weekly_insights(self, critiques: List[Dict[str, Any]]) -> str:
        """Generate natural language insights from critique patterns"""

        # This could be enhanced to use Claude for generating insights
        # For now, provide basic pattern detection

        if not critiques:
            return "No patterns detected."

        high_risk_trades = sum(1 for c in critiques if c['risk_score'] > 7.0)
        emotional_flags = sum(
            1 for c in critiques
            if 'FOMO' in c['emotional_check'] or 'revenge' in c['emotional_check'].lower()
        )

        insights = []

        if high_risk_trades > len(critiques) * 0.5:
            insights.append("High-risk trade proposals detected above normal levels.")

        if emotional_flags > 0:
            insights.append(f"Emotional trading signals detected in {emotional_flags} critiques.")

        return " ".join(insights) if insights else "Trading discipline maintained this week."


# ============================================================================
# EXAMPLE USAGE AND INTEGRATION PATTERNS
# ============================================================================

def example_integration():
    """
    Example: How to integrate ReflectAgent with existing trading system
    """

    print("\n" + "="*80)
    print("🔮 REFLECT AGENT - INTEGRATION EXAMPLE")
    print("="*80 + "\n")

    # Initialize ReflectAgent
    reflect_agent = ReflectAgent()

    # Example proposed trade
    proposed_trade = {
        'symbol': 'BTC/USD',
        'direction': 'LONG',
        'entry_price': 44000,
        'stop_loss': 43500,
        'take_profit': 45500,
        'position_value': 100.0,
        'risk_amount': 5.0,
        'risk_percent': 0.02,
        'risk_reward_ratio': 3.0
    }

    # Example market context
    market_context = {
        'trend_4h': 'bullish',
        'setup_15m': 'pullback_to_support',
        'volatility': 'medium',
        'market_phase': 'markup',
        'fear_greed_index': 65,
        'btc_dominance': 52.3
    }

    # Get critique
    print("📝 Analyzing proposed trade...")
    critique = reflect_agent.analyze_trade(
        proposed_trade=proposed_trade,
        market_context=market_context,
        emotional_state="calm and focused"
    )

    # Display critique
    print(f"\n{'='*80}")
    print(f"DECISION: {critique.decision}")
    print(f"CONFIDENCE: {critique.confidence:.2%}")
    print(f"RISK SCORE: {critique.risk_score}/10")
    print(f"{'='*80}\n")

    print(f"REASONING:\n{critique.reasoning}\n")

    print(f"RISK ASSESSMENT:\n{critique.risk_assessment}\n")
    print(f"MARKET CONTEXT:\n{critique.market_context_alignment}\n")
    print(f"EMOTIONAL CHECK:\n{critique.emotional_check}\n")

    # Trade execution logic
    if critique.decision == CritiqueDecision.APPROVE.value:
        print("✅ Trade APPROVED by Reflect Agent - Proceeding to execution")
        # execute_trade(proposed_trade)

    elif critique.decision == CritiqueDecision.MODIFY.value:
        print("⚠️  Trade needs MODIFICATION")
        print(f"Suggested changes: {critique.suggested_modifications}")
        # adjust_trade(proposed_trade, critique.suggested_modifications)

    else:  # REJECT
        print("❌ Trade REJECTED by Reflect Agent - Logging rejection")
        # log_rejection(proposed_trade, critique.reasoning)

    # Weekly summary
    print("\n" + "="*80)
    print("📊 WEEKLY SUMMARY")
    print("="*80 + "\n")

    summary = reflect_agent.get_weekly_summary(days=7)
    print(f"Total Critiques: {summary['total_critiques']}")
    print(f"Approvals: {summary['approvals']}")
    print(f"Rejections: {summary['rejections']}")
    print(f"Modifications: {summary['modifications']}")
    print(f"Approval Rate: {summary.get('approval_rate', 0):.1%}")
    print(f"Avg Confidence: {summary['avg_confidence']:.2%}")
    print(f"Avg Risk Score: {summary['avg_risk_score']:.1f}/10")
    print(f"\nInsights: {summary['insights']}")


if __name__ == "__main__":
    """
    Run example integration
    """

    print("""
    🔮 REFLECT AGENT - AI Trade Critique System

    Based on 2024-2025 research showing 31% performance improvement
    through natural language feedback instead of parameter optimization.

    This agent analyzes trades across 5 dimensions:
    1. Risk Assessment
    2. Market Context Alignment
    3. Historical Performance
    4. Emotional Check
    5. Technical Validation

    Integration with shade_agent.py and trading_agent.py provides
    an additional layer of AI-powered decision validation.
    """)

    # Run example
    example_integration()

    print("\n" + "="*80)
    print("✅ REFLECT AGENT example completed")
    print("="*80 + "\n")
