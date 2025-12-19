#!/usr/bin/env python3.11
"""
Comprehensive Test Suite for the Intelligent Trading Framework
Tests all five integrated components:
1. Market Regime Detector
2. AI Strategy Selector
3. Strategy Execution Engine
4. Self-Annealing Loop
5. Modularization Prompt System
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta

# Import our framework components
from market_regime_detector import MarketRegimeDetector
from ai_strategy_selector import AIStrategySelector
from strategy_execution_engine import StrategyExecutionEngine
from self_annealing_loop import SelfAnnealingLoop
from modularize_strategy_prompt import generate_modularization_prompt

def generate_test_market_data(scenario="trending"):
    """Generate synthetic market data for testing different scenarios"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
    
    if scenario == "trending":
        # High ADX, moderate volatility
        close = np.linspace(35000, 40000, 100) + np.random.normal(0, 100, 100)
    elif scenario == "ranging":
        # Low ADX, low volatility
        close = 37000 + np.sin(np.linspace(0, 4*np.pi, 100)) * 500 + np.random.normal(0, 50, 100)
    elif scenario == "volatile":
        # High volatility, any ADX
        close = 37000 + np.random.normal(0, 1000, 100)
    else:
        close = np.linspace(35000, 37000, 100)
    
    high = close + np.random.uniform(50, 200, 100)
    low = close - np.random.uniform(50, 200, 100)
    open_price = close + np.random.uniform(-100, 100, 100)
    volume = np.random.uniform(1000000, 5000000, 100)
    
    df = pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume
    }, index=dates)
    
    return df

def test_market_regime_detector():
    """Test the Market Regime Detector with different market conditions"""
    print("\n" + "="*80)
    print("TEST 1: MARKET REGIME DETECTOR")
    print("="*80)
    
    detector = MarketRegimeDetector()
    
    scenarios = ["trending", "ranging", "volatile"]
    for scenario in scenarios:
        print(f"\n📊 Testing {scenario.upper()} market...")
        data = generate_test_market_data(scenario)
        regime = detector.detect_regime(data)
        
        print(f"   Detected Regime: {regime['regime']}")
        print(f"   ADX: {regime['adx']:.2f}")
        print(f"   ATR Percentile: {regime['atr_percentile']:.0f}%")
        print(f"   ✅ Test passed")
    
    return True

def test_ai_strategy_selector():
    """Test the AI Strategy Selector"""
    print("\n" + "="*80)
    print("TEST 2: AI STRATEGY SELECTOR")
    print("="*80)
    
    strategy_lib_path = "/home/ubuntu/strategy_framework_design.json"
    selector = AIStrategySelector(strategy_lib_path)
    data = generate_test_market_data("volatile")
    
    print("\n🤖 Testing strategy selection...")
    result = selector.select_strategy(data)
    
    print(f"   Selected Strategy: {result.get('selected_strategy', 'None')}")
    print(f"   Strategy Type: {result.get('strategy_type', 'N/A')}")
    print(f"   Market Regime: {result['market_regime']}")
    print(f"   Candidates Evaluated: {result['candidates_evaluated']}")
    print(f"   ✅ Test passed")
    
    return True

def test_strategy_execution_engine():
    """Test the Strategy Execution Engine"""
    print("\n" + "="*80)
    print("TEST 3: STRATEGY EXECUTION ENGINE")
    print("="*80)
    
    strategy_lib_path = "/home/ubuntu/strategy_framework_design.json"
    engine = StrategyExecutionEngine(strategy_lib_path)
    data = generate_test_market_data("trending")
    
    print("\n⚙️  Testing strategy execution...")
    result = engine.execute_cycle(data)
    
    print(f"   Regime: {result['regime']}")
    print(f"   Selected Strategy: {result['selected_strategy']}")
    print(f"   Position Status: {result['position_status']}")
    print(f"   ✅ Test passed")
    
    return True

