"""
Strategy: RSI Divergence
Generated: 2025-12-23T23:02:25.082653
Status: PAPER_TESTING
"""

STRATEGY_CONFIG = {
    "name": "RSI Divergence",
    "status": "paper",
    "entry_rules": [
    "RSI < 30 with price higher low"
],
    "exit_rules": [
    "RSI > 70 or 5% profit"
],
    "indicators": [
    "RSI"
],
    "timeframe": "4h",
    "assets": [
    "BTC/USDT",
    "ETH/USDT"
],
    "risk_per_trade": 0.02,
    "max_positions": 3,
}

# Performance tracking
PERFORMANCE = {
    "trades": 0,
    "wins": 0,
    "losses": 0,
    "pnl": 0.0,
    "created": "2025-12-23T23:02:25.082675",
}

def should_enter(data):
    """Check entry conditions"""
    # TODO: Implement based on entry_rules
    pass

def should_exit(data, position):
    """Check exit conditions"""
    # TODO: Implement based on exit_rules
    pass
