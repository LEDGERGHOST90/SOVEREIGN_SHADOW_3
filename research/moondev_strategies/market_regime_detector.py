#!/usr/bin/env python3.11
"""
Market Regime Detector
Analyzes market data to determine the current trading regime
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class MarketRegimeDetector:
    """
    Detects market regime based on ADX and ATR percentile.
    
    Regimes:
    - High Volatility Trend: ADX > 25, ATR Percentile > 70%
    - Low Volatility Trend: ADX > 25, ATR Percentile < 30%
    - High Volatility Range: ADX < 20, ATR Percentile > 70%
    - Low Volatility Range: ADX < 20, ATR Percentile < 30%
    - Transitioning Market: ADX 20-25, ATR Percentile 30-70%
    """
    
    def __init__(self, data_path: str = None, adx_period: int = 14, atr_period: int = 14, atr_lookback: int = 100):
        """
        Initialize the detector.
        
        Args:
            data_path: Path to CSV data file
            adx_period: Period for ADX calculation
            atr_period: Period for ATR calculation
            atr_lookback: Lookback period for ATR percentile calculation
        """
        self.adx_period = adx_period
        self.atr_period = atr_period
        self.atr_lookback = atr_lookback
        self.df = None
        
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, data_path: str):
        """Load market data from CSV"""
        self.df = pd.read_csv(data_path)
        # Clean column names
        self.df.columns = self.df.columns.str.strip().str.lower()
        return self.df
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()
        return atr
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Average Directional Index"""
        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculate ATR for normalization
        atr = self.calculate_atr(high, low, close)
        
        # Calculate smoothed +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=self.adx_period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.adx_period).mean() / atr)
        
        # Calculate DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        
        # Calculate ADX (smoothed DX)
        adx = dx.rolling(window=self.adx_period).mean()
        
        return adx
    
    def calculate_atr_percentile(self, atr: pd.Series) -> pd.Series:
        """Calculate ATR percentile rank over lookback period"""
        def percentile_rank(series):
            if len(series) < 2:
                return 50.0
            return (series.rank(pct=True).iloc[-1]) * 100
        
        atr_percentile = atr.rolling(window=self.atr_lookback).apply(percentile_rank, raw=False)
        return atr_percentile
    
    def detect_regime(self, df: pd.DataFrame) -> Tuple[str, Dict]:
        """
        Detect the current market regime.
        
        Args:
            df: DataFrame with columns ['High', 'Low', 'Close'] or ['high', 'low', 'close']
        
        Returns:
            Tuple of (regime_name, regime_metrics)
        """
        # Normalize column names
        df_normalized = df.copy()
        df_normalized.columns = df_normalized.columns.str.capitalize()
        
        # Calculate indicators
        atr = self.calculate_atr(df_normalized['High'], df_normalized['Low'], df_normalized['Close'])
        adx = self.calculate_adx(df_normalized['High'], df_normalized['Low'], df_normalized['Close'])
        atr_percentile = self.calculate_atr_percentile(atr)
        
        # Get latest values
        current_adx = adx.iloc[-1]
        current_atr_percentile = atr_percentile.iloc[-1]
        
        # Determine regime
        if current_adx > 25:
            if current_atr_percentile > 70:
                regime = "High Volatility Trend"
            elif current_atr_percentile < 30:
                regime = "Low Volatility Trend"
            else:
                regime = "Transitioning Market"
        elif current_adx < 20:
            if current_atr_percentile > 70:
                regime = "High Volatility Range"
            elif current_atr_percentile < 30:
                regime = "Low Volatility Range"
            else:
                regime = "Transitioning Market"
        else:
            regime = "Transitioning Market"
        
        # Get recommended strategy types
        recommended_types = self.get_recommended_strategies(regime)
        
        result = {
            "regime": regime,
            "adx": round(current_adx, 2),
            "atr_percentile": round(current_atr_percentile, 2),
            "atr": round(atr.iloc[-1], 4),
            "recommended_strategy_types": recommended_types
        }
        
        return result
    
    def get_recommended_strategies(self, regime: str) -> list:
        """
        Get recommended strategy types for a given regime.
        
        Args:
            regime: Market regime name
        
        Returns:
            List of recommended strategy types
        """
        regime_to_strategy_map = {
            "High Volatility Trend": ["Trend Following", "Breakout", "Volatility", "Momentum"],
            "Low Volatility Trend": ["Trend Following", "Pullback", "Momentum"],
            "High Volatility Range": ["Mean Reversion", "Volatility", "Scalping", "Arbitrage"],
            "Low Volatility Range": ["Mean Reversion", "Volatility Squeeze", "Accumulation", "Band-Based"],
            "Transitioning Market": ["Divergence", "Adaptive", "Harmonic"]
        }
        
        return regime_to_strategy_map.get(regime, [])


# Example usage
if __name__ == "__main__":
    # Test with sample data
    print("Market Regime Detector - Test Mode")
    print("=" * 60)
    
    # Load BTC data if available
    try:
        df = pd.read_csv('/home/ubuntu/upload/BTC-USD-15m.csv')
        # Clean column names (remove spaces and commas)
        df.columns = df.columns.str.strip().str.replace(',', '').str.lower()
        
        # Initialize detector
        detector = MarketRegimeDetector()
        
        # Detect regime
        regime, metrics = detector.detect_regime(df)
        
        print(f"\n📊 Current Market Regime: {regime}")
        print(f"\nMetrics:")
        print(f"  ADX: {metrics['adx']}")
        print(f"  ATR Percentile: {metrics['atr_percentile']}%")
        print(f"  ATR: {metrics['atr']}")
        
        # Get recommended strategies
        recommended = detector.get_recommended_strategies(regime)
        print(f"\n✅ Recommended Strategy Types:")
        for i, strategy_type in enumerate(recommended, 1):
            print(f"  {i}. {strategy_type}")
        
        print(f"\n" + "=" * 60)
        print("✅ Market Regime Detector is operational!")
        
    except FileNotFoundError:
        print("⚠️  BTC data file not found. Detector code is ready but needs market data to run.")
    except Exception as e:
        print(f"❌ Error: {e}")
