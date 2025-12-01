#!/usr/bin/env python3
"""
Market Data Client for Synoptic Core
Provides OHLCV data and technical indicators
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class MarketDataClient:
    """
    Fetches market data and calculates technical indicators
    Uses CCXT for exchange data access
    """

    def __init__(self, exchange_id: str = "binance"):
        try:
            self.exchange = getattr(ccxt, exchange_id)({
                'enableRateLimit': True,
            })
        except Exception:
            # Fallback to public API only
            self.exchange = None

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        days: int = 30
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol

        Args:
            symbol: Asset symbol (e.g., "BTC", "ETH")
            timeframe: Candle timeframe (1h, 4h, 1d)
            days: Number of days of history

        Returns:
            DataFrame with OHLCV columns
        """
        # Map common symbols to exchange format
        pair = f"{symbol}/USDT" if "/" not in symbol else symbol

        try:
            if self.exchange:
                since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                ohlcv = self.exchange.fetch_ohlcv(pair, timeframe, since=since)

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
        except Exception as e:
            print(f"Exchange fetch failed: {e}")

        # Return mock data for development/offline use
        return self._mock_ohlcv(symbol, days)

    def _mock_ohlcv(self, symbol: str, days: int) -> pd.DataFrame:
        """Generate mock OHLCV data for testing"""
        # Base prices for common assets
        base_prices = {
            "BTC": 95000,
            "ETH": 3500,
            "SOL": 225,
            "XRP": 2.30,
            "AAVE": 350
        }

        base_price = base_prices.get(symbol.upper(), 100)

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        np.random.seed(42)  # Reproducible

        # Generate price walk
        returns = np.random.normal(0.001, 0.03, days)
        prices = base_price * np.cumprod(1 + returns)

        df = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'high': prices * (1 + np.random.uniform(0, 0.03, days)),
            'low': prices * (1 - np.random.uniform(0, 0.03, days)),
            'close': prices,
            'volume': np.random.uniform(1e6, 1e8, days)
        }, index=dates)

        return df

    def get_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate technical indicators from OHLCV data

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dict with calculated indicators
        """
        if df.empty:
            return {}

        close = df['close']
        high = df['high']
        low = df['low']

        indicators = {
            'close': float(close.iloc[-1]),
            'high_period': float(high.max()),
            'low_period': float(low.min())
        }

        # RSI (14-period)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        indicators['rsi'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50

        # EMAs
        indicators['ema_20'] = float(close.ewm(span=20).mean().iloc[-1])
        indicators['ema_50'] = float(close.ewm(span=50).mean().iloc[-1])

        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        indicators['macd'] = {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

        # ATR (Average True Range)
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        indicators['atr'] = float(atr) if not pd.isna(atr) else 0
        indicators['atr_pct'] = (indicators['atr'] / indicators['close']) * 100

        # Bollinger Bands
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        indicators['bb_upper'] = float((sma_20 + 2 * std_20).iloc[-1])
        indicators['bb_lower'] = float((sma_20 - 2 * std_20).iloc[-1])
        indicators['bb_middle'] = float(sma_20.iloc[-1])

        # Volume analysis
        avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        indicators['volume_ratio'] = float(current_volume / avg_volume) if avg_volume > 0 else 1.0

        return indicators


# Test
if __name__ == "__main__":
    client = MarketDataClient()

    print("Testing Market Data Client...")
    df = client.get_ohlcv("BTC", "1d", 30)
    print(f"\nOHLCV Shape: {df.shape}")
    print(df.tail())

    indicators = client.get_indicators(df)
    print(f"\nIndicators:")
    for k, v in indicators.items():
        print(f"  {k}: {v}")
