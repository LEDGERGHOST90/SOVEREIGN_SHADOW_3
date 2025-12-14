#!/usr/bin/env python3
"""
Order Book Deep RL Scaffold - Sovereign Shadow III
Based on 2024-2025 Research: Training on Full Limit Order Book (LOB) Snapshots

Key Insight: Train on LOB microstructure rather than OHLCV candles to capture
information invisible to price-only strategies.

Architecture:
- DDQN (Double Deep Q-Network) with Prioritized Experience Replay
- State: LOB snapshot features (spread, imbalance, depth, flow)
- Actions: BUY, SELL, HOLD
- Reward: PnL with transaction costs

References:
- "Deep Reinforcement Learning for Market Making" (2024)
- "Order Flow Imbalance and High-Frequency Trading" (2024)
- "LOB Feature Engineering for Algorithmic Trading" (2025)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import logging
import json

# CCXT for exchange integration
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    logging.warning("CCXT not available - install with: pip install ccxt")

# PyTorch for neural networks (optional for now)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - install with: pip install torch")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ORDER BOOK DATA STRUCTURES
# ============================================================================

@dataclass
class OrderBookSnapshot:
    """Single order book snapshot with microstructure features"""
    timestamp: datetime
    symbol: str

    # Raw order book data
    bids: List[Tuple[float, float]]  # [(price, volume), ...]
    asks: List[Tuple[float, float]]  # [(price, volume), ...]

    # Derived features (computed on initialization)
    spread: float = 0.0
    mid_price: float = 0.0
    vwmp: float = 0.0  # Volume-weighted mid price
    imbalance: float = 0.0  # Order book imbalance
    bid_depth: List[float] = None  # Cumulative bid depth
    ask_depth: List[float] = None  # Cumulative ask depth

    def __post_init__(self):
        """Compute derived features from raw order book"""
        if not self.bids or not self.asks:
            return

        # Best bid/ask
        best_bid = self.bids[0][0]
        best_ask = self.asks[0][0]

        # Spread
        self.spread = best_ask - best_bid

        # Mid price
        self.mid_price = (best_bid + best_ask) / 2.0

        # Volume-weighted mid price (VWMP)
        bid_vwap = sum(p * v for p, v in self.bids[:5]) / sum(v for _, v in self.bids[:5])
        ask_vwap = sum(p * v for p, v in self.asks[:5]) / sum(v for _, v in self.asks[:5])
        self.vwmp = (bid_vwap + ask_vwap) / 2.0

        # Order book imbalance: (bid_vol - ask_vol) / (bid_vol + ask_vol)
        total_bid_vol = sum(v for _, v in self.bids[:10])
        total_ask_vol = sum(v for _, v in self.asks[:10])
        if total_bid_vol + total_ask_vol > 0:
            self.imbalance = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol)

        # Cumulative depth at price levels
        self.bid_depth = [sum(v for _, v in self.bids[:i+1]) for i in range(min(10, len(self.bids)))]
        self.ask_depth = [sum(v for _, v in self.asks[:i+1]) for i in range(min(10, len(self.asks)))]

    def to_feature_vector(self) -> np.ndarray:
        """
        Convert order book snapshot to feature vector for ML

        Features (53 dimensions):
        - Spread (1)
        - Mid price (1)
        - VWMP (1)
        - Imbalance (1)
        - Bid prices L1-L10 (10)
        - Ask prices L1-L10 (10)
        - Bid volumes L1-L10 (10)
        - Ask volumes L1-L10 (10)
        - Bid cumulative depth L1-L10 (10)
        """
        features = []

        # Scalar features
        features.extend([
            self.spread,
            self.mid_price,
            self.vwmp,
            self.imbalance
        ])

        # Bid/ask prices and volumes (normalize later)
        for i in range(10):
            if i < len(self.bids):
                features.append(self.bids[i][0])  # Bid price
            else:
                features.append(0.0)

        for i in range(10):
            if i < len(self.asks):
                features.append(self.asks[i][0])  # Ask price
            else:
                features.append(0.0)

        for i in range(10):
            if i < len(self.bids):
                features.append(self.bids[i][1])  # Bid volume
            else:
                features.append(0.0)

        for i in range(10):
            if i < len(self.asks):
                features.append(self.asks[i][1])  # Ask volume
            else:
                features.append(0.0)

        # Cumulative depth
        for i in range(10):
            if i < len(self.bid_depth):
                features.append(self.bid_depth[i])
            else:
                features.append(0.0)

        return np.array(features, dtype=np.float32)


# ============================================================================
# ORDER BOOK COLLECTOR
# ============================================================================

class OrderBookCollector:
    """
    Collects real-time order book snapshots from exchanges

    Supports:
    - Coinbase Advanced Trade
    - Kraken
    - Binance US
    - Any CCXT-supported exchange
    """

    def __init__(self, exchange_id: str = 'coinbase', credentials: Dict = None):
        """
        Initialize order book collector

        Args:
            exchange_id: Exchange name ('coinbase', 'kraken', 'binance')
            credentials: API credentials (if needed for private endpoints)
        """
        if not CCXT_AVAILABLE:
            raise ImportError("CCXT required - install with: pip install ccxt")

        self.exchange_id = exchange_id
        self.credentials = credentials or {}

        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'enableRateLimit': True,
            **self.credentials
        })

        logger.info(f"OrderBookCollector initialized for {exchange_id}")

    def get_orderbook_snapshot(
        self,
        symbol: str,
        depth: int = 20
    ) -> Optional[OrderBookSnapshot]:
        """
        Fetch current order book snapshot

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            depth: Number of price levels to fetch

        Returns:
            OrderBookSnapshot or None if fetch failed
        """
        try:
            # Fetch order book
            ob = self.exchange.fetch_order_book(symbol, limit=depth)

            # Convert to our format
            snapshot = OrderBookSnapshot(
                timestamp=datetime.utcnow(),
                symbol=symbol,
                bids=[(price, volume) for price, volume in ob['bids']],
                asks=[(price, volume) for price, volume in ob['asks']]
            )

            return snapshot

        except Exception as e:
            logger.error(f"Failed to fetch order book for {symbol}: {e}")
            return None

    def collect_historical_snapshots(
        self,
        symbol: str,
        duration_minutes: int = 60,
        interval_seconds: int = 5,
        depth: int = 20
    ) -> List[OrderBookSnapshot]:
        """
        Collect order book snapshots over time

        Args:
            symbol: Trading pair
            duration_minutes: How long to collect data
            interval_seconds: Seconds between snapshots
            depth: Order book depth

        Returns:
            List of OrderBookSnapshot objects
        """
        import time

        snapshots = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        logger.info(f"Collecting {symbol} order book for {duration_minutes} min...")

        while time.time() < end_time:
            snapshot = self.get_orderbook_snapshot(symbol, depth)
            if snapshot:
                snapshots.append(snapshot)
                logger.info(f"Snapshot {len(snapshots)}: spread=${snapshot.spread:.2f}, imbalance={snapshot.imbalance:.3f}")

            time.sleep(interval_seconds)

        logger.info(f"Collection complete: {len(snapshots)} snapshots")
        return snapshots

    def save_snapshots(self, snapshots: List[OrderBookSnapshot], filepath: str):
        """Save snapshots to JSON file"""
        data = []
        for snap in snapshots:
            data.append({
                'timestamp': snap.timestamp.isoformat(),
                'symbol': snap.symbol,
                'bids': snap.bids[:10],  # Save top 10 levels
                'asks': snap.asks[:10],
                'spread': snap.spread,
                'mid_price': snap.mid_price,
                'vwmp': snap.vwmp,
                'imbalance': snap.imbalance
            })

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(snapshots)} snapshots to {filepath}")

    def load_snapshots(self, filepath: str) -> List[OrderBookSnapshot]:
        """Load snapshots from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        snapshots = []
        for item in data:
            snapshot = OrderBookSnapshot(
                timestamp=datetime.fromisoformat(item['timestamp']),
                symbol=item['symbol'],
                bids=[(p, v) for p, v in item['bids']],
                asks=[(p, v) for p, v in item['asks']]
            )
            snapshots.append(snapshot)

        logger.info(f"Loaded {len(snapshots)} snapshots from {filepath}")
        return snapshots


