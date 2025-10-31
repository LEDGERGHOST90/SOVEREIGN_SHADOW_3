import os
from dotenv import load_dotenv
import ccxt

load_dotenv()

exchanges = {
    'Coinbase': ccxt.coinbase({
        'apiKey': os.getenv('COINBASE_API_KEY'),
        'secret': os.getenv('COINBASE_API_SECRET'),
    }),
    'OKX': ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_API_SECRET'),
        'password': os.getenv('OKX_API_PASSPHRASE'),
    }),
    'Kraken': ccxt.kraken({
        'apiKey': os.getenv('KRAKEN_API_KEY'),
        'secret': os.getenv('KRAKEN_API_SECRET'),
    })
}

print('\n🔍 TESTING EXCHANGE CONNECTIONS:\n')
for name, exchange in exchanges.items():
    try:
        balance = exchange.fetch_balance()
        print(f'✅ {name}: CONNECTED - Total Balance: ${balance["total"].get("USDT", 0):.2f}')
    except Exception as e:
        print(f'❌ {name}: FAILED - {str(e)[:100]}')

print('\n✅ Test complete! Run: python3 test_apis.py')
