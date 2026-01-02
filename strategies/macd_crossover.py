"""
Strategy: MACD Crossover
Generated: 2025-12-23T23:02:25.081922
Status: PAPER_TESTING
"""

STRATEGY_CONFIG = {
    "name": "MACD Crossover",
    "status": "paper",
    "entry_rules": [
    "MACD crosses above signal"
],
    "exit_rules": [
    "MACD crosses below signal"
],
    "indicators": [
    "MACD"
],
    "timeframe": "1h",
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
    "created": "2025-12-23T23:02:25.081953",
}

def should_enter(data):
    """Check entry conditions"""
    # TODO: Implement based on entry_rules
    pass

def should_exit(data, position):
    """Check exit conditions"""
    # TODO: Implement based on exit_rules
    pass
