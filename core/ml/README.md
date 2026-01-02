# FreqAI-Inspired Self-Adaptive ML Scaffold

**Created:** December 2025
**Author:** AURORA (Claude)
**Project:** SOVEREIGN_SHADOW_3

## Overview

This module implements a FreqAI-inspired self-adaptive machine learning engine for crypto trading, based on the critical insight that **models should be <4 hours old for optimal performance** in fast-moving crypto markets.

Unlike traditional "train once, deploy forever" approaches, this engine implements continuous retraining to address model decay.

## Key Features

### 1. Self-Adaptive Retraining
- Automatic model retraining on configurable intervals (default: 4 hours)
- Model age tracking and staleness detection
- Addresses model decay in volatile crypto markets

### 2. Advanced Feature Engineering
- 100+ technical indicators from OHLCV data
- **Momentum Indicators:** RSI (7, 14, 21), MACD, Stochastic, ROC, Williams %R
- **Volatility Indicators:** Bollinger Bands (20, 50), ATR (7, 14, 21), Historical Volatility
- **Trend Indicators:** SMA/EMA (7-200 periods), ADX, MA Crossovers
- **Volume Indicators:** OBV, VPT, MFI, Volume Ratios
- **Pattern Features:** Candlestick patterns, body/shadow analysis
- **Time Features:** Cyclical hour/day encoding

### 3. Outlier Detection
- IsolationForest-based anomaly detection
- Automatic filtering of outliers from training data
- Configurable contamination threshold (default: 5%)

### 4. Multiple Model Support
- **LightGBM** (primary, production-ready)
- **XGBoost** (production-ready)
- **CatBoost** (production-ready)
- **PyTorch LSTM** (scaffold ready)
- **RL Agents:** PPO, A2C, DQN (scaffold ready)

### 5. Model Persistence & Monitoring
- Save/load models with metadata
- Training metrics history tracking
- TensorBoard integration for visualization
- Feature importance analysis

## Installation

### Basic Installation (Required)

```bash
cd /Volumes/LegacySafe/SS_III/core/ml
pip install -r requirements.txt
```

### Core Dependencies

```bash
pip install numpy pandas scikit-learn
pip install lightgbm xgboost catboost
```

### Optional Dependencies

```bash
# For LSTM/RL agents (future)
pip install torch tensorboard

# For advanced indicators (requires C library)
# brew install ta-lib  # macOS
# pip install ta-lib
```

## Quick Start

### Example 1: Basic Training and Prediction

```python
from core.ml import AdaptiveMLEngine, create_sample_data

# Create sample OHLCV data
df = create_sample_data(n_samples=1000)

# Initialize engine
engine = AdaptiveMLEngine(
    model_type='lightgbm',
    retrain_hours=4.0,
    enable_outlier_detection=True
)

# Train model
metrics = engine.train(df, test_size=0.2)
print(f"Validation Accuracy: {metrics.val_accuracy:.4f}")

# Make predictions
predictions = engine.predict(df.tail(5))
for pred in predictions:
    signal_name = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}[pred.signal]
    print(f"Signal: {signal_name}, Confidence: {pred.probability:.2%}")
```

### Example 2: Integration with Live Trading

```python
from core.ml import AdaptiveMLEngine
import pandas as pd

# Initialize engine
engine = AdaptiveMLEngine(
    model_type='lightgbm',
    retrain_hours=4.0,
    model_dir='/Volumes/LegacySafe/SS_III/models'
)

# Load existing model or train new one
try:
    engine.load_model('models/latest_model.pkl')
except FileNotFoundError:
    # Train initial model
    historical_df = fetch_historical_data()  # Your data fetch function
    engine.train(historical_df)
    engine.save_model('models/latest_model.pkl')

# Generate signal for current market
current_candle = fetch_current_candle()  # Your data fetch function
prediction = engine.predict(current_candle, auto_retrain=True)

if prediction.signal == 1:
    print(f"BUY signal with {prediction.probability:.2%} confidence")
    # Execute buy order
elif prediction.signal == -1:
    print(f"SELL signal with {prediction.probability:.2%} confidence")
    # Execute sell order
else:
    print("HOLD - no action")
```

### Example 3: Feature Engineering Only

```python
from core.ml import FeatureEngineering
import pandas as pd

# Load your OHLCV data
df = pd.read_csv('btc_usdt_1h.csv')

# Generate all features
df_with_features = FeatureEngineering.generate_all_features(df)

print(f"Original columns: {len(df.columns)}")
print(f"With features: {len(df_with_features.columns)}")

# Get feature importance from trained model
feature_importance = engine.get_feature_importance(top_n=20)
print(feature_importance)
```

