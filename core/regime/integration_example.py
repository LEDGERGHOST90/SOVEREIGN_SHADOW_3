"""
HMM Regime Detector - Integration Example

This script demonstrates how to integrate the HMM Regime Detector
into the SOVEREIGN_SHADOW_3 trading system.

Author: SOVEREIGN_SHADOW_3
Created: 2025-12-14
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append('/Volumes/LegacySafe/SS_III')

from core.regime.hmm_regime_detector import HMMRegimeDetector, RegimeType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegimeAwareTrader:
    """
    Example trader that uses HMM regime detection to adapt strategies
    """

    def __init__(
        self,
        model_path: str = "/Volumes/LegacySafe/SS_III/core/regime/models/btc_model.pkl",
        base_position_size: float = 100.0,  # Base USD position size
        max_position_size: float = 500.0    # Max USD position size
    ):
        self.model_path = model_path
        self.base_position_size = base_position_size
        self.max_position_size = max_position_size

        # Initialize regime detector
        self.detector = HMMRegimeDetector()

        # Load or train model
        self._initialize_model()

        logger.info("RegimeAwareTrader initialized")

    def _initialize_model(self):
        """Load existing model or prompt for training"""
        if os.path.exists(self.model_path):
            logger.info(f"Loading model from {self.model_path}")
            self.detector.load_model(self.model_path)
        else:
            logger.warning("No trained model found. Need to train first.")
            logger.warning(f"Expected path: {self.model_path}")
            logger.warning("Use train_model() method with historical data")

    def train_model(self, ohlcv_data: pd.DataFrame, save: bool = True):
        """
        Train HMM model on historical data

        Args:
            ohlcv_data: DataFrame with OHLCV columns
            save: Save model after training
        """
        logger.info(f"Training model on {len(ohlcv_data)} samples")

        # Train
        self.detector.fit(ohlcv_data)

        # Save if requested
        if save:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.detector.save_model(self.model_path)
            logger.info(f"Model saved to {self.model_path}")

    def evaluate_trade_signal(
        self,
        signal: str,
        current_ohlcv: pd.DataFrame,
        strategy_confidence: float = 1.0
    ) -> dict:
        """
        Evaluate a trade signal using regime detection

        Args:
            signal: 'BUY', 'SELL', or 'HOLD'
            current_ohlcv: Recent OHLCV data (needs >= 20 rows)
            strategy_confidence: Confidence from trading strategy (0-1)

        Returns:
            dict with decision, position_size, and metadata
        """
        # Predict current regime
        regime, metadata = self.detector.predict_regime(current_ohlcv)
        rules = self.detector.get_trading_rules(regime)

        # Build response
        response = {
            'regime': regime.value,
            'regime_metadata': metadata,
            'original_signal': signal,
            'modified_signal': signal,
            'allow_trade': True,
            'position_size': 0.0,
            'reason': ''
        }

        # Check if trading should be paused
        if rules.pause_trading:
            response['allow_trade'] = False
            response['modified_signal'] = 'HOLD'
            response['reason'] = f"Trading paused - {regime.value}"
            logger.warning(f"Trade blocked: {response['reason']}")
            return response

        # Check if signal matches allowed directions
        if signal == 'BUY' and not rules.allow_long:
            response['allow_trade'] = False
            response['modified_signal'] = 'HOLD'
            response['reason'] = f"Long trades not allowed in {regime.value}"
            logger.info(f"Trade modified: {response['reason']}")
            return response

        if signal == 'SELL' and not rules.allow_short:
            response['allow_trade'] = False
            response['modified_signal'] = 'HOLD'
            response['reason'] = f"Short trades not allowed in {regime.value}"
            logger.info(f"Trade modified: {response['reason']}")
            return response

        # Calculate position size with regime adjustment
        base_size = self.base_position_size * strategy_confidence
        adjusted_size = base_size * rules.position_size_multiplier

        # Cap at max position size
        final_size = min(adjusted_size, self.max_position_size)

        response['position_size'] = final_size
        response['reason'] = f"Trade approved in {regime.value}"

        logger.info(
            f"Trade approved: {signal} ${final_size:.2f} "
            f"(regime multiplier: {rules.position_size_multiplier}x)"
        )

        return response

    def check_retrain(self, full_historical_data: pd.DataFrame) -> bool:
        """
        Check if model needs retraining and retrain if necessary

        Args:
            full_historical_data: Complete OHLCV history

        Returns:
            True if retrained, False otherwise
        """
        if self.detector.should_retrain():
            logger.info("Model needs retraining")
            self.detector.retrain(full_historical_data)

            # Save retrained model
            self.detector.save_model(self.model_path)
            logger.info("Model retrained and saved")
            return True

        logger.info("Model is up to date")
        return False

    def get_regime_status(self) -> dict:
        """Get current regime status"""
        return {
            'current_regime': self.detector.current_regime.value,
            'previous_regime': self.detector.previous_regime.value,
            'is_fitted': self.detector.is_fitted,
            'last_train_date': str(self.detector.last_train_date),
            'should_retrain': self.detector.should_retrain()
        }


def example_trading_loop():
    """
    Example trading loop with regime detection
    """
    print("=" * 80)
    print("REGIME-AWARE TRADING LOOP EXAMPLE")
    print("=" * 80)

    # Initialize trader
    trader = RegimeAwareTrader(
        base_position_size=100.0,
        max_position_size=500.0
    )

    # Generate sample data (in practice, fetch from exchange)
    print("\nGenerating sample OHLCV data...")
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
    price = 50000  # BTC starting price

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

    # Train model if not already trained
    if not trader.detector.is_fitted:
        print("\nTraining model on sample data...")
        trader.train_model(df)

    # Simulate trading signals
    print("\n" + "=" * 80)
    print("SIMULATING TRADE SIGNALS")
    print("=" * 80)

    signals = [
        ('BUY', 0.9),   # High confidence buy
        ('BUY', 0.5),   # Low confidence buy
        ('SELL', 0.8),  # High confidence sell
        ('HOLD', 1.0)   # Hold signal
    ]

    for signal, confidence in signals:
        print(f"\n{'=' * 80}")
        print(f"Signal: {signal} (confidence: {confidence:.1%})")
        print("=" * 80)

        # Evaluate signal
        decision = trader.evaluate_trade_signal(
            signal=signal,
            current_ohlcv=df.tail(30),  # Last 30 periods
            strategy_confidence=confidence
        )

        # Display results
        print(f"\nRegime: {decision['regime']}")
        print(f"Allow Trade: {decision['allow_trade']}")
        print(f"Modified Signal: {decision['modified_signal']}")
        print(f"Position Size: ${decision['position_size']:.2f}")
        print(f"Reason: {decision['reason']}")

        # Show regime details
        metadata = decision['regime_metadata']
        print(f"\nRegime Details:")
        print(f"  State: {metadata['state']}")
        print(f"  Confidence: {metadata['max_probability']:.2%}")
        print(f"  Is Transition: {metadata['is_transition']}")

    # Check regime status
    print("\n" + "=" * 80)
    print("REGIME STATUS")
    print("=" * 80)
    status = trader.get_regime_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    # Check if retrain needed
    print("\n" + "=" * 80)
    print("RETRAIN CHECK")
    print("=" * 80)
    needs_retrain = trader.detector.should_retrain()
    print(f"Needs retrain: {needs_retrain}")

    if needs_retrain:
        print("\nRetraining would be triggered here with full historical data")

    print("\n" + "=" * 80)
    print("INTEGRATION EXAMPLE COMPLETE")
    print("=" * 80)


def integration_with_existing_bot():
    """
    Example showing integration with existing trading bot
    """
    print("\n" + "=" * 80)
    print("INTEGRATION WITH EXISTING BOT")
    print("=" * 80)

    example_code = """
