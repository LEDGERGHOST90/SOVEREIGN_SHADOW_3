#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW - TERMINAL INTERFACE
Direct command-line interaction with your trading system
"""

import os
import sys
import subprocess
from datetime import datetime

def clear_screen():
    os.system('clear')

def print_header():
    clear_screen()
    print("═══════════════════════════════════════════════════════════════════")
    print("🏴 SOVEREIGN SHADOW TRADING SYSTEM")
    print("═══════════════════════════════════════════════════════════════════")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("💰 Portfolio: $8,260 total")
    print("   🔒 Ledger: $6,600 (protected)")
    print("   ⚡ Coinbase: $1,660 (active)")
    print("")
    print("🔥 Safety: DISABLED | ⚡ Live Exchanges: ACTIVE")
    print("═══════════════════════════════════════════════════════════════════")
    print("")

def run_command(cmd, description):
    print(f"\n🚀 {description}...")
    print("─" * 67)
    result = subprocess.run(cmd, shell=True, cwd="/Volumes/LegacySafe/SovereignShadow")
    print("─" * 67)
    return result.returncode

def main():
    while True:
        print_header()
        
        print("COMMANDS:")
        print("")
        print("  scan      - 🔍 Scan for arbitrage opportunities")
        print("  balance   - 💰 Check real exchange balances")
        print("  market    - 📊 View market intelligence")
        print("  trade     - 🚀 Execute manual trade")
        print("  status    - ⚡ System status")
        print("  clear     - 🧹 Clear screen")
        print("  exit      - ❌ Exit")
        print("")
        
        try:
            command = input("🏴 > ").strip().lower()
            
            if command == "exit" or command == "quit":
                print("\n👋 Goodbye\n")
                sys.exit(0)
            
            elif command == "clear":
                continue
            
            elif command == "scan":
                run_command(
                    "source .venv/bin/activate && python3 scripts/claude_arbitrage_trader.py",
                    "Scanning arbitrage opportunities"
                )
                input("\n⏸️  Press Enter to continue...")
            
            elif command == "balance":
                run_command(
                    "source .venv/bin/activate && python3 scripts/get_real_balances.py",
                    "Fetching real balances"
                )
                input("\n⏸️  Press Enter to continue...")
            
            elif command == "market":
                run_command(
                    "source .venv/bin/activate && python3 shadow_scope.py",
                    "Loading market intelligence"
                )
                input("\n⏸️  Press Enter to continue...")
            
            elif command == "trade":
                run_command(
                    "source .venv/bin/activate && python3 EXECUTE_MANUAL_TRADE.py",
                    "Manual trade execution"
                )
                input("\n⏸️  Press Enter to continue...")
            
            elif command == "status":
                print("\n⚡ SYSTEM STATUS:")
                print("─" * 67)
                os.system("ps aux | grep -E '(python3|trading)' | grep -v grep | head -5")
                print("─" * 67)
                input("\n⏸️  Press Enter to continue...")
            
            elif command == "":
                continue
            
            else:
                print(f"\n❌ Unknown command: {command}")
                input("\n⏸️  Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()

