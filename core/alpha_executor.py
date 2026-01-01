"""
ALPHA EXECUTOR: Translates research intelligence into autonomous trading decisions.

This module bridges:
- ALPHA_DIGEST.md (research synthesis)
- alpha_bias.json (calibrated parameters)
- overnight_runner.py (execution engine)
- Replit Shadow AI (web dashboard sync)

Three-Tier Execution Model:
- Tier 1 (AUTO): Small positions, high confidence, blue chips
- Tier 2 (QUEUE): Medium positions, require human approval
- Tier 3 (ALERT): Large positions, whale signals, notify only
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Paths
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
BIAS_CONFIG = SS3_ROOT / "config" / "alpha_bias.json"
BRAIN_JSON = SS3_ROOT / "BRAIN.json"
PENDING_QUEUE = SS3_ROOT / "data" / "pending_approvals.json"

# Replit webhook (from your BRAIN.json)
REPLIT_WEBHOOK = "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev/api/manus-webhook"
NTFY_TOPIC = "sovereignshadow_dc4d2fa1"


class ExecutionTier(Enum):
    TIER_1_AUTO = "auto"
    TIER_2_QUEUE = "queue"
    TIER_3_ALERT = "alert"


@dataclass
class TradeSignal:
    symbol: str
    side: str  # BUY or SELL
    confidence: float
    sector: str
    position_size_usd: float
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    source: str  # overnight_runner, whale_alert, sector_rotation
    timestamp: datetime
    tier: ExecutionTier = None

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "confidence": self.confidence,
            "sector": self.sector,
            "position_size_usd": self.position_size_usd,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit_1": self.take_profit_1,
            "take_profit_2": self.take_profit_2,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "tier": self.tier.value if self.tier else None
        }


class AlphaExecutor:
    """
    Core execution engine that applies research bias to trading decisions.
    """

    def __init__(self):
        self.bias = self._load_bias()
        self.brain = self._load_brain()
        self.pending_queue: List[TradeSignal] = []
        self.executed_today: List[dict] = []
        self.daily_loss_limit = 50.0  # USD
        self.daily_loss_current = 0.0

    def _load_bias(self) -> dict:
        """Load alpha bias configuration."""
        if BIAS_CONFIG.exists():
            with open(BIAS_CONFIG) as f:
                return json.load(f)
        return self._default_bias()

    def _load_brain(self) -> dict:
        """Load BRAIN.json for portfolio context."""
        if BRAIN_JSON.exists():
            with open(BRAIN_JSON) as f:
                return json.load(f)
        return {}

    def _default_bias(self) -> dict:
        """Fallback conservative bias."""
        return {
            "execution_bias": {"long_bias": 0.5, "confidence_threshold": 70},
            "risk_parameters": {"stop_loss_pct": 3, "take_profit_1_pct": 5},
            "market_regime": {"recommendation": "HOLD"}
        }

    def classify_tier(self, signal: TradeSignal) -> ExecutionTier:
        """
        Determine execution tier based on alpha bias rules.

        Tier 1 (AUTO): Execute immediately
        - Position < $50
        - Blue chip asset
        - Confidence > 80
        - Within daily loss limit

        Tier 2 (QUEUE): Queue for human approval
        - Position $50-$200
        - Confidence 60-80

        Tier 3 (ALERT): Notify only
        - Position > $200
        - Confidence < 60
        - Whale signals
        """
        rules = self.bias.get("autonomous_rules", {})
        blue_chips = self.bias.get("sector_weights", {}).get("BLUE_CHIP", {}).get("tokens", [])

        # Check Tier 1 conditions
        if (signal.position_size_usd < 50 and
            signal.symbol in blue_chips and
            signal.confidence > 80 and
            self.daily_loss_current < self.daily_loss_limit):
            return ExecutionTier.TIER_1_AUTO

        # Check Tier 2 conditions
        if (50 <= signal.position_size_usd <= 200 and
            60 <= signal.confidence <= 80):
            return ExecutionTier.TIER_2_QUEUE

        # Default to Tier 3
        return ExecutionTier.TIER_3_ALERT

    def apply_bias(self, raw_signal: dict) -> Optional[TradeSignal]:
        """
        Apply alpha bias to a raw signal from overnight_runner.

        Adjustments based on research:
        - Increase long bias during extreme fear
        - Boost confidence for whale accumulation tokens
        - Apply sector weights
        - Adjust position sizing based on regime
        """
        bias = self.bias
        regime = bias.get("market_regime", {})
        exec_bias = bias.get("execution_bias", {})
        risk_params = bias.get("risk_parameters", {})

        symbol = raw_signal.get("symbol", "")
        side = raw_signal.get("side", "BUY")
        base_confidence = raw_signal.get("confidence", 50)

        # === BIAS ADJUSTMENTS ===

        # 1. Regime adjustment
        if regime.get("recommendation") == "ACCUMULATE" and side == "BUY":
            base_confidence += 10  # Boost buys during accumulation regime

        # 2. Extreme fear bonus
        if regime.get("fear_greed_status") == "EXTREME_FEAR" and side == "BUY":
            base_confidence += 5  # Contrarian bonus

        # 3. Whale accumulation bonus
        whale_tokens = [w["token"] for w in bias.get("whale_signals", {}).get("accumulation_alerts", [])]
        if symbol in whale_tokens:
            base_confidence += 15  # Whale following bonus

        # 4. Hayes rotation bonus
        hayes_tokens = bias.get("whale_signals", {}).get("hayes_rotation", {}).get("tokens", [])
        if symbol in hayes_tokens:
            base_confidence += 10

        # 5. Sector weight adjustment
        sector = self._get_sector(symbol)
        sector_data = bias.get("sector_weights", {}).get(sector, {})
        sector_weight = sector_data.get("weight", 0.1)

        # Cap confidence at 100
        final_confidence = min(base_confidence, 100)

        # === POSITION SIZING ===
        base_size = raw_signal.get("position_size_usd", 25)
        size_multiplier = exec_bias.get("position_size_multiplier", 1.0)
        adjusted_size = base_size * size_multiplier * sector_weight * 4  # Normalize sector weight

        # === RISK LEVELS ===
        entry = raw_signal.get("entry_price", 0)
        stop_pct = risk_params.get("stop_loss_pct", 5) / 100
        tp1_pct = risk_params.get("take_profit_1_pct", 15) / 100
        tp2_pct = risk_params.get("take_profit_2_pct", 30) / 100

        if side == "BUY":
            stop_loss = entry * (1 - stop_pct)
            tp1 = entry * (1 + tp1_pct)
            tp2 = entry * (1 + tp2_pct)
        else:
            stop_loss = entry * (1 + stop_pct)
            tp1 = entry * (1 - tp1_pct)
            tp2 = entry * (1 - tp2_pct)

        # === CREATE SIGNAL ===
        signal = TradeSignal(
            symbol=symbol,
            side=side,
            confidence=final_confidence,
            sector=sector,
            position_size_usd=adjusted_size,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            source=raw_signal.get("source", "overnight_runner"),
            timestamp=datetime.now()
        )

        # Classify tier
        signal.tier = self.classify_tier(signal)

        # Filter by confidence threshold
        threshold = exec_bias.get("confidence_threshold", 60)
        if final_confidence < threshold:
            return None

        return signal

    def _get_sector(self, symbol: str) -> str:
        """Determine sector from symbol."""
        sector_map = self.bias.get("sector_weights", {})
        for sector, data in sector_map.items():
            if symbol in data.get("tokens", []):
                return sector
        return "UNKNOWN"

    def process_signal(self, signal: TradeSignal) -> dict:
        """
        Process a signal based on its tier.

        Returns action taken.
        """
        if signal.tier == ExecutionTier.TIER_1_AUTO:
            return self._execute_auto(signal)
        elif signal.tier == ExecutionTier.TIER_2_QUEUE:
            return self._queue_for_approval(signal)
        else:
            return self._send_alert(signal)

    def _execute_auto(self, signal: TradeSignal) -> dict:
        """
        Execute Tier 1 signal automatically.

        This creates a paper trade or live trade depending on mode.
        """
        print(f"[TIER 1 AUTO] Executing {signal.side} {signal.symbol} @ ${signal.entry_price:.2f}")

        # Log execution
        execution = {
            "action": "EXECUTED",
            "tier": "TIER_1_AUTO",
            **signal.to_dict()
        }

        self.executed_today.append(execution)

        # Notify mobile
        self._notify(f"AUTO EXECUTED: {signal.side} {signal.symbol} ${signal.position_size_usd:.0f}")

        # Sync to Replit
        self._sync_to_replit(execution)

        return execution

    def _queue_for_approval(self, signal: TradeSignal) -> dict:
        """
        Queue Tier 2 signal for human approval.
        """
        print(f"[TIER 2 QUEUE] Queuing {signal.side} {signal.symbol} for approval")

        queued = {
            "action": "QUEUED",
            "tier": "TIER_2_QUEUE",
            **signal.to_dict()
        }

        self.pending_queue.append(signal)
        self._save_pending_queue()

        # Notify for approval
        self._notify(f"APPROVAL NEEDED: {signal.side} {signal.symbol} ${signal.position_size_usd:.0f} ({signal.confidence:.0f}% conf)")

        return queued

    def _send_alert(self, signal: TradeSignal) -> dict:
        """
        Send Tier 3 alert without execution.
        """
        print(f"[TIER 3 ALERT] Alert for {signal.side} {signal.symbol}")

        alert = {
            "action": "ALERT_ONLY",
            "tier": "TIER_3_ALERT",
            **signal.to_dict()
        }

        # Notify
        self._notify(f"ALPHA ALERT: {signal.side} {signal.symbol} - {signal.source}")

        return alert

    def _save_pending_queue(self):
        """Save pending approvals to disk."""
        PENDING_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        queue_data = [s.to_dict() for s in self.pending_queue]
        with open(PENDING_QUEUE, 'w') as f:
            json.dump(queue_data, f, indent=2)

    def _notify(self, message: str):
        """Send mobile notification via ntfy."""
        try:
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=message.encode('utf-8'),
                timeout=5
            )
        except Exception as e:
            print(f"Notification failed: {e}")

    def _sync_to_replit(self, data: dict):
        """Sync execution to Replit Shadow AI dashboard."""
        try:
            requests.post(
                REPLIT_WEBHOOK,
                json={"event": "execution", "data": data},
                timeout=10
            )
        except Exception as e:
            print(f"Replit sync failed: {e}")

    def approve_pending(self, index: int) -> dict:
        """
        Approve a pending signal from the queue.

        Usage: executor.approve_pending(0)  # Approve first in queue
        """
        if 0 <= index < len(self.pending_queue):
            signal = self.pending_queue.pop(index)
            signal.tier = ExecutionTier.TIER_1_AUTO  # Promote to auto
            self._save_pending_queue()
            return self._execute_auto(signal)
        return {"error": "Invalid index"}

    def reject_pending(self, index: int) -> dict:
        """Reject a pending signal."""
        if 0 <= index < len(self.pending_queue):
            signal = self.pending_queue.pop(index)
            self._save_pending_queue()
            return {"action": "REJECTED", **signal.to_dict()}
        return {"error": "Invalid index"}

    def list_pending(self) -> List[dict]:
        """List all pending approvals."""
        return [s.to_dict() for s in self.pending_queue]

    def get_regime_summary(self) -> dict:
        """Get current market regime from bias config."""
        return self.bias.get("market_regime", {})

    def get_watchlist(self) -> dict:
        """Get current watchlist from bias config."""
        return self.bias.get("watchlist", {})


# === CLI INTERFACE ===

def main():
    """CLI for alpha executor."""
    import argparse

    parser = argparse.ArgumentParser(description="Alpha Executor - Research to Execution")
    parser.add_argument("--regime", action="store_true", help="Show current regime")
    parser.add_argument("--pending", action="store_true", help="List pending approvals")
    parser.add_argument("--approve", type=int, help="Approve pending signal by index")
    parser.add_argument("--reject", type=int, help="Reject pending signal by index")
    parser.add_argument("--watchlist", action="store_true", help="Show current watchlist")
    parser.add_argument("--test", action="store_true", help="Test with sample signal")

    args = parser.parse_args()
    executor = AlphaExecutor()

    if args.regime:
        regime = executor.get_regime_summary()
        print("\n=== MARKET REGIME ===")
        print(f"Classification: {regime.get('classification')}")
        print(f"Peak Indicators: {regime.get('peak_indicators_triggered')}/{regime.get('peak_indicators_total')}")
        print(f"Fear & Greed: {regime.get('fear_greed_index')} ({regime.get('fear_greed_status')})")
        print(f"Recommendation: {regime.get('recommendation')}")

    elif args.pending:
        pending = executor.list_pending()
        print(f"\n=== PENDING APPROVALS ({len(pending)}) ===")
        for i, p in enumerate(pending):
            print(f"[{i}] {p['side']} {p['symbol']} ${p['position_size_usd']:.0f} ({p['confidence']:.0f}% conf)")

    elif args.approve is not None:
        result = executor.approve_pending(args.approve)
        print(f"Approved: {result}")

    elif args.reject is not None:
        result = executor.reject_pending(args.reject)
        print(f"Rejected: {result}")

    elif args.watchlist:
        wl = executor.get_watchlist()
        print("\n=== WATCHLIST ===")
        print(f"Immediate: {wl.get('immediate')}")
        print(f"Accumulate on Dip: {wl.get('accumulate_on_dip')}")
        print(f"Whale Tracking: {wl.get('whale_tracking')}")
        print(f"Avoid: {wl.get('avoid')}")

    elif args.test:
        # Test signal
        raw = {
            "symbol": "ENA",
            "side": "BUY",
            "confidence": 65,
            "entry_price": 1.25,
            "position_size_usd": 30,
            "source": "test"
        }
        signal = executor.apply_bias(raw)
        if signal:
            print(f"\n=== TEST SIGNAL ===")
            print(f"Symbol: {signal.symbol}")
            print(f"Confidence: {signal.confidence:.0f}% (was 65%)")
            print(f"Tier: {signal.tier.value}")
            print(f"Position: ${signal.position_size_usd:.2f}")
            result = executor.process_signal(signal)
            print(f"Result: {result['action']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
