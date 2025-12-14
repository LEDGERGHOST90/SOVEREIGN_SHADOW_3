# FreqAI ML Engine - Quick Start Guide

**5-Minute Setup for SOVEREIGN_SHADOW_3**

---

## Step 1: Install Dependencies (2 minutes)

```bash
cd /Volumes/LegacySafe/SS_III/core/ml
pip install -r requirements.txt
```

**Minimal Installation (just LightGBM):**
```bash
pip install numpy pandas scikit-learn lightgbm
```

**Full Installation (all models + TensorBoard):**
```bash
pip install numpy pandas scikit-learn
pip install lightgbm xgboost catboost
pip install torch tensorboard
```

---

## Step 2: Test Installation (1 minute)

```bash
# Run the example
python freqai_scaffold.py
```

**Expected output:**
- Sample data generation (1000 candles)
- Feature engineering (100+ features)
- Model training with LightGBM
- Validation accuracy: ~60-70%
- Top 10 feature importance
- 5 sample predictions
- Model saved to disk

---

## Step 3: First Prediction (2 minutes)

### Option A: Quick Test with Sample Data

```python
from core.ml import AdaptiveMLEngine, create_sample_data

# Create sample data
df = create_sample_data(n_samples=500)

# Train model
engine = AdaptiveMLEngine(model_type='lightgbm', retrain_hours=4.0)
metrics = engine.train(df)

# Make prediction
prediction = engine.predict(df.tail(1))
print(f"Signal: {prediction.signal}")  # -1=SELL, 0=HOLD, 1=BUY
print(f"Confidence: {prediction.probability:.2%}")
```

### Option B: Use Your Own OHLCV Data

```python
from core.ml import AdaptiveMLEngine
import pandas as pd

# Load your OHLCV data
df = pd.read_csv('btc_usdt_1h.csv')  # Must have: timestamp, open, high, low, close, volume

# Train model
engine = AdaptiveMLEngine(model_type='lightgbm', retrain_hours=4.0)
metrics = engine.train(df)

# Get latest signal
current_signal = engine.predict(df.tail(1))

if current_signal.signal == 1:
    print(f"BUY signal with {current_signal.probability:.1%} confidence")
elif current_signal.signal == -1:
    print(f"SELL signal with {current_signal.probability:.1%} confidence")
else:
    print("HOLD - no clear signal")
```

---

## Step 4: Integration with Trading (Optional)

### Integrate with Your Trading Agent

```python
# In your trading agent (e.g., core/agents/aurora.py)
from core.ml import AdaptiveMLEngine

class YourTradingAgent:
    def __init__(self):
        self.ml_engine = AdaptiveMLEngine(
            model_type='lightgbm',
            retrain_hours=4.0,
            model_dir='/Volumes/LegacySafe/SS_III/models/ml'
        )

        # Load or train initial model
        try:
            self.ml_engine.load_model('models/latest_btc_model.pkl')
        except FileNotFoundError:
            historical_data = self.fetch_historical_data()
            self.ml_engine.train(historical_data)
            self.ml_engine.save_model('models/latest_btc_model.pkl')

    def decide_trade(self, market_data):
        # Get ML signal
        ml_signal = self.ml_engine.predict(market_data, auto_retrain=True)

        # Use in your decision logic
        if ml_signal.signal == 1 and ml_signal.probability > 0.65:
            return 'BUY'
        elif ml_signal.signal == -1 and ml_signal.probability > 0.65:
            return 'SELL'
        else:
            return 'HOLD'
```

---

## Common Use Cases

### Use Case 1: Get Daily Signals

```python
from core.ml import AdaptiveMLEngine
from datetime import datetime

# Load trained model
engine = AdaptiveMLEngine()
engine.load_model('models/btc_model.pkl')

# Get current market data (your implementation)
current_candles = fetch_last_200_candles('BTC/USD')

# Get signal
signal = engine.predict(current_candles)

print(f"[{datetime.now()}] BTC/USD Signal: {signal.signal}")
print(f"Confidence: {signal.probability:.1%}")
print(f"Model age: {signal.model_age_hours:.1f}h")
```

### Use Case 2: Automatic Retraining Every 4 Hours

Create `retrain.py`:

```python
#!/usr/bin/env python3
from core.ml import AdaptiveMLEngine

# Load engine
engine = AdaptiveMLEngine(model_type='lightgbm', retrain_hours=4.0)

# Fetch fresh 7-day data
fresh_data = fetch_last_7_days('BTC/USD')  # Your implementation

# Train
metrics = engine.train(fresh_data)
print(f"Retrained! Val accuracy: {metrics.val_accuracy:.4f}")

# Save
engine.save_model('models/latest_btc_model.pkl')
```

