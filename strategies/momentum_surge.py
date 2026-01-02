"""
Strategy: Momentum Surge
Generated: 2025-12-23T23:02:25.082493
Status: PAPER_TESTING
"""

STRATEGY_CONFIG = {
    "name": "Momentum Surge",
    "status": "paper",
    "entry_rules": [
    "Price > 20 EMA, RSI > 50, Volume spike"
],
    "exit_rules": [
    "RSI > 80 or trailing stop 3%"
],
    "indicators": [
    "Momentum"
],
    "timeframe": "15m",
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
    "created": "2025-12-23T23:02:25.082515",
}

def should_enter(data):
    """Check entry conditions"""
    # TODO: Implement based on entry_rules
    pass

def should_exit(data, position):
    """Check exit conditions"""
    # TODO: Implement based on exit_rules
    pass
