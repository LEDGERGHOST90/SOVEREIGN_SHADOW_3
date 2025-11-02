#!/usr/bin/env python3
# Sovereign Shadow - Unified Rebalance Orchestrator
# Location: core/rebalancing/rebalance_run.py

import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from config_loader import load_portfolio_targets

# Dynamic path resolution
BASE_DIR = Path(__file__).parent.parent.parent  # Go up from core/rebalancing/
LOG_DIR = BASE_DIR / "logs"
CORE_REBALANCING = BASE_DIR / "core" / "rebalancing"

# CONFIGURATION + GUARDRAILS
SIM_PATH = LOG_DIR / "rebalance_sim_result.json"
EXEC_PATH = CORE_REBALANCING / "rebalance_grace.py"

ENV = os.getenv("ENV", "paper")
DISABLE_REAL = os.getenv("DISABLE_REAL_EXCHANGES", "1") == "1"
ALLOW_LIVE = os.getenv("ALLOW_LIVE_EXCHANGE", "0") == "1"

print("=" * 70)
print("🧭  Sovereign Shadow :: Unified Rebalance Run")
print("=" * 70)
print(f"ENV={ENV} | REAL_EXCHANGES={'ENABLED' if not DISABLE_REAL else 'DISABLED'} | ALLOW_LIVE={ALLOW_LIVE}\n")

# STEP 1 — Run Simulation if no existing sim result
def run_simulation():
    print("🔍 Running adaptive volatility simulation...")
    sim_script = CORE_REBALANCING / "rebalance_sim.py"
    if not sim_script.exists():
        print(f"❌ Missing {sim_script}, aborting.")
        return False
    try:
        subprocess.run(["python3", str(sim_script)], check=True)
        print("✅ Simulation complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Simulation failed: {e}")
        return False

if not SIM_PATH.exists():
    print("⚠️ No existing sim result found — launching new simulation.")
    if not run_simulation():
        exit(1)
else:
    print(f"✅ Found previous simulation result: {SIM_PATH.name}\n")

# STEP 2 — Load Adaptive Targets
try:
    with open(SIM_PATH, "r") as f:
        sim_data = json.load(f)
        targets = sim_data.get("targets", {})
        sharpe = sim_data.get("sharpe_estimate", 0)
        print(f"📊 Loaded targets from sim: {targets}")
        print(f"🔹 Simulated Sharpe Ratio: {sharpe:.2f}\n")
except Exception as e:
    print(f"❌ Could not load simulation data: {e}")
    targets = load_portfolio_targets()
    print(f"Using fallback targets from config: {targets}\n")

# STEP 3 — User Confirmation
print("💡 Ready to execute rebalance with the following adaptive targets:")
for k, v in targets.items():
    print(f"   • {k}: {v*100:.1f}%")

mode_desc = "PAPER" if DISABLE_REAL else "LIVE"

# Auto-confirm if AUTO_EXECUTE is set (for terminal automation)
auto_execute = os.getenv("AUTO_EXECUTE", "0") == "1"
if auto_execute:
    confirm = "EXECUTE"
    print(f"\n🤖 AUTO_EXECUTE enabled - proceeding in {mode_desc} mode automatically")
else:
    confirm = input(f"\nType 'EXECUTE' to run in {mode_desc} mode, or press Enter to cancel: ").strip().upper()

if confirm != "EXECUTE":
    print("❌ Rebalance aborted by user.")
    exit(0)

# STEP 4 — Execute Rebalance
if not EXEC_PATH.exists():
    print(f"❌ Missing execution script: {EXEC_PATH}")
    exit(1)

try:
    print(f"🚀 Launching {EXEC_PATH.name}...\n")
    subprocess.run(["python3", str(EXEC_PATH)], check=True)
    print("✅ Graceful rebalance complete.\n")
except subprocess.CalledProcessError as e:
    print(f"❌ Execution failed: {e}")
    exit(1)

# STEP 5 — Post-Rebalance Variance Check
def variance_check(final_alloc, target_alloc):
    diffs = {}
    for k in target_alloc:
        cur = final_alloc.get(k, 0)
        tgt = target_alloc[k]
        diffs[k] = round((cur - tgt) * 100, 2)
    return diffs

print("🔎 Running post-rebalance variance check...")
try:
    from portfolio_state import get_portfolio_allocation
    final = get_portfolio_allocation()
    final_weights = {a: final[a]["weight"] for a in final if a != "_metadata"}
    drift = variance_check(final_weights, targets)

    print("\n📊 Final Allocation Drift (pp):")
    for k, v in drift.items():
        sym = "+" if v > 0 else ""
        flag = "✅" if abs(v) < 2 else "⚠️"
        print(f"  {flag} {k}: {sym}{v:.2f}pp from target")

except Exception as e:
    print(f"⚠️ Could not verify final allocation: {e}")
    drift = "unverified"

# STEP 6 — Log Results
out = {
    "timestamp": datetime.utcnow().isoformat(),
    "env": ENV,
    "real_mode": not DISABLE_REAL,
    "targets": targets,
    "variance_check": drift,
}

try:
    MEMORY_VAULT = BASE_DIR / "memory" / "vault"
    ledger = MEMORY_VAULT / "allocation_log.json"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a") as f:
        json.dump(out, f)
        f.write("\n")
    print(f"\n🧾 Logged to {ledger}")
except Exception as e:
    print(f"⚠️ Could not log to ledger: {e}")

print("\n🎉 Sovereign Shadow Rebalance sequence complete.")
print("=" * 70)