# ============================================================================
# ORDER FLOW FEATURES
# ============================================================================

class OrderFlowAnalyzer:
    """Analyzes order flow from sequential order book snapshots"""

    @staticmethod
    def compute_order_flow_imbalance(
        prev_snapshot: OrderBookSnapshot,
        curr_snapshot: OrderBookSnapshot
    ) -> float:
        """
        Compute order flow imbalance (OFI) between two snapshots

        OFI = (ΔBid_volume - ΔAsk_volume) at best prices

        Positive OFI indicates buying pressure, negative indicates selling pressure
        """
        if not prev_snapshot or not curr_snapshot:
            return 0.0

        # Change in bid volume at best price
        prev_best_bid_vol = prev_snapshot.bids[0][1] if prev_snapshot.bids else 0
        curr_best_bid_vol = curr_snapshot.bids[0][1] if curr_snapshot.bids else 0
        delta_bid = curr_best_bid_vol - prev_best_bid_vol

        # Change in ask volume at best price
        prev_best_ask_vol = prev_snapshot.asks[0][1] if prev_snapshot.asks else 0
        curr_best_ask_vol = curr_snapshot.asks[0][1] if curr_snapshot.asks else 0
        delta_ask = curr_best_ask_vol - prev_best_ask_vol

        return delta_bid - delta_ask

    @staticmethod
    def detect_price_level_changes(
        prev_snapshot: OrderBookSnapshot,
        curr_snapshot: OrderBookSnapshot
    ) -> Dict[str, int]:
        """
        Detect changes in price levels

        Returns:
            {
                'bid_levels_added': int,
                'bid_levels_removed': int,
                'ask_levels_added': int,
                'ask_levels_removed': int
            }
        """
        prev_bid_prices = set(p for p, _ in prev_snapshot.bids)
        curr_bid_prices = set(p for p, _ in curr_snapshot.bids)

        prev_ask_prices = set(p for p, _ in prev_snapshot.asks)
        curr_ask_prices = set(p for p, _ in curr_snapshot.asks)

        return {
            'bid_levels_added': len(curr_bid_prices - prev_bid_prices),
            'bid_levels_removed': len(prev_bid_prices - curr_bid_prices),
            'ask_levels_added': len(curr_ask_prices - prev_ask_prices),
            'ask_levels_removed': len(prev_ask_prices - curr_ask_prices)
        }