### Example 4: Scheduled Retraining (Cron Job)

```python
#!/usr/bin/env python3
"""
Scheduled retraining script for FreqAI engine.
Add to crontab: 0 */4 * * * /path/to/retrain.py
"""

from core.ml import AdaptiveMLEngine
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_model():
    # Load engine
    engine = AdaptiveMLEngine(
        model_type='lightgbm',
        retrain_hours=4.0,
        model_dir='/Volumes/LegacySafe/SS_III/models'
    )

    # Fetch fresh data
    fresh_data = fetch_last_7_days_data()  # Your implementation

    # Train
    metrics = engine.train(fresh_data)
    logger.info(f"Retraining complete: val_acc={metrics.val_accuracy:.4f}")

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    engine.save_model(f'lightgbm_model_{timestamp}.pkl')
    engine.save_model('latest_model.pkl')  # Always keep latest

if __name__ == '__main__':
    retrain_model()
```

## API Reference

### AdaptiveMLEngine

**Constructor:**
```python
AdaptiveMLEngine(
    model_type='lightgbm',        # 'lightgbm', 'xgboost', 'catboost'
    retrain_hours=4.0,             # Hours between retraining
    data_lookback_hours=168,       # Data window (default: 7 days)
    model_dir=None,                # Directory for model persistence
    enable_outlier_detection=True, # Use IsolationForest
    enable_tensorboard=False,      # TensorBoard logging
    random_state=42                # Reproducibility seed
)
```

**Methods:**

- `train(df, target_col=None, test_size=0.2, forward_periods=4)` - Train/retrain model
- `predict(df, auto_retrain=True, return_probabilities=True)` - Generate predictions
- `should_retrain()` - Check if model needs retraining
- `save_model(filename=None)` - Persist model to disk
- `load_model(filepath)` - Load model from disk
- `get_feature_importance(top_n=20)` - Get top features
- `close()` - Clean up resources

### FeatureEngineering

**Static Methods:**

- `generate_all_features(df)` - Generate all 100+ features
- `add_returns(df)` - Price returns (1h, 4h, 24h, 7d, log)
- `add_momentum_indicators(df)` - RSI, MACD, Stochastic, ROC, Williams %R
- `add_volatility_indicators(df)` - Bollinger Bands, ATR, Historical Vol
- `add_trend_indicators(df)` - Moving averages, ADX, crossovers
- `add_volume_indicators(df)` - OBV, VPT, MFI, volume ratios
- `add_pattern_features(df)` - Candlestick patterns
- `add_time_features(df)` - Cyclical time encoding

### ModelMetrics

**Attributes:**
- `timestamp` - Training timestamp (ISO format)
- `train_accuracy` - Training set accuracy
- `val_accuracy` - Validation set accuracy
- `feature_count` - Number of features used
- `sample_count` - Number of training samples
- `training_duration_seconds` - Training time
- `model_type` - Model type used

### PredictionResult

**Attributes:**
- `signal` - Trading signal: -1 (sell), 0 (hold), 1 (buy)
- `probability` - Confidence score [0, 1]
- `timestamp` - Prediction timestamp (ISO format)
- `model_age_hours` - Model age in hours
- `features_used` - Number of features in prediction

## Integration with SOVEREIGN_SHADOW_3

### Trading Agent Integration

```python
# In your trading agent (e.g., core/agents/aurora.py)
from core.ml import AdaptiveMLEngine

class AuroraAgent:
    def __init__(self):
        self.ml_engine = AdaptiveMLEngine(
            model_type='lightgbm',
            retrain_hours=4.0
        )

    def get_ml_signal(self, market_data):
        """Get ML-based trading signal."""
        prediction = self.ml_engine.predict(
            market_data,
            auto_retrain=True
        )

        return {
            'action': prediction.signal,
            'confidence': prediction.probability,
            'model_age': prediction.model_age_hours
        }
```

### Council Integration

```python
# In council voting system
def council_vote(market_data):
    votes = []

    # ML Signal
    ml_prediction = ml_engine.predict(market_data)
    votes.append({
        'agent': 'ML_ENGINE',
        'vote': ml_prediction.signal,
        'weight': ml_prediction.probability
    })

    # Other agents...
    # GIO analysis, technical indicators, etc.

    return aggregate_votes(votes)
```

## Performance Considerations

### Model Age Threshold

The default 4-hour threshold is based on FreqAI research for crypto markets. Adjust based on:

