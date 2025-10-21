#!/usr/bin/env python3
"""
🧪 Test Trading API Client

Test all endpoints of the Sovereign Shadow Trading API.

Usage:
    python3 scripts/test_trading_api.py --host localhost --port 8000
    python3 scripts/test_trading_api.py --test all
    python3 scripts/test_trading_api.py --test health
    python3 scripts/test_trading_api.py --test websocket

Part of the Sovereign Shadow Trading System
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

try:
    import requests
    import websockets
except ImportError:
    print("⚠️ Required packages not installed. Run:")
    print("pip install requests websockets")
    sys.exit(1)


class TradingAPITester:
    """Test client for the Trading API"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}"
        self.host = host
        self.port = port
        
        print("="*70)
        print("🧪 Sovereign Shadow Trading API - Test Client")
        print("="*70)
        print(f"Base URL: {self.base_url}")
        print(f"WebSocket URL: {self.ws_url}")
        print("="*70)
        print()
    
    def test_health(self):
        """Test health check endpoint"""
        print("🏥 Testing Health Check...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health Check Passed")
                print(f"   Status: {data['status']}")
                print(f"   Uptime: {data['uptime_seconds']:.1f} seconds")
                print(f"   Active Strategies: {data['active_strategies']}")
                print(f"   Risk Gate: {data['risk_gate_status']}")
                print(f"   Session P&L: ${data['session_pnl']:.2f}")
                if data.get('aave_health_factor'):
                    print(f"   Aave HF: {data['aave_health_factor']:.2f}")
                return True
            else:
                print(f"❌ Health Check Failed: HTTP {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("\n💡 Make sure the API server is running:")
            print("   ./bin/START_API_SERVER.sh")
            return False
    
    def test_strategy_performance(self):
        """Test strategy performance endpoint"""
        print("\n📊 Testing Strategy Performance...")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/strategy/performance",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Strategy Performance Retrieved")
                print(f"   Total Profit: ${data['total_profit']:.2f}")
                print(f"   Total Trades: {data['total_trades']}")
                print(f"   Session Start: {data['session_start']}")
                
                print(f"\n   Strategies ({len(data['strategies'])}):")
                for strategy in data['strategies']:
                    print(f"   - {strategy['name']}")
                    print(f"     Type: {strategy['type']}")
                    print(f"     Trades: {strategy['total_trades']}")
                    print(f"     Profit: ${strategy['total_profit']:.2f}")
                    print(f"     Success Rate: {strategy['success_rate']*100:.1f}%")
                    print(f"     Avg Execution: {strategy['avg_execution_time']:.0f}ms")
                    print(f"     Status: {strategy['status']}")
                
                return True
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            return False
    
    def test_trade_execution(self, mode: str = "paper"):
        """Test trade execution endpoint"""
        print(f"\n💸 Testing Trade Execution (mode: {mode})...")
        
        payload = {
            "strategy": "Cross-Exchange Arbitrage",
            "pair": "BTC/USD",
            "amount": 25.0,
            "exchanges": ["coinbase", "okx"],
            "side": "auto",
            "mode": mode
        }
        
        print(f"   Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/trade/execute",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Trade Executed")
                print(f"   Trade ID: {data['trade_id']}")
                print(f"   Status: {data['status']}")
                print(f"   Profit: ${data.get('profit', 0):.2f}")
                print(f"   Execution Time: {data.get('execution_time', 0):.3f}s")
                print(f"   Timestamp: {data['timestamp']}")
                
                if data.get('validation_warnings'):
                    print("\n   Warnings:")
                    for warning in data['validation_warnings']:
                        print(f"   {warning}")
                
                if data.get('risk_adjustments'):
                    adj = data['risk_adjustments']
                    print("\n   Risk Adjustments:")
                    print(f"   Original Amount: ${adj['original_amount']:.2f}")
                    print(f"   Adjusted Amount: ${adj['adjusted_amount']:.2f}")
                    print(f"   Size Multiplier: {adj['size_multiplier']:.2f}×")
                    print(f"   Stop Loss: {adj['stop_loss_bps']} bps")
                
                return True
            
            elif response.status_code == 400:
                error = response.json()
                print("❌ Trade Rejected (Risk Gate)")
                print(f"   Reason: {error['detail']['reason']}")
                if error['detail'].get('warnings'):
                    print("   Warnings:")
                    for warning in error['detail']['warnings']:
                        print(f"   {warning}")
                return False
            
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            return False
    
    def test_dashboard_update(self):
        """Test dashboard update endpoint"""
        print("\n📡 Testing Dashboard Update...")
        
        payload = {
            "event": "trade_completed",
            "data": {
                "trade_id": f"test_trade_{int(time.time())}",
                "profit": 2.50,
                "strategy": "arbitrage",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
        
        print(f"   Request: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/dashboard/update",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Dashboard Updated")
                print(f"   Success: {data['success']}")
                print(f"   Dashboard Updated: {data['dashboard_updated']}")
                print(f"   Timestamp: {data['timestamp']}")
                return True
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            return False
    
    async def test_websocket(self, duration: int = 10):
        """Test WebSocket connection"""
        print(f"\n🔌 Testing WebSocket Connection (duration: {duration}s)...")
        
        try:
            uri = f"{self.ws_url}/ws/dashboard"
            print(f"   Connecting to: {uri}")
            
            async with websockets.connect(uri) as websocket:
                # Receive connection message
                message = await websocket.recv()
                data = json.loads(message)
                print("✅ WebSocket Connected")
                print(f"   Event: {data['event']}")
                print(f"   Data: {json.dumps(data['data'], indent=2)}")
                
                # Send ping
                print("\n   Sending ping...")
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Receive pong
                message = await websocket.recv()
                data = json.loads(message)
                print(f"   Received: {data}")
                
                # Request stats
                print("\n   Requesting stats...")
                await websocket.send(json.dumps({"type": "request_stats"}))
                
                # Listen for updates
                print(f"\n   Listening for updates ({duration}s)...")
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0
                        )
                        data = json.loads(message)
                        print(f"   📨 Received: {data['event']}")
                        
                        if data['event'] == 'stats_update':
                            stats = data['data']
                            print(f"      Session P&L: ${stats.get('session_pnl_usd', 0):.2f}")
                            print(f"      Open Trades: {stats.get('open_trades', 0)}")
                            print(f"      Total Trades: {stats.get('total_trades', 0)}")
                        
                        elif data['event'] == 'trade_completed':
                            trade = data['data']
                            print(f"      Trade: {trade.get('trade_id', 'unknown')}")
                            print(f"      Profit: ${trade.get('profit', 0):.2f}")
                    
                    except asyncio.TimeoutError:
                        continue
                
                print("\n✅ WebSocket Test Complete")
                return True
        
        except Exception as e:
            print(f"❌ WebSocket Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("🚀 Running All Tests")
        print("="*70 + "\n")
        
        results = []
        
        # REST API tests
        results.append(("Health Check", self.test_health()))
        results.append(("Strategy Performance", self.test_strategy_performance()))
        results.append(("Trade Execution", self.test_trade_execution("paper")))
        results.append(("Dashboard Update", self.test_dashboard_update()))
        
        # WebSocket test
        print("\n💡 Starting WebSocket test in 3 seconds...")
        time.sleep(3)
        ws_result = asyncio.run(self.test_websocket(duration=10))
        results.append(("WebSocket", ws_result))
        
        # Summary
        print("\n" + "="*70)
        print("📋 Test Summary")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:10} {test_name}")
        
        print("="*70)
        print(f"Results: {passed}/{total} tests passed")
        print("="*70)
        
        return passed == total


def main():
    parser = argparse.ArgumentParser(
        description="🧪 Test Sovereign Shadow Trading API"
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='API server host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--test',
        choices=['all', 'health', 'performance', 'execute', 'dashboard', 'websocket'],
        default='all',
        help='Which test to run (default: all)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['paper', 'test', 'live'],
        default='paper',
        help='Trade execution mode (default: paper)'
    )
    
    args = parser.parse_args()
    
    tester = TradingAPITester(host=args.host, port=args.port)
    
    # Run selected test
    if args.test == 'all':
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    
    elif args.test == 'health':
        success = tester.test_health()
    
    elif args.test == 'performance':
        success = tester.test_strategy_performance()
    
    elif args.test == 'execute':
        success = tester.test_trade_execution(mode=args.mode)
    
    elif args.test == 'dashboard':
        success = tester.test_dashboard_update()
    
    elif args.test == 'websocket':
        success = asyncio.run(tester.test_websocket(duration=10))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

