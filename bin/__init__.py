"""
🏴 Sovereign Shadow II - CLI Interface
Command-line interface for trading system

Note: Lazy imports to avoid circular dependency issues
"""

def get_trading_cli():
    """Lazy import to avoid import errors"""
    from .trading_cli import main, TradingCLI
    return TradingCLI

__all__ = ["get_trading_cli"]