Add to crontab:
```bash
# Retrain every 4 hours
0 */4 * * * cd /Volumes/LegacySafe/SS_III && python3 core/ml/retrain.py >> logs/ml_retrain.log 2>&1
```

### Use Case 3: Multi-Symbol Trading

```python
from core.ml import AdaptiveMLEngine

symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
engines = {}

# Create engine for each symbol
for symbol in symbols:
    engines[symbol] = AdaptiveMLEngine(
        model_type='lightgbm',
        retrain_hours=4.0
    )

    # Load or train
    try:
        engines[symbol].load_model(f'models/{symbol.replace("/", "_")}_model.pkl')
    except FileNotFoundError:
        data = fetch_historical(symbol, days=7)
        engines[symbol].train(data)
        engines[symbol].save_model(f'models/{symbol.replace("/", "_")}_model.pkl')

# Get signals for all symbols
for symbol in symbols:
    current_data = fetch_current(symbol)
    signal = engines[symbol].predict(current_data)
    print(f"{symbol}: {signal.signal} (conf: {signal.probability:.1%})")
```

---

## Monitoring with TensorBoard

Enable TensorBoard logging:

```python
engine = AdaptiveMLEngine(
    model_type='lightgbm',
    enable_tensorboard=True
)
```

Start TensorBoard server:

```bash
tensorboard --logdir /Volumes/LegacySafe/SS_III/core/ml/models/tensorboard_logs
```

Open browser: http://localhost:6006

View:
- Training/validation accuracy over time
- Model age tracking
- Feature count evolution

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'lightgbm'"

**Solution:**
```bash
pip install lightgbm
```

### Issue: Low accuracy (<50%)

**Solutions:**
1. Increase training data: Use more historical candles
2. Adjust signal thresholds in code (default: 2% price change)
3. Try different model: `model_type='xgboost'` or `model_type='catboost'`
4. Enable outlier detection: `enable_outlier_detection=True`

### Issue: Model not retraining automatically

**Check:**
```python
print(f"Model age: {engine.get_model_age_hours():.2f}h")
print(f"Retrain threshold: {engine.retrain_hours}h")
print(f"Should retrain: {engine.should_retrain()}")
```

**Solution:** Set `auto_retrain=True` in predict():
```python
prediction = engine.predict(data, auto_retrain=True)
```

### Issue: Predictions too slow

**Solutions:**
1. Use LightGBM (fastest): `model_type='lightgbm'`
2. Reduce features: Use only top 30 important features
3. Reduce training data: `data_lookback_hours=72` instead of 168

---

## Performance Tips

### Optimize for Speed

```python
engine = AdaptiveMLEngine(
    model_type='lightgbm',  # Fastest model
    retrain_hours=6.0,      # Retrain less frequently
    enable_outlier_detection=False,  # Skip outlier detection
    enable_tensorboard=False  # Disable logging
)
```

### Optimize for Accuracy

```python
engine = AdaptiveMLEngine(
    model_type='catboost',  # Most accurate (but slower)
    retrain_hours=2.0,      # Retrain more frequently
    data_lookback_hours=336,  # Use 14 days of data
    enable_outlier_detection=True
)
```

### Optimize for Balanced Performance

```python
engine = AdaptiveMLEngine(
    model_type='lightgbm',
    retrain_hours=4.0,      # FreqAI recommended
    data_lookback_hours=168,  # 7 days
    enable_outlier_detection=True,
    enable_tensorboard=True
)
```

---

## Next Steps

1. **Backtest:** Test on historical data before live trading
2. **Paper Trade:** Run in paper trading mode for 1-2 weeks
3. **Monitor:** Track model performance and retrain frequency
4. **Optimize:** Tune `forward_periods` and signal thresholds based on results
5. **Scale:** Add more symbols and ensemble multiple models

---

## File Structure

```
/Volumes/LegacySafe/SS_III/core/ml/
├── freqai_scaffold.py        # Main ML engine (984 lines)
├── __init__.py                # Module exports
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
├── FREQAI_QUICKSTART.md      # This file
├── integration_example.py    # Council integration examples
├── test_structure.py         # Structure verification
└── models/                   # Saved models (auto-created)
    └── tensorboard_logs/     # TensorBoard logs (auto-created)
```

---

## Support

- **Full Documentation:** See README.md
- **Integration Examples:** See integration_example.py
- **Code Reference:** See freqai_scaffold.py docstrings

---

**Remember:** Models retrain automatically every 4 hours. This is the FreqAI way - fresh models for fresh markets!

**Happy Trading!**
