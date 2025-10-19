#!/usr/bin/env python3
"""
🏴 SHADOW SDK - COINBASE INTEGRATION
Sovereign Shadow Coinbase trading interface
"""

import ccxt
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

load_dotenv()

class ShadowCoinbase:
    """Shadow SDK Coinbase integration"""
    
    def __init__(self):
        self.exchange = ccxt.coinbaseexchange({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
            'password': os.getenv('COINBASE_PASSWORD'),
            'enableRateLimit': True
        })
        self.name = "Coinbase"
        self.capital = 1660  # From Shadow SDK constants
        
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            return {
                'status': 'success',
                'balance': balance,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_price(self, pair: str) -> Dict[str, Any]:
        """Get current price for trading pair"""
        try:
            ticker = self.exchange.fetch_ticker(pair)
            return {
                'status': 'success',
                'pair': pair,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_trade(self, pair: str, side: str, amount_usd: float, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a trade"""
        try:
            # Get current price
            price_data = self.get_price(pair)
            if price_data['status'] != 'success':
                return price_data
            
            execution_price = price_data['ask'] if side == 'buy' else price_data['bid']
            quantity = amount_usd / execution_price
            
            if dry_run:
                return {
                    'status': 'success',
                    'mode': 'dry_run',
                    'pair': pair,
                    'side': side,
                    'amount_usd': amount_usd,
                    'quantity': quantity,
                    'execution_price': execution_price,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Live execution
            order = self.exchange.create_market_order(
                symbol=pair,
                side=side,
                amount=quantity
            )
            
            return {
                'status': 'success',
                'mode': 'live',
                'order_id': order['id'],
                'pair': pair,
                'side': side,
                'amount_usd': amount_usd,
                'quantity': quantity,
                'execution_price': execution_price,
                'order_status': order['status'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_markets(self) -> Dict[str, Any]:
        """Get available markets"""
        try:
            markets = self.exchange.fetch_markets()
            return {
                'status': 'success',
                'markets_count': len(markets),
                'markets': [m['symbol'] for m in markets if m['active']],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def main():
    """Test Shadow Coinbase integration"""
    print("🏴 SHADOW SDK - COINBASE INTEGRATION TEST")
    print("=" * 60)
    
    coinbase = ShadowCoinbase()
    
    # Test markets
    print("\n🔍 Testing markets...")
    markets = coinbase.get_markets()
    if markets['status'] == 'success':
        print(f"   ✅ {markets['markets_count']} markets available")
    else:
        print(f"   ❌ Error: {markets['error']}")
    
    # Test price
    print("\n📊 Testing price fetch...")
    price = coinbase.get_price('BTC/USD')
    if price['status'] == 'success':
        print(f"   ✅ BTC/USD: ${price['last']:,.2f}")
        print(f"   📈 Bid: ${price['bid']:,.2f}, Ask: ${price['ask']:,.2f}")
    else:
        print(f"   ❌ Error: {price['error']}")
    
    # Test dry run trade
    print("\n🧪 Testing dry run trade...")
    trade = coinbase.execute_trade('BTC/USD', 'buy', 10.0, dry_run=True)
    if trade['status'] == 'success':
        print(f"   ✅ Dry run successful")
        print(f"   💰 ${trade['amount_usd']} → {trade['quantity']:.8f} BTC @ ${trade['execution_price']:,.2f}")
    else:
        print(f"   ❌ Error: {trade['error']}")
    
    print("\n" + "=" * 60)
    print("🎯 SHADOW COINBASE READY FOR TRADING!")

if __name__ == "__main__":
    main()
