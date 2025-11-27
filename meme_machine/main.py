#!/usr/bin/env python3
"""
MemeMachine CLI
Meme coin scanner and analyzer for Solana
"""
import argparse
import sys

from .scanner import MemeMachine
from .analyzer import BreakoutAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="MemeMachine - Solana Meme Coin Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SCANNING (free, no limits)
  python -m meme_machine --dex              # DexScreener scan
  python -m meme_machine --search BONK      # Search tokens

  # BREAKOUT DETECTION
  python -m meme_machine --breakout         # Find breakout candidates
  python -m meme_machine --score <addr>     # Score a token (0-100)
  python -m meme_machine --snipe <addr>     # Get YES/NO decision

  # DEEP ANALYSIS
  python -m meme_machine --deep <addr>      # Helius holder analysis
  python -m meme_machine --analyze <addr>   # Full Birdeye analysis

  # OTHER
  python -m meme_machine --trending         # Trending meme tokens
  python -m meme_machine --watch <addr>     # Watch price live
        """
    )

    # Scanning commands
    parser.add_argument('--dex', action='store_true',
                        help='Scan using DexScreener (FREE, no rate limits)')
    parser.add_argument('--scan', action='store_true',
                        help='Scan using Birdeye (rate limited)')
    parser.add_argument('--search', type=str, metavar='QUERY',
                        help='Search for tokens by name/symbol')

    # Breakout detection (NEW)
    parser.add_argument('--breakout', action='store_true',
                        help='Scan for breakout candidates (scored)')
    parser.add_argument('--score', type=str, metavar='ADDRESS',
                        help='Score a token 0-100 with full analysis')
    parser.add_argument('--snipe', type=str, metavar='ADDRESS',
                        help='Get final YES/NO snipe decision')
    parser.add_argument('--min-score', type=int, default=60,
                        help='Minimum score for breakout scan (default: 60)')

    # Deep analysis
    parser.add_argument('--analyze', type=str, metavar='ADDRESS',
                        help='Full Birdeye analysis of a token')
    parser.add_argument('--deep', type=str, metavar='ADDRESS',
                        help='Helius deep dive (metadata, holders, rug risk)')

    # Other
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
        print("\n🎯 QUICK WORKFLOW:")
        print("  1. --breakout         Find candidates")
        print("  2. --score <addr>     Analyze in detail")
        print("  3. --snipe <addr>     Get final decision")
        print("\n💡 All scanning is FREE via DexScreener (no rate limits)")
        return

    # Breakout analyzer (new)
    if args.breakout or args.score or args.snipe:
        analyzer = BreakoutAnalyzer()

        if args.breakout:
            analyzer.scan_breakouts(min_score=args.min_score)

        elif args.score:
            result = analyzer.quick_verdict(args.score)
            print(result)

        elif args.snipe:
            decision, reason = analyzer.snipe_decision(args.snipe)
            print("\n" + "=" * 60)
            print("🎯 SNIPE DECISION")
            print("=" * 60)
            print(f"\n{reason}\n")
            if decision:
                print("Action: PROCEED WITH CAUTION - Set stop loss!")
            else:
                print("Action: SKIP THIS ONE")
            print()

    # Original scanner
    else:
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
