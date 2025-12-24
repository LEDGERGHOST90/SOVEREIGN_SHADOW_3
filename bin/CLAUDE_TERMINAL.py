#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW - CLAUDE TERMINAL
Simple command interface for your trading system
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def clear():
    os.system('clear')

def get_live_portfolio():
    """Get live portfolio value from exchanges"""
    total = 0.0
    try:
        # Try to read from live status file first (faster)
        status_file = PROJECT_ROOT / "memory" / "LIVE_STATUS.json"
        if status_file.exists():
            with open(status_file) as f:
                data = json.load(f)
                if "portfolio" in data:
                    return data["portfolio"].get("total_usd", 0)

        # Fallback: Try Coinbase API
        from core.exchanges.coinbase_connector import CoinbaseConnector
        cb = CoinbaseConnector()
        balances = cb.get_balances()
        for asset, info in balances.items():
            total += info.get("usd_value", 0)
    except Exception:
        # If all else fails, return placeholder
        total = 0
    return total

def header():
    print("\n" + "="*70)
    print("🏴 SOVEREIGN SHADOW TRADING SYSTEM")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get live portfolio
    portfolio = get_live_portfolio()
    if portfolio > 0:
        print(f"💰 Portfolio: ${portfolio:,.2f} | 🎯 Target: $50,000")
    else:
        print(f"💰 Portfolio: [Run 'balance' to fetch] | 🎯 Target: $50,000")

    print("="*70 + "\n")

def run(cmd):
    """Run command and show output with error handling"""
    print(f"\n🚀 Running: {cmd}\n")
    print("-"*70)
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd="/Volumes/LegacySafe/SOVEREIGN_SHADOW_3",
            check=False,  # Don't raise on non-zero exit
            timeout=300  # 5 minute timeout
        )
        if result.returncode != 0:
            print(f"\n⚠️ Command exited with code {result.returncode}")
    except subprocess.TimeoutExpired:
        print("\n⏱️ Command timed out after 5 minutes")
    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        print(f"\n⚠️ Terminal connection issue: {type(e).__name__}")
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
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

🧠 DS-STAR (AI Analysis)
  score BTC    - Get Smart Asset Score (0-100)
  ask "..."    - Ask market questions (e.g. ask "ETH trend?")
  dstest       - Test all DS-STAR modules

🤖 SYSTEM
  status       - System status & running processes
  validate     - Validate API connections
  logs         - View recent logs

📚 HELP
  help         - Show this menu
  clear        - Clear screen
  exit         - Exit terminal

🎯 QUICK START: Type 'dstest' to test the AI analysis system
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

            # DS-STAR (AI ANALYSIS)
            elif cmd == 'dstest':
                run("python3 ds_star/mcp_server.py --test")

            elif cmd.startswith('score '):
                asset = cmd.split(' ', 1)[1].upper()
                run(f"python3 -c \"from ds_star import SynopticCore; r = SynopticCore().assess('{asset}'); print(f'🎯 {asset} Score: {{r.smart_asset_score}}/100'); print(f'📊 Technical: {{r.components.get(\\\"technical\\\", 0)}}/100'); print(f'⛓️ On-Chain: {{r.components.get(\\\"on_chain\\\", 0)}}/100'); print(f'📈 Trend: {{r.recommendation}}')\"")

            elif cmd.startswith('ask '):
                question = cmd.split(' ', 1)[1].strip('"').strip("'")
                run(f"python3 -c \"from ds_star import OracleInterface; r = OracleInterface().query('{question}'); print(r.get('caption', 'No answer'))\"")

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
        
        except (KeyboardInterrupt, EOFError):
            # Terminal disconnected or Ctrl+C
            print("\n\n👋 Goodbye!\n")
            break
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            # Terminal connection lost
            print(f"\n⚠️ Terminal connection lost: {type(e).__name__}")
            print("👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            # Continue running after error

if __name__ == "__main__":
    main()

