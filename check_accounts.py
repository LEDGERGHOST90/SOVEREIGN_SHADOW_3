#!/usr/bin/env python3
"""
Check all Coinbase accounts to find Ledger Ghost 90
"""

from coinbase.rest import RESTClient
import os
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.getenv('COINBASE_API_KEY')
api_secret = os.getenv('COINBASE_API_SECRET')

client = RESTClient(api_key=api_key, api_secret=api_secret)

print('🔍 CHECKING ALL ACCOUNTS - INCLUDING LEDGER GHOST 90...')

accounts = client.get_accounts()

print(f'Total accounts found: {len(accounts.accounts)}')
print('\nAll accounts (checking for Ledger Ghost 90):')

ledger_accounts = []
significant_accounts = []

for i, account in enumerate(accounts.accounts):
    name = account.name
    currency = account.currency
    account_type = account.type
    
    # Get balance
    balance = 0
    if hasattr(account, 'available_balance') and account.available_balance:
        if hasattr(account.available_balance, 'value'):
            balance = float(account.available_balance.value)
        else:
            balance = float(account.available_balance.get('value', 0))
    
    # Check if this is the Ledger Ghost 90 account
    is_ledger = any(keyword in name.lower() for keyword in ['ledger', 'ghost', '90'])
    
    print(f'{i+1}. {name} ({currency}) - ${balance:.2f} - Type: {account_type}')
    
    if is_ledger:
        print(f'   🎯 POTENTIAL LEDGER GHOST 90 ACCOUNT!')
        ledger_accounts.append((name, currency, balance))
    
    if balance > 100:
        print(f'   💰 SIGNIFICANT BALANCE!')
        significant_accounts.append((name, currency, balance))
    
    print()

print('\n' + '='*60)
print('SUMMARY:')
print('='*60)

if ledger_accounts:
    print('🎯 LEDGER GHOST 90 ACCOUNTS FOUND:')
    for name, currency, balance in ledger_accounts:
        print(f'   {name} ({currency}): ${balance:.2f}')
else:
    print('❌ No accounts with "Ledger", "Ghost", or "90" in the name')

if significant_accounts:
    print('\n💰 ACCOUNTS WITH SIGNIFICANT BALANCES (>$100):')
    for name, currency, balance in significant_accounts:
        print(f'   {name} ({currency}): ${balance:.2f}')
else:
    print('\n❌ No accounts with significant balances found')

total_significant = sum(balance for _, _, balance in significant_accounts)
print(f'\nTotal significant balance: ${total_significant:.2f}')

if total_significant < 1000:
    print('\n⚠️  This API key appears to be connected to the wrong account!')
    print('   You need an API key for your $1,660 account.')
