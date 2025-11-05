#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - CLI INTERFACE
Production-ready command-line interface for trading system

Usage:
    # Validate trade
    python -m cli.trading_cli validate-trade --symbol BTC/USDT --type long \\
        --entry 99000 --stop 97000 --target 103000 --emotion confident \\
        --market-context '{"trend_4h": "bullish", "setup_15m": "pullback_bounce"}'

    # Execute trade
    python -m cli.trading_cli execute-trade --trade-id abc123 --entry 99100

    # Close trade
    python -m cli.trading_cli close-trade --trade-id abc123 --exit 103000 \\
        --emotion-after satisfied --status target_hit

    # View dashboard
    python -m cli.trading_cli dashboard

    # Check system status
    python -m cli.trading_cli status

    # Start lesson
    python -m cli.trading_cli lesson start

    # Take quiz
    python -m cli.trading_cli lesson quiz --answers 1,1
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.master_trading_system import MasterTradingSystem
from agents.mentor_system import MentorSystem
from schemas.trade_schemas import (
    TradeValidationRequest,
    validate_json_input,
    example_trade_validation_request
)


class TradingCLI:
    """
    Production-ready CLI for Sovereign Shadow II trading system
    """

    def __init__(self, account_balance: float = 1660.0):
        """Initialize CLI with trading system"""
        self.system = MasterTradingSystem(account_balance=account_balance)

    def validate_trade(self, args) -> Dict[str, Any]:
        """
        Validate a trade setup

        Returns JSON result
        """
        # Parse market context JSON
        try:
            market_context = json.loads(args.market_context)
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid market_context JSON: {e}",
                "success": False
            }

        # Create request dict
        request_data = {
            "symbol": args.symbol,
            "trade_type": args.type,
            "entry_price": args.entry,
            "stop_loss": args.stop,
            "take_profit": args.target,
            "emotion_state": args.emotion,
            "emotion_intensity": args.intensity,
            "market_context": market_context,
            "notes": args.notes
        }

        # Validate with Pydantic schema
        valid, model, error = validate_json_input(request_data, TradeValidationRequest)

        if not valid:
            return {
                "error": f"Invalid trade request: {error}",
                "success": False
            }

        # Run validation through system
        result = self.system.pre_trade_check(
            symbol=model.symbol,
            trade_type=model.trade_type.value,
            entry_price=model.entry_price,
            stop_loss=model.stop_loss,
            take_profit=model.take_profit,
            emotion_state=model.emotion_state.value,
            emotion_intensity=model.emotion_intensity,
            market_context=model.market_context.model_dump(),
            notes=model.notes
        )

        result["success"] = True
        return result

    def execute_trade(self, args) -> Dict[str, Any]:
        """Execute an approved trade"""
        try:
            self.system.execute_trade(
                trade_id=args.trade_id,
                actual_entry=args.entry
            )
            return {
                "success": True,
                "trade_id": args.trade_id,
                "actual_entry": args.entry,
                "message": "Trade executed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def close_trade(self, args) -> Dict[str, Any]:
        """Close a trade"""
        try:
            # Parse mistakes if provided
            mistakes = args.mistakes.split(',') if args.mistakes else None

            result = self.system.close_trade(
                trade_id=args.trade_id,
                exit_price=args.exit,
                emotion_after=args.emotion_after,
                status=args.status,
                mistakes=mistakes,
                lessons_learned=args.lessons
            )

            result["success"] = True
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def display_dashboard(self) -> Dict[str, Any]:
        """Display trading dashboard"""
        self.system.display_dashboard()
        return {
            "success": True,
            "message": "Dashboard displayed"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get system status as JSON"""
        status = self.system.get_system_status()
        status["success"] = True
        return status

    def lesson_start(self) -> Dict[str, Any]:
        """Start current lesson"""
        mentor = self.system.mentor
        lesson = mentor.get_current_lesson()

        if not lesson:
            return {
                "success": False,
                "error": "No lessons available"
            }

        mentor.display_lesson(lesson)

        return {
            "success": True,
            "lesson_id": lesson["lesson_id"],
            "lesson_title": lesson["lesson_title"],
            "has_quiz": bool(lesson.get("quiz"))
        }

    def lesson_quiz(self, args) -> Dict[str, Any]:
        """Take quiz for current lesson"""
        mentor = self.system.mentor
        lesson = mentor.get_current_lesson()

        if not lesson:
            return {
                "success": False,
                "error": "No current lesson"
            }

        if not lesson.get("quiz"):
            return {
                "success": False,
                "error": "Current lesson has no quiz"
            }

        # Parse answers
        try:
            answers = [int(a.strip()) for a in args.answers.split(',')]
        except ValueError:
            return {
                "success": False,
                "error": "Invalid answer format. Use comma-separated numbers (e.g., 1,1)"
            }

        # Grade quiz
        score = mentor.take_quiz(lesson["lesson_id"], answers)

        # Check passing score (80%)
        passed = score >= 0.8

        if passed:
            mentor.complete_lesson(lesson["lesson_id"], quiz_score=score)
            return {
                "success": True,
                "passed": True,
                "score": score,
                "message": f"✅ Passed with {score:.0%}! Lesson complete."
            }
        else:
            return {
                "success": True,
                "passed": False,
                "score": score,
                "message": f"❌ Score: {score:.0%}. Need 80% to pass. Review and try again."
            }


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(
        description='🏴 Sovereign Shadow II Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate trade
  %(prog)s validate-trade --symbol BTC/USDT --type long --entry 99000 \\
      --stop 97000 --target 103000 --emotion confident \\
      --market-context '{"trend_4h": "bullish"}'

  # Execute trade
  %(prog)s execute-trade --trade-id abc123 --entry 99100

  # View dashboard
  %(prog)s dashboard

  # Start lesson
  %(prog)s lesson start

Philosophy: "System over emotion. Every single time."
        """
    )

    parser.add_argument(
        '--account-balance',
        type=float,
        default=1660.0,
        help='Account balance in USD (default: 1660.0)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # ========================================================================
    # VALIDATE TRADE
    # ========================================================================
    validate_parser = subparsers.add_parser(
        'validate-trade',
        help='Validate a trade setup'
    )
    validate_parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTC/USDT)')
    validate_parser.add_argument('--type', required=True, choices=['long', 'short'], help='Trade direction')
    validate_parser.add_argument('--entry', type=float, required=True, help='Entry price')
    validate_parser.add_argument('--stop', type=float, required=True, help='Stop loss price')
    validate_parser.add_argument('--target', type=float, required=True, help='Take profit price')
    validate_parser.add_argument('--emotion', required=True,
                                  choices=['confident', 'neutral', 'anxious', 'fearful', 'greedy', 'revenge', 'fomo'],
                                  help='Current emotion')
    validate_parser.add_argument('--intensity', type=int, default=5, help='Emotion intensity 1-10 (default: 5)')
    validate_parser.add_argument('--market-context', required=True, help='Market context as JSON string')
    validate_parser.add_argument('--notes', help='Additional trade notes')

    # ========================================================================
    # EXECUTE TRADE
    # ========================================================================
    execute_parser = subparsers.add_parser(
        'execute-trade',
        help='Execute an approved trade'
    )
    execute_parser.add_argument('--trade-id', required=True, help='Trade ID from validation')
    execute_parser.add_argument('--entry', type=float, required=True, help='Actual execution price')

    # ========================================================================
    # CLOSE TRADE
    # ========================================================================
    close_parser = subparsers.add_parser(
        'close-trade',
        help='Close a trade'
    )
    close_parser.add_argument('--trade-id', required=True, help='Trade ID to close')
    close_parser.add_argument('--exit', type=float, required=True, help='Exit price')
    close_parser.add_argument('--emotion-after', required=True,
                               choices=['satisfied', 'frustrated', 'regret', 'confident', 'neutral'],
                               help='Emotion after trade')
    close_parser.add_argument('--status', required=True,
                               choices=['target_hit', 'stopped', 'manually_closed', 'breakeven'],
                               help='How trade ended')
    close_parser.add_argument('--mistakes', help='Comma-separated mistakes (e.g., moved_stop,early_exit)')
    close_parser.add_argument('--lessons', help='Lessons learned')

    # ========================================================================
    # DASHBOARD
    # ========================================================================
    subparsers.add_parser(
        'dashboard',
        help='Display trading dashboard'
    )

    # ========================================================================
    # STATUS
    # ========================================================================
    subparsers.add_parser(
        'status',
        help='Get system status as JSON'
    )

    # ========================================================================
    # LESSON COMMANDS
    # ========================================================================
    lesson_parser = subparsers.add_parser(
        'lesson',
        help='Lesson and education commands'
    )
    lesson_subparsers = lesson_parser.add_subparsers(dest='lesson_command')

    # Start lesson
    lesson_subparsers.add_parser('start', help='Start current lesson')

    # Take quiz
    quiz_parser = lesson_subparsers.add_parser('quiz', help='Take quiz for current lesson')
    quiz_parser.add_argument('--answers', required=True, help='Comma-separated answers (e.g., 1,1)')

    # ========================================================================
    # EXAMPLE
    # ========================================================================
    subparsers.add_parser(
        'example',
        help='Show example trade validation request'
    )

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = TradingCLI(account_balance=args.account_balance)

    # Route commands
    result = None

    try:
        if args.command == 'validate-trade':
            result = cli.validate_trade(args)

        elif args.command == 'execute-trade':
            result = cli.execute_trade(args)

        elif args.command == 'close-trade':
            result = cli.close_trade(args)

        elif args.command == 'dashboard':
            result = cli.display_dashboard()

        elif args.command == 'status':
            result = cli.get_status()

        elif args.command == 'lesson':
            if args.lesson_command == 'start':
                result = cli.lesson_start()
            elif args.lesson_command == 'quiz':
                result = cli.lesson_quiz(args)
            else:
                print("Error: No lesson command specified")
                sys.exit(1)

        elif args.command == 'example':
            example = example_trade_validation_request()
            print(json.dumps(example, indent=2))
            sys.exit(0)

        # Output result
        if args.json and result:
            print(json.dumps(result, indent=2))
        elif result and not result.get("success"):
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
