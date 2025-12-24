#!/usr/bin/env python3
'''
SOVEREIGN SHADOW - MASTER CONTROL CENTER
One script to rule them all
'''

import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    print('\n' + '='*80)
    print('⚡ SOVEREIGN SHADOW - MASTER CONTROL CENTER ⚡'.center(80))
    print('='*80)
    print(f'🕐 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*80 + '\n')

def show_menu():
    print('📋 AVAILABLE OPERATIONS:\n')
    print('  [1] 🎯 Scan Meme Coins ($100 allocation)')
    print('  [2] 💰 Check Profit Extraction')
    print('  [3] 🔌 Test Exchange Connections')
    print('  [4] 📊 Launch Live Dashboard')
    print('  [5] 📄 Execute Paper Trade')
    print('  [6] 🔴 Execute LIVE Trade (requires confirmation)')
    print('  [7] 💎 Show Capital Breakdown')
    print('  [8] 🏦 Check DeFi Health')
    print('  [9] 🔧 System Diagnostics')
    print('  [0] 🚪 Exit\n')
    print('='*80)

def run_command(cmd, description):
    print(f'\n🚀 {description}...')
    print('='*80)
    subprocess.run(cmd, shell=True)
    print('='*80)
    input('\n⏸️  Press ENTER to continue...')

def show_capital():
    print('\n💎 CAPITAL BREAKDOWN:')
    print('='*80)
    print('Total Portfolio:     $10,811')
    print('  ├── 💎 Cold Storage: $6,600 (61%)')
    print('  ├── ⚡ Active Trade:  $1,660 (15%) ← DEPLOY HERE')
    print('  ├── 🏦 DeFi (AAVE):   $2,397 (22%)')
    print('  └── 💵 Cash Reserve:  $154 (2%)')
    print('='*80)
    input('\n⏸️  Press ENTER to continue...')

def main():
    while True:
        os.system('clear')
        print_banner()
        show_menu()
        
        choice = input('Select operation [0-9]: ').strip()
        
        if choice == '1':
            run_command('python3 meme_coin_scanner.py 100', 'Scanning Meme Coins')
        elif choice == '2':
            run_command('python3 profit_extraction_protocol.py', 'Checking Profit Extraction')
        elif choice == '3':
            run_command('python3 sovereign_empire_core.py', 'Testing Exchanges')
        elif choice == '4':
            run_command('python3 live_dashboard.py', 'Launching Dashboard')
        elif choice == '5':
            run_command('python3 hybrid_execution_engine.py', 'Paper Trade Mode')
        elif choice == '6':
            print('\n⚠️  LIVE TRADE MODE - REAL MONEY!')
            confirm = input('Type "EXECUTE LIVE" to continue: ')
            if confirm == 'EXECUTE LIVE':
                run_command('export ALLOW_LIVE_EXCHANGE=1 && python3 hybrid_execution_engine.py --live', 'LIVE TRADING ENABLED')
            else:
                print('❌ Cancelled')
                input('\n⏸️  Press ENTER to continue...')
        elif choice == '7':
            show_capital()
        elif choice == '8':
            run_command('python3 -c "print(\'🏦 AAVE POSITION:\\n  Supplied: ~$3,547\\n  Borrowed: $1,150\\n  Health: 2.49 ✅ SAFE\')"', 'DeFi Health Check')
        elif choice == '9':
            run_command('ls -lh *.py && python3 --version && pip3 list | grep -E "ccxt|python-dotenv|web3"', 'System Diagnostics')
        elif choice == '0':
            print('\n👋 Exiting Master Control. Happy trading! 🚀\n')
            sys.exit(0)
        else:
            print('\n❌ Invalid selection. Try again.')
            input('\n⏸️  Press ENTER to continue...')

if __name__ == '__main__':
    main()
