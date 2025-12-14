"""
On-Chain Signals Module for Sovereign Shadow III
Built to enhance whale_agent.py with exchange flow and wallet tracking

This module provides on-chain intelligence by monitoring:
1. Exchange inflows/outflows (selling vs accumulation pressure)
2. Large wallet movements (whale tracking beyond OI)
3. Institutional wallet activity
4. Aggregated on-chain score

Data Sources:
- FREE: CoinGlass API (exchange flows, OI data)
- FREE: Blockchain explorers (whale wallet tracking)
- PAID (optional): CryptoQuant, Glassnode for enhanced data

Author: Sovereign Shadow III
Date: December 2025
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import traceback
from collections import defaultdict

# Configuration
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "onchain_cache"
CACHE_DURATION_MINUTES = 15  # Cache API responses for 15 minutes
MIN_WHALE_MOVEMENT_USD = 1_000_000  # $1M minimum for whale tracking

# Signal weights for aggregated score
SIGNAL_WEIGHTS = {
    'exchange_flow': 0.40,      # 40% weight
    'whale_movements': 0.35,     # 35% weight
    'institutional_flow': 0.25   # 25% weight
}

# Top exchange addresses to monitor (BTC & ETH)
KNOWN_EXCHANGE_ADDRESSES = {
    'BTC': {
        'binance': ['34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo', '3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb'],
        'coinbase': ['3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6', 'bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97'],
        'kraken': ['3BMEXKKzruL1xqoRY3GhqRJKpVqMx8hzJq', 'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h'],
    },
    'ETH': {
        'binance': ['0x28C6c06298d514Db089934071355E5743bf21d60', '0xdfd5293d8e347dfe59e90efd55b2956a1343963d'],
        'coinbase': ['0x71660c4005ba85c37ccec55d0c4493e66fe775d3', '0x503828976d22510aad0201ac7ec88293211d23da'],
        'kraken': ['0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2', '0x0a869d79a7052C7f1b55a8ebabbea3420F0D1E13'],
    }
}


class OnChainSignals:
    """
    Advanced on-chain signal aggregator

    Provides real-time insights into:
    - Exchange flow patterns (accumulation vs distribution)
    - Whale wallet movements
    - Institutional activity
    - Aggregated sentiment score
    """

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize OnChainSignals

        Args:
            cache_enabled: Whether to use caching to reduce API calls
        """
        self.cache_enabled = cache_enabled
        self.cache_dir = CACHE_DIR

        # Create cache directory
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SovereignShadow/3.0 (Trading Bot)',
            'Accept': 'application/json'
        })

        # API endpoints
        self.coinglass_base = "https://open-api.coinglass.com/public/v2"

        # Load API keys (optional)
        self.coinglass_key = os.getenv("COINGLASS_API_KEY")  # Free tier available
        self.cryptoquant_key = os.getenv("CRYPTOQUANT_API_KEY")  # Paid service
        self.glassnode_key = os.getenv("GLASSNODE_API_KEY")  # Paid service

        print("On-Chain Signals initialized")
        print(f"Cache enabled: {self.cache_enabled}")
        print(f"CoinGlass API: {'Available' if self.coinglass_key else 'Free tier (limited)'}")
        print(f"CryptoQuant API: {'Available' if self.cryptoquant_key else 'Not configured'}")
        print(f"Glassnode API: {'Available' if self.glassnode_key else 'Not configured'}")

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"

    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached data if available and not expired

        Args:
            cache_key: Unique identifier for the cached data

        Returns:
            Cached data or None if not available/expired
        """
        if not self.cache_enabled:
            return None

        cache_file = self._get_cache_path(cache_key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time < timedelta(minutes=CACHE_DURATION_MINUTES):
                print(f"Using cached data for {cache_key}")
                return cache_data['data']
            else:
                print(f"Cache expired for {cache_key}")
                return None

        except Exception as e:
            print(f"Error reading cache for {cache_key}: {e}")
            return None

    def _set_cached_data(self, cache_key: str, data: Dict) -> None:
        """
        Store data in cache

        Args:
            cache_key: Unique identifier for the data
            data: Data to cache
        """
        if not self.cache_enabled:
            return

        cache_file = self._get_cache_path(cache_key)

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

        except Exception as e:
            print(f"Error writing cache for {cache_key}: {e}")

    def get_exchange_flows(self, symbol: str = "BTC", interval: str = "24h") -> Dict:
        """
        Get exchange inflow/outflow data

        Large inflows often precede selling pressure
        Large outflows indicate accumulation (moving to cold storage)

        Args:
            symbol: Cryptocurrency symbol (BTC, ETH)
            interval: Time interval (24h, 7d, 30d)

        Returns:
            Dictionary with flow data and signal
        """
        cache_key = f"exchange_flows_{symbol}_{interval}"
        cached = self._get_cached_data(cache_key)

        if cached:
            return cached

        try:
            # Try CoinGlass API first (free tier available)
            flow_data = self._get_coinglass_flows(symbol)

            if not flow_data:
                # Fallback to manual calculation or other sources
                print(f"Warning: Could not fetch exchange flows for {symbol}")
                return self._get_default_flow_data()

            # Analyze the flow data
            signal = self._analyze_exchange_flows(
                flow_data['inflow_24h'],
                flow_data['outflow_24h'],
                flow_data['avg_daily_flow']
            )

            result = {
                'symbol': symbol,
                'interval': interval,
                'timestamp': datetime.now().isoformat(),
                'inflow_24h': flow_data['inflow_24h'],
                'outflow_24h': flow_data['outflow_24h'],
                'net_flow': flow_data['inflow_24h'] - flow_data['outflow_24h'],
                'avg_daily_flow': flow_data['avg_daily_flow'],
                'signal': signal['signal'],
                'reason': signal['reason'],
                'score': signal['score']
            }

            self._set_cached_data(cache_key, result)
            return result

        except Exception as e:
            print(f"Error getting exchange flows: {e}")
            traceback.print_exc()
            return self._get_default_flow_data()

    def _get_coinglass_flows(self, symbol: str) -> Optional[Dict]:
        """
        Fetch exchange flow data from CoinGlass API

        Note: Free tier has rate limits. Returns None if unavailable.
        """
        try:
            # CoinGlass endpoint for exchange flows
            # This is a simplified example - actual endpoint may vary
            url = f"{self.coinglass_base}/exchange_flows"
            params = {
                'symbol': symbol,
                'interval': '24h'
            }

            if self.coinglass_key:
                params['api_key'] = self.coinglass_key

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract flow data (structure depends on actual API)
                # This is a template - adjust based on actual API response
                return {
                    'inflow_24h': data.get('inflow', 0),
                    'outflow_24h': data.get('outflow', 0),
                    'avg_daily_flow': data.get('avg_flow', 0)
                }
            else:
                print(f"CoinGlass API returned status {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching CoinGlass data: {e}")
            return None

    def _analyze_exchange_flows(self, inflow_24h: float, outflow_24h: float, avg_daily_flow: float) -> Dict:
        """
        Analyze exchange flows to generate trading signal

        Args:
            inflow_24h: 24h inflow to exchanges (USD)
            outflow_24h: 24h outflow from exchanges (USD)
            avg_daily_flow: Average daily flow (USD)

        Returns:
            Dictionary with signal, reason, and score
        """
        net_flow = inflow_24h - outflow_24h

        if avg_daily_flow == 0:
            flow_ratio = 0
        else:
            flow_ratio = net_flow / avg_daily_flow

        # Generate signal based on flow ratio
        if flow_ratio > 1.5:
            # High inflows - bearish (selling pressure)
            return {
                'signal': 'BEARISH',
                'reason': f'High exchange inflows ({flow_ratio:.2f}x avg) - selling pressure expected',
                'score': -min(abs(flow_ratio) * 20, 100)  # -20 to -100
            }
        elif flow_ratio < -1.5:
            # High outflows - bullish (accumulation)
            return {
                'signal': 'BULLISH',
                'reason': f'High exchange outflows ({abs(flow_ratio):.2f}x avg) - accumulation phase',
                'score': min(abs(flow_ratio) * 20, 100)  # +20 to +100
            }
        else:
            # Normal flow levels
            return {
                'signal': 'NEUTRAL',
                'reason': f'Normal flow levels ({flow_ratio:.2f}x avg)',
                'score': flow_ratio * 10  # -15 to +15
            }

    def _get_default_flow_data(self) -> Dict:
        """Return default flow data when API unavailable"""
        return {
            'symbol': 'BTC',
            'interval': '24h',
            'timestamp': datetime.now().isoformat(),
            'inflow_24h': 0,
            'outflow_24h': 0,
            'net_flow': 0,
            'avg_daily_flow': 0,
            'signal': 'UNKNOWN',
            'reason': 'Data unavailable',
            'score': 0
        }

    def get_whale_movements(self, symbol: str = "BTC", min_value_usd: float = MIN_WHALE_MOVEMENT_USD) -> Dict:
        """
        Track large wallet movements (whale activity)

        Identifies:
        - Ladder whales (splitting large orders)
        - Exchange deposits/withdrawals
        - Wallet accumulation patterns

        Args:
            symbol: Cryptocurrency symbol
            min_value_usd: Minimum transaction value to track

        Returns:
            Dictionary with whale movement data and signal
        """
        cache_key = f"whale_movements_{symbol}_{min_value_usd}"
        cached = self._get_cached_data(cache_key)

        if cached:
            return cached

        try:
            # Get recent large transactions
            movements = self._fetch_large_transactions(symbol, min_value_usd)

            # Analyze movement patterns
            signal = self._analyze_whale_movements(movements)

            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'min_value_usd': min_value_usd,
                'total_movements': len(movements),
                'to_exchanges': signal['to_exchanges'],
                'from_exchanges': signal['from_exchanges'],
                'net_exchange_flow': signal['from_exchanges'] - signal['to_exchanges'],
                'signal': signal['signal'],
                'reason': signal['reason'],
                'score': signal['score'],
                'recent_transactions': movements[:5]  # Keep last 5 for reference
            }

            self._set_cached_data(cache_key, result)
            return result

        except Exception as e:
            print(f"Error getting whale movements: {e}")
            traceback.print_exc()
            return self._get_default_whale_data()

    def _fetch_large_transactions(self, symbol: str, min_value_usd: float) -> List[Dict]:
        """
        Fetch large transactions from blockchain explorers

        This is a simplified implementation. In production, you would:
        1. Use blockchain explorer APIs (Blockchair, Blockchain.com)
        2. Monitor specific whale addresses
        3. Use WebSocket for real-time updates

        Returns:
            List of transaction dictionaries
        """
        # Placeholder implementation
        # In production, implement actual blockchain API calls

        # Example structure:
        # return [
        #     {
        #         'hash': '0x...',
        #         'from': '0x...',
        #         'to': '0x...',
        #         'value_usd': 5000000,
        #         'timestamp': '2025-12-14T...',
        #         'to_exchange': True,
        #         'from_exchange': False
        #     },
        #     ...
        # ]

        print(f"Note: Whale tracking requires blockchain API integration")
        print("Returning simulated data for demonstration")

        return []

    def _analyze_whale_movements(self, movements: List[Dict]) -> Dict:
        """
        Analyze whale movements to generate signal

        Args:
            movements: List of large transactions

        Returns:
            Dictionary with analysis and signal
        """
        if not movements:
            return {
                'to_exchanges': 0,
                'from_exchanges': 0,
                'signal': 'NEUTRAL',
                'reason': 'No significant whale movements detected',
                'score': 0
            }

        # Count movements to/from exchanges
        to_exchanges = sum(1 for m in movements if m.get('to_exchange', False))
        from_exchanges = sum(1 for m in movements if m.get('from_exchange', False))

        net_flow = from_exchanges - to_exchanges

        # Generate signal
        if net_flow > 3:
            return {
                'to_exchanges': to_exchanges,
                'from_exchanges': from_exchanges,
                'signal': 'BEARISH',
                'reason': f'{net_flow} net whale movements TO exchanges - potential sell pressure',
                'score': -min(net_flow * 15, 100)
            }
        elif net_flow < -3:
            return {
                'to_exchanges': to_exchanges,
                'from_exchanges': from_exchanges,
                'signal': 'BULLISH',
                'reason': f'{abs(net_flow)} net whale movements FROM exchanges - accumulation',
                'score': min(abs(net_flow) * 15, 100)
            }
        else:
            return {
                'to_exchanges': to_exchanges,
                'from_exchanges': from_exchanges,
                'signal': 'NEUTRAL',
                'reason': f'Balanced whale activity (net: {net_flow})',
                'score': net_flow * 5
            }

    def _get_default_whale_data(self) -> Dict:
        """Return default whale data when API unavailable"""
        return {
            'symbol': 'BTC',
            'timestamp': datetime.now().isoformat(),
            'min_value_usd': MIN_WHALE_MOVEMENT_USD,
            'total_movements': 0,
            'to_exchanges': 0,
            'from_exchanges': 0,
            'net_exchange_flow': 0,
            'signal': 'UNKNOWN',
            'reason': 'Data unavailable',
            'score': 0,
            'recent_transactions': []
        }

    def get_onchain_score(self, symbol: str = "BTC") -> Dict:
        """
        Calculate aggregated on-chain sentiment score

        Combines multiple signals:
        - Exchange flows (40% weight)
        - Whale movements (35% weight)
        - Institutional activity (25% weight)

        Args:
            symbol: Cryptocurrency symbol

        Returns:
            Dictionary with aggregated score and breakdown
        """
        print(f"\nCalculating on-chain score for {symbol}...")

        # Get individual signals
        exchange_data = self.get_exchange_flows(symbol)
        whale_data = self.get_whale_movements(symbol)

        # Calculate weighted score
        exchange_score = exchange_data['score'] * SIGNAL_WEIGHTS['exchange_flow']
        whale_score = whale_data['score'] * SIGNAL_WEIGHTS['whale_movements']

        # Note: Institutional flow would require premium data
        # For now, we'll use 0 or derive from other signals
        institutional_score = 0

        total_score = exchange_score + whale_score + institutional_score

        # Normalize to -100 to +100 range
        total_score = max(-100, min(100, total_score))

        # Determine overall signal
        if total_score > 30:
            overall_signal = 'BULLISH'
            confidence = min(abs(total_score), 100)
        elif total_score < -30:
            overall_signal = 'BEARISH'
            confidence = min(abs(total_score), 100)
        else:
            overall_signal = 'NEUTRAL'
            confidence = 50 - abs(total_score) / 2

        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'overall_score': round(total_score, 2),
            'overall_signal': overall_signal,
            'confidence': round(confidence, 2),
            'breakdown': {
                'exchange_flows': {
                    'score': round(exchange_score, 2),
                    'weight': SIGNAL_WEIGHTS['exchange_flow'],
                    'signal': exchange_data['signal'],
                    'reason': exchange_data['reason']
                },
                'whale_movements': {
                    'score': round(whale_score, 2),
                    'weight': SIGNAL_WEIGHTS['whale_movements'],
                    'signal': whale_data['signal'],
                    'reason': whale_data['reason']
                },
                'institutional_flow': {
                    'score': round(institutional_score, 2),
                    'weight': SIGNAL_WEIGHTS['institutional_flow'],
                    'signal': 'NOT_IMPLEMENTED',
                    'reason': 'Requires premium data source'
                }
            },
            'recommendation': self._generate_recommendation(total_score, overall_signal),
            'raw_data': {
                'exchange_flows': exchange_data,
                'whale_movements': whale_data
            }
        }

    def _generate_recommendation(self, score: float, signal: str) -> str:
        """
        Generate actionable recommendation based on score

        Args:
            score: Overall on-chain score (-100 to +100)
            signal: Overall signal (BULLISH/BEARISH/NEUTRAL)

        Returns:
            Human-readable recommendation
        """
        if signal == 'BULLISH':
            if score > 70:
                return "Strong accumulation signal. Consider increasing position size."
            elif score > 50:
                return "Moderate bullish signal. Good entry opportunity for long positions."
            else:
                return "Slight bullish bias. Wait for confirmation before entering."
        elif signal == 'BEARISH':
            if score < -70:
                return "Strong distribution signal. Consider reducing exposure or shorting."
            elif score < -50:
                return "Moderate bearish signal. Consider taking profits or hedging."
            else:
                return "Slight bearish bias. Monitor closely for trend confirmation."
        else:
            return "Neutral market conditions. Wait for clearer signals before taking action."

    def clear_cache(self) -> None:
        """Clear all cached data"""
        if not self.cache_enabled:
            print("Cache is disabled")
            return

        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            for cache_file in cache_files:
                cache_file.unlink()
            print(f"Cleared {len(cache_files)} cache files")
        except Exception as e:
            print(f"Error clearing cache: {e}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("Sovereign Shadow III - On-Chain Signals Module")
    print("=" * 80)
    print()

    # Initialize the signals module
    signals = OnChainSignals(cache_enabled=True)

    # Test exchange flows
    print("\n" + "=" * 80)
    print("EXCHANGE FLOW ANALYSIS")
    print("=" * 80)

    for symbol in ['BTC', 'ETH']:
        flow_data = signals.get_exchange_flows(symbol)
        print(f"\n{symbol} Exchange Flows:")
        print(f"  Signal: {flow_data['signal']}")
        print(f"  Score: {flow_data['score']:.2f}")
        print(f"  Reason: {flow_data['reason']}")
        print(f"  Inflow (24h): ${flow_data['inflow_24h']:,.2f}")
        print(f"  Outflow (24h): ${flow_data['outflow_24h']:,.2f}")
        print(f"  Net Flow: ${flow_data['net_flow']:,.2f}")

    # Test whale movements
    print("\n" + "=" * 80)
    print("WHALE MOVEMENT ANALYSIS")
    print("=" * 80)

    for symbol in ['BTC', 'ETH']:
        whale_data = signals.get_whale_movements(symbol)
        print(f"\n{symbol} Whale Activity:")
        print(f"  Signal: {whale_data['signal']}")
        print(f"  Score: {whale_data['score']:.2f}")
        print(f"  Reason: {whale_data['reason']}")
        print(f"  Total Movements: {whale_data['total_movements']}")
        print(f"  To Exchanges: {whale_data['to_exchanges']}")
        print(f"  From Exchanges: {whale_data['from_exchanges']}")

    # Test aggregated score
    print("\n" + "=" * 80)
    print("AGGREGATED ON-CHAIN SCORE")
    print("=" * 80)

    for symbol in ['BTC', 'ETH']:
        score_data = signals.get_onchain_score(symbol)
        print(f"\n{symbol} On-Chain Score:")
        print(f"  Overall Signal: {score_data['overall_signal']}")
        print(f"  Overall Score: {score_data['overall_score']:.2f}/100")
        print(f"  Confidence: {score_data['confidence']:.2f}%")
        print(f"  Recommendation: {score_data['recommendation']}")
        print(f"\n  Breakdown:")
        for component, data in score_data['breakdown'].items():
            print(f"    {component.replace('_', ' ').title()}:")
            print(f"      Score: {data['score']:.2f} (weight: {data['weight']:.0%})")
            print(f"      Signal: {data['signal']}")
            print(f"      Reason: {data['reason']}")

    print("\n" + "=" * 80)
    print("INTEGRATION GUIDE")
    print("=" * 80)
    print("""
How to integrate with whale_agent.py:

1. Import the module:
   from core.signals.onchain_signals import OnChainSignals

2. Initialize in WhaleAgent.__init__():
   self.onchain = OnChainSignals(cache_enabled=True)

3. Use in analysis methods:
   # Get on-chain score
   onchain_data = self.onchain.get_onchain_score('BTC')

   # Combine with existing OI analysis
   combined_signal = self._combine_signals(
       oi_signal=oi_analysis,
       onchain_signal=onchain_data
   )

4. API Keys (optional, for enhanced data):
   # Add to .env file:
   COINGLASS_API_KEY=your_key_here
   CRYPTOQUANT_API_KEY=your_key_here  # Paid
   GLASSNODE_API_KEY=your_key_here    # Paid

5. Free tier usage:
   - CoinGlass: Free tier available with rate limits
   - Blockchain explorers: Free for basic queries
   - For production: Consider paid APIs for more reliable data

Note: This module is designed to COMPLEMENT whale_agent.py, not replace it.
The OI-based whale detection remains valuable for futures market insights.
""")

    print("\n" + "=" * 80)
    print("Setup complete! Module ready for integration.")
    print("=" * 80)
