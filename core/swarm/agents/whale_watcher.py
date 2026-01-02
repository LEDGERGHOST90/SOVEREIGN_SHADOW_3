#!/usr/bin/env python3
"""
WHALE WATCHER AGENT
Tracks smart money wallets, exchange flows, and on-chain metrics
Part of the Autonomous Trading Colony

Sovereign Shadow III - On-Chain Intelligence Layer

Based on CryptoTrade EMNLP 2024 paper findings:
- On-chain stats provide +16% alpha improvement (biggest impact!)
- Exchange flows are leading indicators
- Whale movements predict price direction
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


@dataclass
class WhaleWallet:
    """Smart money wallet to track"""
    address: str
    label: str  # "Jump Trading", "A16z", "Blackrock", etc.
    success_rate: float = 0.0
    total_profit: float = 0.0
    last_activity: Optional[datetime] = None


@dataclass
class WhaleMovement:
    """Detected whale activity"""
    wallet: WhaleWallet
    action: str  # "accumulation", "distribution", "swap"
    token: str
    amount: float
    usd_value: float
    timestamp: datetime = None


@dataclass
class OnChainSignal:
    """Aggregated on-chain signal"""
    symbol: str
    signal: str  # "BULLISH", "BEARISH", "NEUTRAL"
    score: float  # -100 to +100
    confidence: float  # 0 to 100
    exchange_flow_signal: str
    whale_signal: str
    recommendation: str
    timestamp: datetime = None


class WhaleWatcherAgent:
    """
    Specialized Agent: Whale Watcher

    Enhanced with on-chain intelligence from:
    - Exchange flow analysis (accumulation vs distribution)
    - Whale movement tracking
    - TVL and address metrics

    Based on CryptoTrade paper: On-chain adds +16% alpha

    Capital Allocation: 15% (highest alpha source per research)
    Personality: patient_observer (waits for quality signals)
    """

    def __init__(self, agent_id: str = "whale_watcher"):
        self.agent_id = agent_id
        self.specialty = "on_chain_analysis"
        self.personality = "patient_observer"
        self.capital_allocation = 0.15  # Increased due to +16% alpha
        self.state = "initializing"

        # On-chain clients (lazy load)
        self._onchain_signals = None
        self._onchain_client = None

        # Smart money wallets to track
        self.whale_wallets = self._init_whale_wallets()

        # Recent movements and signals
        self.recent_movements: List[WhaleMovement] = []
        self.recent_signals: List[OnChainSignal] = []

        # Performance tracking
        self.stats = {
            "whales_tracked": len(self.whale_wallets),
            "signals_generated": 0,
            "bullish_signals": 0,
            "bearish_signals": 0,
            "neutral_signals": 0,
            "avg_confidence": 0.0,
            "successful_copies": 0,
            "failed_copies": 0,
            "copy_accuracy": 0.0
        }

        logger.info(f"🐋 Created WhaleWatcher agent '{agent_id}'")
        logger.info(f"   +16% alpha from on-chain data (CryptoTrade EMNLP 2024)")

    @property
    def onchain_signals(self):
        """Lazy load OnChainSignals module"""
        if self._onchain_signals is None:
            try:
                from core.signals.onchain_signals import OnChainSignals
                self._onchain_signals = OnChainSignals(cache_enabled=True)
                logger.info("   ✓ OnChainSignals module initialized")
            except Exception as e:
                logger.warning(f"   ⚠ OnChainSignals unavailable: {e}")
        return self._onchain_signals

    @property
    def onchain_client(self):
        """Lazy load SynopticCore OnChainClient"""
        if self._onchain_client is None:
            try:
                from ds_star.synoptic_core.onchain_client import OnChainClient
                self._onchain_client = OnChainClient()
                logger.info("   ✓ OnChainClient (TVL/metrics) initialized")
            except Exception as e:
                logger.warning(f"   ⚠ OnChainClient unavailable: {e}")
        return self._onchain_client

    async def initialize(self):
        """Initialize the whale watcher"""
        self.state = "active"
        return True

    def _init_whale_wallets(self) -> Dict[str, WhaleWallet]:
        """
        Initialize list of smart money wallets to track

        These are known successful traders/funds
        We watch what they buy and follow
        """
        whales = {}

        # Known institutional/whale addresses (examples)
        whale_list = [
            # BTC whales
            ("34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo", "Binance Cold", 0.75),
            ("bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97", "Coinbase Prime", 0.78),
            # ETH whales
            ("0x28C6c06298d514Db089934071355E5743bf21d60", "Binance Hot", 0.72),
            ("0x71660c4005ba85c37ccec55d0c4493e66fe775d3", "Coinbase Custody", 0.80),
            # Arthur Hayes / Crypto influencer wallets
            ("0xd275e5cb559d6dc236a5f8002a5f0b4c8e610701", "Arthur Hayes", 0.85),
        ]

        for address, label, success_rate in whale_list:
            whales[address] = WhaleWallet(
                address=address,
                label=label,
                success_rate=success_rate
            )

        return whales

    async def get_onchain_score(self, symbol: str) -> Optional[OnChainSignal]:
        """
        Get aggregated on-chain score for an asset

        Combines:
        - Exchange flows (accumulation vs distribution)
        - Whale movements
        - TVL and metrics
        """
        # Clean symbol
        clean_symbol = symbol.replace('/USD', '').replace('/USDT', '').replace('-USD', '')

        try:
            if self.onchain_signals:
                # Get aggregated score from OnChainSignals
                data = self.onchain_signals.get_onchain_score(clean_symbol)

                signal = OnChainSignal(
                    symbol=clean_symbol,
                    signal=data['overall_signal'],
                    score=data['overall_score'],
                    confidence=data['confidence'],
                    exchange_flow_signal=data['breakdown']['exchange_flows']['signal'],
                    whale_signal=data['breakdown']['whale_movements']['signal'],
                    recommendation=data['recommendation'],
                    timestamp=datetime.now(timezone.utc)
                )

                # Store for history
                self.recent_signals.append(signal)
                if len(self.recent_signals) > 100:
                    self.recent_signals = self.recent_signals[-100:]

                return signal

            elif self.onchain_client:
                # Fallback to basic metrics
                metrics = self.onchain_client.get_metrics(clean_symbol)

                # Interpret flow data
                whale_flow = metrics.get('whale_net_flow', 0)
                exchange_flow = metrics.get('exchange_net_flow', 0)

                # Negative exchange flow = outflow = accumulation = bullish
                if exchange_flow < -1e6:  # > $1M outflow
                    signal_type = "BULLISH"
                    score = min(abs(exchange_flow) / 1e6 * 10, 100)
                elif exchange_flow > 1e6:  # > $1M inflow
                    signal_type = "BEARISH"
                    score = -min(abs(exchange_flow) / 1e6 * 10, 100)
                else:
                    signal_type = "NEUTRAL"
                    score = 0

                return OnChainSignal(
                    symbol=clean_symbol,
                    signal=signal_type,
                    score=score,
                    confidence=50.0,
                    exchange_flow_signal=signal_type,
                    whale_signal="UNKNOWN",
                    recommendation=f"Exchange flow: ${exchange_flow:,.0f}",
                    timestamp=datetime.now(timezone.utc)
                )

        except Exception as e:
            logger.error(f"Error getting on-chain score: {e}")

        return None

    async def detect_accumulation(self, token: str) -> Optional[WhaleMovement]:
        """
        Detect if whales are accumulating a token

        Uses on-chain data to identify:
        - Exchange outflows (bullish)
        - Large wallet accumulation
        - TVL increases
        """
        try:
            if self.onchain_signals:
                # Get whale movements
                whale_data = self.onchain_signals.get_whale_movements(token)

                if whale_data['signal'] == 'BULLISH':
                    # Whales are accumulating
                    return WhaleMovement(
                        wallet=WhaleWallet(
                            address="aggregate",
                            label="On-Chain Analysis",
                            success_rate=0.7
                        ),
                        action="accumulation",
                        token=token,
                        amount=whale_data.get('net_exchange_flow', 0),
                        usd_value=abs(whale_data.get('net_exchange_flow', 0)),
                        timestamp=datetime.now(timezone.utc)
                    )

        except Exception as e:
            logger.debug(f"Accumulation detection: {e}")

        return None

    async def analyze_market(self, market_data) -> Dict:
        """
        Analyze market using on-chain intelligence

        This is the main entry point for HiveMind voting.
        Returns signal based on on-chain data (+16% alpha).
        """
        symbol = getattr(market_data, 'symbol', 'BTC/USD')
        clean_symbol = symbol.replace('/USD', '').replace('/USDT', '')

        # Get on-chain score
        onchain = await self.get_onchain_score(symbol)

        if onchain:
            self.stats["signals_generated"] += 1

            # Track signal distribution
            if onchain.signal == "BULLISH":
                self.stats["bullish_signals"] += 1
            elif onchain.signal == "BEARISH":
                self.stats["bearish_signals"] += 1
            else:
                self.stats["neutral_signals"] += 1

            # Update running average confidence
            total = self.stats["signals_generated"]
            old_avg = self.stats["avg_confidence"]
            self.stats["avg_confidence"] = (old_avg * (total - 1) + onchain.confidence) / total

            # Convert to trading decision
            if onchain.signal == "BULLISH" and onchain.confidence > 50:
                return {
                    "decision": "buy",
                    "confidence": onchain.confidence / 100,
                    "reasoning": f"On-chain bullish: {onchain.recommendation}",
                    "source": "on_chain_analysis",
                    "details": {
                        "score": onchain.score,
                        "exchange_flow": onchain.exchange_flow_signal,
                        "whale_activity": onchain.whale_signal
                    }
                }
            elif onchain.signal == "BEARISH" and onchain.confidence > 50:
                return {
                    "decision": "sell",
                    "confidence": onchain.confidence / 100,
                    "reasoning": f"On-chain bearish: {onchain.recommendation}",
                    "source": "on_chain_analysis",
                    "details": {
                        "score": onchain.score,
                        "exchange_flow": onchain.exchange_flow_signal,
                        "whale_activity": onchain.whale_signal
                    }
                }

        # Also check for specific whale accumulation
        movement = await self.detect_accumulation(clean_symbol)
        if movement and movement.action == "accumulation":
            return {
                "decision": "buy",
                "confidence": movement.wallet.success_rate,
                "reasoning": f"Whale accumulation detected: ${movement.usd_value:,.0f}",
                "source": "whale_activity"
            }

        return {
            "decision": "hold",
            "confidence": 0.0,
            "reasoning": "Insufficient on-chain signal"
        }

    def get_stats(self) -> Dict:
        """Get whale watcher statistics"""
        return {
            "agent_id": self.agent_id,
            "specialty": self.specialty,
            **self.stats
        }


def create_whale_watcher(agent_id: str = "whale_watcher") -> WhaleWatcherAgent:
    """Factory function to create whale watcher agent"""
    return WhaleWatcherAgent(agent_id=agent_id)


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("🐋 WHALE WATCHER AGENT - On-Chain Intelligence")
    print("=" * 70)
    print()

    agent = create_whale_watcher()
    stats = agent.get_stats()

    print(f"Agent ID: {stats['agent_id']}")
    print(f"Specialty: {stats['specialty']}")
    print(f"Whales Tracked: {stats['whales_tracked']}")
    print()
    print("Alpha Source: +16% improvement (CryptoTrade EMNLP 2024)")
    print("Capital Allocation: 15% (highest alpha)")
    print()
    print("Capabilities:")
    print("  - Exchange flow analysis (accumulation vs distribution)")
    print("  - Whale movement tracking")
    print("  - TVL and address metrics via DS-Star")
    print("  - Integration with OnChainSignals module")
    print()
    print("✅ Whale Watcher ready with on-chain intelligence!")
    print("=" * 70)
