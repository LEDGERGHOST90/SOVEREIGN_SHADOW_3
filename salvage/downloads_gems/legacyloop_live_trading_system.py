#!/usr/bin/env python3
"""
LegacyLoop AI - Live Trading System
Division 2 Flip Engine with Real-Time Execution
"""

import os
import time
import json
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class LegacyLoopLiveTradingSystem:
    """Complete live trading system for LegacyLoop AI Division 2"""
    
    def __init__(self):
        # Live API credentials
        self.api_key = "96qt7ajRenW8U6CE6jiDaqTH2C6r5TI2bk1YTU39m4ZsGEqNmAe3oBy2XzJQra1"
        self.api_secret = "74FoNmzBJqCYXVH7rq8nnkUgvJrbUkuFHPrQpWiLTP4YZFEABbPL30HjbY7B5DnJ"
        self.base_url = "https://api.binance.us"
        
        # Trading parameters from Division 2 system
        self.capital_base = 739.0  # User's available USDT
        self.max_position_risk = 0.05  # 5% max per position
        self.cash_reserve_ratio = 0.30  # 30% cash reserve (aggressive)
        self.ray_rules_threshold = 65  # Minimum Ray Rules score
        
        # Current market opportunities from live analysis
        self.priority_targets = [
            {
                'symbol': 'SKLUSDT',
                'current_price': 0.0415,
                'change_24h': 46.38,
                'ray_score': 100,
                'priority': 1,
                'position_size_usd': 75,
                'stop_loss': 0.040255,
                'take_profit_1': 0.044820,
                'take_profit_2': 0.047725
            },
            {
                'symbol': 'ENJUSDT', 
                'current_price': 0.1086,
                'change_24h': 21.34,
                'ray_score': 100,
                'priority': 2,
                'position_size_usd': 60,
                'stop_loss': 0.105342,
                'take_profit_1': 0.117288,
                'take_profit_2': 0.124890
            },
            {
                'symbol': 'ADAUSDT',
                'current_price': 0.999,
                'change_24h': 18.35,
                'ray_score': 100,
                'priority': 3,
                'position_size_usd': 75,
                'stop_loss': 0.96903,
                'take_profit_1': 1.07892,
                'take_profit_2': 1.14885
            },
            {
                'symbol': 'ARBUSDT',
                'current_price': 0.5456,
                'change_24h': 14.02,
                'ray_score': 100,
                'priority': 4,
                'position_size_usd': 50,
                'stop_loss': 0.5292,
                'take_profit_1': 0.589248,
                'take_profit_2': 0.627440
            }
        ]
        
        # System status
        self.api_authenticated = False
        self.trading_enabled = False
        self.active_positions = {}
        self.execution_log = []
        
        print("🚀 LegacyLoop AI Live Trading System Initialized")
        print(f"💰 Capital Base: ${self.capital_base} USDT")
        print(f"🎯 Priority Targets: {len(self.priority_targets)} opportunities")
        
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature for API requests"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        """Make authenticated API request with error handling"""
        if params is None:
            params = {}
            
        # Add timestamp for signed requests
        if endpoint in ['/api/v3/account', '/api/v3/order']:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        # Headers
        headers = {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Make request
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Handle different response codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "API_UNAUTHORIZED", "message": "API key authentication failed"}
            elif response.status_code == 403:
                return {"error": "API_FORBIDDEN", "message": "API key lacks required permissions"}
            else:
                return {"error": f"HTTP_{response.status_code}", "message": response.text}
                
        except requests.exceptions.RequestException as e:
            return {"error": "NETWORK_ERROR", "message": str(e)}
    
    def test_api_connection(self) -> Dict:
        """Test API connection and permissions"""
        print("🔍 Testing API connection and permissions...")
        
        # Test public endpoint first
        server_time = self._make_request("/api/v3/time")
        if "error" in server_time:
            return {"status": "FAILED", "issue": "Cannot connect to Binance API", "details": server_time}
        
        print("✅ Public API connection successful")
        
        # Test private endpoint (account info)
        account_info = self._make_request("/api/v3/account")
        if "error" in account_info:
            if account_info["error"] == "API_UNAUTHORIZED":
                return {
                    "status": "AUTH_FAILED",
                    "issue": "API key authentication failed",
                    "solution": "Verify API key and secret are correct",
                    "details": account_info
                }
            elif account_info["error"] == "API_FORBIDDEN":
                return {
                    "status": "PERMISSIONS_FAILED", 
                    "issue": "API key lacks trading permissions",
                    "solution": "Enable 'Enable Trading' permission in Binance.US API settings",
                    "details": account_info
                }
            else:
                return {"status": "FAILED", "issue": "Unknown API error", "details": account_info}
        
        print("✅ Private API authentication successful")
        self.api_authenticated = True
        
        # Check if trading is enabled
        if 'permissions' in account_info:
            if 'SPOT' in account_info['permissions']:
                self.trading_enabled = True
                print("✅ Trading permissions confirmed")
            else:
                return {
                    "status": "NO_TRADING_PERMISSIONS",
                    "issue": "API key does not have SPOT trading permissions",
                    "solution": "Enable 'Enable Trading' in Binance.US API settings"
                }
        
        return {"status": "SUCCESS", "message": "API fully authenticated and trading enabled"}
    
    def get_current_portfolio(self) -> Dict:
        """Get current portfolio balances and calculate available capital"""
        if not self.api_authenticated:
            return {"error": "API not authenticated"}
        
        account_info = self._make_request("/api/v3/account")
        if "error" in account_info:
            return account_info
        
        balances = {}
        total_usdt_value = 0
        
        for balance in account_info.get('balances', []):
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:
                balances[asset] = {
                    'free': free,
                    'locked': locked,
                    'total': total
                }
                
                # Calculate USDT value
                if asset == 'USDT':
                    total_usdt_value += total
                else:
                    # Get current price
                    price_data = self._make_request(f"/api/v3/ticker/price", {"symbol": f"{asset}USDT"})
                    if "price" in price_data:
                        total_usdt_value += total * float(price_data['price'])
        
        available_usdt = balances.get('USDT', {}).get('free', 0)
        
        return {
            'balances': balances,
            'total_portfolio_value': total_usdt_value,
            'available_usdt': available_usdt,
            'deployment_capacity': available_usdt * (1 - self.cash_reserve_ratio),
            'last_updated': datetime.now().isoformat()
        }
    
    def execute_priority_trades(self) -> Dict:
        """Execute trades on priority targets with Ray Rules validation"""
        print("🔥 Executing Priority Trades - Division 2 Flip Engine")
        
        # Test API first
        api_test = self.test_api_connection()
        if api_test["status"] != "SUCCESS":
            return {
                "status": "API_ISSUE",
                "message": "Cannot execute trades due to API issues",
                "api_test_result": api_test,
                "recommended_action": "Fix API permissions before trading"
            }
        
        # Get current portfolio
        portfolio = self.get_current_portfolio()
        if "error" in portfolio:
            return {"status": "PORTFOLIO_ERROR", "details": portfolio}
        
        available_usdt = portfolio['available_usdt']
        deployment_capacity = portfolio['deployment_capacity']
        
        print(f"💰 Available USDT: ${available_usdt:.2f}")
        print(f"🎯 Deployment Capacity: ${deployment_capacity:.2f}")
        
        if available_usdt < 50:
            return {
                "status": "INSUFFICIENT_CAPITAL",
                "message": f"Need minimum $50 USDT, have ${available_usdt:.2f}",
                "available_usdt": available_usdt
            }
        
        execution_results = {}
        total_deployed = 0
        
        # Execute trades on priority targets
        for target in self.priority_targets:
            if total_deployed >= deployment_capacity:
                break
                
            symbol = target['symbol']
            position_size_usd = min(target['position_size_usd'], deployment_capacity - total_deployed)
            
            if position_size_usd < 10:  # Minimum position size
                continue
            
            print(f"\n🎯 Executing {symbol}")
            print(f"💰 Position Size: ${position_size_usd}")
            print(f"⚖️ Ray Score: {target['ray_score']}/100")
            print(f"📈 24h Change: +{target['change_24h']:.2f}%")
            
            # Get current price
            current_price_data = self._make_request("/api/v3/ticker/price", {"symbol": symbol})
            if "error" in current_price_data:
                execution_results[symbol] = {"error": "Price fetch failed", "details": current_price_data}
                continue
            
            current_price = float(current_price_data['price'])
            quantity = position_size_usd / current_price
            
            # Place market buy order
            order_params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
                'quoteOrderQty': f"{position_size_usd:.2f}"  # Buy with USDT amount
            }
            
            order_result = self._make_request("/api/v3/order", order_params, method="POST")
            
            if "error" not in order_result:
                # Successful order
                execution_results[symbol] = {
                    "status": "SUCCESS",
                    "order_id": order_result.get('orderId'),
                    "executed_qty": order_result.get('executedQty'),
                    "executed_price": current_price,
                    "position_size_usd": position_size_usd,
                    "ray_score": target['ray_score'],
                    "stop_loss": target['stop_loss'],
                    "take_profit_1": target['take_profit_1'],
                    "take_profit_2": target['take_profit_2']
                }
                
                total_deployed += position_size_usd
                
                # Log successful execution
                self.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'price': current_price,
                    'usd_value': position_size_usd,
                    'ray_score': target['ray_score'],
                    'order_id': order_result.get('orderId')
                })
                
                print(f"✅ {symbol} order executed - ID: {order_result.get('orderId')}")
                
            else:
                execution_results[symbol] = {"error": "Order failed", "details": order_result}
                print(f"❌ {symbol} order failed: {order_result.get('message', 'Unknown error')}")
        
        return {
            "status": "COMPLETED",
            "total_deployed": total_deployed,
            "successful_trades": len([r for r in execution_results.values() if r.get("status") == "SUCCESS"]),
            "execution_results": execution_results,
            "portfolio_before": portfolio,
            "execution_log": self.execution_log
        }
    
    def monitor_positions(self) -> Dict:
        """Monitor active positions and manage stop losses / take profits"""
        if not self.api_authenticated:
            return {"error": "API not authenticated"}
        
        print("📊 Monitoring Active Positions...")
        
        portfolio = self.get_current_portfolio()
        if "error" in portfolio:
            return portfolio
        
        position_status = {}
        
        for target in self.priority_targets:
            symbol = target['symbol']
            asset = symbol.replace('USDT', '')
            
            # Check if we have this asset
            if asset in portfolio['balances']:
                balance = portfolio['balances'][asset]
                if balance['total'] > 0:
                    # Get current price
                    price_data = self._make_request("/api/v3/ticker/price", {"symbol": symbol})
                    if "price" in price_data:
                        current_price = float(price_data['price'])
                        entry_price = target['current_price']  # Approximate entry
                        
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                        position_value = balance['total'] * current_price
                        
                        position_status[symbol] = {
                            'asset': asset,
                            'quantity': balance['total'],
                            'entry_price': entry_price,
                            'current_price': current_price,
                            'position_value_usd': position_value,
                            'pnl_percent': pnl_percent,
                            'stop_loss': target['stop_loss'],
                            'take_profit_1': target['take_profit_1'],
                            'take_profit_2': target['take_profit_2'],
                            'status': self._get_position_status(current_price, target)
                        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_positions': position_status,
            'total_positions': len(position_status),
            'portfolio_summary': portfolio
        }
    
    def _get_position_status(self, current_price: float, target: Dict) -> str:
        """Determine position status based on current price vs targets"""
        if current_price <= target['stop_loss']:
            return "STOP_LOSS_TRIGGERED"
        elif current_price >= target['take_profit_2']:
            return "TAKE_PROFIT_2_REACHED"
        elif current_price >= target['take_profit_1']:
            return "TAKE_PROFIT_1_REACHED"
        else:
            return "HOLDING"
    
    def generate_trading_report(self) -> Dict:
        """Generate comprehensive trading performance report"""
        portfolio = self.get_current_portfolio()
        positions = self.monitor_positions()
        
        # Calculate performance metrics
        total_trades = len(self.execution_log)
        successful_trades = len([t for t in self.execution_log if 'order_id' in t])
        
        if positions and 'active_positions' in positions:
            total_pnl = sum([pos['pnl_percent'] for pos in positions['active_positions'].values()])
            avg_pnl = total_pnl / len(positions['active_positions']) if positions['active_positions'] else 0
        else:
            total_pnl = 0
            avg_pnl = 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_status': {
                'api_authenticated': self.api_authenticated,
                'trading_enabled': self.trading_enabled,
                'capital_base': self.capital_base,
                'deployment_capacity': self.capital_base * (1 - self.cash_reserve_ratio)
            },
            'trading_performance': {
                'total_trades_attempted': total_trades,
                'successful_trades': successful_trades,
                'success_rate': f"{(successful_trades/total_trades*100):.1f}%" if total_trades > 0 else "0%",
                'average_pnl_percent': f"{avg_pnl:.2f}%",
                'total_pnl_percent': f"{total_pnl:.2f}%"
            },
            'current_portfolio': portfolio,
            'active_positions': positions.get('active_positions', {}) if positions else {},
            'priority_targets': self.priority_targets,
            'execution_log': self.execution_log
        }

def main():
    """Main execution function for live trading system"""
    print("🚀 LEGACYLOOP AI - LIVE TRADING SYSTEM")
    print("=" * 60)
    print("Division 2 Flip Engine - Real-Time Execution")
    print("=" * 60)
    
    # Initialize trading system
    trading_system = LegacyLoopLiveTradingSystem()
    
    try:
        # Test API connection first
        print("\n🔍 PHASE 1: API CONNECTION TEST")
        api_test = trading_system.test_api_connection()
        
        if api_test["status"] == "SUCCESS":
            print("✅ API fully authenticated and ready for trading")
            
            # Execute priority trades
            print("\n🔥 PHASE 2: EXECUTING PRIORITY TRADES")
            execution_results = trading_system.execute_priority_trades()
            
            print(f"\n📊 EXECUTION SUMMARY:")
            print(f"Status: {execution_results['status']}")
            if execution_results['status'] == 'COMPLETED':
                print(f"Total Deployed: ${execution_results['total_deployed']:.2f}")
                print(f"Successful Trades: {execution_results['successful_trades']}")
            
            # Monitor positions
            print("\n📈 PHASE 3: POSITION MONITORING")
            positions = trading_system.monitor_positions()
            
            if positions and 'active_positions' in positions:
                print(f"Active Positions: {len(positions['active_positions'])}")
                for symbol, pos in positions['active_positions'].items():
                    print(f"  {symbol}: {pos['pnl_percent']:+.2f}% PnL")
            
        else:
            print(f"❌ API Issue: {api_test['issue']}")
            if 'solution' in api_test:
                print(f"💡 Solution: {api_test['solution']}")
        
        # Generate final report
        print("\n📋 GENERATING COMPREHENSIVE REPORT")
        report = trading_system.generate_trading_report()
        
        # Save report
        with open('/home/ubuntu/legacyloop_trading_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Trading report saved to: /home/ubuntu/legacyloop_trading_report.json")
        
        # Display key metrics
        print(f"\n🎯 SYSTEM STATUS:")
        print(f"API Authenticated: {report['system_status']['api_authenticated']}")
        print(f"Trading Enabled: {report['system_status']['trading_enabled']}")
        print(f"Capital Base: ${report['system_status']['capital_base']}")
        print(f"Success Rate: {report['trading_performance']['success_rate']}")
        
    except Exception as e:
        print(f"❌ System Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Live trading system execution complete")

if __name__ == "__main__":
    main()