# ============================================================================
# RL ENVIRONMENT (Gym-style)
# ============================================================================

class OrderBookEnv:
    """
    OpenAI Gym-style environment for order book RL

    State: Order book snapshot features (53 dimensions)
    Actions: 0=HOLD, 1=BUY, 2=SELL
    Reward: PnL with transaction costs
    """

    def __init__(
        self,
        snapshots: List[OrderBookSnapshot],
        initial_balance: float = 10000.0,
        position_size: float = 0.01,  # As fraction of balance
        transaction_cost: float = 0.0006,  # 0.06% fee
        lookback: int = 10  # Include last N snapshots in state
    ):
        """
        Initialize RL environment

        Args:
            snapshots: Historical order book snapshots
            initial_balance: Starting capital in USD
            position_size: Position size as fraction of balance
            transaction_cost: Trading fee (0.0006 = 0.06%)
            lookback: Number of previous snapshots to include in state
        """
        self.snapshots = snapshots
        self.initial_balance = initial_balance
        self.position_size = position_size
        self.transaction_cost = transaction_cost
        self.lookback = lookback

        # Environment state
        self.current_step = lookback  # Start after lookback period
        self.balance = initial_balance
        self.position = 0.0  # Current BTC position
        self.entry_price = 0.0
        self.total_trades = 0

        # Action space
        self.action_space = ['HOLD', 'BUY', 'SELL']
        self.n_actions = len(self.action_space)

        # State space (53 features * lookback)
        self.state_dim = 53 * lookback

        # History tracking
        self.history = {
            'balance': [initial_balance],
            'position': [0.0],
            'actions': [],
            'rewards': [],
            'pnl': []
        }

        logger.info(f"OrderBookEnv initialized: {len(snapshots)} snapshots, lookback={lookback}")

    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        self.current_step = self.lookback
        self.balance = self.initial_balance
        self.position = 0.0
        self.entry_price = 0.0
        self.total_trades = 0

        self.history = {
            'balance': [self.initial_balance],
            'position': [0.0],
            'actions': [],
            'rewards': [],
            'pnl': []
        }

        return self._get_state()

    def _get_state(self) -> np.ndarray:
        """
        Get current state (order book features from last N snapshots)

        Returns:
            State vector (lookback * 53 dimensions)
        """
        state_vectors = []

        # Get last N snapshots
        for i in range(self.current_step - self.lookback, self.current_step):
            snapshot = self.snapshots[i]
            features = snapshot.to_feature_vector()
            state_vectors.append(features)

        # Flatten into single vector
        state = np.concatenate(state_vectors)

        # Normalize (simple min-max, improve this in production)
        # TODO: Use proper feature scaling (StandardScaler, MinMaxScaler)

        return state

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action and return (next_state, reward, done, info)

        Args:
            action: 0=HOLD, 1=BUY, 2=SELL

        Returns:
            (next_state, reward, done, info)
        """
        # Get current and next price
        current_snapshot = self.snapshots[self.current_step]
        current_price = current_snapshot.mid_price

        # Execute action
        reward = 0.0
        action_name = self.action_space[action]

        if action == 1:  # BUY
            if self.position == 0.0:  # Only buy if not already in position
                # Calculate position size
                trade_amount = self.balance * self.position_size
                coins = trade_amount / current_price
                fee = trade_amount * self.transaction_cost

                self.position = coins
                self.entry_price = current_price
                self.balance -= (trade_amount + fee)
                self.total_trades += 1

                logger.debug(f"BUY: {coins:.6f} @ ${current_price:.2f}, fee=${fee:.2f}")

        elif action == 2:  # SELL
            if self.position > 0.0:  # Only sell if we have a position
                # Sell entire position
                proceeds = self.position * current_price
                fee = proceeds * self.transaction_cost

                # Calculate PnL
                pnl = proceeds - (self.position * self.entry_price) - fee
                reward = pnl / self.initial_balance  # Normalize reward

                self.balance += (proceeds - fee)
                self.position = 0.0
                self.entry_price = 0.0
                self.total_trades += 1

                logger.debug(f"SELL: ${proceeds:.2f}, PnL=${pnl:.2f}, reward={reward:.4f}")

                self.history['pnl'].append(pnl)

        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.snapshots) - 1

        # Track history
        self.history['balance'].append(self.balance)
        self.history['position'].append(self.position)
        self.history['actions'].append(action_name)
        self.history['rewards'].append(reward)

        # Get next state
        next_state = self._get_state() if not done else np.zeros(self.state_dim)

        # Info dict
        info = {
            'balance': self.balance,
            'position': self.position,
            'current_price': current_price,
            'total_trades': self.total_trades,
            'step': self.current_step
        }

        return next_state, reward, done, info

    def get_total_value(self) -> float:
        """Get current portfolio value (balance + position value)"""
        if self.position > 0 and self.current_step < len(self.snapshots):
            current_price = self.snapshots[self.current_step].mid_price
            return self.balance + (self.position * current_price)
        return self.balance

    def get_performance_summary(self) -> Dict:
        """Get performance metrics"""
        final_value = self.get_total_value()
        total_return = (final_value - self.initial_balance) / self.initial_balance

        return {
            'initial_balance': self.initial_balance,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'total_trades': self.total_trades,
            'total_pnl': sum(self.history['pnl']),
            'avg_pnl_per_trade': np.mean(self.history['pnl']) if self.history['pnl'] else 0.0
        }


# ============================================================================
# DDQN AGENT (SCAFFOLD - Requires PyTorch)
# ============================================================================

class DDQNAgent:
    """
    Double Deep Q-Network with Prioritized Experience Replay

    SCAFFOLD ONLY - Implement full training loop separately

    Architecture:
    - Input: Order book features (53 * lookback dimensions)
    - Hidden: 256 -> 128 -> 64
    - Output: Q-values for 3 actions (HOLD, BUY, SELL)
    """

    def __init__(
        self,
        state_dim: int,
        n_actions: int = 3,
        learning_rate: float = 0.0001,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        buffer_size: int = 10000
    ):
        """
        Initialize DDQN agent

        Args:
            state_dim: State space dimensions
            n_actions: Number of actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Epsilon decay rate
            buffer_size: Replay buffer size
        """
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        # Experience replay buffer
        self.memory = deque(maxlen=buffer_size)

        # PyTorch models (placeholder - implement when PyTorch available)
        if TORCH_AVAILABLE:
            self.q_network = self._build_network()
            self.target_network = self._build_network()
            self.target_network.load_state_dict(self.q_network.state_dict())
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
            self.criterion = nn.MSELoss()

            logger.info("DDQN agent initialized with PyTorch")
        else:
            logger.warning("PyTorch not available - DDQN is scaffold only")
            self.q_network = None
            self.target_network = None

    def _build_network(self):
        """Build Q-network (placeholder)"""
        if not TORCH_AVAILABLE:
            return None

        # Simple feedforward network
        model = nn.Sequential(
            nn.Linear(self.state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.n_actions)
        )
        return model

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy

        Args:
            state: Current state
            training: If True, use epsilon-greedy, else greedy

        Returns:
            Action index (0=HOLD, 1=BUY, 2=SELL)
        """
        # Epsilon-greedy exploration
        if training and np.random.random() < self.epsilon:
            return np.random.randint(0, self.n_actions)

        # Greedy action (exploit)
        if self.q_network is not None:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                q_values = self.q_network(state_tensor)
                return q_values.argmax().item()
        else:
            # Fallback: random action
            return np.random.randint(0, self.n_actions)

    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """Store transition in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))

    def train_step(self, batch_size: int = 32):
        """
        Perform one training step (PLACEHOLDER)

        Implement:
        1. Sample batch from replay buffer
        2. Compute target Q-values using target network
        3. Compute current Q-values
        4. Compute loss and backpropagate
        5. Update target network periodically
        """
        if len(self.memory) < batch_size:
            return 0.0

        # TODO: Implement full DDQN training loop
        # - Sample batch
        # - Compute targets: Q_target = reward + gamma * max_a Q_target(s', a)
        # - Compute loss: MSE(Q(s, a), Q_target)
        # - Backpropagate
        # - Soft update target network

        logger.debug("train_step() is a placeholder - implement full training loop")
        return 0.0

    def update_epsilon(self):
        """Decay epsilon for exploration"""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def save_model(self, filepath: str):
        """Save model weights"""
        if self.q_network is not None:
            torch.save(self.q_network.state_dict(), filepath)
            logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load model weights"""
        if self.q_network is not None:
            self.q_network.load_state_dict(torch.load(filepath))
            self.target_network.load_state_dict(self.q_network.state_dict())
            logger.info(f"Model loaded from {filepath}")


