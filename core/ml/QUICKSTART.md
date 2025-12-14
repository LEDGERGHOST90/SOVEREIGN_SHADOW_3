# Order Book RL - Quick Start Guide

## Installation

```bash
cd /Volumes/LegacySafe/SS_III
pip install ccxt numpy pandas torch
```

## 1. Collect Real Order Book Data (5 minutes)

```bash
python core/ml/collect_orderbook_data.py \
    --symbol BTC/USD \
    --duration 60 \
    --interval 5
```

**Output:** `data/orderbook/BTC_USD_60min_TIMESTAMP.json`

## 2. Load and Explore Data

```python
from core.ml.orderbook_rl_scaffold import OrderBookCollector

# Load data
collector = OrderBookCollector()
snapshots = collector.load_snapshots('data/orderbook/BTC_USD_60min_20251214_133000.json')

# Explore
print(f"Snapshots: {len(snapshots)}")
print(f"First snapshot: {snapshots[0]}")
print(f"Spread: ${snapshots[0].spread:.2f}")
print(f"Imbalance: {snapshots[0].imbalance:.4f}")
```

## 3. Create RL Environment

```python
from core.ml.orderbook_rl_scaffold import OrderBookEnv

env = OrderBookEnv(
    snapshots=snapshots,
    initial_balance=10000.0,
    position_size=0.1,
    transaction_cost=0.0006,
    lookback=10
)

# Run random episode
state = env.reset()
done = False

while not done:
    action = env.action_space.index('HOLD')  # Or 'BUY', 'SELL'
    next_state, reward, done, info = env.step(action)
    print(f"Step {info['step']}: balance=${info['balance']:.2f}")
    state = next_state

# Check performance
perf = env.get_performance_summary()
print(f"Return: {perf['total_return_pct']:.2f}%")
```

## 4. Initialize DDQN Agent

```python
from core.ml.orderbook_rl_scaffold import DDQNAgent

agent = DDQNAgent(
    state_dim=53 * 10,  # 10 snapshots lookback
    n_actions=3,
    learning_rate=0.0001,
    gamma=0.99
)

# Select action
state = env.reset()
action = agent.select_action(state, training=True)
print(f"Action: {env.action_space[action]}")
```

## 5. Train Agent (Scaffold - Implement Full Loop)

```python
# Training loop (basic structure)
for episode in range(100):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        # Select action
        action = agent.select_action(state, training=True)

        # Execute
        next_state, reward, done, info = env.step(action)
        total_reward += reward

        # Store transition
        agent.store_transition(state, action, reward, next_state, done)

        # Train (implement full DDQN update here)
        if len(agent.memory) > 32:
            agent.train_step(batch_size=32)

        state = next_state

    # Decay exploration
    agent.update_epsilon()

    print(f"Episode {episode}: reward={total_reward:.4f}, epsilon={agent.epsilon:.4f}")
```

## 6. Backtest Performance

```python
# After training, test on validation data
agent.epsilon = 0.0  # Greedy policy only

state = env.reset()
done = False

while not done:
    action = agent.select_action(state, training=False)
    next_state, reward, done, info = env.step(action)
    state = next_state

perf = env.get_performance_summary()
print(f"Validation return: {perf['total_return_pct']:.2f}%")
print(f"Total trades: {perf['total_trades']}")
print(f"Avg PnL/trade: ${perf['avg_pnl_per_trade']:.2f}")
```

## 7. Save/Load Models

```python
# Save trained model
agent.save_model('models/ddqn/btc_usd_ddqn.pth')

# Load model
agent.load_model('models/ddqn/btc_usd_ddqn.pth')
```

## Common Commands

### Collect 24 hours of data
```bash
python core/ml/collect_orderbook_data.py \
    --symbol BTC/USD \
    --duration 1440 \
    --interval 5
```

### Collect multiple assets
```bash
# BTC
python core/ml/collect_orderbook_data.py --symbol BTC/USD --duration 1440 --interval 5

# ETH
python core/ml/collect_orderbook_data.py --symbol ETH/USD --duration 1440 --interval 5

# SOL
python core/ml/collect_orderbook_data.py --symbol SOL/USD --duration 1440 --interval 5
```

### Run full scaffold demo
```bash
python core/ml/orderbook_rl_scaffold.py
```

## File Locations

```
SS_III/
├── core/ml/
│   ├── orderbook_rl_scaffold.py     # Main implementation
│   ├── collect_orderbook_data.py    # Data collection CLI
│   ├── README_ORDERBOOK_RL.md       # Full documentation
│   └── QUICKSTART.md                # This file
├── data/orderbook/                  # Collected snapshots
│   ├── BTC_USD_*.json
│   └── ETH_USD_*.json
└── models/ddqn/                     # Trained models
    └── *.pth
```

## Troubleshooting

### CCXT not installed
```bash
pip install ccxt
```

### PyTorch not installed
```bash
pip install torch
```

### Rate limit errors
Increase `--interval` to reduce API call frequency:
```bash
python collect_orderbook_data.py --interval 10  # 10 seconds instead of 5
```

### Memory issues with large datasets
Use smaller lookback window:
```python
env = OrderBookEnv(snapshots=snapshots, lookback=5)  # Instead of 10
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `initial_balance` | 10000.0 | Starting capital ($) |
| `position_size` | 0.1 | Position as fraction of capital (10%) |
| `transaction_cost` | 0.0006 | Trading fee (0.06% for Coinbase) |
| `lookback` | 10 | Number of snapshots in state |
| `learning_rate` | 0.0001 | DDQN learning rate |
| `gamma` | 0.99 | Discount factor |
| `epsilon_start` | 1.0 | Initial exploration rate |
| `epsilon_end` | 0.01 | Minimum exploration rate |
| `epsilon_decay` | 0.995 | Epsilon decay per episode |

## Next Steps

1. Collect 24h of BTC/USD data
2. Implement full DDQN training loop
3. Backtest on validation set
4. Paper trade if profitable
5. Scale to multiple assets

## Support

- Full docs: `core/ml/README_ORDERBOOK_RL.md`
- Implementation: `core/ml/orderbook_rl_scaffold.py`
- Summary: `core/ml/ORDERBOOK_RL_SUMMARY.md`

---

**Created:** 2025-12-14
**Status:** Production scaffold - ready for development
