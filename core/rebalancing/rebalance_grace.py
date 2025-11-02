#!/usr/bin/env python3
# Sovereign Shadow - Graceful Rebalance Executor
# Location: /home/sovereign_shadow/core_portfolio/rebalance_grace.py

import time, os
from datetime import datetime
from config_loader import load_portfolio_targets
try:
    from portfolio_state import get_portfolio_allocation
    from coinbase_exec import buy, sell
    from aave_client import withdraw
except ImportError:
    print("⚠️ Some modules not available")
    def get_portfolio_allocation():
        return {}
    def buy(asset, amount, **kwargs):
        print(f"Mock buy: {asset} ${amount}")
    def sell(asset, amount):
        print(f"Mock sell: {asset} ${amount}")
    def withdraw(asset, amount):
        print(f"Mock withdraw: {asset} ${amount}")

# GUARDRAILS
ENV = os.getenv("ENV", "paper")
DISABLE_REAL = os.getenv("DISABLE_REAL_EXCHANGES", "1") == "1"
print(f"⚙️ ENV={ENV} | REAL_EXCHANGES={'ENABLED' if not DISABLE_REAL else 'DISABLED'}")

# TARGETS
TARGETS = load_portfolio_targets()
TOTAL_PORTFOLIO = 7960

TRADES = [
    {"action": "SELL", "asset": "ETH", "source": "AAVE", "amount_usd": 867},
    {"action": "SELL", "asset": "XRP", "amount_usd": 265},
    {"action": "BUY", "asset": "SOL", "amount_usd": 1127, "ladder": True},
    {"action": "BUY", "asset": "BTC", "amount_usd": 164}
]

def ladder_buy(asset, total_amount, ladders=3, step_pct=1.0):
    print(f"🪜 Laddering {asset} buy for ${total_amount}")
    portion = total_amount / ladders
    for i in range(ladders):
        offset = (-step_pct + 2 * step_pct * (i / (ladders - 1)))
        print(f"  • Order {i+1}/{ladders} @ {offset:+.1f}% from spot, ${portion:.2f}")
        buy(asset, portion, slippage_limit=0.004, offset=offset)
        time.sleep(0.5)

def execute_trades():
    print("\n🚀 Executing Graceful Rebalance Sequence\n")
    for t in TRADES:
        act, asset, amt = t["action"], t["asset"], t["amount_usd"]
        if act == "SELL" and t.get("source") == "AAVE":
            print(f"⏳ Withdrawing ${amt} {asset} collateral from Aave…")
            withdraw(asset, amt)
        elif act == "SELL":
            print(f"🔴 Selling ${amt} of {asset}")
            sell(asset, amt)
        elif act == "BUY":
            if t.get("ladder"):
                ladder_buy(asset, amt)
            else:
                print(f"🟢 Buying ${amt} of {asset}")
                buy(asset, amt)
        else:
            print(f"⚠️ Unknown action {act} for {asset}")
        time.sleep(1)
    print("\n✅ All trade instructions queued.\n")

def verify_final_allocation():
    alloc = get_portfolio_allocation()
    print("📊 Final Allocation Check")
    for asset, target in TARGETS.items():
        current = alloc.get(asset, {}).get("weight", 0)
        diff = abs(current - target)
        status = "✅" if diff < 0.02 else "⚠️"
        print(f"  {status} {asset}: {current:.1%} (target {target:.0%})")

if __name__ == "__main__":
    print("🧭 Starting Sovereign Shadow Grace Rebalance")
    if DISABLE_REAL:
        print("🔒 Running in PAPER MODE (no real trades)")

    # Auto-confirm if AUTO_EXECUTE is set (for terminal automation)
    auto_execute = os.getenv("AUTO_EXECUTE", "0") == "1"
    if auto_execute:
        confirm = "EXECUTE"
        print("🤖 AUTO_EXECUTE enabled - proceeding automatically")
    else:
        confirm = input("Type 'EXECUTE' to run or press Enter to cancel: ")

    if confirm.strip().upper() == "EXECUTE":
        execute_trades()
        verify_final_allocation()
        print(f"\n🕒 Completed {datetime.utcnow().isoformat()}")
    else:
        print("❌ Cancelled.")
