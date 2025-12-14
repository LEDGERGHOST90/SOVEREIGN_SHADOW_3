#!/usr/bin/env python3
"""
Integration Example: FreqAI ML Engine with SOVEREIGN_SHADOW_3
==============================================================

This example demonstrates how to integrate the FreqAI-inspired ML engine
with your existing trading system, agents, and council.

Author: AURORA (Claude)
Date: December 2025
Project: SOVEREIGN_SHADOW_3
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Note: These imports will work once dependencies are installed
# For now, this serves as a reference implementation

try:
    from core.ml import AdaptiveMLEngine, FeatureEngineering, create_sample_data
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML dependencies not installed. This is a reference implementation.")
    print("Install with: pip install -r requirements.txt")
    print()


class MLTradingSignalGenerator:
    """
    ML-powered signal generator for trading agents.

    Integrates FreqAI engine with SOVEREIGN_SHADOW_3 trading architecture.
    """

    def __init__(
        self,
        symbol: str = 'BTC/USD',
        retrain_hours: float = 4.0,
        model_dir: str = '/Volumes/LegacySafe/SS_III/models/ml',
        enable_auto_retrain: bool = True
    ):
        """
        Initialize ML signal generator.

        Args:
            symbol: Trading pair symbol
            retrain_hours: Hours between automatic retraining
            model_dir: Directory for model persistence
            enable_auto_retrain: Enable automatic retraining
        """
        self.symbol = symbol
        self.enable_auto_retrain = enable_auto_retrain

        if not ML_AVAILABLE:
            raise ImportError("ML dependencies not installed. Run: pip install -r requirements.txt")

        # Initialize ML engine
        self.engine = AdaptiveMLEngine(
            model_type='lightgbm',
            retrain_hours=retrain_hours,
            model_dir=Path(model_dir),
            enable_outlier_detection=True,
            enable_tensorboard=True
        )

        # Try to load existing model
        self._load_latest_model()

    def _load_latest_model(self):
        """Load the most recent model if available."""
        model_dir = self.engine.model_dir
        model_files = sorted(model_dir.glob('lightgbm_model_*.pkl'))

        if model_files:
            latest_model = model_files[-1]
            try:
                self.engine.load_model(latest_model)
                print(f"✓ Loaded model: {latest_model.name}")
                print(f"  Model age: {self.engine.get_model_age_hours():.2f} hours")
            except Exception as e:
                print(f"⚠️  Failed to load model {latest_model}: {e}")
        else:
            print("ℹ️  No existing model found. Train one with train_initial_model()")

    def train_initial_model(self, historical_data=None, lookback_days: int = 7):
        """
        Train initial model on historical data.

        Args:
            historical_data: DataFrame with OHLCV data (optional, will use sample data if None)
            lookback_days: Days of historical data to use

        Returns:
            ModelMetrics object
        """
        if historical_data is None:
            print(f"ℹ️  No historical data provided, using sample data...")
            historical_data = create_sample_data(n_samples=lookback_days * 24)

        print(f"Training model on {len(historical_data)} samples...")
        metrics = self.engine.train(
            historical_data,
            test_size=0.2,
            forward_periods=4
        )

        # Save model
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.engine.save_model(f'lightgbm_model_{timestamp}.pkl')

        print(f"✓ Training complete!")
        print(f"  Train accuracy: {metrics.train_accuracy:.4f}")
        print(f"  Val accuracy: {metrics.val_accuracy:.4f}")
        print(f"  Features: {metrics.feature_count}")

        return metrics

    def get_signal(self, current_data) -> Dict:
        """
        Get ML trading signal for current market data.

        Args:
            current_data: DataFrame with recent OHLCV candles (minimum 200 for all indicators)

        Returns:
            Dictionary with signal, confidence, and metadata
        """
        if self.engine.model is None:
            raise ValueError("Model not trained. Call train_initial_model() first.")

        # Generate prediction
        prediction = self.engine.predict(
            current_data.tail(1),
            auto_retrain=self.enable_auto_retrain
        )

        # Convert signal to action
        signal_map = {
            -1: 'SELL',
            0: 'HOLD',
            1: 'BUY'
        }

        return {
            'symbol': self.symbol,
            'action': signal_map[prediction.signal],
            'confidence': prediction.probability,
            'signal_value': prediction.signal,
            'model_age_hours': prediction.model_age_hours,
            'features_used': prediction.features_used,
            'timestamp': prediction.timestamp,
            'needs_retrain': self.engine.should_retrain()
        }

    def get_feature_importance(self, top_n: int = 20):
        """Get top important features from trained model."""
        return self.engine.get_feature_importance(top_n=top_n)


class CouncilMLIntegration:
    """
    Integration layer between ML engine and AI council voting system.
    """

    def __init__(self, symbols: List[str] = None):
        """
        Initialize council ML integration.

        Args:
            symbols: List of trading pairs to monitor
        """
        self.symbols = symbols or ['BTC/USD', 'ETH/USD', 'SOL/USD']
        self.ml_generators = {}

        # Create ML signal generator for each symbol
        for symbol in self.symbols:
            try:
                self.ml_generators[symbol] = MLTradingSignalGenerator(
                    symbol=symbol,
                    retrain_hours=4.0
                )
            except ImportError:
                print(f"⚠️  ML not available for {symbol}")

    def get_ml_vote(self, symbol: str, market_data) -> Dict:
        """
        Get ML vote for council decision.

        Args:
            symbol: Trading pair symbol
            market_data: Current market data

        Returns:
            Vote dictionary with action, weight, and metadata
        """
        if symbol not in self.ml_generators:
            return {
                'agent': 'ML_ENGINE',
                'vote': 'HOLD',
                'weight': 0.0,
                'reason': 'ML not available for this symbol'
            }

        ml_gen = self.ml_generators[symbol]
        signal = ml_gen.get_signal(market_data)

        return {
            'agent': 'ML_ENGINE',
            'vote': signal['action'],
            'weight': signal['confidence'],
            'confidence': signal['confidence'],
            'model_age': signal['model_age_hours'],
            'needs_retrain': signal['needs_retrain'],
            'reason': f"ML prediction with {signal['confidence']:.1%} confidence"
        }

    def aggregate_council_votes(self, symbol: str, market_data) -> Dict:
        """
        Aggregate votes from all council members including ML.

        This is a placeholder showing how to integrate ML with existing agents.

        Args:
            symbol: Trading pair
            market_data: Current market data

        Returns:
            Aggregated decision
        """
        votes = []

        # Get ML vote
        ml_vote = self.get_ml_vote(symbol, market_data)
        votes.append(ml_vote)

        # TODO: Add other agent votes
        # votes.append(aurora_vote)
        # votes.append(gio_vote)
        # votes.append(architect_vote)

        # Simple weighted average for demo
        total_weight = sum(v['weight'] for v in votes)
        if total_weight == 0:
            return {'action': 'HOLD', 'confidence': 0.0}

        # Map actions to numeric values
        action_values = {'SELL': -1, 'HOLD': 0, 'BUY': 1}
        weighted_sum = sum(
            action_values.get(v['vote'], 0) * v['weight']
            for v in votes
        )
        avg_signal = weighted_sum / total_weight

        # Convert back to action
        if avg_signal > 0.3:
            final_action = 'BUY'
        elif avg_signal < -0.3:
            final_action = 'SELL'
        else:
            final_action = 'HOLD'

        return {
            'action': final_action,
            'confidence': abs(avg_signal),
            'votes': votes,
            'total_agents': len(votes)
        }


def example_usage():
    """Demonstrate ML integration with trading system."""

    print("=" * 80)
    print("FreqAI ML Engine Integration Example")
    print("=" * 80)
    print()

    if not ML_AVAILABLE:
        print("This is a reference implementation.")
        print("Install dependencies to run: pip install -r requirements.txt")
        print()
        print("Expected workflow:")
        print("1. Initialize ML signal generator for each trading pair")
        print("2. Train initial models on historical data")
        print("3. Generate signals for current market conditions")
        print("4. Integrate ML votes with council decision system")
        print("5. Models automatically retrain every 4 hours")
        return

    # Example 1: Single symbol signal generation
    print("Example 1: Generate ML signal for BTC/USD")
    print("-" * 80)

    ml_gen = MLTradingSignalGenerator(
        symbol='BTC/USD',
        retrain_hours=4.0
    )

    # Train initial model (using sample data)
    print("Training initial model...")
    ml_gen.train_initial_model()
    print()

    # Generate signal
    sample_data = create_sample_data(n_samples=200)
    signal = ml_gen.get_signal(sample_data)

    print("ML Signal:")
    print(f"  Action: {signal['action']}")
    print(f"  Confidence: {signal['confidence']:.2%}")
    print(f"  Model age: {signal['model_age_hours']:.2f}h")
    print(f"  Needs retrain: {signal['needs_retrain']}")
    print()

    # Feature importance
    print("Top 10 Important Features:")
    importance = ml_gen.get_feature_importance(top_n=10)
    for idx, row in importance.iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.6f}")
    print()

    # Example 2: Council integration
    print("=" * 80)
    print("Example 2: Council Integration")
    print("-" * 80)

    council = CouncilMLIntegration(symbols=['BTC/USD', 'ETH/USD'])

    # Get council decision
    decision = council.aggregate_council_votes('BTC/USD', sample_data)

    print("Council Decision:")
    print(f"  Final Action: {decision['action']}")
    print(f"  Confidence: {decision['confidence']:.2%}")
    print(f"  Total Agents: {decision['total_agents']}")
    print()
    print("  Individual Votes:")
    for vote in decision['votes']:
        print(f"    {vote['agent']:15s}: {vote['vote']:4s} (weight: {vote['weight']:.2%})")
    print()

    print("=" * 80)
    print("Integration Complete!")
    print()
    print("Next steps:")
    print("1. Replace sample_data with real market data from Coinbase/Binance")
    print("2. Add other council agents (AURORA, GIO, ARCHITECT_PRIME)")
    print("3. Set up cron job for automatic retraining every 4 hours")
    print("4. Monitor performance via TensorBoard")
    print("5. Backtest strategy with historical data")
    print("=" * 80)


if __name__ == '__main__':
    example_usage()
