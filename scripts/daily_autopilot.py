#!/usr/bin/env python3
"""
DAILY AUTOPILOT - Runs automatically, no human input needed
Saves report to daily_reports/ folder
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv('/Volumes/legacysafe/sovereignshadow_II/.env')

import ccxt

REPORT_DIR = Path('/Volumes/legacysafe/sovereignshadow_II/daily_reports')
REPORT_DIR.mkdir(exist_ok=True)

def get_coinbase_balances():
    """Get actual balances from Coinbase"""
    try:
        cb = ccxt.coinbase({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
        })
        balance = cb.fetch_balance()
        holdings = {}
        for asset, data in balance['total'].items():
            if data and data > 0:
                holdings[asset] = data
        return holdings, None
    except Exception as e:
        return {}, str(e)

def get_kraken_balances():
    """Get actual balances from Kraken"""
    try:
        kraken = ccxt.kraken({
            'apiKey': os.getenv('KRAKEN_API_KEY'),
            'secret': os.getenv('KRAKEN_PRIVATE_KEY'),
        })
        balance = kraken.fetch_balance()
        holdings = {}
        for asset, data in balance['total'].items():
            if data and data > 0:
                holdings[asset] = data
        return holdings, None
    except Exception as e:
        return {}, str(e)

def get_binance_us_balances():
    """Get actual balances from Binance US"""
    try:
        binance = ccxt.binanceus({
            'apiKey': os.getenv('BINANCE_US_API_KEY'),
            'secret': os.getenv('BINANCE_US_SECRET_KEY'),
            'enableRateLimit': True,
        })
        balance = binance.fetch_balance()
        holdings = {}
        for asset, data in balance['total'].items():
            if data and data > 0:
                holdings[asset] = data
        return holdings, None
    except Exception as e:
        return {}, str(e)

def get_prices():
    """Get current prices"""
    try:
        cb = ccxt.coinbase()
        assets = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD']
        prices = {}
        for symbol in assets:
            try:
                ticker = cb.fetch_ticker(symbol)
                prices[symbol.split('/')[0]] = ticker['last']
            except:
                continue
        return prices, None
    except Exception as e:
        return {}, str(e)

def generate_report():
    """Generate daily report"""
    now = datetime.now()
    
    report = []
    report.append('=' * 60)
    report.append(f'SOVEREIGN SHADOW II - DAILY AUTOPILOT REPORT')
    report.append(f'Generated: {now.strftime("%Y-%m-%d %H:%M:%S")}')
    report.append('=' * 60)
    
    # Get prices
    prices, price_err = get_prices()
    report.append('\n## MARKET PRICES')
    report.append('-' * 40)
    if prices:
        for asset, price in prices.items():
            report.append(f'{asset}: ${price:,.2f}')
    else:
        report.append(f'Error fetching prices: {price_err}')
    
    # Get Coinbase balances
    cb_holdings, cb_err = get_coinbase_balances()
    report.append('\n## COINBASE HOLDINGS')
    report.append('-' * 40)
    if cb_holdings:
        total_usd = 0
        for asset, amount in sorted(cb_holdings.items()):
            if asset in prices:
                value = amount * prices[asset]
                total_usd += value
                report.append(f'{asset}: {amount:.6f} (${value:,.2f})')
            elif asset in ['USD', 'USDC', 'USDT']:
                total_usd += amount
                report.append(f'{asset}: ${amount:,.2f}')
            else:
                report.append(f'{asset}: {amount:.6f}')
        report.append(f'\nCOINBASE TOTAL: ${total_usd:,.2f}')
    else:
        report.append(f'Error or empty: {cb_err}')
    
    # Kraken disabled - not actively using
    # To re-enable, uncomment below:
    # kr_holdings, kr_err = get_kraken_balances()
    # report.append('\n## KRAKEN HOLDINGS')
    # report.append('-' * 40)
    # if kr_holdings:
    #     for asset, amount in sorted(kr_holdings.items()):
    #         report.append(f'{asset}: {amount:.6f}')
    # else:
    #     report.append(f'Error or empty: {kr_err}')

    # Get Binance US balances
    bn_holdings, bn_err = get_binance_us_balances()
    report.append('\n## BINANCE US HOLDINGS')
    report.append('-' * 40)
    if bn_holdings:
        total_usd = 0
        for asset, amount in sorted(bn_holdings.items()):
            if asset in prices:
                value = amount * prices[asset]
                total_usd += value
                report.append(f'{asset}: {amount:.6f} (${value:,.2f})')
            elif asset in ['USD', 'USDC', 'USDT']:
                total_usd += amount
                report.append(f'{asset}: ${amount:,.2f}')
            else:
                report.append(f'{asset}: {amount:.6f}')
        report.append(f'\nBINANCE US TOTAL: ${total_usd:,.2f}')
    else:
        report.append(f'Error or empty: {bn_err}')

    # Simple action items
    report.append('\n## TODAY\'S FOCUS')
    report.append('-' * 40)
    report.append('1. Check AAVE health factor (target: >2.0)')
    report.append('2. Review any positions >10% profit (consider trim)')
    report.append('3. Review any positions >5% loss (consider stop)')
    
    report.append('\n' + '=' * 60)
    report.append('END REPORT')
    report.append('=' * 60)
    
    return '\n'.join(report)

def main():
    report = generate_report()
    
    # Save to file
    today = datetime.now().strftime('%Y-%m-%d')
    filepath = REPORT_DIR / f'report_{today}.txt'
    with open(filepath, 'w') as f:
        f.write(report)
    
    # Also save as latest
    latest = REPORT_DIR / 'LATEST.txt'
    with open(latest, 'w') as f:
        f.write(report)
    
    print(report)
    print(f'\nSaved to: {filepath}')

if __name__ == '__main__':
    main()
