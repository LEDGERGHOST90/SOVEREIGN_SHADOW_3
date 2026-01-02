#!/usr/bin/env python3
"""
Portfolio Config - Single source of truth for SS_III portfolio values
All modules should import from here instead of hardcoding values.

Usage:
    from core.config.portfolio_config import get_portfolio_config, get_initial_capital

    config = get_portfolio_config()
    initial = get_initial_capital()
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Paths
PROJECT_ROOT = Path("/Volumes/LegacySafe/SS_III")
BRAIN_PATH = PROJECT_ROOT / "BRAIN.json"
BRAIN_JOT_PATH = PROJECT_ROOT / "BRAIN_JOT.json"


def load_brain() -> Dict[str, Any]:
    """Load BRAIN.json - the source of truth."""
    try:
        if BRAIN_PATH.exists():
            return json.loads(BRAIN_PATH.read_text())
    except Exception as e:
        print(f"Warning: Could not load BRAIN.json: {e}")
    return {}


def get_portfolio_config() -> Dict[str, Any]:
    """
    Get current portfolio configuration from BRAIN.json.

    Returns:
        Dict with portfolio values, positions, and metadata
    """
    brain = load_brain()
    portfolio = brain.get("portfolio", {})

    return {
        "total_value_usd": portfolio.get("total_value_usd", 0),
        "usdc_available": portfolio.get("usdc_available", 0),
        "positions": portfolio.get("positions_filled", []),
        "last_update": portfolio.get("last_update"),

        # Net worth breakdown (from CLAUDE.md values as baseline)
        "net_worth": {
            "total": 5438,  # ~$5,438 as of 2026-01-01
            "ledger_cold_storage": 5000,
            "exchange_capital": 950,
            "aave_debt": -609
        },

        # Exchange breakdown
        "exchanges": {
            "coinbase": 764,
            "binance_us": 111,
            "kraken": 73
        },

        # Ledger breakdown
        "ledger": {
            "wsteth_collateral": 2979,
            "btc": 1463,
            "xrp": 638,
            "dust": 17
        }
    }


def get_initial_capital(exchange: str = None) -> float:
    """
    Get initial capital for P&L tracking.

    Args:
        exchange: Specific exchange or None for total

    Returns:
        Initial capital value in USD
    """
    # These are the ACTUAL starting values for SS_III
    # Updated: 2026-01-01
    initial_capitals = {
        "coinbase": float(os.getenv("COINBASE_INITIAL_CAPITAL", 764)),
        "binance_us": float(os.getenv("BINANCE_US_INITIAL_CAPITAL", 111)),
        "kraken": float(os.getenv("KRAKEN_INITIAL_CAPITAL", 73)),
        "okx": float(os.getenv("OKX_INITIAL_CAPITAL", 0)),
        "ledger": float(os.getenv("LEDGER_INITIAL_VALUE", 5000)),
        "total_exchange": float(os.getenv("TOTAL_EXCHANGE_CAPITAL", 950)),
        "total_net_worth": float(os.getenv("TOTAL_NET_WORTH", 5438))
    }

    if exchange:
        return initial_capitals.get(exchange.lower(), 0)

    return initial_capitals["total_net_worth"]


def get_aave_config() -> Dict[str, Any]:
    """
    Get AAVE-specific configuration.
    """
    return {
        "debt_usd": 609,
        "collateral_wsteth_usd": 2979,
        "health_factor": 3.96,
        "min_hf_threshold": 2.5,
        "strategy": "strategic_good_debt",
        "rule": "DO NOT repay unless HF < 2.5"
    }


def get_target_allocation() -> Dict[str, float]:
    """
    Get target portfolio allocation percentages.
    """
    return {
        "BTC": 40,
        "ETH": 30,
        "SOL": 20,
        "XRP": 10
    }


def get_rwa_focus() -> Dict[str, Any]:
    """
    Get RWA thesis focus configuration.
    """
    return {
        "primary_focus": ["LINK", "INJ", "QNT", "ONDO", "PLUME"],
        "infrastructure": {
            "LINK": {"role": "Oracle backbone", "thesis": "Swift integration"},
            "QNT": {"role": "Bank connectivity", "thesis": "Overledger"}
        },
        "accumulation_targets": {
            "LINK": {"buy_zone": [18, 22], "stop_loss": 16.50},
            "ONDO": {"buy_zone": [0.31, 0.35], "stop_loss": 0.28},
            "INJ": {"buy_zone": [3.50, 5.00], "stop_loss": 2.50},
            "QNT": {"buy_zone": [65, 75], "stop_loss": 58}
        }
    }


def update_portfolio_value(new_value: float, source: str = "manual") -> bool:
    """
    Update portfolio value in BRAIN.json.

    Args:
        new_value: New total portfolio value
        source: Where this update came from

    Returns:
        True if successful
    """
    try:
        brain = load_brain()
        if "portfolio" not in brain:
            brain["portfolio"] = {}

        brain["portfolio"]["total_value_usd"] = new_value
        brain["portfolio"]["last_update"] = datetime.now().isoformat()
        brain["portfolio"]["update_source"] = source

        BRAIN_PATH.write_text(json.dumps(brain, indent=2))
        return True
    except Exception as e:
        print(f"Error updating portfolio: {e}")
        return False


# Quick access
PORTFOLIO = get_portfolio_config()
INITIAL_CAPITAL = get_initial_capital()
AAVE = get_aave_config()
RWA = get_rwa_focus()


if __name__ == "__main__":
    print("=" * 50)
    print("SS_III Portfolio Configuration")
    print("=" * 50)

    config = get_portfolio_config()
    print(f"\nNet Worth: ${config['net_worth']['total']:,}")
    print(f"  Ledger: ${config['net_worth']['ledger_cold_storage']:,}")
    print(f"  Exchanges: ${config['net_worth']['exchange_capital']:,}")
    print(f"  AAVE Debt: ${config['net_worth']['aave_debt']:,}")

    print(f"\nExchange Breakdown:")
    for ex, val in config['exchanges'].items():
        print(f"  {ex}: ${val}")

    print(f"\nInitial Capital (for P&L): ${get_initial_capital():,}")

    aave = get_aave_config()
    print(f"\nAAVE Status:")
    print(f"  Health Factor: {aave['health_factor']}")
    print(f"  Rule: {aave['rule']}")