# In your existing trading bot (e.g., /Volumes/LegacySafe/SS_III/launch_autonomous.py):

from core.regime.integration_example import RegimeAwareTrader

# Initialize regime-aware trader
regime_trader = RegimeAwareTrader(
    base_position_size=50.0,  # December campaign: max $50/position
    max_position_size=50.0
)

# In your main trading loop:
def execute_strategy():
    # Your existing signal generation
    signal = generate_trading_signal()  # Returns 'BUY', 'SELL', or 'HOLD'
    confidence = calculate_signal_confidence()  # Returns 0-1

    # Fetch recent OHLCV data
    ohlcv_data = exchange.fetch_ohlcv(
        symbol='BTC/USD',
        timeframe='1h',
        limit=50
    )
    df = pd.DataFrame(
        ohlcv_data,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )

    # Evaluate signal with regime detection
    decision = regime_trader.evaluate_trade_signal(
        signal=signal,
        current_ohlcv=df,
        strategy_confidence=confidence
    )

    # Execute if allowed
    if decision['allow_trade'] and decision['modified_signal'] != 'HOLD':
        position_size = decision['position_size']

        # Apply December campaign rules
        position_size = min(position_size, 50.0)  # Max $50

        execute_trade(
            side=decision['modified_signal'],
            size=position_size,
            stop_loss=0.03,   # 3%
            take_profit=0.05  # 5%
        )

        logger.info(f"Trade executed: {decision['modified_signal']} ${position_size}")
    else:
        logger.info(f"Trade blocked: {decision['reason']}")

# Periodic retraining (e.g., weekly cron)
def weekly_maintenance():
    # Fetch full 4-year history
    historical_data = fetch_historical_ohlcv(days=1460)

    # Check and retrain if needed
    regime_trader.check_retrain(historical_data)
    """

    print(example_code)


if __name__ == "__main__":
    # Check if hmmlearn is installed
    try:
        import hmmlearn
        print("hmmlearn installed: OK")
    except ImportError:
        print("ERROR: hmmlearn not installed")
        print("Install with: pip install hmmlearn")
        sys.exit(1)

    # Run example trading loop
    example_trading_loop()

    # Show integration example
    integration_with_existing_bot()

    print("\n" + "=" * 80)
    print("To use in production:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Train model with real historical data")
    print("3. Integrate into launch_autonomous.py")
    print("4. Set up weekly retraining cron job")
    print("=" * 80)
