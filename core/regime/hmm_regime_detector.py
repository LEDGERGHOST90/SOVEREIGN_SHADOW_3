import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class RegimeHMMDetector:
    """
    REGIME: HMM Regime Detector Module
    Implements a Hidden Markov Model to detect different market regimes
    (e.g., bull, bear, volatile, sideways) based on price action and volatility.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.n_components = self.config.get("n_components", 3) # Number of hidden states (regimes)
        self.covariance_type = self.config.get("covariance_type", "diag") # "spherical", "diag", "full", "tied"
        self.n_iter = self.config.get("n_iter", 100)
        self.random_state = self.config.get("random_state", 42)
        self.hmm_model: Optional[hmm.GaussianHMM] = None
        self.scaler: Optional[StandardScaler] = None
        self.regime_names = self.config.get("regime_names", {0: "Bear", 1: "Sideways", 2: "Bull"})

        logger.info(f"REGIME HMM Detector initialized with {self.n_components} components.")

    def train_model(self, historical_data: pd.DataFrame):
        """
        Trains the HMM model using historical market data.
        `historical_data` should contain features like 'returns' and 'volatility'.
        Example features: log returns, rolling volatility.
        """
        if historical_data.empty:
            logger.error("Cannot train HMM model with empty historical data.")
            return

        # Prepare features for HMM (e.g., daily returns and a measure of volatility)
        # For this example, let's assume `historical_data` has a 'Close' column
        if 'Close' not in historical_data.columns:
            logger.error("Historical data must contain a 'Close' column for feature engineering.")
            return
        
        historical_data['returns'] = np.log(historical_data['Close'] / historical_data['Close'].shift(1))
        historical_data['volatility'] = historical_data['returns'].rolling(window=self.config.get("volatility_window", 20)).std()

        # Drop NaN values introduced by shift and rolling
        features = historical_data[['returns', 'volatility']].dropna()

        if features.empty:
            logger.error("Features are empty after dropping NaN. Not enough data to train.")
            return

        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features)

        self.hmm_model = hmm.GaussianHMM(n_components=self.n_components,
                                         covariance_type=self.covariance_type,
                                         n_iter=self.n_iter,
                                         random_state=self.random_state)
        try:
            self.hmm_model.fit(scaled_features)
            logger.info("HMM model trained successfully.")
        except Exception as e:
            logger.error(f"Error training HMM model: {e}")
            self.hmm_model = None

    def predict_regime(self, latest_data: pd.DataFrame) -> Optional[str]:
        """
        Predicts the current market regime based on the latest data.
        `latest_data` should be a DataFrame with the same features used for training.
        """
        if self.hmm_model is None or self.scaler is None:
            logger.warning("HMM model or scaler not trained. Cannot predict regime.")
            return "UNKNOWN_UNTRAINED"

        if latest_data.empty:
            logger.warning("Latest data is empty. Cannot predict regime.")
            return "UNKNOWN_EMPTY_DATA"

        # Ensure latest_data has 'Close' and calculate features
        if 'Close' not in latest_data.columns:
            logger.error("Latest data must contain a 'Close' column for feature engineering.")
            return "UNKNOWN_MISSING_CLOSE"

        latest_data['returns'] = np.log(latest_data['Close'] / latest_data['Close'].shift(1))
        latest_data['volatility'] = latest_data['returns'].rolling(window=self.config.get("volatility_window", 20)).std()

        features = latest_data[['returns', 'volatility']].dropna()
        
        if features.empty:
            logger.warning("Features for latest data are empty after dropping NaN. Cannot predict.")
            return "UNKNOWN_INSUFFICIENT_FEATURES"

        scaled_features = self.scaler.transform(features)

        try:
            # Predict the hidden states (regimes) for the given sequence
            hidden_states = self.hmm_model.predict(scaled_features)
            # The last predicted state is the most recent regime
            current_regime_index = hidden_states[-1]
            return self.regime_names.get(current_regime_index, f"Regime_{current_regime_index}")
        except Exception as e:
            logger.error(f"Error predicting regime: {e}")
            return "UNKNOWN_PREDICTION_ERROR"

# Example usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Generate some dummy historical data for demonstration
    np.random.seed(0)
    n_samples = 500
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    data = {
        'Close': np.cumsum(np.random.randn(n_samples)) + 100
    }
    historical_df = pd.DataFrame(data, index=dates)
    # Simulate a regime change
    historical_df.loc[historical_df.index > '2024-01-01', 'Close'] = (np.cumsum(np.random.randn(len(historical_df[historical_df.index > '2024-01-01'])) * 0.5) + 120)
    historical_df.loc[historical_df.index > '2024-06-01', 'Close'] = (np.cumsum(np.random.randn(len(historical_df[historical_df.index > '2024-06-01'])) * 1.5) + 110)
    
    # Add some noise
    historical_df['Close'] += np.random.randn(n_samples) * 0.5

    regime_detector = RegimeHMMDetector(config={
        "n_components": 3, # e.g., Bear, Sideways, Bull
        "volatility_window": 20,
        "regime_names": {0: "Bear", 1: "Sideways", 2: "Bull"}
    })

    print("\n--- Training HMM Model ---")
    regime_detector.train_model(historical_df.copy())

    print("\n--- Predicting Regimes ---")
    # Predict regime for a recent period
    recent_data = historical_df.tail(30).copy()
    predicted_regime = regime_detector.predict_regime(recent_data)
    print(f"Predicted current market regime: {predicted_regime}")

    # Simulate a new data point for prediction
    new_date = historical_df.index.max() + timedelta(days=1)
    new_close = historical_df['Close'].iloc[-1] * (1 + np.random.randn() * 0.005)
    new_data = pd.DataFrame({'Close': [new_close]}, index=[new_date])
    
    # Need enough data for rolling volatility in new_data, so combine with recent_data
    combined_data = pd.concat([historical_df.tail(20), new_data])

    predicted_new_regime = regime_detector.predict_regime(combined_data)
    print(f"Predicted regime for new data: {predicted_new_regime}")
