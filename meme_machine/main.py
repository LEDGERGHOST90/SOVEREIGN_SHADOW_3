#!/usr/bin/env python3
"""
MemeMachine CLI
Meme coin scanner and analyzer for Solana
"""
import argparse
import sys

from .scanner import MemeMachine


def main():
    parser = argparse.ArgumentParser(
        description="MemeMachine - Solana Meme Coin Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m meme_machine --dex              # DexScreener scan (free, no limits)
  python -m meme_machine --scan             # Birdeye scan (rate limited)
  python -m meme_machine --search BONK      # Search for a token
  python -m meme_machine --analyze <addr>   # Full token analysis
  python -m meme_machine --deep <addr>      # Helius deep dive (holders, rug risk)
  python -m meme_machine --trending         # Get trending meme tokens
  python -m meme_machine --watch <addr>     # Watch token price live
        """
    )

    parser.add_argument('--dex', action='store_true',
                        help='Scan using DexScreener (FREE, no rate limits)')
    parser.add_argument('--scan', action='store_true',
                        help='Scan using Birdeye (rate limited)')
    parser.add_argument('--search', type=str, metavar='QUERY',
                        help='Search for tokens by name/symbol')
    parser.add_argument('--analyze', type=str, metavar='ADDRESS',
                        help='Full Birdeye analysis of a token')
    parser.add_argument('--deep', type=str, metavar='ADDRESS',
                        help='Helius deep dive (metadata, holders, rug risk)')
    parser.add_argument('--trending', action='store_true',
                        help='Get trending meme tokens')
    parser.add_argument('--watch', type=str, metavar='ADDRESS',
                        help='Watch token price live')
    parser.add_argument('--duration', type=int, default=60,
                        help='Watch duration in minutes (default: 60)')

    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "=" * 60)
        print("MEMEMACHINE - Solana Meme Coin Sniper")
        print("=" * 60)
        print("\nQuick Start:")
        print("  1. Run --dex for free unlimited scanning")
        print("  2. Use --deep <address> to check rug risk")
        print("  3. Use --analyze <address> for full token data")
        return

    machine = MemeMachine()

    if args.dex:
        machine.dex_scan()

    elif args.scan:
        machine.birdeye_scan()

    elif args.search:
        machine.dex_search(args.search)

    elif args.analyze:
        machine.analyze_token(args.analyze)

    elif args.deep:
        machine.deep_dive(args.deep)

    elif args.trending:
        machine.get_trending()

    elif args.watch:
        machine.watch_token(args.watch, args.duration)


if __name__ == '__main__':
    main()
