#!/usr/bin/env python3
"""
Secure Portfolio Analyzer for Binance.US
Run this script locally with your own .env credentials
NEVER share your API credentials with external systems
"""

import os
import requests
import hmac
import hashlib
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import urllib.parse

class SecureBinanceUSAnalyzer:
    """
    Secure portfolio analyzer for Binance.US
    Runs locally with user's own credentials
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.us"
        self.api_key = None
        self.api_secret = None
        self.load_credentials()
        
    def load_credentials(self):
        """Load credentials from .env file (local only)"""
        try:
            # Try to load from .env file
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('BINANCE_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip()
                        elif line.startswith('BINANCE_API_SECRET='):
                            self.api_secret = line.split('=', 1)[1].strip()
            
            # Fallback to environment variables
            if not self.api_key:
                self.api_key = os.getenv('BINANCE_API_KEY')
            if not self.api_secret:
                self.api_secret = os.getenv('BINANCE_API_SECRET')
                
            if not self.api_key or not self.api_secret:
                print("⚠️  WARNING: No API credentials found")
                print("Create a .env file with:")
                print("BINANCE_API_KEY=your_key_here")
                print("BINANCE_API_SECRET=your_secret_here")
                return False
                
            print("✅ Credentials loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load credentials: {e}")
            return False
    
    def create_signature(self, query_string: str) -> str:
        """Create HMAC SHA256 signature"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def make_request(self, endpoint: str, params: Dict = None, signed: bool = False) -> Dict[str, Any]:
        """Make authenticated request to Binance.US API"""
        if not self.api_key or not self.api_secret:
            return {'error': 'No API credentials available'}
        
        url = f"{self.base_url}{endpoint}"
        headers = {'X-MBX-APIKEY': self.api_key}
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = urllib.parse.urlencode(params)
            signature = self.create_signature(query_string)
            params['signature'] = signature
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'API request failed: {e}'}
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information and balances"""
        return self.make_request('/api/v3/account', signed=True)
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders"""
        result = self.make_request('/api/v3/openOrders', signed=True)
        return result if isinstance(result, list) else []
    
    def get_recent_trades(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent trades (last 24 hours by default)"""
        # Get all trades and filter by time
        all_trades = self.make_request('/api/v3/myTrades', signed=True)
        if not isinstance(all_trades, list):
            return []
        
        # Filter trades from last N hours
        cutoff_time = int((time.time() - hours * 3600) * 1000)
        recent_trades = [trade for trade in all_trades if int(trade.get('time', 0)) > cutoff_time]
        
        return recent_trades
    
    def get_ticker_prices(self) -> Dict[str, float]:
        """Get current ticker prices"""
        tickers = self.make_request('/api/v3/ticker/price')
        if isinstance(tickers, list):
            return {ticker['symbol']: float(ticker['price']) for ticker in tickers}
        return {}
    
    def analyze_portfolio(self, local_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis
        
        Args:
            local_timezone: Your local timezone (e.g., 'US/Eastern', 'Europe/London')
        """
        print("🔍 SECURE PORTFOLIO ANALYSIS STARTING...")
        print("=" * 60)
        
        # Get account data
        account_info = self.get_account_info()
        if 'error' in account_info:
            return {'error': account_info['error']}
        
        # Get current prices
        ticker_prices = self.get_ticker_prices()
        
        # Get open orders
        open_orders = self.get_open_orders()
        
        # Get recent trades
        recent_trades = self.get_recent_trades(24)
        
        # Process balances
        balances = []
        total_usd_value = 0.0
        
        for balance in account_info.get('balances', []):
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:  # Only include non-zero balances
                # Get USD value
                usd_value = 0.0
                current_price = 0.0
                
                if asset == 'USD' or asset == 'USDT':
                    usd_value = total
                    current_price = 1.0
                else:
                    # Try different ticker combinations
                    for quote in ['USDT', 'USD', 'BUSD']:
                        ticker_symbol = f"{asset}{quote}"
                        if ticker_symbol in ticker_prices:
                            current_price = ticker_prices[ticker_symbol]
                            usd_value = total * current_price
                            break
                
                if usd_value > 0.01:  # Only include balances > $0.01
                    balances.append({
                        'asset': asset,
                        'free': free,
                        'locked': locked,
                        'total': total,
                        'current_price': current_price,
                        'usd_value': usd_value
                    })
                    total_usd_value += usd_value
        
        # Sort balances by USD value
        balances.sort(key=lambda x: x['usd_value'], reverse=True)
        
        # Calculate percentages
        for balance in balances:
            balance['percentage'] = (balance['usd_value'] / total_usd_value * 100) if total_usd_value > 0 else 0
        
        # Process open orders
        processed_orders = []
        for order in open_orders:
            processed_orders.append({
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'quantity': float(order['origQty']),
                'price': float(order['price']) if order['price'] != '0.00000000' else 'MARKET',
                'status': order['status'],
                'time': datetime.fromtimestamp(int(order['time'])/1000, tz=timezone.utc).isoformat()
            })
        
        # Process recent trades
        processed_trades = []
        for trade in recent_trades[-20:]:  # Last 20 trades
            processed_trades.append({
                'symbol': trade['symbol'],
                'side': 'BUY' if trade['isBuyer'] else 'SELL',
                'quantity': float(trade['qty']),
                'price': float(trade['price']),
                'commission': float(trade['commission']),
                'commission_asset': trade['commissionAsset'],
                'time': datetime.fromtimestamp(int(trade['time'])/1000, tz=timezone.utc).isoformat()
            })
        
        # SLEEP/FLIP allocation analysis
        sleep_assets = ['ADA', 'KAVA', 'INJ', 'COTI', 'ALGO', 'XTZ', 'ATOM', 'FLOW', 'NEAR']
        flip_assets = ['BTC', 'ETH', 'BONK', 'WIF', 'RNDR', 'STMX']  # Active trading assets
        
        sleep_value = sum(b['usd_value'] for b in balances if b['asset'] in sleep_assets)
        flip_value = sum(b['usd_value'] for b in balances if b['asset'] in flip_assets)
        other_value = total_usd_value - sleep_value - flip_value
        
        sleep_percentage = (sleep_value / total_usd_value * 100) if total_usd_value > 0 else 0
        flip_percentage = (flip_value / total_usd_value * 100) if total_usd_value > 0 else 0
        
        # Generate timestamp
        current_time = datetime.now(timezone.utc)
        world_time_sync = f"World Time Sync – {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return {
            'timestamp': world_time_sync,
            'account_summary': {
                'total_usd_value': round(total_usd_value, 2),
                'asset_count': len(balances),
                'open_orders_count': len(processed_orders),
                'recent_trades_count': len(processed_trades)
            },
            'balances': balances,
            'open_orders': processed_orders,
            'recent_trades': processed_trades,
            'allocation_analysis': {
                'sleep_tier': {
                    'value': round(sleep_value, 2),
                    'percentage': round(sleep_percentage, 1),
                    'assets': [b for b in balances if b['asset'] in sleep_assets]
                },
                'flip_tier': {
                    'value': round(flip_value, 2),
                    'percentage': round(flip_percentage, 1),
                    'assets': [b for b in balances if b['asset'] in flip_assets]
                },
                'other': {
                    'value': round(other_value, 2),
                    'percentage': round(100 - sleep_percentage - flip_percentage, 1)
                }
            },
            'alerts': self.generate_alerts(sleep_percentage, flip_percentage, balances)
        }
    
    def generate_alerts(self, sleep_pct: float, flip_pct: float, balances: List[Dict]) -> List[str]:
        """Generate portfolio alerts"""
        alerts = []
        
        # Target allocation: 60% SLEEP, 40% FLIP (example)
        target_sleep = 60.0
        target_flip = 40.0
        
        if abs(sleep_pct - target_sleep) > 5.0:
            alerts.append(f"🚨 SLEEP allocation {sleep_pct:.1f}% deviates >5% from target {target_sleep}%")
        
        if abs(flip_pct - target_flip) > 5.0:
            alerts.append(f"🚨 FLIP allocation {flip_pct:.1f}% deviates >5% from target {target_flip}%")
        
        # Check for large positions
        for balance in balances:
            if balance['percentage'] > 25.0:
                alerts.append(f"⚠️  Large position: {balance['asset']} represents {balance['percentage']:.1f}% of portfolio")
        
        return alerts
    
    def print_portfolio_report(self, analysis: Dict[str, Any]):
        """Print formatted portfolio report"""
        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return
        
        print(f"📊 PORTFOLIO SNAPSHOT")
        print(f"⏰ {analysis['timestamp']}")
        print("=" * 60)
        
        # Account Summary
        summary = analysis['account_summary']
        print(f"💰 Total Portfolio Value: ${summary['total_usd_value']:,.2f}")
        print(f"📈 Active Assets: {summary['asset_count']}")
        print(f"📋 Open Orders: {summary['open_orders_count']}")
        print(f"⏱️  Recent Trades (24h): {summary['recent_trades_count']}")
        
        # Top Holdings
        print(f"\n📈 TOP HOLDINGS")
        print("-" * 60)
        for balance in analysis['balances'][:10]:  # Top 10
            pnl_indicator = "📈" if balance['percentage'] > 5 else "📊"
            print(f"{pnl_indicator} {balance['asset']:<8} | "
                  f"{balance['total']:>12,.4f} | "
                  f"${balance['usd_value']:>8,.2f} | "
                  f"{balance['percentage']:>5.1f}%")
        
        # Allocation Analysis
        alloc = analysis['allocation_analysis']
        print(f"\n🎯 ALLOCATION ANALYSIS")
        print("-" * 60)
        print(f"💤 SLEEP Tier: ${alloc['sleep_tier']['value']:,.2f} ({alloc['sleep_tier']['percentage']:.1f}%)")
        print(f"⚡ FLIP Tier:  ${alloc['flip_tier']['value']:,.2f} ({alloc['flip_tier']['percentage']:.1f}%)")
        print(f"🔄 Other:      ${alloc['other']['value']:,.2f} ({alloc['other']['percentage']:.1f}%)")
        
        # Open Orders
        if analysis['open_orders']:
            print(f"\n📋 OPEN ORDERS")
            print("-" * 60)
            for order in analysis['open_orders'][:5]:  # Last 5
                print(f"🎯 {order['symbol']} | {order['side']} | "
                      f"{order['quantity']:.4f} @ ${order['price']} | {order['status']}")
        
        # Recent Trades
        if analysis['recent_trades']:
            print(f"\n⏱️  RECENT TRADES (Last 5)")
            print("-" * 60)
            for trade in analysis['recent_trades'][-5:]:  # Last 5
                side_icon = "🟢" if trade['side'] == 'BUY' else "🔴"
                print(f"{side_icon} {trade['symbol']} | {trade['side']} | "
                      f"{trade['quantity']:.4f} @ ${trade['price']:.6f}")
        
        # Alerts
        if analysis['alerts']:
            print(f"\n🚨 ALERTS")
            print("-" * 60)
            for alert in analysis['alerts']:
                print(alert)
        
        print("\n" + "=" * 60)
        print("✅ Portfolio analysis complete")

def main():
    """Main function - run portfolio analysis"""
    print("🔒 SECURE BINANCE.US PORTFOLIO ANALYZER")
    print("=" * 60)
    print("⚠️  This script runs locally with YOUR credentials")
    print("🛡️  Never share your API keys with external systems")
    print()
    
    analyzer = SecureBinanceUSAnalyzer()
    
    if not analyzer.api_key or not analyzer.api_secret:
        print("❌ No API credentials found. Exiting for security.")
        return
    
    # Run analysis
    analysis = analyzer.analyze_portfolio()
    
    # Print report
    analyzer.print_portfolio_report(analysis)
    
    # Save to file
    with open('portfolio_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n📄 Detailed analysis saved to: portfolio_analysis.json")

if __name__ == "__main__":
    main()

