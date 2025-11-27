#!/usr/bin/env python3
"""
MemeMachine CLI
Meme coin scanner and analyzer for Solana
"""
import argparse
import sys

from .scanner import MemeMachine
from .analyzer import BreakoutAnalyzer
from .smart_money import SmartMoneyTracker


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

  # SMART MONEY TRACKING
  python -m meme_machine --holders <addr>   # Analyze holder quality
  python -m meme_machine --wallet <addr>    # Analyze wallet win rate
  python -m meme_machine --smart-buys       # Find smart money entries
  python -m meme_machine --track-wallet <addr> --as smart  # Add to watchlist

  # DEEP ANALYSIS
  python -m meme_machine --deep <addr>      # Helius holder analysis
  python -m meme_machine --analyze <addr>   # Full Birdeye analysis
        """
    )

    # Scanning commands
    parser.add_argument('--dex', action='store_true',
                        help='Scan using DexScreener (FREE, no rate limits)')
    parser.add_argument('--scan', action='store_true',
                        help='Scan using Birdeye (rate limited)')
    parser.add_argument('--search', type=str, metavar='QUERY',
                        help='Search for tokens by name/symbol')

    # Pump.fun commands (earliest entry)
    parser.add_argument('--pumpfun', action='store_true',
                        help='Scan pump.fun for newest launches (earliest entry)')
    parser.add_argument('--graduating', action='store_true',
                        help='Find tokens about to graduate to Raydium')
    parser.add_argument('--kings', action='store_true',
                        help='Get King of the Hill tokens (most momentum)')

    # Breakout detection
    parser.add_argument('--breakout', action='store_true',
                        help='Scan for breakout candidates (scored)')
    parser.add_argument('--score', type=str, metavar='ADDRESS',
                        help='Score a token 0-100 with full analysis')
    parser.add_argument('--snipe', type=str, metavar='ADDRESS',
                        help='Get final YES/NO snipe decision')
    parser.add_argument('--min-score', type=int, default=60,
                        help='Minimum score for breakout scan (default: 60)')

    # Smart money tracking (NEW)
    parser.add_argument('--holders', type=str, metavar='TOKEN',
                        help='Analyze quality of token holders (smart money vs dumpers)')
    parser.add_argument('--wallet', type=str, metavar='WALLET',
                        help='Analyze a wallet\'s trading win rate')
    parser.add_argument('--smart-buys', action='store_true',
                        help='Find tokens smart money wallets recently bought')
    parser.add_argument('--track-wallet', type=str, metavar='WALLET',
                        help='Add wallet to tracking database')
    parser.add_argument('--as', type=str, dest='wallet_class', metavar='CLASS',
                        choices=['smart', 'dumper', 'neutral'],
                        help='Classification for --track-wallet (smart/dumper/neutral)')
    parser.add_argument('--list-wallets', action='store_true',
                        help='List all tracked wallets')

    # Discovery tools (NEW)
    parser.add_argument('--discover', action='store_true',
                        help='Discover smart wallets from successful tokens (BONK, WIF, etc)')
    parser.add_argument('--auto-track', action='store_true',
                        help='Auto-track discovered wallets (use with --discover)')
    parser.add_argument('--whales', action='store_true',
                        help='Scan for whale activity on trending tokens')

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
        print("  3. --holders <addr>   Check holder quality")
        print("  4. --snipe <addr>     Get final decision")
        print("\n🧠 SMART MONEY:")
        print("  --wallet <addr>       Analyze trader's win rate")
        print("  --smart-buys          See what winners are buying")
        print("\n💡 All scanning is FREE via DexScreener (no rate limits)")
        return

    # Smart money commands
    if args.holders or args.wallet or args.smart_buys or args.track_wallet or args.list_wallets or args.discover or args.whales:
        tracker = SmartMoneyTracker()

        if args.discover:
            if args.auto_track:
                tracker.auto_discover(auto_track=True)
            else:
                tracker.discover_winners()

        elif args.whales:
            tracker.scan_whale_activity()

        elif args.holders:
            tracker.analyze_token_holders(args.holders)

        elif args.wallet:
            profile = tracker.analyze_wallet(args.wallet)
            print(f"\n📊 WALLET ANALYSIS")
            print("=" * 60)
            print(f"Address:        {profile.address[:20]}...{profile.address[-8:]}")
            print(f"Total Trades:   {profile.total_trades}")
            print(f"Win Rate:       {profile.win_rate:.1f}%")
            print(f"Classification: {profile.classification}")
            print(f"Confidence:     {profile.confidence}")
            print(f"Last Active:    {profile.last_active}")

        elif args.smart_buys:
            tracker.find_smart_money_entries()

        elif args.track_wallet:
            if not args.wallet_class:
                print("❌ Must specify --as smart/dumper/neutral")
            else:
                class_map = {
                    'smart': 'SMART_MONEY',
                    'dumper': 'DUMPER',
                    'neutral': 'NEUTRAL'
                }
                tracker.add_known_wallet(
                    args.track_wallet,
                    class_map[args.wallet_class]
                )

        elif args.list_wallets:
            tracker.list_tracked_wallets()

    # Breakout analyzer
    elif args.breakout or args.score or args.snipe:
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

        if args.pumpfun:
            machine.pumpfun_scan()

        elif args.graduating:
            machine.pumpfun_graduating()

        elif args.kings:
            machine.pumpfun_kings()

        elif args.dex:
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
