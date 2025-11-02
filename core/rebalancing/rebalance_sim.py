#!/usr/bin/env python3
# Sovereign Shadow - Rebalance Simulator
# Location: /home/sovereign_shadow/core_portfolio/rebalance_sim.py

import json, random, statistics
from datetime import datetime
from config_loader import load_portfolio_targets

# CONFIGURATION
PORTFOLIO_USD = 7960
CURRENT_WEIGHTS = {"ETH": 0.51, "BTC": 0.28, "XRP": 0.13, "SOL": 0.06, "LINK": 0.00}
TARGETS = load_portfolio_targets()
PRICES = {"ETH": 4000, "BTC": 69000, "SOL": 185, "XRP": 2.50, "LINK": 15.00}

# ATR (Average True Range) Volatility Proxy
ATR14 = {"BTC": 1500, "ETH": 230, "SOL": 18, "XRP": 0.22, "LINK": 1.2}

def volatility_ratio(sol_atr, btc_atr):
    ratio = sol_atr / btc_atr
    return max(0.15, min(0.15 + 0.05 * (ratio > 1.2), 0.25))

def compute_drift(current, target):
    return {a: round((current[a] - target[a]) * 100, 2) for a in target}

def simulate_fee(amount):
    return amount * random.uniform(0.001, 0.0025)

def simulate_slippage(amount):
    return amount * random.uniform(0.001, 0.003)

def simulate_trade_cost(amount):
    return simulate_fee(amount) + simulate_slippage(amount)

def simulate_portfolio_change(prices, weights, move):
    """move is +0.5 for +50% bull or -0.3 for -30% bear"""
    return sum(v * (1 + move) for v in weights.values())

def sharpe_ratio(returns, risk_free=0.02):
    avg = statistics.mean(returns)
    std = statistics.pstdev(returns)
    return (avg - risk_free) / std if std != 0 else 0

if __name__ == "__main__":
    print("🔬 Sovereign Shadow Rebalance Simulation")
    print("========================================\n")

    # Optional: Apply adaptive volatility adjustment to SOL if it exists
    # Comment this out to use pure config targets
    if "SOL" in TARGETS and "SOL" in ATR14 and "BTC" in ATR14:
        sol_target = volatility_ratio(ATR14["SOL"], ATR14["BTC"])
        print(f"ℹ️  Adaptive SOL target: {sol_target*100:.1f}% (original: {TARGETS['SOL']*100:.1f}%)")
        # Uncomment below to apply adaptive logic:
        # TARGETS["SOL"] = sol_target

    print(f"Loaded Targets: {TARGETS}\n")

    drift = compute_drift(CURRENT_WEIGHTS, TARGETS)
    print(f"Current drift (%): {drift}\n")

    tx_cost = sum(simulate_trade_cost(PORTFOLIO_USD * abs(d) / 100) for d in drift.values())
    print(f"Estimated total fees + slippage: ${tx_cost:.2f}\n")

    bull = simulate_portfolio_change(PRICES, TARGETS, +0.5)
    bear = simulate_portfolio_change(PRICES, TARGETS, -0.3)
    returns = [bull / PORTFOLIO_USD - 1, bear / PORTFOLIO_USD - 1]
    print(f"Simulated Sharpe Ratio: {sharpe_ratio(returns):.2f}")

    print("\n✅ Simulation complete. No funds moved.")
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "targets": TARGETS,
        "drift": drift,
        "tx_cost_estimate": tx_cost,
        "sharpe_estimate": sharpe_ratio(returns)
    }
    
    import os
    from pathlib import Path
    
    # Use relative logs directory or environment variable
    log_dir = Path(os.getenv("SOVEREIGN_SHADOW_LOGS", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = log_dir / "rebalance_sim_result.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"📄 Log saved to {log_path}\n")
