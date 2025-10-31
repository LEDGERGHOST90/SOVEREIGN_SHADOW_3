#!/usr/bin/env python3
"""
🏴 COINBASE CDP TRADE EXECUTOR
Uses Coinbase Developer Platform SDK
"""

import os
import sys
from cdp import Cdp, Wallet
from decimal import Decimal
from datetime import datetime

# Load CDP credentials
api_key_name = os.getenv('COINBASE_API_KEY')
private_key = os.getenv('COINBASE_API_SECRET', '')

def execute_cdp_trade(pair, side, amount_usd, dry_run=True):
    """Execute trade via Coinbase CDP"""
    print(f"\n{'='*70}")
    print(f"🎯 COINBASE CDP TRADE EXECUTION")
    print(f"{'='*70}")
    print(f"Pair: {pair}")
    print(f"Side: {side.upper()}")
    print(f"Amount: ${amount_usd:.2f}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    try:
        # Initialize CDP
        Cdp.configure(api_key_name, private_key)
        
        # Get or create wallet
        print("📊 Connecting to Coinbase CDP...")
        wallet = Wallet.create()
        print(f"   Wallet ID: {wallet.id}")
        
        # Get balance
        balance = wallet.balance(pair.split('/')[0])
        print(f"   Balance: {balance}")
        
        if dry_run:
            print(f"\n✅ DRY RUN: Would execute {side} of ${amount_usd} {pair}")
            return True
        
        # Live execution
        print(f"\n⚠️  LIVE EXECUTION")
        response = input(f"Type 'EXECUTE' to confirm: ")
        
        if response != 'EXECUTE':
            print("❌ Cancelled")
            return False
        
        # Execute trade
        print(f"🚀 Executing {side}...")
        
        if side == 'buy':
            trade = wallet.trade(
                amount=Decimal(str(amount_usd)),
                from_asset_id='usd',
                to_asset_id=pair.split('/')[0].lower()
            )
        else:
            trade = wallet.trade(
                amount=Decimal(str(amount_usd)),
                from_asset_id=pair.split('/')[0].lower(),
                to_asset_id='usd'
            )
        
        trade.wait()
        
        print(f"\n✅ TRADE COMPLETE!")
        print(f"   Trade ID: {trade.transaction.transaction_hash}")
        print(f"   Status: {trade.transaction.status}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TRADE FAILED: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute CDP trades")
    parser.add_argument('pair', help="Trading pair (e.g. BTC/USD)")
    parser.add_argument('side', choices=['buy', 'sell'], help="Buy or sell")
    parser.add_argument('amount', type=float, help="Amount in USD")
    parser.add_argument('--live', action='store_true', help="Execute real trade")
    
    args = parser.parse_args()
    
    success = execute_cdp_trade(
        pair=args.pair,
        side=args.side,
        amount_usd=args.amount,
        dry_run=not args.live
    )
    
    sys.exit(0 if success else 1)

