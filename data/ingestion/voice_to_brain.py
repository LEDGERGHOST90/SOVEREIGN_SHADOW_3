#!/usr/bin/env python3
"""
Voice-to-Brain Signal Extractor
Parses research feed and extracts actionable trading signals

This module:
1. Analyzes research_feed items in BRAIN.json
2. Extracts and normalizes trading signals
3. Scores signals by confidence and urgency
4. Formats signals for trading agents
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

BRAIN_PATH = Path(__file__).parent.parent / "BRAIN.json"

# Signal classification
BULLISH_KEYWORDS = [
    "buy", "long", "bullish", "accumulate", "breakout", "support",
    "momentum", "uptrend", "oversold", "bottom", "reversal up"
]

BEARISH_KEYWORDS = [
    "sell", "short", "bearish", "distribute", "breakdown", "resistance",
    "downtrend", "overbought", "top", "reversal down", "dump"
]

URGENCY_KEYWORDS = {
    "high": ["now", "immediately", "urgent", "breaking", "alert"],
    "medium": ["soon", "watch", "monitor", "prepare"],
    "low": ["consider", "maybe", "possibly", "long-term"]
}


def load_brain() -> dict:
    """Load BRAIN.json"""
    with open(BRAIN_PATH) as f:
        return json.load(f)


def save_brain(brain: dict):
    """Save BRAIN.json"""
    brain["last_updated"] = datetime.now().isoformat()
    with open(BRAIN_PATH, 'w') as f:
        json.dump(brain, f, indent=2)


def extract_ticker(text: str) -> Optional[str]:
    """Extract ticker symbol from text"""
    # Match $BTC or BTC patterns
    patterns = [
        r'\$([A-Z]{2,5})',  # $BTC format
        r'\b(BTC|ETH|SOL|XRP|AVAX|LINK|AAVE|UNI|MATIC|DOT|ADA|DOGE|SHIB|PEPE)\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)
    return None


def classify_sentiment(text: str, existing_sentiment: dict = None) -> dict:
    """Classify sentiment from text or use existing"""
    if existing_sentiment and existing_sentiment.get("score"):
        return existing_sentiment

    text_lower = text.lower()

    bullish_count = sum(1 for kw in BULLISH_KEYWORDS if kw in text_lower)
    bearish_count = sum(1 for kw in BEARISH_KEYWORDS if kw in text_lower)

    if bullish_count > bearish_count:
        direction = "bullish"
        score = min(1.0, 0.5 + (bullish_count - bearish_count) * 0.1)
    elif bearish_count > bullish_count:
        direction = "bearish"
        score = max(-1.0, -0.5 - (bearish_count - bullish_count) * 0.1)
    else:
        direction = "neutral"
        score = 0.0

    return {
        "direction": direction,
        "score": score,
        "bullish_signals": bullish_count,
        "bearish_signals": bearish_count
    }


def determine_urgency(text: str) -> str:
    """Determine signal urgency from text"""
    text_lower = text.lower()

    for level, keywords in URGENCY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return level

    return "medium"


def calculate_confidence(item: dict) -> float:
    """Calculate signal confidence score (0-1)"""
    confidence = 0.5  # Base confidence

    # Has ticker identified
    if item.get("ticker"):
        confidence += 0.15

    # Has clear sentiment
    sentiment = item.get("sentiment", {})
    if abs(sentiment.get("score", 0)) > 0.5:
        confidence += 0.15

    # Has multiple signals
    signals = item.get("signals", [])
    if len(signals) >= 2:
        confidence += 0.1

    # Has insights
    if item.get("insights"):
        confidence += 0.1

    return min(1.0, confidence)


def create_trading_signal(item: dict) -> Optional[dict]:
    """Create a normalized trading signal from research item"""
    # Get ticker
    ticker = item.get("ticker")
    if not ticker and item.get("transcript_summary"):
        ticker = extract_ticker(item["transcript_summary"])

    if not ticker:
        return None  # Can't trade without a ticker

    # Get sentiment
    summary_text = item.get("transcript_summary", "") + " ".join(item.get("insights", []))
    sentiment = classify_sentiment(summary_text, item.get("sentiment"))

    # Determine action
    if sentiment["direction"] == "bullish":
        action = "BUY"
    elif sentiment["direction"] == "bearish":
        action = "SELL"
    else:
        action = "HOLD"

    # Calculate metrics
    confidence = calculate_confidence(item)
    urgency = determine_urgency(summary_text)

    return {
        "signal_id": f"voice_{item['id']}",
        "source_type": "voice_research",
        "source_id": item["id"],
        "created_at": datetime.now().isoformat(),
        "research_timestamp": item.get("timestamp"),

        # Trading data
        "ticker": ticker,
        "action": action,
        "sentiment": sentiment,
        "confidence": confidence,
        "urgency": urgency,

        # Context
        "title": item.get("title", "Voice Research"),
        "summary": item.get("transcript_summary", "")[:200],
        "insights": item.get("insights", [])[:3],
        "raw_signals": item.get("signals", []),

        # Status
        "status": "pending",
        "agent_assigned": None,
        "executed_at": None
    }


def aggregate_signals(signals: List[dict]) -> Dict[str, dict]:
    """Aggregate signals by ticker for consensus"""
    by_ticker = defaultdict(list)

    for signal in signals:
        by_ticker[signal["ticker"]].append(signal)

    consensus = {}
    for ticker, ticker_signals in by_ticker.items():
        # Calculate consensus
        bullish = sum(1 for s in ticker_signals if s["action"] == "BUY")
        bearish = sum(1 for s in ticker_signals if s["action"] == "SELL")
        total = len(ticker_signals)

        if bullish > bearish:
            consensus_action = "BUY"
            consensus_strength = bullish / total
        elif bearish > bullish:
            consensus_action = "SELL"
            consensus_strength = bearish / total
        else:
            consensus_action = "HOLD"
            consensus_strength = 0.5

        # Average confidence
        avg_confidence = sum(s["confidence"] for s in ticker_signals) / total

        # Highest urgency
        urgency_order = {"high": 3, "medium": 2, "low": 1}
        max_urgency = max(ticker_signals, key=lambda s: urgency_order.get(s["urgency"], 0))["urgency"]

        consensus[ticker] = {
            "ticker": ticker,
            "consensus_action": consensus_action,
            "consensus_strength": consensus_strength,
            "average_confidence": avg_confidence,
            "urgency": max_urgency,
            "signal_count": total,
            "signals": [s["signal_id"] for s in ticker_signals],
            "updated_at": datetime.now().isoformat()
        }

    return consensus


def process_research_feed():
    """Main processing: extract signals from research feed"""
    print("=" * 50)
    print("VOICE-TO-BRAIN SIGNAL EXTRACTOR")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    brain = load_brain()

    research_feed = brain.get("research_feed", {}).get("items", [])
    if not research_feed:
        print("\nNo research items to process")
        return

    print(f"\nProcessing {len(research_feed)} research items...")

    # Initialize signal queue if not exists
    if "signal_queue" not in brain:
        brain["signal_queue"] = {
            "signals": [],
            "consensus": {},
            "last_processed": None,
            "total_generated": 0
        }

    # Get existing signal IDs
    existing_ids = {s["signal_id"] for s in brain["signal_queue"]["signals"]}

    # Process each research item
    new_signals = []
    for item in research_feed:
        signal = create_trading_signal(item)
        if signal and signal["signal_id"] not in existing_ids:
            new_signals.append(signal)
            print(f"  + Signal: {signal['ticker']} {signal['action']} (conf: {signal['confidence']:.2f})")

    if new_signals:
        brain["signal_queue"]["signals"].extend(new_signals)
        brain["signal_queue"]["total_generated"] += len(new_signals)

        # Update consensus
        all_pending = [s for s in brain["signal_queue"]["signals"] if s["status"] == "pending"]
        brain["signal_queue"]["consensus"] = aggregate_signals(all_pending)

    brain["signal_queue"]["last_processed"] = datetime.now().isoformat()

    save_brain(brain)

    # Summary
    print("\n" + "-" * 50)
    print(f"New signals generated: {len(new_signals)}")
    print(f"Total pending signals: {len([s for s in brain['signal_queue']['signals'] if s['status'] == 'pending'])}")

    if brain["signal_queue"]["consensus"]:
        print("\nConsensus by ticker:")
        for ticker, data in brain["signal_queue"]["consensus"].items():
            print(f"  {ticker}: {data['consensus_action']} ({data['consensus_strength']:.0%} strength, {data['signal_count']} signals)")

    print("=" * 50)


def get_actionable_signals(min_confidence: float = 0.6) -> List[dict]:
    """Get signals ready for agent execution"""
    brain = load_brain()

    signals = brain.get("signal_queue", {}).get("signals", [])

    actionable = [
        s for s in signals
        if s["status"] == "pending"
        and s["confidence"] >= min_confidence
        and s["action"] in ["BUY", "SELL"]
    ]

    # Sort by urgency and confidence
    urgency_order = {"high": 3, "medium": 2, "low": 1}
    actionable.sort(key=lambda s: (urgency_order.get(s["urgency"], 0), s["confidence"]), reverse=True)

    return actionable


def mark_signal_executed(signal_id: str, agent: str = None):
    """Mark a signal as executed"""
    brain = load_brain()

    for signal in brain.get("signal_queue", {}).get("signals", []):
        if signal["signal_id"] == signal_id:
            signal["status"] = "executed"
            signal["executed_at"] = datetime.now().isoformat()
            signal["agent_assigned"] = agent
            break

    save_brain(brain)


if __name__ == "__main__":
    process_research_feed()

    print("\n\nActionable signals (confidence >= 0.6):")
    print("-" * 40)
    for signal in get_actionable_signals():
        print(f"{signal['ticker']}: {signal['action']} | Confidence: {signal['confidence']:.2f} | Urgency: {signal['urgency']}")
