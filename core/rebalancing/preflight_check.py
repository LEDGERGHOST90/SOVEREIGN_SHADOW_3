#!/usr/bin/env python3
# Sovereign Shadow - Pre-flight Checks
# Location: core/rebalancing/preflight_check.py

import os
import json
from pathlib import Path
from config_loader import load_portfolio_targets, get_all_asset_symbols

# Dynamic path resolution
BASE_DIR = Path(__file__).parent.parent.parent  # Go up from core/rebalancing/ to project root
CORE_REBALANCING = BASE_DIR / "core" / "rebalancing"
LOGS_DIR = BASE_DIR / "logs"
MEMORY_VAULT = BASE_DIR / "memory" / "vault"

CHECKS = []

def check(name, condition, critical=True):
    status = "✅" if condition else ("🚨" if critical else "⚠️")
    CHECKS.append({"name": name, "status": status, "pass": condition, "critical": critical})
    print(f"{status} {name}")
    return condition

print("🔍 Sovereign Shadow Pre-Flight Checks\n")
print("=" * 60)

# Environment checks
check("ENV variable set", os.getenv("ENV") in ["paper", "prod"])
check("DISABLE_REAL_EXCHANGES set", os.getenv("DISABLE_REAL_EXCHANGES") is not None)
check("Coinbase API key configured", bool(os.getenv("COINBASE_API_KEY")))
check("Coinbase API secret configured", bool(os.getenv("COINBASE_API_SECRET")))

# File structure checks
check("Core rebalancing dir exists", CORE_REBALANCING.exists())
check("Logs dir exists", LOGS_DIR.exists())
check("Memory vault exists", MEMORY_VAULT.exists())

# Module checks
check("portfolio_state.py exists", (CORE_REBALANCING / "portfolio_state.py").exists())
check("coinbase_exec.py exists", (CORE_REBALANCING / "coinbase_exec.py").exists())
check("rebalance_sim.py exists", (CORE_REBALANCING / "rebalance_sim.py").exists())
check("rebalance_grace.py exists", (CORE_REBALANCING / "rebalance_grace.py").exists())
check("rebalance_run.py exists", (CORE_REBALANCING / "rebalance_run.py").exists())

# Test imports
try:
    from portfolio_state import get_portfolio_allocation
    check("portfolio_state imports", True)
except Exception as e:
    check(f"portfolio_state imports ({e})", False)

try:
    from coinbase_exec import buy, sell
    check("coinbase_exec imports", True)
except Exception as e:
    check(f"coinbase_exec imports ({e})", False)

# Portfolio configuration check
try:
    targets = load_portfolio_targets()
    asset_count = len(targets)
    total_weight = sum(targets.values())
    
    check(f"Portfolio config loaded ({asset_count} assets)", asset_count > 0)
    check(f"Target weights sum to 100% ({total_weight:.1%})", abs(total_weight - 1.0) < 0.01, critical=False)
    
    # Verify each asset has valid weight
    for asset, weight in targets.items():
        check(f"  {asset} target weight valid (0 < {weight:.1%} < 1)", 0 < weight < 1, critical=False)
        
except Exception as e:
    check(f"Portfolio config validation ({e})", False, critical=False)

# Simulation check
sim_result = LOGS_DIR / "rebalance_sim_result.json"
if sim_result.exists():
    with open(sim_result) as f:
        data = json.load(f)
        check("Valid simulation result exists", "targets" in data, critical=False)
        
        # Verify sim targets match config (for any number of assets)
        if "targets" in data:
            sim_targets = set(data["targets"].keys())
            config_targets = set(get_all_asset_symbols())
            match = sim_targets == config_targets
            check(f"Sim targets match config ({len(config_targets)} assets)", match, critical=False)
else:
    check("Simulation has been run", False, critical=False)

# AAVE health factor check (if using)
try:
    from aave_client import get_health_factor
    hf = get_health_factor()
    check(f"AAVE health factor safe (HF: {hf:.2f})", hf > 2.0, critical=False)
except:
    check("AAVE client available", False, critical=False)

print("=" * 60)

# Summary
critical_failures = [c for c in CHECKS if not c["pass"] and c["critical"]]
warnings = [c for c in CHECKS if not c["pass"] and not c["critical"]]

if critical_failures:
    print(f"\n🚨 {len(critical_failures)} CRITICAL FAILURES - DO NOT GO LIVE")
    for f in critical_failures:
        print(f"   ❌ {f['name']}")
    exit(1)
elif warnings:
    print(f"\n⚠️ {len(warnings)} warnings (non-critical)")
    for w in warnings:
        print(f"   ⚠️ {w['name']}")
    print("\n✅ Safe to proceed, but review warnings")
else:
    print("\n🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT")

print(f"\nPassed: {sum(1 for c in CHECKS if c['pass'])}/{len(CHECKS)}")
