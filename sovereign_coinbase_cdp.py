#!/usr/bin/env python3
import os
import json
from coinbase.rest import RESTClient

# Load CDP credentials
key_file = os.getenv('COINBASE_CDP_KEY_FILE', '.keys/cdp_api_key.json')
with open(key_file, 'r') as f:
    creds = json.load(f)

api_key = creds['name']
api_secret = creds['privateKey']

# Initialize CDP client
client = RESTClient(api_key=api_key, api_secret=api_secret)

# Test connection
try:
    accounts = client.get_accounts()
    print('✅ Coinbase CDP: CONNECTED')
    print(f'Accounts: {len(accounts.get("accounts", []))}')
except Exception as e:
    print(f'❌ CDP Error: {e}')
