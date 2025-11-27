#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - DATA LOADER
Historical data loader for backtesting

Loads OHLCV data for multiple assets/timeframes:
- Assets: BTC, ETH, SOL, XRP
- Timeframes: 15m, 4h, 1d
- Source: Coinbase/Binance historical data

Philosophy: "Test on real data, not fantasies"

Author: SovereignShadow Trading System
Created: 2025-11-24
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json


class DataLoader:
    """
    Historical data loader for backtesting

    Supports:
    - Multiple assets (BTC, ETH, SOL, XRP)
    - Multiple timeframes (15m, 4h, 1d)
    - Synthetic data generation (for testing)
    - Real exchange data loading (when available)
    """

    def __init__(self, data_dir: str = "backtest_data"):
        """
        Initialize data loader

        Args:
            data_dir: Directory to store/load historical data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        print("📊 DATA LOADER initialized")
        print(f"   Data Directory: {self.data_dir}")

    def load_all_datasets(
        self,
        assets: List[str] = ['BTC', 'ETH', 'SOL', 'XRP'],
        timeframes: List[str] = ['15m', '4h', '1d'],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_synthetic: bool = True
    ) -> Dict[Tuple[str, str], pd.DataFrame]:
        """
        Load all asset/timeframe combinations

        Args:
            assets: List of asset symbols
            timeframes: List of timeframes ('15m', '4h', '1d')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            use_synthetic: Generate synthetic data if real data unavailable

        Returns:
            Dict of {(asset, timeframe): DataFrame}
        """
        # Default to 6 months of data
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

        datasets = {}

        print(f"\n📥 Loading datasets...")
        print(f"   Assets: {', '.join(assets)}")
        print(f"   Timeframes: {', '.join(timeframes)}")
        print(f"   Period: {start_date} to {end_date}")

        for asset in assets:
            for timeframe in timeframes:
                try:
                    # Try to load real data
                    data = self._load_real_data(asset, timeframe, start_date, end_date)

                    if data is None and use_synthetic:
                        # Fallback to synthetic data
                        data = self._generate_synthetic_data(
                            asset, timeframe, start_date, end_date
                        )

                    if data is not None:
                        datasets[(asset, timeframe)] = data
                        print(f"   ✅ {asset}-{timeframe}: {len(data)} candles")
                    else:
                        print(f"   ⚠️  {asset}-{timeframe}: No data available")

                except Exception as e:
                    print(f"   ❌ {asset}-{timeframe}: Error - {str(e)}")

        print(f"\n✅ Loaded {len(datasets)} datasets")
        return datasets

    def _load_real_data(
        self,
        asset: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Load real historical data from exchange

        Currently returns None - implement when exchange API available
        """
        # Check if cached data exists
        cache_file = self.data_dir / f"{asset}_{timeframe}_{start_date}_{end_date}.csv"

        if cache_file.exists():
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            return df

        # TODO: Implement real data fetching from Coinbase/Binance
        # For now, return None to trigger synthetic data generation
        return None

    def _generate_synthetic_data(
        self,
        asset: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Generate synthetic OHLCV data for testing

        Uses realistic price movements:
        - Trend + noise + volatility
        - Volume patterns
        - Proper OHLC relationships
        """
        # Parse dates
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        # Determine candle frequency
        freq_map = {
            '15m': '15T',
            '4h': '4H',
            '1d': '1D'
        }
        freq = freq_map.get(timeframe, '1D')

        # Generate date range
        dates = pd.date_range(start=start, end=end, freq=freq)
        n_candles = len(dates)

        # Asset-specific parameters
        asset_params = {
            'BTC': {'base_price': 100000, 'daily_vol': 0.03, 'trend': 0.0001},
            'ETH': {'base_price': 3200, 'daily_vol': 0.04, 'trend': 0.0002},
            'SOL': {'base_price': 235, 'daily_vol': 0.05, 'trend': 0.0003},
            'XRP': {'base_price': 2.1, 'daily_vol': 0.06, 'trend': 0.0001}
        }

        params = asset_params.get(asset, {'base_price': 100, 'daily_vol': 0.04, 'trend': 0})

        # Generate price series (geometric Brownian motion)
        returns = np.random.normal(
            params['trend'],
            params['daily_vol'] / np.sqrt(24),  # Scale by time
            n_candles
        )

        # Add some trend
        trend = np.linspace(0, params['trend'] * n_candles, n_candles)
        returns = returns + trend

        # Calculate prices
        prices = params['base_price'] * np.exp(np.cumsum(returns))

        # Generate OHLC
        data = []
        for i, price in enumerate(prices):
            # Random high/low around close
            high = price * (1 + abs(np.random.normal(0, 0.005)))
            low = price * (1 - abs(np.random.normal(0, 0.005)))
            open_price = np.random.uniform(low, high)
            close = price

            # Ensure OHLC relationships
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            # Volume (with some variation)
            base_volume = 1000000
            volume = base_volume * (1 + np.random.uniform(-0.5, 1.5))

            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })

        # Create DataFrame
        df = pd.DataFrame(data, index=dates)

        return df

    def save_data(
        self,
        data: pd.DataFrame,
        asset: str,
        timeframe: str,
        start_date: str,
        end_date: str
    ):
        """Save data to cache"""
        cache_file = self.data_dir / f"{asset}_{timeframe}_{start_date}_{end_date}.csv"
        data.to_csv(cache_file)
        print(f"✅ Saved {asset}-{timeframe} data to {cache_file}")


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common technical indicators

    Adds columns:
    - SMA_50, SMA_200: Simple moving averages
    - RSI: Relative Strength Index
    - MACD: MACD line
    - ATR: Average True Range
    - BB_upper, BB_lower: Bollinger Bands
    """
    df = data.copy()

    # Simple Moving Averages
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # RSI (14 period)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # ATR (14 period)
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()

    # Bollinger Bands (20 period, 2 std)
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * bb_std)
    df['bb_lower'] = df['bb_middle'] - (2 * bb_std)

    return df


if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 DATA LOADER - Testing")
    print("="*80)

    # Initialize loader
    loader = DataLoader(data_dir="backtest_data")

    # Load all datasets (synthetic for now)
    datasets = loader.load_all_datasets(
        assets=['BTC', 'ETH', 'SOL', 'XRP'],
        timeframes=['15m', '4h', '1d'],
        use_synthetic=True
    )

    # Show example data
    if datasets:
        asset, timeframe = list(datasets.keys())[0]
        data = datasets[(asset, timeframe)]

        print(f"\n📈 Example: {asset}-{timeframe}")
        print(f"   Candles: {len(data)}")
        print(f"   Date Range: {data.index[0]} to {data.index[-1]}")
        print(f"\n   First 3 candles:")
        print(data.head(3))

        # Calculate indicators
        data_with_indicators = calculate_technical_indicators(data)
        print(f"\n   Technical Indicators Added:")
        print(f"   {data_with_indicators.columns.tolist()}")

    print("\n" + "="*80 + "\n")