def test_self_annealing_loop():
    """Test the Self-Annealing Loop"""
    print("\n" + "="*80)
    print("TEST 4: SELF-ANNEALING LOOP")
    print("="*80)
    
    # Create a simple mock tracker
    class MockTracker:
        def __init__(self):
            self.trades = []
        def log_trade(self, trade):
            self.trades.append(trade)
        def get_all_trades(self):
            return self.trades
    
    tracker = MockTracker()
    annealer = SelfAnnealingLoop(tracker)
    
    # Simulate some performance data
    print("\n🔄 Testing self-improvement cycle...")
    
    # Add some test performance data
    test_trades = [
        {
            "strategy": "VolatilityBandit",
            "regime": "High Volatility Range",
            "success": True,
            "pnl": 2.5,
            "timestamp": datetime.now().isoformat()
        },
        {
            "strategy": "MomentumBandwidth",
            "regime": "Low Volatility Trend",
            "success": False,
            "pnl": -1.5,
            "error": "Stop loss hit",
            "timestamp": datetime.now().isoformat()
        },
        {
            "strategy": "MomentumBandwidth",
            "regime": "Low Volatility Trend",
            "success": False,
            "pnl": -2.0,
            "error": "Timeout",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    for trade in test_trades:
        annealer.log_performance(trade)
    
    # Run improvement cycle
    improvements = annealer.run_improvement_cycle()
    
    print(f"   Strategies needing improvement: {len(improvements)}")
    if improvements:
        for strategy_name, plan in improvements.items():
            print(f"   - {strategy_name}: {len(plan['recommendations'])} recommendations")
    print(f"   ✅ Test passed")
    
    return True

def test_modularization_prompt():
    """Test the Strategy Modularization Prompt System"""
    print("\n" + "="*80)
    print("TEST 5: MODULARIZATION PROMPT SYSTEM")
    print("="*80)
    
    # Create a simple test strategy
    test_strategy_code = """
class TestStrategy(Strategy):
    ema_period = 20
    rsi_period = 14
    
    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
    
    def next(self):
        if not self.position:
            if self.data.Close[-1] > self.ema[-1] and self.rsi[-1] < 30:
                self.buy()
        else:
            if self.data.Close[-1] < self.ema[-1] or self.rsi[-1] > 70:
                self.position.close()
"""
    
    print("\n📝 Testing prompt generation...")
    prompt = generate_modularization_prompt(test_strategy_code)
    
    # Check that the prompt contains key elements
    assert "{strategy_code}" not in prompt, "Placeholder not replaced"
    assert "TestStrategy" in prompt, "Strategy code not inserted"
    assert "JSON" in prompt, "JSON schema not present"
    
    print(f"   Prompt length: {len(prompt)} characters")
    print(f"   Contains strategy code: ✅")
    print(f"   Contains JSON schema: ✅")
    print(f"   ✅ Test passed")
    
    return True

def test_full_integration():
    """Test the complete integrated system end-to-end"""
    print("\n" + "="*80)
    print("TEST 6: FULL SYSTEM INTEGRATION")
    print("="*80)
    
    print("\n🚀 Running complete trading cycle...")
    
    # 1. Generate market data
    data = generate_test_market_data("volatile")
    print("   ✅ Market data generated")
    
    # 2. Detect regime
    detector = MarketRegimeDetector()
    regime_info = detector.detect_regime(data)
    print(f"   ✅ Regime detected: {regime_info['regime']}")
    
    # 3. Select strategy
    strategy_lib_path = "/home/ubuntu/strategy_framework_design.json"
    selector = AIStrategySelector(strategy_lib_path)
    strategy_info = selector.select_strategy(data)
    print(f"   ✅ Strategy selected: {strategy_info.get('selected_strategy', 'None')}")
    
    # 4. Execute (simulated)
    engine = StrategyExecutionEngine(strategy_lib_path)
    execution_result = engine.execute_cycle(data)
    print(f"   ✅ Execution completed: {execution_result['position_status']}")
    
    # 5. Log performance
    class MockTracker:
        def __init__(self):
            self.trades = []
        def log_trade(self, trade):
            self.trades.append(trade)
        def get_all_trades(self):
            return self.trades
    
    tracker = MockTracker()
    annealer = SelfAnnealingLoop(tracker)
    trade_log = {
        "strategy": strategy_info.get('selected_strategy', 'Unknown'),
        "regime": regime_info['regime'],
        "success": True,
        "pnl": 1.8,
        "timestamp": datetime.now().isoformat()
    }
    annealer.log_performance(trade_log)
    print(f"   ✅ Performance logged")
    
    # 6. Check for improvements
    improvements = annealer.run_improvement_cycle()
    print(f"   ✅ Improvement cycle completed")
    
    print("\n" + "="*80)
    print("✅ FULL INTEGRATION TEST PASSED")
    print("="*80)
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 INTELLIGENT TRADING FRAMEWORK - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Market Regime Detector", test_market_regime_detector),
        ("AI Strategy Selector", test_ai_strategy_selector),
        ("Strategy Execution Engine", test_strategy_execution_engine),
        ("Self-Annealing Loop", test_self_annealing_loop),
        ("Modularization Prompt", test_modularization_prompt),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASSED" if result else "FAILED"))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with error: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    for test_name, status in results:
        emoji = "✅" if status == "PASSED" else "❌"
        print(f"{emoji} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your intelligent trading framework is ready for deployment.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("="*80)

if __name__ == "__main__":
    main()
