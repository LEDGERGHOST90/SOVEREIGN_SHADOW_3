#!/usr/bin/env python3
"""
📊 AAVE HEALTH FACTOR DASHBOARD
Visual real-time display of position health
"""

import os
import sys
import time
from pathlib import Path
from decimal import Decimal, getcontext
from datetime import datetime

# Set precision
getcontext().prec = 28

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules' / 'safety'))

from aave_monitor_v2 import AaveMonitor

def get_status_indicator(hf):
    """Get visual status indicator"""
    if hf == Decimal('Infinity'):
        return "🟢", "PERFECT", "No debt - no liquidation risk"
    elif hf >= Decimal('3.0'):
        return "🟢", "SAFE", "Strong position"
    elif hf >= Decimal('2.5'):
        return "🟡", "CAUTION", "Adequate buffer"
    elif hf >= Decimal('2.0'):
        return "🟠", "WARNING", "Monitor closely"
    elif hf >= Decimal('1.8'):
        return "🔴", "DANGER", "Consider adding collateral"
    elif hf >= Decimal('1.5'):
        return "🚨", "CRITICAL", "Add collateral NOW"
    else:
        return "💀", "EXTREME", "Near liquidation"

def draw_health_bar(hf, width=50):
    """Draw visual health bar"""
    if hf == Decimal('Infinity'):
        fill = width
    else:
        # Scale: 1.0 = 0%, 3.0+ = 100%
        pct = min(100, max(0, ((hf - Decimal('1.0')) / Decimal('2.0')) * 100))
        fill = int((pct / 100) * width)

    filled = "█" * fill
    empty = "░" * (width - fill)

    if hf == Decimal('Infinity'):
        return f"[{filled}] ∞"
    elif hf >= Decimal('2.5'):
        return f"[{filled}{empty}] {hf:.2f}"
    elif hf >= Decimal('2.0'):
        return f"[{filled}{empty}] {hf:.2f}"
    else:
        return f"[{filled}{empty}] {hf:.2f}"

def format_usd(value):
    """Format USD value"""
    return f"${value:,.2f}"

def format_pct(value):
    """Format percentage"""
    return f"{value:.1f}%"

def print_dashboard(monitor):
    """Print main dashboard"""
    # Get current position
    position = monitor.get_position()
    hf = position.health_factor
    emoji, status, description = get_status_indicator(hf)

    # Calculate key metrics
    collateral = position.collateral_usd
    debt = position.debt_usd
    net_value = collateral - debt

    # Get block info
    block = monitor.w3.eth.block_number
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Clear screen (optional, comment out if you don't want this)
    # os.system('clear' if os.name != 'nt' else 'cls')

    print(f"\n{'='*70}")
    print(f"📊 AAVE HEALTH FACTOR DASHBOARD")
    print(f"{'='*70}")
    print(f"⏰ {timestamp} | Block: {block:,}")
    print(f"{'='*70}\n")

    # Main Status
    print(f"{emoji} STATUS: {status}")
    print(f"   {description}")
    print()

    # Health Factor Bar
    print(f"🏥 HEALTH FACTOR:")
    bar = draw_health_bar(hf)
    print(f"   {bar}")
    print()

    # Position Details
    print(f"💰 POSITION:")
    print(f"   Collateral: {format_usd(collateral)} wstETH")
    print(f"   Debt:       {format_usd(debt)} USDC")
    print(f"   Net Value:  {format_usd(net_value)}")
    print()

    # Threshold Distances
    if hf != Decimal('Infinity'):
        print(f"🎯 DISTANCE TO THRESHOLDS:")

        thresholds = [
            (Decimal('3.0'), "🟢 SAFE", "safe"),
            (Decimal('2.5'), "🟡 CAUTION", "caution"),
            (Decimal('2.0'), "🟠 WARNING", "warning"),
            (Decimal('1.8'), "🔴 DANGER", "danger"),
            (Decimal('1.5'), "🚨 CRITICAL", "critical"),
            (Decimal('1.0'), "💀 LIQUIDATION", "liquidation")
        ]

        for threshold_hf, label, _ in thresholds:
            drop_pct = monitor.calculate_collateral_drop_to_hf(position, threshold_hf)

            if hf > threshold_hf:
                # Above threshold - show cushion
                status_str = f"↓ {format_pct(drop_pct)} cushion"
            elif hf == threshold_hf:
                status_str = "← AT THRESHOLD"
            else:
                # Below threshold - show how far below
                status_str = "✗ BELOW"

            print(f"   {label:<20} HF {threshold_hf:<4} | {status_str}")

        print()

    # Repay Recommendations
    if hf != Decimal('Infinity') and hf < Decimal('3.0'):
        print(f"💊 REPAY TO IMPROVE HF:")

        targets = [
            (Decimal('2.5'), "Return to CAUTION"),
            (Decimal('3.0'), "Return to SAFE"),
            (Decimal('3.5'), "Strong position"),
        ]

        for target_hf, desc in targets:
            if hf < target_hf:
                repay = monitor.calculate_repay_to_target(position, target_hf)
                if repay > 0:
                    print(f"   HF {target_hf} ({desc}): Repay {format_usd(repay)} USDC")

        print()

    # Quick Actions
    print(f"⚡ QUICK ACTIONS:")
    print(f"   python3 scripts/emergency_aave_repay.py --target-hf 2.5")
    print(f"   python3 scripts/calculate_risk_scenarios.py")
    print(f"   python3 scripts/aave_guardian_monitor.py")
    print()

    print(f"{'='*70}\n")

def print_compact_dashboard(monitor):
    """Print compact one-line dashboard"""
    position = monitor.get_position()
    hf = position.health_factor
    emoji, status, _ = get_status_indicator(hf)

    timestamp = datetime.now().strftime('%H:%M:%S')
    coll = position.collateral_usd
    debt = position.debt_usd

    if hf == Decimal('Infinity'):
        hf_str = "∞"
    else:
        hf_str = f"{hf:.2f}"

    print(f"[{timestamp}] {emoji} HF:{hf_str} | ${coll:,.0f} coll | ${debt:,.0f} debt | {status}")

def watch_mode(monitor, interval=60, compact=False):
    """Continuous watch mode"""
    print(f"\n🔄 WATCH MODE - Updating every {interval}s (Press Ctrl+C to stop)\n")

    try:
        while True:
            if compact:
                print_compact_dashboard(monitor)
            else:
                print_dashboard(monitor)
                print(f"⏳ Next update in {interval}s...\n")

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n✅ Watch mode stopped\n")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AAVE Health Factor Dashboard')
    parser.add_argument('--watch', action='store_true',
                       help='Continuous watch mode')
    parser.add_argument('--interval', type=int, default=60,
                       help='Update interval in seconds (default: 60)')
    parser.add_argument('--compact', action='store_true',
                       help='Compact one-line output (for watch mode)')

    args = parser.parse_args()

    monitor = AaveMonitor()

    if args.watch:
        watch_mode(monitor, interval=args.interval, compact=args.compact)
    else:
        print_dashboard(monitor)

if __name__ == '__main__':
    main()
