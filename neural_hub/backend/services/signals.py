#!/usr/bin/env python3
"""
Signal Service - Manages trading signals
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class SignalService:
    """Service for managing trading signals"""

    def __init__(self):
        self.signals_file = PROJECT_ROOT / "memory" / "neural_signals.json"
        self.signals_file.parent.mkdir(exist_ok=True)
        self._load_signals()

    def _load_signals(self):
        """Load signals from file"""
        if self.signals_file.exists():
            try:
                self.signals = json.loads(self.signals_file.read_text())
            except:
                self.signals = {"signals": [], "history": []}
        else:
            self.signals = {"signals": [], "history": []}

    def _save_signals(self):
        """Save signals to file"""
        self.signals_file.write_text(json.dumps(self.signals, indent=2))

    async def get_signals(self, status: Optional[str] = None) -> Dict:
        """Get signals, optionally filtered by status"""
        signals = self.signals.get("signals", [])

        if status:
            signals = [s for s in signals if s.get("status") == status]

        return {
            "signals": signals,
            "count": len(signals),
            "pending": len([s for s in self.signals.get("signals", []) if s.get("status") == "pending"]),
            "accepted": len([s for s in self.signals.get("signals", []) if s.get("status") == "accepted"]),
            "rejected": len([s for s in self.signals.get("signals", []) if s.get("status") == "rejected"])
        }

    async def save_signal(self, signal) -> Dict:
        """Save a new signal"""
        signal_data = {
            "id": str(uuid.uuid4())[:8],
            "symbol": signal.symbol,
            "action": signal.action,
            "confidence": signal.confidence,
            "reasoning": signal.reasoning,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit_1": signal.take_profit_1,
            "take_profit_2": signal.take_profit_2,
            "risk_level": signal.risk_level,
            "timeframe": signal.timeframe,
            "position_size_pct": signal.position_size_pct,
            "timestamp": signal.timestamp,
            "status": "pending"
        }

        self.signals["signals"].append(signal_data)

        # Keep only last 50 signals
        if len(self.signals["signals"]) > 50:
            old = self.signals["signals"][:-50]
            self.signals["history"].extend(old)
            self.signals["signals"] = self.signals["signals"][-50:]

        self._save_signals()
        return signal_data

    async def accept_signal(self, signal_id: str) -> Dict:
        """Accept a signal"""
        for signal in self.signals["signals"]:
            if signal["id"] == signal_id:
                signal["status"] = "accepted"
                signal["accepted_at"] = datetime.now().isoformat()
                self._save_signals()

                # TODO: Create position via swing engine
                return {"status": "accepted", "signal": signal}

        return {"error": "Signal not found"}

    async def reject_signal(self, signal_id: str) -> Dict:
        """Reject a signal"""
        for signal in self.signals["signals"]:
            if signal["id"] == signal_id:
                signal["status"] = "rejected"
                signal["rejected_at"] = datetime.now().isoformat()
                self._save_signals()
                return {"status": "rejected", "signal": signal}

        return {"error": "Signal not found"}
