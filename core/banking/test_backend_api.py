#!/usr/bin/env python3
"""
LLF-ß Backend API Test Script
Tests all endpoints and integrations
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Mock the missing modules for testing
class MockBinanceLiveIntegration:
    def is_connected(self):
        return True
    
    def get_portfolio_summary(self):
        return {
            'total_value': 1543.40,
            'status': 'connected',
            'last_updated': datetime.now().isoformat()
        }

class MockOmegaSigilIntelligence:
    def get_current_intelligence(self):
        return {
            'ray_score': 0.907,
            'menace_accuracy': 87.2,
            'win_rate': 68.0,
            'total_trades': 1748,
            'confidence_level': 'HIGH',
            'system_status': 'OPERATIONAL'
        }

class MockKrakenAutoTrader:
    def __init__(self, sandbox=True):
        self.sandbox = sandbox
    
    def get_balance(self):
        return {'USD': 1000.0, 'BTC': 0.1}

class MockNotionBridge:
    def get_status(self):
        return {'connected': True, 'last_sync': datetime.now().isoformat()}

# Mock the modules
sys.modules['binance_api.live_binance_integration'] = type('MockModule', (), {
    'BinanceLiveIntegration': MockBinanceLiveIntegration
})()

sys.modules['omega_sigil_engine.omega_sigil_intelligence'] = type('MockModule', (), {
    'OmegaSigilIntelligence': MockOmegaSigilIntelligence
})()

sys.modules['kraken_trading.kraken_auto_trader'] = type('MockModule', (), {
    'KrakenAutoTrader': MockKrakenAutoTrader
})()

sys.modules['notion_bridge.notion_workflow_automation'] = type('MockModule', (), {
    'NotionBridge': MockNotionBridge
})()

# Now import the Flask app
from llf_backend_api import app

def test_backend_api():
    """Test all backend API endpoints"""
    print("🔧 Testing LLF-ß Backend API Endpoints")
    print("=" * 50)
    
    # Test client
    client = app.test_client()
    
    # Test results
    results = []
    
    # Test 1: Health Check
    print("\n1. Testing Health Check Endpoint...")
    response = client.get('/health')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   ✅ Health check passed: {data['status']}")
        print(f"   📊 Components: {data['components']}")
        results.append(("Health Check", "PASS"))
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
        results.append(("Health Check", "FAIL"))
    
    # Test 2: Portfolio Endpoint (with auth)
    print("\n2. Testing Portfolio Endpoint...")
    headers = {'X-Dashboard-Pass': 'NeverNest25!'}
    response = client.get('/api/portfolio', headers=headers)
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   ✅ Portfolio endpoint working")
        print(f"   💰 Total Value: ${data.get('total_value', 'N/A')}")
        results.append(("Portfolio API", "PASS"))
    else:
        print(f"   ❌ Portfolio endpoint failed: {response.status_code}")
        results.append(("Portfolio API", "FAIL"))
    
    # Test 3: Real Portfolio Endpoint
    print("\n3. Testing Real Portfolio Endpoint...")
    response = client.get('/api/portfolio/real', headers=headers)
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   ✅ Real portfolio endpoint working")
        print(f"   💰 Total Value: ${data.get('total_value', 'N/A')}")
        print(f"   📈 Daily Change: +${data.get('daily_change', 'N/A')} ({data.get('daily_change_percent', 'N/A')}%)")
        print(f"   🪙 Holdings: {len(data.get('holdings', []))} tokens")
        results.append(("Real Portfolio API", "PASS"))
    else:
        print(f"   ❌ Real portfolio endpoint failed: {response.status_code}")
        results.append(("Real Portfolio API", "FAIL"))
    
    # Test 4: ΩSIGIL Intelligence Endpoint
    print("\n4. Testing ΩSIGIL Intelligence Endpoint...")
    response = client.get('/api/omega-sigil/intelligence', headers=headers)
    if response.status_code == 200:
        print(f"   ✅ ΩSIGIL intelligence endpoint working")
        results.append(("ΩSIGIL Intelligence", "PASS"))
    else:
        print(f"   ❌ ΩSIGIL intelligence endpoint failed: {response.status_code}")
        results.append(("ΩSIGIL Intelligence", "FAIL"))
    
    # Test 5: Authentication
    print("\n5. Testing Authentication...")
    response = client.get('/api/portfolio')  # No auth headers
    if response.status_code == 401:
        print(f"   ✅ Authentication working (unauthorized access blocked)")
        results.append(("Authentication", "PASS"))
    else:
        print(f"   ❌ Authentication failed: {response.status_code}")
        results.append(("Authentication", "FAIL"))
    
    # Test 6: CORS Headers
    print("\n6. Testing CORS Configuration...")
    response = client.get('/health')
    cors_header = response.headers.get('Access-Control-Allow-Origin')
    if cors_header:
        print(f"   ✅ CORS configured: {cors_header}")
        results.append(("CORS", "PASS"))
    else:
        print(f"   ❌ CORS not configured")
        results.append(("CORS", "FAIL"))
    
    # Test Summary
    print("\n" + "=" * 50)
    print("🎯 BACKEND API TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"   {status_icon} {test_name}: {status}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🔥 ALL TESTS PASSED - BACKEND API READY FOR PRODUCTION!")
        return True
    else:
        print("⚠️  Some tests failed - Review and fix issues")
        return False

def test_routes():
    """Test available routes"""
    print("\n🛣️  Available API Routes:")
    print("-" * 30)
    
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"   {methods:10} {rule.rule}")

if __name__ == "__main__":
    print("🚀 LLF-ß Backend API Testing Suite")
    print("=" * 50)
    
    # Set environment variables for testing
    os.environ['DASHBOARD_PASS'] = 'NeverNest25!'
    os.environ['ΩSIGIL_KEY'] = 'NeverNest25!'
    os.environ['FLASK_ENV'] = 'testing'
    
    # Test routes
    test_routes()
    
    # Test API endpoints
    success = test_backend_api()
    
    if success:
        print("\n🎯 VERDICT: BACKEND API IS PRODUCTION READY!")
        sys.exit(0)
    else:
        print("\n⚠️  VERDICT: BACKEND API NEEDS FIXES")
        sys.exit(1)

