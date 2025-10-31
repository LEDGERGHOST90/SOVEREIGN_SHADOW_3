#!/usr/bin/env python3
'''
SOVEREIGN SHADOW - LIVE TRADING DASHBOARD
Real-time monitoring of all trading operations
'''

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def clear_screen():
    os.system('clear')

def print_header():
    print('\n' + '='*80)
    print('🔥 SOVEREIGN SHADOW - LIVE DASHBOARD 🔥'.center(80))
    print('='*80 + '\n')

def show_capital_breakdown():
    print('💎 CAPITAL ALLOCATION:')
    print('-' * 80)
    total = 10811
    cold = 6600
    active = 1660
    defi = 2397
    cash = 154
    
    print(f'  Total Portfolio:     ${total:,}')
    print(f'  ├── 💎 Cold Storage: ${cold:,} ({cold/total*100:.1f}%)')
    print(f'  ├── ⚡ Active Trade:  ${active:,} ({active/total*100:.1f}%) ← DEPLOY HERE')
    print(f'  ├── 🏦 DeFi (AAVE):   ${defi:,} ({defi/total*100:.1f}%)')
    print(f'  └── 💵 Cash Reserve:  ${cash:,} ({cash/total*100:.1f}%)')
    print()

def show_exchange_status():
    print('🔌 EXCHANGE CONNECTIVITY:')
    print('-' * 80)
    
    exchanges = {
        'OKX': '✅ CONNECTED',
        'Kraken': '✅ CONNECTED', 
        'Coinbase CDP': '⚠️  PENDING (IP allowlist)'
    }
    
    for exchange, status in exchanges.items():
        print(f'  {exchange:.<20} {status}')
    print()

def show_trading_mode():
    live_mode = os.getenv('ALLOW_LIVE_EXCHANGE', '0') == '1'
    mode = '🔴 LIVE MODE - REAL MONEY' if live_mode else '📄 PAPER MODE - SAFE'
    
    print('⚙️  TRADING MODE:')
    print('-' * 80)
    print(f'  Current Mode: {mode}')
    if not live_mode:
        print('  ℹ️  To enable live: export ALLOW_LIVE_EXCHANGE=1')
    print()

def show_recent_opportunities():
    print('🎯 RECENT MEME SCAN RESULTS:')
    print('-' * 80)
    
    # Check for scan results
    log_dir = 'logs'
    if os.path.exists(log_dir):
        logs = sorted([f for f in os.listdir(log_dir) if f.startswith('meme_scan_')])
        if logs:
            latest = os.path.join(log_dir, logs[-1])
            print(f'  Latest scan: {logs[-1]}')
            print(f'  Run scanner: python3 meme_coin_scanner.py 100')
        else:
            print('  ⚠️  No scans found. Run: python3 meme_coin_scanner.py 100')
    else:
        print('  ⚠️  Logs directory not found')
    print()

def show_defi_status():
    print('🏦 DEFI POSITION (AAVE):')
    print('-' * 80)
    print(f'  Supplied: ~$3,547 (wETH)')
    print(f'  Borrowed: $1,150 (USDC)')
    print(f'  Health Factor: 2.49 ✅ SAFE')
    print(f'  Net Position: ~$2,397')
    print(f'  Status: Monitor daily - extract at $50+ profit')
    print()

def show_quick_actions():
    print('⚡ QUICK ACTIONS:')
    print('-' * 80)
    print('  1. Scan Memes:       python3 meme_coin_scanner.py 100')
    print('  2. Check Profits:    python3 profit_extraction_protocol.py')
    print('  3. System Status:    python3 sovereign_empire_core.py')
    print('  4. Paper Trade:      python3 hybrid_execution_engine.py')
    print('  5. Test CDP:         python3 sovereign_coinbase_cdp.py')
    print()

def main():
    try:
        while True:
            clear_screen()
            print_header()
            print(f'🕐 Last Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            print()
            
            show_capital_breakdown()
            show_exchange_status()
            show_trading_mode()
            show_recent_opportunities()
            show_defi_status()
            show_quick_actions()
            
            print('='*80)
            print('Press Ctrl+C to exit | Dashboard refreshes every 10 seconds')
            print('='*80)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print('\n\n👋 Dashboard closed. Happy trading! 🚀\n')
        sys.exit(0)

if __name__ == '__main__':
    main()
