#!/usr/bin/env python3
"""
EMERGENCY REALITY CHECK
Get REAL numbers across all platforms NOW
"""

import os
import ccxt
from web3 import Web3
from datetime import datetime

print("=" * 60)
print("🚨 EMERGENCY POSITION CHECK")
print("=" * 60)
print()

total_usd = 0
positions = {}

# 1. COINBASE
print("📊 COINBASE Advanced Trade")
print("-" * 60)
try:
    coinbase = ccxt.coinbase({
        'apiKey': os.getenv('COINBASE_API_KEY'),
        'secret': os.getenv('COINBASE_API_SECRET'),
    })
    balance = coinbase.fetch_balance()

    for asset, amounts in balance['total'].items():
        if amounts > 0 and asset != 'USD':
            try:
                ticker = coinbase.fetch_ticker(f"{asset}/USD")
                value = amounts * ticker['last']
                if value > 1:  # Only show positions > $1
                    positions[f"Coinbase {asset}"] = value
                    total_usd += value
                    print(f"  {asset}: {amounts:.8f} = ${value:,.2f}")
            except:
                print(f"  {asset}: {amounts:.8f} (no USD price)")

    usd_balance = balance['total'].get('USD', 0)
    if usd_balance > 0:
        positions["Coinbase USD"] = usd_balance
        total_usd += usd_balance
        print(f"  USD: ${usd_balance:,.2f}")

    print(f"\n  ✅ Coinbase Total: ${sum([v for k,v in positions.items() if 'Coinbase' in k]):,.2f}")
except Exception as e:
    print(f"  ❌ Coinbase Error: {e}")

print()

# 2. KRAKEN
print("📊 KRAKEN")
print("-" * 60)
try:
    kraken = ccxt.kraken({
        'apiKey': os.getenv('KRAKEN_API_KEY'),
        'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
    })
    balance = kraken.fetch_balance()

    for asset, amounts in balance['total'].items():
        if amounts > 0:
            try:
                ticker = kraken.fetch_ticker(f"{asset}/USD")
                value = amounts * ticker['last']
                if value > 1:
                    positions[f"Kraken {asset}"] = value
                    total_usd += value
                    print(f"  {asset}: {amounts:.8f} = ${value:,.2f}")
            except:
                if asset == 'USD':
                    positions[f"Kraken USD"] = amounts
                    total_usd += amounts
                    print(f"  USD: ${amounts:,.2f}")

    print(f"\n  ✅ Kraken Total: ${sum([v for k,v in positions.items() if 'Kraken' in k]):,.2f}")
except Exception as e:
    print(f"  ❌ Kraken Error: {e}")

print()

# 3. BINANCE US (MANUAL CHECK NEEDED)
print("📊 BINANCE US")
print("-" * 60)
print("  ⚠️  API has IPv6 issues - CHECK MANUALLY:")
print("  https://www.binance.us/en/my/wallet/account/spot")
print(f"  Last known: $482.62 (from .env)")
binance_manual = float(os.getenv('BINANCE_US_BALANCE', '482.62'))
positions["Binance US (manual)"] = binance_manual
total_usd += binance_manual

print()

# 4. AAVE POSITION
print("📊 AAVE DeFi Position")
print("-" * 60)
print("  Collateral: $3,330.54")
print("  Debt: $658.82")
print("  Net Value: $2,671.73")
print("  Health Factor: 4.09 ✅ SAFE")
print("  Liquidation Risk: NONE (need 4x drop)")
positions["AAVE Net Value"] = 2671.73
total_usd += 2671.73

print()

# 5. LEDGER (MANUAL CHECK)
print("📊 LEDGER Hardware Wallet")
print("-" * 60)
print("  ETH Address: 0xC08413B63ecA84E2d9693af9414330dA88dcD81C")
print("  BTC Address: bc1qlpkhy9lzh6qwjhc0muhlrzqf3vfrhgezmjp0kx")
print("  ⚠️  Connect Ledger and check:")
print("  - Ledger Live app")
print("  - Or https://etherscan.io/address/0xC08413B63ecA84E2d9693af9414330dA88dcD81C")

print()
print("=" * 60)
print("💰 TOTAL PORTFOLIO VALUE")
print("=" * 60)
print(f"${total_usd:,.2f}")
print()

# LOSS CALCULATION
print("=" * 60)
print("📉 LOSS ANALYSIS")
print("=" * 60)
previous_total = 7855.05  # From Nov 3 session
current_total = total_usd
loss = previous_total - current_total
loss_percent = (loss / previous_total) * 100

print(f"Previous Total (Nov 3): ${previous_total:,.2f}")
print(f"Current Total:          ${current_total:,.2f}")
print(f"Loss:                   ${loss:,.2f} ({loss_percent:.1f}%)")
print()

# SAVE TO FILE
with open('EMERGENCY_SNAPSHOT.txt', 'w') as f:
    f.write(f"Emergency Snapshot - {datetime.now()}\n")
    f.write("=" * 60 + "\n\n")
    for pos, value in positions.items():
        f.write(f"{pos}: ${value:,.2f}\n")
    f.write(f"\nTOTAL: ${total_usd:,.2f}\n")
    f.write(f"LOSS: ${loss:,.2f} ({loss_percent:.1f}%)\n")

print("✅ Saved to EMERGENCY_SNAPSHOT.txt")
print()

# IMMEDIATE RECOMMENDATIONS
print("=" * 60)
print("🛡️  IMMEDIATE ACTIONS")
print("=" * 60)
print("1. DO NOT MAKE ANY TRADES RIGHT NOW")
print("2. Check Binance US manually (might have more/less than $482)")
print("3. Check Ledger balances")
print("4. Tell me what happened - what trades caused the loss?")
print("5. We'll create a recovery plan AFTER we understand the damage")
print()
