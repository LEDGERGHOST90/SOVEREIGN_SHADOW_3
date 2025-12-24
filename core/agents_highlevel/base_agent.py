"""
Base Agent Class for ECO SYSTEM 4
All agents inherit from this base.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

# Paths - Updated to SS_III
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
BRAIN_PATH = SS3_ROOT / "BRAIN.json"
CONFIG_PATH = SS3_ROOT / "config"
DATA_PATH = SS3_ROOT / "data"
LOGS_PATH = SS3_ROOT / "logs"


class BaseAgent(ABC):
    """Base class for all SS3 agents."""

    def __init__(self, name: str):
        self.name = name
        self.brain = self._load_brain()
        self.config = self._load_config()
        self.start_time = datetime.now()

    def _load_brain(self) -> dict:
        """Load BRAIN.json - single source of truth."""
        if BRAIN_PATH.exists():
            with open(BRAIN_PATH, 'r') as f:
                return json.load(f)
        return {}

    def _save_brain(self) -> None:
        """Save to BRAIN.json."""
        self.brain['last_updated'] = datetime.now().isoformat()
        with open(BRAIN_PATH, 'w') as f:
            json.dump(self.brain, f, indent=2)

    def _load_config(self) -> dict:
        """Load agent-specific config if exists."""
        config = {}

        # Load risk limits
        risk_path = CONFIG_PATH / "risk_limits.json"
        if risk_path.exists():
            with open(risk_path, 'r') as f:
                config['risk'] = json.load(f)

        # Load exchange config
        exchange_path = CONFIG_PATH / "exchanges.json"
        if exchange_path.exists():
            with open(exchange_path, 'r') as f:
                config['exchanges'] = json.load(f)

        return config

    def update_status(self, status: str) -> None:
        """Update agent status in BRAIN."""
        if 'agents' not in self.brain:
            self.brain['agents'] = {}

        self.brain['agents'][self.name] = {
            'status': status,
            'last_run': datetime.now().isoformat()
        }
        self._save_brain()

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message to agent log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] [{self.name}] {message}"

        # Print to console
        print(log_line)

        # Write to log file
        log_file = LOGS_PATH / "sessions" / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(log_line + "\n")

    def is_paper_mode(self) -> bool:
        """Check if system is in paper trading mode."""
        return self.config.get('risk', {}).get('paper_mode', True)

    def get_approval_stage(self) -> int:
        """Get current approval stage (1=paper, 2=semi-auto, 3=full-auto)."""
        return self.brain.get('approval_stage', 1)

    @abstractmethod
    def run(self) -> dict:
        """Execute agent's main function. Override in subclass."""
        pass


class Signal:
    """Trading signal data structure."""

    def __init__(
        self,
        symbol: str,
        action: str,  # BUY, SELL, HOLD
        confidence: int,  # 0-100
        reasoning: str,
        source_agent: str,
        entry_price: float = None,
        stop_loss: float = None,
        take_profit: float = None
    ):
        self.id = f"SIG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.timestamp = datetime.now().isoformat()
        self.symbol = symbol
        self.action = action
        self.confidence = confidence
        self.reasoning = reasoning
        self.source_agent = source_agent
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.consensus_score = 0
        self.consensus_votes = {}
        self.approved = None
        self.executed = False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'action': self.action,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'source_agent': self.source_agent,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'consensus_score': self.consensus_score,
            'consensus_votes': self.consensus_votes,
            'approved': self.approved,
            'executed': self.executed
        }


class Trade:
    """Paper or live trade data structure."""

    def __init__(
        self,
        signal: Signal,
        position_size_usd: float,
        is_paper: bool = True
    ):
        self.id = f"{'PT' if is_paper else 'LT'}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.signal_id = signal.id
        self.timestamp = datetime.now().isoformat()
        self.symbol = signal.symbol
        self.action = signal.action
        self.entry_price = signal.entry_price
        self.position_size_usd = position_size_usd
        self.stop_loss = signal.stop_loss
        self.take_profit = signal.take_profit
        self.is_paper = is_paper
        self.status = "OPEN"
        self.exit_price = None
        self.exit_timestamp = None
        self.pnl_usd = None
        self.pnl_pct = None

    def close(self, exit_price: float) -> None:
        """Close trade and calculate PnL."""
        self.exit_price = exit_price
        self.exit_timestamp = datetime.now().isoformat()
        self.status = "CLOSED"

        if self.action == "BUY":
            self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL/SHORT
            self.pnl_pct = ((self.entry_price - exit_price) / self.entry_price) * 100

        self.pnl_usd = self.position_size_usd * (self.pnl_pct / 100)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'position_size_usd': self.position_size_usd,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'is_paper': self.is_paper,
            'status': self.status,
            'exit_price': self.exit_price,
            'exit_timestamp': self.exit_timestamp,
            'pnl_usd': self.pnl_usd,
            'pnl_pct': self.pnl_pct
        }
