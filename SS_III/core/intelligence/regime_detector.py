import pandas as pd
import numpy as np

class MarketRegimeDetector:
    def __init__(self):
        self.current_regime = "unknown"

    def analyze_market(self, df):
        """
        Classifies market into:
        - choppy_volatile
        - choppy_calm
        - trending_volatile
        - trending_calm
        """
        if df is None or df.empty:
            return "unknown"

        # Modifying the dataframe in place can cause warnings. We'll work on a copy if we need to return it, 
        # or just calculate series. Since we don't return the modified DF, local vars are fine, 
        # but let's be safe and copy if we were to modify `df`.
        # Here we are assigning to `df` columns, which is a modification.
        df = df.copy()

        # Calculate Indicators if not present
        if 'ATR' not in df.columns:
            df['ATR'] = self._calculate_atr(df)
        
        df['EMA_50'] = df['close'].ewm(span=50).mean()
        df['EMA_200'] = df['close'].ewm(span=200).mean()
        
        last_row = df.iloc[-1]
        
        # Trend Detection
        is_uptrend = last_row['EMA_50'] > last_row['EMA_200']
        
        # Volatility Detection
        # Normalize ATR by price to get percentage volatility
        volatility_pct = last_row['ATR'] / max(last_row['close'], 0.0001)
        is_volatile = volatility_pct > 0.015 # Threshold for crypto (1.5%) - adjustable
        
        if is_volatile:
            if self._is_trending(df):
                 self.current_regime = "trending_volatile"
            else:
                 self.current_regime = "choppy_volatile"
        else:
            if self._is_trending(df):
                 self.current_regime = "trending_calm"
            else:
                 self.current_regime = "choppy_calm"
            
        return self.current_regime

    def _is_trending(self, df):
        # ADX would be better, but using EMA separation for now
        last_row = df.iloc[-1]
        ema_diff = abs(last_row['EMA_50'] - last_row['EMA_200']) / max(last_row['close'], 0.0001)
        return ema_diff > 0.005 # 0.5% separation

    def _calculate_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
