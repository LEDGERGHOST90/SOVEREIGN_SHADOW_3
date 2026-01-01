"""
SOVEREIGN SHADOW II - D.O.E. Pattern Autonomous Trading System

An AI-powered autonomous trading system implementing the D.O.E.
(Directive-Orchestration-Execution) Pattern with a self-annealing learning loop.

Components:
- Directive Layer: Market Regime Detector
- Orchestration Layer: AI Strategy Selector
- Execution Layer: Strategy Engine + Exchange APIs
- Learning Layer: Performance Tracker (SQLite)

Usage:
    python main.py              # Paper trading mode
    python main.py --backtest   # Run backtests
    python main.py --status     # Check system status
"""

__version__ = "2.0.0"
__author__ = "Raymond (LedgerGhost90)"