# ============================================================================
# EXAMPLE USAGE & DATA COLLECTION
# ============================================================================

def example_data_collection():
    """Example: Collect order book data from Coinbase"""
    print("\n" + "="*70)
    print("ORDER BOOK DATA COLLECTION EXAMPLE")
    print("="*70)

    # Initialize collector (no credentials needed for public order book)
    collector = OrderBookCollector(exchange_id='coinbase')

    # Get single snapshot
    print("\n1. Fetching single BTC/USD order book snapshot...")
    snapshot = collector.get_orderbook_snapshot('BTC/USD', depth=20)

    if snapshot:
        print(f"   Timestamp: {snapshot.timestamp}")
        print(f"   Symbol: {snapshot.symbol}")
        print(f"   Spread: ${snapshot.spread:.2f}")
        print(f"   Mid Price: ${snapshot.mid_price:,.2f}")
        print(f"   VWMP: ${snapshot.vwmp:,.2f}")
        print(f"   Imbalance: {snapshot.imbalance:.4f}")
        print(f"   Best Bid: ${snapshot.bids[0][0]:,.2f} ({snapshot.bids[0][1]:.6f} BTC)")
        print(f"   Best Ask: ${snapshot.asks[0][0]:,.2f} ({snapshot.asks[0][1]:.6f} BTC)")

        # Convert to feature vector
        features = snapshot.to_feature_vector()
        print(f"   Feature vector shape: {features.shape}")
        print(f"   Feature vector (first 10): {features[:10]}")

    # Collect historical snapshots (commented out - takes time)
    # print("\n2. Collecting 5 minutes of order book data (30 second intervals)...")
    # snapshots = collector.collect_historical_snapshots(
    #     symbol='BTC/USD',
    #     duration_minutes=5,
    #     interval_seconds=30,
    #     depth=20
    # )
    #
    # # Save to file
    # collector.save_snapshots(snapshots, '/tmp/btc_orderbook_snapshots.json')
    # print(f"   Saved {len(snapshots)} snapshots")


