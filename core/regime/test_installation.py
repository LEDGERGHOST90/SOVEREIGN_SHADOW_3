#!/usr/bin/env python3
"""
Quick test to verify HMM Regime Detector installation

Run this after installing dependencies to verify everything works.

Usage:
    python test_installation.py
"""

import sys

print("=" * 80)
print("HMM REGIME DETECTOR - INSTALLATION TEST")
print("=" * 80)
print()

# Test 1: Check Python version
print("Test 1: Python Version")
print("-" * 80)
print(f"Python {sys.version}")
if sys.version_info < (3, 8):
    print("ERROR: Python 3.8+ required")
    sys.exit(1)
print("✓ PASS")
print()

# Test 2: Import dependencies
print("Test 2: Import Dependencies")
print("-" * 80)

try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except ImportError as e:
    print(f"✗ numpy: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"✓ pandas {pd.__version__}")
except ImportError as e:
    print(f"✗ pandas: {e}")
    sys.exit(1)

try:
    import sklearn
    print(f"✓ scikit-learn {sklearn.__version__}")
except ImportError as e:
    print(f"✗ scikit-learn: {e}")
    sys.exit(1)

try:
    import hmmlearn
    print(f"✓ hmmlearn {hmmlearn.__version__}")
except ImportError as e:
    print(f"✗ hmmlearn: {e}")
    print("\nInstall with: pip install hmmlearn")
    sys.exit(1)

print()

# Test 3: Import module
print("Test 3: Import HMM Module")
print("-" * 80)

try:
    from core.regime.hmm_regime_detector import (
        HMMRegimeDetector,
        RegimeType,
        TradingRules
    )
    print("✓ HMMRegimeDetector imported")
    print("✓ RegimeType imported")
    print("✓ TradingRules imported")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

print()

# Test 4: Create detector instance
print("Test 4: Create Detector Instance")
print("-" * 80)

try:
    detector = HMMRegimeDetector(
        n_states=3,
        lookback_window=20,
        vol_threshold=0.02,
        transition_threshold=0.3
    )
    print("✓ Detector instance created")
    print(f"  States: {detector.n_states}")
    print(f"  Lookback: {detector.lookback_window}")
    print(f"  Vol threshold: {detector.vol_threshold}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 5: Generate sample data
print("Test 5: Generate Sample Data")
print("-" * 80)

try:
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    price = 50000
    prices = []

    for _ in range(100):
        price *= (1 + np.random.randn() * 0.01)
        prices.append(price)

    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.005 for p in prices],
        'low': [p * 0.995 for p in prices],
        'close': prices,
        'volume': np.random.uniform(1e9, 5e9, 100)
    }, index=dates)

    print(f"✓ Generated {len(df)} samples")
    print(f"  Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 6: Train model
print("Test 6: Train Model")
print("-" * 80)

try:
    detector.fit(df)
    print("✓ Model trained successfully")
    print(f"  Fitted: {detector.is_fitted}")
    print(f"  States mapped: {len(detector.state_volatility_map)}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 7: Predict regime
print("Test 7: Predict Regime")
print("-" * 80)

try:
    regime, metadata = detector.predict_regime(df.tail(30))
    print(f"✓ Regime prediction successful")
    print(f"  Current regime: {regime.value}")
    print(f"  State: {metadata['state']}")
    print(f"  Confidence: {metadata['max_probability']:.2%}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 8: Get trading rules
print("Test 8: Get Trading Rules")
print("-" * 80)

try:
    rules = detector.get_trading_rules(regime)
    print("✓ Trading rules generated")
    print(f"  Allow long: {rules.allow_long}")
    print(f"  Allow short: {rules.allow_short}")
    print(f"  Position multiplier: {rules.position_size_multiplier}x")
    print(f"  Pause trading: {rules.pause_trading}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 9: Model persistence
print("Test 9: Model Persistence")
print("-" * 80)

try:
    import tempfile
    import os

    # Save to temp file
    temp_dir = tempfile.gettempdir()
    temp_model = os.path.join(temp_dir, 'test_hmm_model.pkl')

    detector.save_model(temp_model)
    print(f"✓ Model saved to {temp_model}")

    # Load model
    detector2 = HMMRegimeDetector()
    detector2.load_model(temp_model)
    print("✓ Model loaded successfully")

    # Verify
    regime2, metadata2 = detector2.predict_regime(df.tail(30))
    print(f"✓ Loaded model predicts: {regime2.value}")

    # Cleanup
    os.remove(temp_model)
    print("✓ Temp file cleaned up")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Test 10: Regime history
print("Test 10: Regime History (Backtesting)")
print("-" * 80)

try:
    history = detector.get_regime_history(df)
    print(f"✓ Regime history generated")
    print(f"  Periods: {len(history)}")

    regime_counts = history['regime'].value_counts()
    print("  Distribution:")
    for regime_name, count in regime_counts.items():
        pct = (count / len(history)) * 100
        print(f"    {regime_name}: {count} ({pct:.1f}%)")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Summary
print("=" * 80)
print("INSTALLATION TEST COMPLETE")
print("=" * 80)
print()
print("✓ All tests passed!")
print()
print("Your HMM Regime Detector is ready to use.")
print()
print("Next steps:")
print("  1. Fetch 4 years of real BTC OHLCV data")
print("  2. Train production model")
print("  3. Integrate into trading system")
print("  4. Set up weekly retraining")
print()
print("See QUICK_START.md for integration examples.")
print("=" * 80)
