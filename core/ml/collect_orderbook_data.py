#!/usr/bin/env python3
"""
Quick Order Book Data Collection Script
Sovereign Shadow III

Usage:
    python collect_orderbook_data.py --symbol BTC/USD --duration 60 --interval 5
    python collect_orderbook_data.py --symbol ETH/USD --duration 120 --interval 10
"""

import argparse
import os
from datetime import datetime
from orderbook_rl_scaffold import OrderBookCollector

def main():
    parser = argparse.ArgumentParser(description='Collect order book data from Coinbase')
    parser.add_argument('--symbol', type=str, default='BTC/USD',
                        help='Trading pair (default: BTC/USD)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Collection duration in minutes (default: 60)')
    parser.add_argument('--interval', type=int, default=5,
                        help='Seconds between snapshots (default: 5)')
    parser.add_argument('--depth', type=int, default=20,
                        help='Order book depth (default: 20)')
    parser.add_argument('--exchange', type=str, default='coinbase',
                        help='Exchange to use (default: coinbase)')
    parser.add_argument('--output-dir', type=str, default='data/orderbook',
                        help='Output directory (default: data/orderbook)')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize collector
    print(f"\nInitializing {args.exchange} order book collector...")
    collector = OrderBookCollector(exchange_id=args.exchange)

    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    symbol_clean = args.symbol.replace('/', '_')
    filename = f"{symbol_clean}_{args.duration}min_{timestamp}.json"
    filepath = os.path.join(args.output_dir, filename)

    # Collect data
    print(f"\nCollecting {args.symbol} order book data...")
    print(f"  Duration: {args.duration} minutes")
    print(f"  Interval: {args.interval} seconds")
    print(f"  Depth: {args.depth} levels")
    print(f"  Output: {filepath}")
    print(f"\nCollection started at {datetime.now()}")
    print("Press Ctrl+C to stop early\n")

    try:
        snapshots = collector.collect_historical_snapshots(
            symbol=args.symbol,
            duration_minutes=args.duration,
            interval_seconds=args.interval,
            depth=args.depth
        )

        # Save data
        collector.save_snapshots(snapshots, filepath)

        print(f"\n{'='*70}")
        print("COLLECTION COMPLETE")
        print(f"{'='*70}")
        print(f"Total snapshots: {len(snapshots)}")
        print(f"File saved: {filepath}")
        print(f"File size: {os.path.getsize(filepath) / 1024:.2f} KB")

        # Show sample statistics
        if snapshots:
            avg_spread = sum(s.spread for s in snapshots) / len(snapshots)
            avg_imbalance = sum(s.imbalance for s in snapshots) / len(snapshots)
            print(f"\nAverage spread: ${avg_spread:.2f}")
            print(f"Average imbalance: {avg_imbalance:.4f}")

    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        if snapshots:
            print(f"Saving {len(snapshots)} snapshots collected so far...")
            collector.save_snapshots(snapshots, filepath)
            print(f"Partial data saved to: {filepath}")

    except Exception as e:
        print(f"\nError during collection: {e}")
        raise


if __name__ == "__main__":
    main()
