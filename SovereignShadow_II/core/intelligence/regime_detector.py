import pandas as pd
import numpy as np

class MarketRegimeDetector:
    def __init__(self):
        self.current_regime = "unknown"
    
    def detect_regime(self, df):
        """
        Detect market regime based on OHLCV data.
        Returns one of: 
        - trending_bullish
        - trending_bearish
        - choppy_volatile
        - choppy_calm
        """
        if df is None or df.empty:
            return "unknown"
            
        # Calculate volatility (ATR or StdDev)
        df['returns'] = df['close'].pct_change()
        volatility = df['returns'].std() * np.sqrt(len(df)) # Simple annualized-like proxy or rolling std
        
        # Calculate trend (SMA cross or ADX)
        sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
        sma_50 = df['close'].rolling(window=50).mean().iloc[-1]
        
        current_price = df['close'].iloc[-1]
        
        # Simple Logic
        is_trending = abs(sma_20 - sma_50) / sma_50 > 0.01 # 1% divergence
        is_bullish = sma_20 > sma_50 and current_price > sma_20
        is_bearish = sma_20 < sma_50 and current_price < sma_20
        
        # Volatility Threshold (Arbitrary for now, needs calibration)
        # Assuming hourly data, 2% volatility might be high
        is_volatile = volatility > 0.02 
        
        if is_trending:
            if is_bullish:
                regime = "trending_bullish"
            elif is_bearish:
                regime = "trending_bearish"
            else:
                regime = "choppy_volatile" if is_volatile else "choppy_calm"
        else:
            regime = "choppy_volatile" if is_volatile else "choppy_calm"
            
        self.current_regime = regime
        return regime
