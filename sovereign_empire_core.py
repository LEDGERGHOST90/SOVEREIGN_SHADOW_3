#!/usr/bin/env python3
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

print('\n🔥 SOVEREIGN SHADOW EMPIRE - MULTI-EXCHANGE TEST\n')

exchanges = {}

# OKX
try:
    exchanges['okx'] = ccxt.okx({'enableRateLimit': True})
    ticker = exchanges['okx'].fetch_ticker('BTC/USDT')
    print(f'✅ OKX: CONNECTED - BTC ${ticker["last"]:,.2f}')
except Exception as e:
    print(f'❌ OKX: {str(e)[:60]}')

# Kraken  
try:
    exchanges['kraken'] = ccxt.kraken({'enableRateLimit': True})
    ticker = exchanges['kraken'].fetch_ticker('BTC/USD')
    print(f'✅ Kraken: CONNECTED - BTC ${ticker["last"]:,.2f}')
except Exception as e:
    print(f'❌ Kraken: {str(e)[:60]}')

print(f'\n✅ {len(exchanges)}/2 exchanges operational\n')
