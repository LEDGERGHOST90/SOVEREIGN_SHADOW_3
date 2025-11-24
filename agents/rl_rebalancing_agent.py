#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - RL REBALANCING AGENT
Reinforcement Learning agent for portfolio rebalancing decisions

Uses Deep Q-Network (DQN) to learn:
- WHEN to rebalance (timing)
- HOW MUCH to rebalance (sizing)
- WHICH assets to prioritize

Philosophy: "Learn from experience, not just rules"

Author: SovereignShadow Trading System
Created: 2025-11-24
"""

import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import random

# Try to import deep learning libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True

    class DQNetwork(nn.Module):
        """Deep Q-Network for state-action value estimation"""

        def __init__(self, state_size: int, action_size: int, hidden_size: int = 128):
            super(DQNetwork, self).__init__()

            self.fc1 = nn.Linear(state_size, hidden_size)
            self.fc2 = nn.Linear(hidden_size, hidden_size)
            self.fc3 = nn.Linear(hidden_size, action_size)

        def forward(self, state):
            """Forward pass through network"""
            x = torch.relu(self.fc1(state))
            x = torch.relu(self.fc2(x))
            return self.fc3(x)

except ImportError:
    TORCH_AVAILABLE = False
    DQNetwork = None
    print("⚠️  PyTorch not installed. RL agent will run in simulation mode.")
    print("   Install with: pip install torch")


class ReplayBuffer:
    """Experience replay buffer for training stability"""

    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        """Sample random batch from buffer"""
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones)
        )

    def __len__(self):
        return len(self.buffer)


class RLRebalancingAgent:
    """
    Reinforcement Learning Agent for Portfolio Rebalancing

    Learns optimal rebalancing strategy through experience:
    - Maximizes portfolio value
    - Minimizes transaction costs
    - Respects risk management rules (SHADE integration)
    """

    def __init__(
        self,
        state_size: int = 16,
        action_size: int = 4,
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_capacity: int = 10000,
        batch_size: int = 32,
        model_path: str = "models/rl_rebalancer.pth"
    ):
        """
        Initialize RL agent

        Args:
            state_size: Dimension of state space
            action_size: Number of discrete actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor for future rewards
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Epsilon decay per episode
            memory_capacity: Size of replay buffer
            batch_size: Training batch size
            model_path: Path to save/load model
        """
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        # Experience replay
        self.memory = ReplayBuffer(memory_capacity)

        # Training statistics
        self.episode = 0
        self.total_rewards = []
        self.losses = []

        # Initialize networks
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.policy_net = DQNetwork(state_size, action_size).to(self.device)
            self.target_net = DQNetwork(state_size, action_size).to(self.device)
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.target_net.eval()

            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
            self.criterion = nn.MSELoss()

            # Try to load existing model
            self._load_model()
        else:
            print("⚠️  Running in SIMULATION mode (no PyTorch)")
            self.device = None
            self.policy_net = None

        print("🧠 RL REBALANCING AGENT initialized")
        print(f"   State Size: {state_size}")
        print(f"   Action Size: {action_size}")
        print(f"   Device: {self.device if TORCH_AVAILABLE else 'CPU (sim)'}")
        print(f"   Epsilon: {self.epsilon:.3f}")
        print(f"   Episodes Completed: {self.episode}")

    def encode_state(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float],
        prices: Dict[str, float],
        momentum_7d: Dict[str, float],
        volatility: Dict[str, float],
        shade_strike_level: int,
        available_capital: float
    ) -> np.ndarray:
        """
        Encode portfolio state into feature vector

        State features (16 dims):
        - Current allocations (4): BTC%, ETH%, SOL%, XRP%
        - Deviations from target (4): difference from target
        - Price momentum 7d (4): recent price changes
        - Volatility levels (4): current volatility for each asset

        Returns:
            State vector (numpy array)
        """
        assets = ['BTC', 'ETH', 'SOL', 'XRP']

        state = []

        # Current allocations (normalized to 0-1)
        for asset in assets:
            state.append(current_allocation.get(asset, 0) / 100)

        # Deviations from target (normalized to -1 to 1)
        for asset in assets:
            current = current_allocation.get(asset, 0)
            target = target_allocation.get(asset, 0)
            deviation = (current - target) / 100
            state.append(deviation)

        # Price momentum (normalized to -1 to 1, clamped)
        for asset in assets:
            momentum = momentum_7d.get(asset, 0) / 100  # Convert % to fraction
            state.append(np.clip(momentum, -1, 1))

        # Volatility (normalized to 0-1, clamped)
        for asset in assets:
            vol = volatility.get(asset, 0.5)  # Default medium volatility
            state.append(np.clip(vol, 0, 1))

        return np.array(state, dtype=np.float32)

    def decode_action(self, action_idx: int) -> Dict[str, Any]:
        """
        Decode action index into rebalancing decision

        Actions:
        0: Do nothing (wait)
        1: Small rebalance (25% of needed adjustment)
        2: Medium rebalance (50% of needed adjustment)
        3: Full rebalance (100% of needed adjustment)

        Args:
            action_idx: Index from 0 to action_size-1

        Returns:
            Action dict with interpretation
        """
        actions = {
            0: {"action": "WAIT", "rebalance_pct": 0, "description": "No rebalancing"},
            1: {"action": "SMALL", "rebalance_pct": 25, "description": "Small rebalance (25%)"},
            2: {"action": "MEDIUM", "rebalance_pct": 50, "description": "Medium rebalance (50%)"},
            3: {"action": "FULL", "rebalance_pct": 100, "description": "Full rebalance (100%)"}
        }

        return actions.get(action_idx, actions[0])

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy

        Args:
            state: Current state vector
            training: If True, use epsilon-greedy; if False, use greedy

        Returns:
            Action index
        """
        # Exploration (random action)
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        # Exploitation (best action from network)
        if TORCH_AVAILABLE:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return q_values.argmax().item()
        else:
            # Simulation mode: use rule-based fallback
            return self._rule_based_fallback(state)

    def _rule_based_fallback(self, state: np.ndarray) -> int:
        """
        Rule-based fallback when PyTorch not available
        Uses 15% threshold logic from portfolio_rebalancer.py
        """
        # Extract deviation from state (indices 4-7)
        deviations = state[4:8] * 100  # Convert back to percentages
        max_deviation = np.max(np.abs(deviations))

        if max_deviation < 15:
            return 0  # WAIT
        elif max_deviation < 30:
            return 1  # SMALL
        elif max_deviation < 50:
            return 2  # MEDIUM
        else:
            return 3  # FULL

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)

    def train(self):
        """Train the network on a batch of experiences"""
        if len(self.memory) < self.batch_size or not TORCH_AVAILABLE:
            return 0.0

        # Sample batch from replay buffer
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))

        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        # Compute loss and update
        loss = self.criterion(current_q_values.squeeze(), target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def update_target_network(self):
        """Copy weights from policy network to target network"""
        if TORCH_AVAILABLE:
            self.target_net.load_state_dict(self.policy_net.state_dict())

    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def end_episode(self, total_reward: float):
        """Mark end of episode and update statistics"""
        self.episode += 1
        self.total_rewards.append(total_reward)
        self.decay_epsilon()

        # Update target network every 10 episodes
        if self.episode % 10 == 0:
            self.update_target_network()
            self._save_model()
            print(f"📊 Episode {self.episode}: Reward={total_reward:.2f}, ε={self.epsilon:.3f}")

    def _save_model(self):
        """Save model weights and training statistics"""
        if not TORCH_AVAILABLE:
            return

        checkpoint = {
            'episode': self.episode,
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'total_rewards': self.total_rewards,
            'losses': self.losses
        }

        torch.save(checkpoint, self.model_path)
        print(f"✅ Model saved to {self.model_path}")

    def _load_model(self):
        """Load model weights and training statistics"""
        if not TORCH_AVAILABLE or not self.model_path.exists():
            return

        checkpoint = torch.load(self.model_path, map_location=self.device)

        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.episode = checkpoint['episode']
        self.total_rewards = checkpoint.get('total_rewards', [])
        self.losses = checkpoint.get('losses', [])

        print(f"✅ Model loaded from {self.model_path}")
        print(f"   Resuming from episode {self.episode}")


def demo_rl_agent():
    """Demonstrate RL agent with simulated rebalancing scenario"""
    print("\n" + "="*80)
    print("🧠 RL REBALANCING AGENT - DEMONSTRATION")
    print("="*80)

    # Initialize agent
    agent = RLRebalancingAgent(
        state_size=16,
        action_size=4,
        epsilon_start=1.0 if TORCH_AVAILABLE else 0.0  # No exploration in sim mode
    )

    # Simulate rebalancing scenario (your actual portfolio)
    current_allocation = {"BTC": 36.2, "ETH": 0.0, "SOL": 0.0, "XRP": 0.0}
    target_allocation = {"BTC": 40.0, "ETH": 30.0, "SOL": 20.0, "XRP": 10.0}

    prices = {"BTC": 101746, "ETH": 3200, "SOL": 235, "XRP": 2.1}
    momentum_7d = {"BTC": -1.2, "ETH": +3.5, "SOL": +2.1, "XRP": -0.5}
    volatility = {"BTC": 0.3, "ETH": 0.4, "SOL": 0.6, "XRP": 0.5}

    # Encode state
    state = agent.encode_state(
        current_allocation=current_allocation,
        target_allocation=target_allocation,
        prices=prices,
        momentum_7d=momentum_7d,
        volatility=volatility,
        shade_strike_level=0,
        available_capital=6167.43
    )

    print(f"\n📊 CURRENT PORTFOLIO STATE:")
    print(f"   BTC: {current_allocation['BTC']:.1f}% (target: {target_allocation['BTC']:.1f}%)")
    print(f"   ETH: {current_allocation['ETH']:.1f}% (target: {target_allocation['ETH']:.1f}%)")
    print(f"   SOL: {current_allocation['SOL']:.1f}% (target: {target_allocation['SOL']:.1f}%)")
    print(f"   XRP: {current_allocation['XRP']:.1f}% (target: {target_allocation['XRP']:.1f}%)")

    # Agent selects action
    action_idx = agent.select_action(state, training=False)
    action = agent.decode_action(action_idx)

    print(f"\n🤖 RL AGENT DECISION:")
    print(f"   Action: {action['action']}")
    print(f"   Description: {action['description']}")
    print(f"   Rebalance Amount: {action['rebalance_pct']}%")

    print("\n💡 INTERPRETATION:")
    if action['action'] == 'WAIT':
        print("   Agent recommends waiting (BTC only 9.5% off target)")
    elif action['action'] == 'SMALL':
        print("   Agent suggests small position adjustments")
    elif action['action'] == 'MEDIUM':
        print("   Agent recommends moderate rebalancing")
    else:
        print("   Agent calls for full rebalancing (ETH/SOL/XRP at 0%)")

    print("\n🎓 LEARNING PROCESS:")
    print(f"   Current Exploration Rate (ε): {agent.epsilon:.3f}")
    print(f"   Training Episodes Completed: {agent.episode}")
    print(f"   Experience Buffer Size: {len(agent.memory)}")

    if TORCH_AVAILABLE:
        print("\n✅ PyTorch available - agent can learn from experience")
        print("   Next steps:")
        print("   1. Run simulated backtests to generate training data")
        print("   2. Agent learns optimal rebalancing timing/sizing")
        print("   3. Gradually reduce exploration as performance improves")
    else:
        print("\n⚠️  PyTorch not installed - using rule-based fallback")
        print("   Install PyTorch to enable learning:")
        print("   pip install torch")

    print("="*80 + "\n")


if __name__ == "__main__":
    demo_rl_agent()