def example_rl_environment():
    """Example: Create RL environment with synthetic data"""
    print("\n" + "="*70)
    print("RL ENVIRONMENT EXAMPLE (Synthetic Data)")
    print("="*70)

    # Create synthetic order book snapshots for testing
    print("\n1. Creating synthetic order book snapshots...")

    snapshots = []
    base_price = 100000.0  # $100k BTC

    for i in range(100):
        # Simulate price movement
        price = base_price + np.random.randn() * 100

        # Create synthetic bids/asks
        bids = [(price - j*10, np.random.uniform(0.1, 2.0)) for j in range(1, 21)]
        asks = [(price + j*10, np.random.uniform(0.1, 2.0)) for j in range(1, 21)]

        snapshot = OrderBookSnapshot(
            timestamp=datetime.utcnow(),
            symbol='BTC/USD',
            bids=bids,
            asks=asks
        )
        snapshots.append(snapshot)

    print(f"   Created {len(snapshots)} synthetic snapshots")

    # Create environment
    print("\n2. Initializing OrderBookEnv...")
    env = OrderBookEnv(
        snapshots=snapshots,
        initial_balance=10000.0,
        position_size=0.1,
        lookback=5
    )

    print(f"   State dimension: {env.state_dim}")
    print(f"   Action space: {env.action_space}")

    # Run random episode
    print("\n3. Running random episode (50 steps)...")
    state = env.reset()

    for step in range(50):
        action = np.random.randint(0, 3)  # Random action
        next_state, reward, done, info = env.step(action)

        if reward != 0:
            print(f"   Step {step}: {env.action_space[action]} | Reward: {reward:.4f} | Balance: ${info['balance']:.2f}")

        if done:
            break

        state = next_state

    # Performance summary
    print("\n4. Performance Summary:")
    perf = env.get_performance_summary()
    for key, value in perf.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")


