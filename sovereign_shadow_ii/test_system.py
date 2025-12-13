#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - SYSTEM TEST

Tests all components end-to-end in FAKE mode
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🏴 SOVEREIGN SHADOW II - SYSTEM TEST")
print("="*70)

# Test 1: Imports
print("\n📦 TEST 1: Checking dependencies...")
try:
    import pandas as pd
    import numpy as np
    print("   ✅ pandas installed")
    print("   ✅ numpy installed")
except ImportError as e:
    print(f"   ❌ Missing dependency: {e}")
    print("\n   Install with: pip install pandas numpy")
    sys.exit(1)

# Test 2: Regime Detector
print("\n🔍 TEST 2: Testing Regime Detector...")
try:
    from core.intelligence.regime_detector import MarketRegimeDetector, MarketRegime
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    trend = np.linspace(90000, 100000, 100)
    noise = np.random.normal(0, 500, 100)
    close_prices = trend + noise
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices - 100,
        'high': close_prices + 200,
        'low': close_prices - 200,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    detector = MarketRegimeDetector()
    result = detector.detect_regime(df)
    
    print(f"   ✅ Regime Detected: {result.regime.value}")
    print(f"   ✅ Confidence: {result.confidence:.1f}%")
    
except Exception as e:
    print(f"   ❌ Regime Detector failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Performance Tracker
print("\n💾 TEST 3: Testing Performance Tracker...")
try:
    from core.intelligence.performance_tracker import PerformanceTracker, TradeRecord
    from datetime import datetime
    
    tracker = PerformanceTracker(db_path="data/test_system.db")
    
    # Log a test trade
    trade = TradeRecord(
        trade_id="TEST_001",
        strategy_name="ElderReversion",
        regime="choppy_volatile",
        symbol="BTC/USDT",
        entry_time=datetime.now(),
        exit_time=datetime.now(),
        entry_price=99000,
        exit_price=100000,
        position_size=0.01,
        pnl=100,
        pnl_percent=1.01,
        exit_reason="take_profit",
        market_context={}
    )
    
    tracker.log_trade(trade)
    
    # Get performance
    performance = tracker.get_strategy_performance("ElderReversion", "choppy_volatile")
    
    if performance:
        print(f"   ✅ Performance Tracker working")
        print(f"   ✅ Logged trade: ${performance[0].total_pnl:.2f} PnL")
    
    tracker.close()
    
except Exception as e:
    print(f"   ❌ Performance Tracker failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Strategy Selector
print("\n🎯 TEST 4: Testing Strategy Selector...")
try:
    from core.intelligence.strategy_selector import StrategySelector
    from core.intelligence.regime_detector import RegimeAnalysis
    
    tracker = PerformanceTracker(db_path="data/test_system.db")
    selector = StrategySelector(tracker)
    
    # Mock regime
    regime_analysis = RegimeAnalysis(
        regime=MarketRegime.CHOPPY_VOLATILE,
        confidence=75.0,
        indicators={},
        timestamp=datetime.now(),
        reasoning="Test"
    )
    
    recommendation = selector.select_strategy(regime_analysis)
    
    print(f"   ✅ Strategy Selected: {recommendation.strategy_name}")
    print(f"   ✅ Confidence: {recommendation.confidence:.1f}%")
    
    tracker.close()
    
except Exception as e:
    print(f"   ❌ Strategy Selector failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Strategy Modules
print("\n⚙️  TEST 5: Testing Strategy Modules...")
try:
    # Test Elder Reversion
    sys.path.insert(0, str(Path(__file__).parent / "strategies" / "modularized"))
    
    from elder_reversion.entry import ElderReversionEntry
    from elder_reversion.exit import ElderReversionExit
    from elder_reversion.risk import ElderReversionRisk
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='1H')
    prices = np.linspace(99000, 99500, 50) + np.random.normal(0, 100, 50)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [p - 50 for p in prices],
        'high': [p + 100 for p in prices],
        'low': [p - 100 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, 50)
    })
    
    # Test entry
    entry = ElderReversionEntry()
    signal = entry.generate_signal(df)
    print(f"   ✅ Elder Reversion Entry: {signal.signal}")
    
    # Test exit
    exit_module = ElderReversionExit()
    exit_signal = exit_module.generate_signal(df, 99000)
    print(f"   ✅ Elder Reversion Exit: {exit_signal.signal}")
    
    # Test risk
    risk = ElderReversionRisk()
    sizing = risk.calculate_position_size(10000, 99000, 500, 75)
    print(f"   ✅ Elder Reversion Risk: ${sizing.position_value_usd:.2f} position")
    
except Exception as e:
    print(f"   ❌ Strategy Modules failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Orchestrator (Discovery only, not full run)
print("\n🎼 TEST 6: Testing Orchestrator...")
try:
    from core.orchestrator import SovereignShadowOrchestrator
    
    orchestrator = SovereignShadowOrchestrator(
        exchange_name="coinbase",
        mode="FAKE",
        portfolio_value=10000
    )
    
    status = orchestrator.get_status()
    
    print(f"   ✅ Orchestrator initialized")
    print(f"   ✅ Mode: {status['mode']}")
    print(f"   ✅ Portfolio: ${status['portfolio_value']:,.2f}")
    print(f"   ✅ Strategies available: {status['available_strategies']}")
    
except Exception as e:
    print(f"   ❌ Orchestrator failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ SYSTEM TEST COMPLETE")
print("="*70)
print("\n💡 Next Steps:")
print("   1. Review test results above")
print("   2. Fix any failures")
print("   3. Configure .env file")
print("   4. Run: python core/orchestrator.py")
print("\n" + "="*70 + "\n")
