#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW - CLAUDE TERMINAL
Simple command interface for your trading system
"""

import os
import sys
import subprocess
from datetime import datetime

def clear():
    os.system('clear')

def header():
    print("\n" + "="*70)
    print("🏴 SOVEREIGN SHADOW TRADING SYSTEM")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Portfolio: $8,260 | 🎯 Target: $50,000")
    print("="*70 + "\n")

def run(cmd):
    """Run command and show output"""
    print(f"\n🚀 Running: {cmd}\n")
    print("-"*70)
    subprocess.run(cmd, shell=True, cwd="/Volumes/LegacySafe/SovereignShadow")
    print("-"*70)

def help_menu():
    print("""
📋 AVAILABLE COMMANDS:

🔍 MARKET ANALYSIS
  scan         - Scan for arbitrage opportunities
  market       - View market intelligence (Shadow Scope)
  prices       - Check current prices across exchanges
  
💰 PORTFOLIO
  balance      - Check exchange balances
  portfolio    - View complete portfolio
  aave         - Check Aave position & health factor
  
⚡ TRADING
  trade        - Execute manual trade
  test         - Test trading system (no real trades)
  strategies   - List all 9 trading strategies
  
🤖 SYSTEM
  status       - System status & running processes
  validate     - Validate API connections
  logs         - View recent logs
  
📚 HELP
  help         - Show this menu
  clear        - Clear screen
  exit         - Exit terminal

🎯 QUICK START: Type 'test' to test the system
""")

def main():
    clear()
    header()
    help_menu()
    
    while True:
        try:
            cmd = input("\n🏴 > ").strip().lower()
            
            if not cmd:
                continue
            
            elif cmd in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            elif cmd == 'clear':
                clear()
                header()
            
            elif cmd == 'help':
                help_menu()
            
            # MARKET ANALYSIS
            elif cmd == 'scan':
                run("python3 live_market_scanner.py")
            
            elif cmd == 'market':
                run("python3 shadow_scope.py")
            
            elif cmd == 'prices':
                run("python3 scripts/validate_api_connections.py")
            
            # PORTFOLIO
            elif cmd == 'balance':
                run("python3 scripts/validate_api_connections.py")
            
            elif cmd == 'portfolio':
                print("\n💰 YOUR PORTFOLIO:")
                print("-"*70)
                print("🔒 Ledger (Cold Storage): $6,600 (READ-ONLY)")
                print("⚡ Coinbase (Hot Wallet): $1,660 (ACTIVE)")
                print("🏦 Aave Position: $2,397 net")
                print("💎 Total Capital: $10,811")
                print("-"*70)
            
            elif cmd == 'aave':
                run("python3 core/portfolio/check_aave_position.py")
            
            # TRADING
            elif cmd == 'trade':
                run("python3 core/trading/EXECUTE_MANUAL_TRADE.py")
            
            elif cmd == 'test':
                run("python3 sovereign_shadow_orchestrator.py")
            
            elif cmd == 'strategies':
                run("python3 -c \"from strategy_knowledge_base import StrategyKnowledgeBase; kb = StrategyKnowledgeBase(); [print(f'⚡ {s.name} - {s.description}') for s in kb.get_all_strategies().values()]\"")
            
            # SYSTEM
            elif cmd == 'status':
                print("\n⚡ SYSTEM STATUS:")
                print("-"*70)
                os.system("ps aux | grep -E '(python3.*shadow|python3.*scanner|python3.*orchestrator)' | grep -v grep")
                print("-"*70)
            
            elif cmd == 'validate':
                run("python3 scripts/validate_api_connections.py")
            
            elif cmd == 'logs':
                print("\n📊 RECENT LOGS:")
                print("-"*70)
                os.system("tail -20 logs/ai_enhanced/sovereign_shadow_unified.log 2>/dev/null || echo 'No logs found'")
                print("-"*70)
            
            else:
                print(f"\n❌ Unknown command: '{cmd}'")
                print("💡 Type 'help' to see available commands")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