- **More volatile markets:** Decrease to 2-3 hours
- **Stable markets:** Increase to 6-8 hours
- **Backtesting results:** Optimize based on your strategy

### Feature Selection

100+ features can lead to overfitting. Consider:

1. Use `get_feature_importance()` to identify top features
2. Remove low-importance features
3. Test with 20-50 most important features

### Training Data Window

Default: 168 hours (7 days). Adjust based on:

- **Short-term trading:** 24-72 hours
- **Swing trading:** 168-336 hours (7-14 days)
- **Position trading:** 720+ hours (30+ days)

### Computational Requirements

- **LightGBM:** Fastest, recommended for production
- **XGBoost:** Slightly slower, sometimes more accurate
- **CatBoost:** Slowest, good for categorical features
- **LSTM/RL:** Requires GPU, significantly slower

## Monitoring & Debugging

### TensorBoard Visualization

```bash
# Enable TensorBoard in engine
engine = AdaptiveMLEngine(enable_tensorboard=True)

# Start TensorBoard server
tensorboard --logdir /Volumes/LegacySafe/SS_III/core/ml/models/tensorboard_logs

# Open browser: http://localhost:6006
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Train with verbose output
engine.train(df)  # Will log feature counts, outliers, accuracy, etc.
```

### Model Persistence

Models are saved with complete metadata:

```python
# Save
engine.save_model('my_model.pkl')

# Saved data includes:
# - Trained model
# - Feature scaler
# - Feature names
# - Training timestamp
# - Metrics history
# - Outlier detector (if enabled)

# Load and inspect
loaded_engine = AdaptiveMLEngine()
loaded_engine.load_model('my_model.pkl')
print(f"Model age: {loaded_engine.get_model_age_hours():.2f}h")
print(f"Features: {len(loaded_engine.feature_names)}")
```

## Roadmap

### Implemented
- ✅ LightGBM, XGBoost, CatBoost support
- ✅ 100+ feature engineering pipeline
- ✅ Outlier detection (IsolationForest)
- ✅ Automatic retraining logic
- ✅ Model persistence
- ✅ TensorBoard integration
- ✅ Feature importance analysis

### Planned (Scaffolding Ready)
- ⏳ PyTorch LSTM implementation
- ⏳ RL agents (PPO, A2C, DQN)
- ⏳ Multi-model ensemble voting
- ⏳ Hyperparameter optimization (Optuna)
- ⏳ Walk-forward optimization
- ⏳ Real-time data pipeline integration
- ⏳ Backtesting framework
- ⏳ Paper trading integration

## Troubleshooting

### ImportError: No module named 'lightgbm'

```bash
pip install lightgbm xgboost catboost scikit-learn
```

### Model accuracy is low (<60%)

1. Check data quality (sufficient samples, no gaps)
2. Adjust signal thresholds in `_generate_targets()`
3. Increase `data_lookback_hours` for more training data
4. Try different `forward_periods` for signal generation
5. Enable outlier detection
6. Experiment with different model types

### Model not retraining automatically

Check `should_retrain()` logic:

```python
print(f"Model age: {engine.get_model_age_hours():.2f}h")
print(f"Threshold: {engine.retrain_hours}h")
print(f"Should retrain: {engine.should_retrain()}")
```

### Memory issues with large datasets

1. Reduce `data_lookback_hours`
2. Use sample subset for training: `df.sample(frac=0.5)`
3. Reduce feature count (remove low-importance features)
4. Use LightGBM instead of XGBoost/CatBoost

## Testing

Run the included example:

```bash
cd /Volumes/LegacySafe/SS_III/core/ml
python freqai_scaffold.py
```

Expected output:
- Sample data generation
- Feature engineering (100+ features)
- Model training (LightGBM)
- Validation accuracy metrics
- Feature importance ranking
- Sample predictions
- Model persistence

## Contributing

This module is part of SOVEREIGN_SHADOW_3. For improvements:

1. Test changes with backtesting data
2. Maintain backward compatibility with saved models
3. Document new features in this README
4. Update version in `__init__.py`

## License

Part of SOVEREIGN_SHADOW_3 trading system.
© 2025 memphis | AURORA (Claude)

## Contact

- System: SOVEREIGN_SHADOW_3
- Location: /Volumes/LegacySafe/SS_III/
- Website: sovereignnshadowii.abacusai.app
- Notifications: ntfy.sh/sovereignshadow_dc4d2fa1

---

**Remember:** This is a self-adaptive system. Models retrain automatically. Always monitor model age and performance metrics.