def example_ddqn_agent():
    """Example: Initialize DDQN agent"""
    print("\n" + "="*70)
    print("DDQN AGENT EXAMPLE")
    print("="*70)

    if not TORCH_AVAILABLE:
        print("\n   PyTorch not installed - showing scaffold only")
        print("   Install with: pip install torch")

    # Initialize agent
    print("\n1. Initializing DDQN agent...")
    agent = DDQNAgent(
        state_dim=53 * 5,  # 5 snapshots lookback
        n_actions=3,
        learning_rate=0.0001,
        gamma=0.99
    )

    print(f"   State dim: {agent.state_dim}")
    print(f"   Actions: {agent.n_actions}")
    print(f"   Epsilon: {agent.epsilon}")
    print(f"   Memory size: {len(agent.memory)}")

    if TORCH_AVAILABLE and agent.q_network:
        print(f"\n2. Q-Network Architecture:")
        print(agent.q_network)


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("ORDER BOOK DEEP RL SCAFFOLD - SOVEREIGN SHADOW III")
    print("="*70)
    print("\nBased on 2024-2025 Research:")
    print("- Training on full LOB snapshots vs OHLCV candles")
    print("- Capturing microstructure information for better alpha")
    print("- DDQN with prioritized experience replay")
    print("\nThis is a SCAFFOLD for future development.")
    print("Focus: Data collection and feature engineering that works NOW.")

    # Run examples
    try:
        example_data_collection()
    except Exception as e:
        logger.error(f"Data collection example failed: {e}")

    try:
        example_rl_environment()
    except Exception as e:
        logger.error(f"RL environment example failed: {e}")

    try:
        example_ddqn_agent()
    except Exception as e:
        logger.error(f"DDQN agent example failed: {e}")

    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Collect real order book data: python orderbook_rl_scaffold.py")
    print("2. Build training dataset: 24-48 hours of snapshots")
    print("3. Implement full DDQN training loop")
    print("4. Add prioritized experience replay")
    print("5. Backtest trained agent on historical data")
    print("6. Paper trade with live order book feed")
    print("7. Deploy to production with risk controls")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
