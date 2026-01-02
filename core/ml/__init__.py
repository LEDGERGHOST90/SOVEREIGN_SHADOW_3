"""
Machine Learning Module for SOVEREIGN_SHADOW_3
===============================================

FreqAI-inspired self-adaptive ML scaffold for crypto trading.

Key components:
- AdaptiveMLEngine: Self-retraining ML engine (<4h model age)
- FeatureEngineering: 100+ technical indicators from OHLCV
- OutlierDetector: IsolationForest-based anomaly detection
- ModelMetrics: Training performance tracking
- PredictionResult: Structured prediction outputs

Example:
    from core.ml import AdaptiveMLEngine, FeatureEngineering

    # Initialize engine
    engine = AdaptiveMLEngine(
        model_type='lightgbm',
        retrain_hours=4.0
    )

    # Train on OHLCV data
    metrics = engine.train(df)

    # Make predictions
    predictions = engine.predict(recent_df)

    for pred in predictions:
        print(f"Signal: {pred.signal}, Confidence: {pred.probability}")
"""

from .freqai_scaffold import AdaptFreqAIScaffold

# Alias for backwards compatibility
AdaptiveMLEngine = AdaptFreqAIScaffold

__all__ = [
    'AdaptFreqAIScaffold',
    'AdaptiveMLEngine',
]

__version__ = '1.0.0'
__author__ = 'AURORA (Claude)'
__date__ = 'December 2025'
