#!/usr/bin/env python3
"""
📊 AAVE Risk Scenario Calculator
Shows what happens at different collateral price drops
"""

import sys
from pathlib import Path
from decimal import Decimal, getcontext

# Set precision
getcontext().prec = 28

# Add aave monitor to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules' / 'safety'))

from aave_monitor_v2 import AaveMonitor

def calculate_hf_at_price_drop(collateral_usd, debt_usd, price_drop_pct, liquidation_threshold=0.81):
    """Calculate HF after price drop"""
    new_collateral = collateral_usd * (Decimal(1) - price_drop_pct / Decimal(100))
    new_hf = (new_collateral * Decimal(liquidation_threshold)) / debt_usd
    return new_hf, new_collateral

def main():
    print(f"\n{'='*70}")
    print(f"📊 AAVE RISK SCENARIO CALCULATOR")
    print(f"{'='*70}\n")

    # Get current position
    print("🔍 Fetching current AAVE position...")
    monitor = AaveMonitor()
    position = monitor.get_position()

    current_collateral = position.collateral_usd
    current_debt = position.debt_usd
    current_hf = position.health_factor

    print(f"   ✅ Current Position:")
    print(f"      Collateral: ${current_collateral:,.2f}")
    print(f"      Debt: ${current_debt:,.2f}")
    print(f"      Health Factor: {current_hf:.2f}")
    print()

    # Price drop scenarios
    scenarios = [
        (0, "Current"),
        (5, "Mild drop"),
        (8.6, "Today's LSETH drop"),
        (10, "Moderate drop"),
        (15, "Significant drop"),
        (18.1, "WARNING threshold (HF 2.0)"),
        (20, "Major drop"),
        (25, "Severe drop"),
        (26.3, "DANGER threshold (HF 1.8)"),
        (30, "Extreme drop"),
        (38.6, "CRITICAL threshold (HF 1.5)"),
        (50, "Catastrophic drop"),
        (59, "LIQUIDATION (HF 1.0)"),
    ]

    print(f"📉 PRICE DROP SCENARIOS:")
    print(f"{'='*70}")
    print(f"{'Drop %':<10} {'New Coll':<15} {'New HF':<10} {'Status':<20} {'Action'}")
    print(f"{'='*70}")

    for drop_pct, description in scenarios:
        new_hf, new_collateral = calculate_hf_at_price_drop(
            current_collateral,
            current_debt,
            Decimal(drop_pct)
        )

        # Determine status
        if new_hf >= Decimal('2.5'):
            status = "✅ SAFE"
            action = "Monitor"
        elif new_hf >= Decimal('2.0'):
            status = "🟠 CAUTION"
            action = "Watch closely"
        elif new_hf >= Decimal('1.8'):
            status = "🔴 WARNING"
            repay = monitor.calculate_repay_to_target(position, Decimal('2.5'))
            action = f"Repay ${repay:.0f}"
        elif new_hf >= Decimal('1.5'):
            status = "🚨 DANGER"
            action = "URGENT REPAY"
        elif new_hf >= Decimal('1.0'):
            status = "💀 CRITICAL"
            action = "EMERGENCY"
        else:
            status = "☠️  LIQUIDATED"
            action = "TOO LATE"

        print(f"{drop_pct:<10.1f} ${new_collateral:<14,.2f} {float(new_hf):<10.2f} {status:<20} {action}")

    print(f"{'='*70}\n")

    # Calculate current cushions
    print(f"🛡️  LIQUIDATION CUSHIONS (from current position):")
    print(f"{'='*70}")

    thresholds = [
        (Decimal('2.5'), "SAFE zone", "🟢"),
        (Decimal('2.0'), "WARNING zone", "🟠"),
        (Decimal('1.8'), "DANGER zone", "🔴"),
        (Decimal('1.5'), "CRITICAL zone", "🚨"),
        (Decimal('1.2'), "Near liquidation", "💀"),
        (Decimal('1.0'), "LIQUIDATION", "☠️"),
    ]

    for target_hf, description, emoji in thresholds:
        drop = monitor.calculate_collateral_drop_to_hf(position, target_hf)
        print(f"{emoji} HF {target_hf:<4} ({description:<20}): {drop:>6.1f}% collateral drop")

    print(f"{'='*70}\n")

    # Today's situation
    print(f"🔍 TODAY'S SITUATION ANALYSIS:")
    print(f"{'='*70}")

    todays_drop = Decimal('8.6')
    new_hf, new_collateral = calculate_hf_at_price_drop(current_collateral, current_debt, todays_drop)

    print(f"LSETH dropped: {todays_drop}%")
    print(f"Your collateral: ${current_collateral:,.2f} → ${new_collateral:,.2f}")
    print(f"Collateral loss: ${current_collateral - new_collateral:,.2f}")
    print(f"Health Factor: {current_hf:.2f} → {new_hf:.2f}")
    print(f"HF change: {current_hf - new_hf:.2f}")
    print()

    # Remaining cushion
    warning_drop = monitor.calculate_collateral_drop_to_hf(position, Decimal('2.0'))
    remaining = warning_drop - todays_drop

    print(f"Distance to WARNING (HF 2.0):")
    print(f"   Total drop needed: {warning_drop:.1f}%")
    print(f"   Already dropped: {todays_drop:.1f}%")
    print(f"   Remaining cushion: {remaining:.1f}%")
    print()

    if remaining > Decimal('5'):
        print(f"✅ Status: SAFE - Good cushion remaining")
    elif remaining > Decimal('2'):
        print(f"🟠 Status: CAUTION - Cushion getting thin")
    else:
        print(f"🔴 Status: WARNING - Very close to danger zone")

    print(f"{'='*70}\n")

    # Repay recommendations
    print(f"💊 REPAY RECOMMENDATIONS:")
    print(f"{'='*70}")

    repay_scenarios = [
        (Decimal('2.5'), "Return to SAFE zone"),
        (Decimal('3.0'), "Comfortable buffer"),
        (Decimal('3.5'), "Strong position"),
        (Decimal('4.0'), "Very safe"),
    ]

    for target_hf, description in repay_scenarios:
        repay_amount = monitor.calculate_repay_to_target(position, target_hf)

        if repay_amount > 0:
            new_debt = current_debt - repay_amount
            print(f"To reach HF {target_hf} ({description}):")
            print(f"   Repay: ${repay_amount:,.2f} USDC")
            print(f"   New debt: ${new_debt:,.2f}")
            print(f"   BTC to sell: {float(repay_amount / Decimal(104444)):.4f} BTC (~${repay_amount:,.0f})")
            print()

    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
