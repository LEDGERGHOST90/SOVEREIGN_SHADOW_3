#!/usr/bin/env python3
"""
LIVE DATA PIPELINE - Feeds real-time data into SS_III components

Connects:
- Exchange APIs → Live prices
- Birdeye API → Whale/liquidation data
- Research Swarm → Multi-AI analysis
- Strategy Engine → Regime detection + signals
- Agent Council → Trading decisions
"""

import os
import json
import requests
import asyncio
import ccxt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import pandas as pd

# Load environment
# Trading profiles for dynamic SL/TP
try:
    from core.config.trading_profiles import get_profile_for_symbol, get_active_profile
except ImportError:
    get_profile_for_symbol = None
    get_active_profile = None
load_dotenv(Path(__file__).parent.parent.parent / '.env', override=True)

SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")


@dataclass
class LivePrice:
    """Real-time price data"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    source: str
    timestamp: str


@dataclass
class WhaleActivity:
    """Whale movement data"""
    symbol: str
    net_flow: float  # positive = accumulation
    large_txs: int
    exchange_flow: str  # 'inflow' or 'outflow'
    timestamp: str


@dataclass
class MarketSignal:
    """Unified market signal"""
    symbol: str
    regime: str
    direction: str  # 'LONG', 'SHORT', 'NEUTRAL'
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reasoning: str
    sources: List[str]
    timestamp: str


class LiveDataPipeline:
    """
    Unified live data pipeline for SS_III
    Uses CCXT for real exchange prices
    """

    def __init__(self):
        # API keys
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')

        # Initialize CCXT exchange (Coinbase)
        self.exchange = ccxt.coinbase({
            'apiKey': os.getenv('COINBASE_API_KEY'),
            'secret': os.getenv('COINBASE_API_SECRET'),
        })

        # DISCOVERY watchlist - assets to find buying opportunities
        self.symbols = [
            # Major caps
            'BTC', 'ETH', 'SOL', 'XRP', 'AAVE',
            # Layer 1s
            'ADA', 'AVAX', 'DOT', 'ATOM', 'NEAR', 'APT', 'SUI',
            # Layer 2s
            'MATIC', 'ARB', 'OP',
            # DeFi
            'UNI', 'LINK', 'MKR', 'CRV', 'LDO',
            # Memes with volume
            'DOGE', 'SHIB', 'PEPE',
            # AI/Compute
            'FET', 'RNDR', 'TAO'
        ]

        # Cache
        self.price_cache = {}
        self.whale_cache = {}
        self.cache_ttl = 60  # seconds

    # =========================================================================
    # PRICE DATA - CCXT
    # =========================================================================

    def get_live_prices(self) -> Dict[str, LivePrice]:
        """Fetch live prices from Coinbase via CCXT"""
        # Check cache validity
        if self.price_cache:
            try:
                # Check age of first item
                first_item = next(iter(self.price_cache.values()))
                cache_time = datetime.fromisoformat(first_item.timestamp)
                age = (datetime.now() - cache_time).total_seconds()
                
                if age < self.cache_ttl:
                    return self.price_cache
            except Exception as e:
                # If date parsing fails, ignore cache
                pass

        prices = {}
        
        # Optimize: Try to fetch all tickers at once if possible, or stick to loop but strictly cached
        # For now, we keep the loop but it will only run ONCE per cycle per cache_ttl
        for symbol in self.symbols:
            try:
                pair = f"{symbol}/USD"
                ticker = self.exchange.fetch_ticker(pair)

                prices[symbol] = LivePrice(
                    symbol=symbol,
                    price=ticker.get('last', 0),
                    change_24h=ticker.get('percentage', 0) or 0,
                    volume_24h=ticker.get('quoteVolume', 0) or 0,
                    source='coinbase',
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                # Asset not available on Coinbase, skip
                pass

        self.price_cache = prices
        return prices

    def get_current_prices(self) -> Dict[str, Dict]:
        """Get current prices as simple dict for paper trader"""
        prices = self.get_live_prices()
        return {symbol: {'price': p.price, 'change_24h': p.change_24h} for symbol, p in prices.items()}

    def get_ohlcv(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data from Coinbase via CCXT"""
        try:
            pair = f"{symbol}/USD"
            timeframe = '1h'  # 1 hour candles
            limit = days * 24  # hours in days

            ohlcv = self.exchange.fetch_ohlcv(pair, timeframe, limit=limit)

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            print(f"OHLCV fetch error for {symbol}: {e}")
            return pd.DataFrame()

    # =========================================================================
    # WHALE DATA (Birdeye)
    # =========================================================================

    def get_whale_activity(self, symbol: str) -> Optional[WhaleActivity]:
        """Fetch whale activity from multiple sources"""

        # For BTC/ETH - use CoinGlass Open Interest data
        if symbol in ['BTC', 'ETH']:
            return self._get_oi_whale_signal(symbol)

        # For Solana ecosystem - use Birdeye
        if not self.birdeye_key:
            return None

        if symbol in ['SOL', 'BONK', 'WIF', 'JUP']:
            return self._get_birdeye_whale(symbol)

        # Default: no whale data available
        return WhaleActivity(
            symbol=symbol,
            net_flow=0,
            large_txs=0,
            exchange_flow='neutral',
            timestamp=datetime.now().isoformat()
        )

    def _get_oi_whale_signal(self, symbol: str) -> Optional[WhaleActivity]:
        """Get BTC/ETH whale signal using CCXT volume analysis"""
        try:
            # Use volume spike as whale activity proxy
            ticker = self.exchange.fetch_ticker(f"{symbol}/USD")

            # Get recent OHLCV for volume comparison
            ohlcv = self.exchange.fetch_ohlcv(f"{symbol}/USD", '1h', limit=24)
            if not ohlcv:
                raise Exception("No OHLCV data")

            volumes = [candle[5] for candle in ohlcv]  # Volume is index 5
            avg_volume = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else volumes[0]
            current_volume = volumes[-1]

            # Volume spike detection (whale activity proxy)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            price_change = ticker.get('percentage', 0) or 0

            # Interpret: High volume + price up = accumulation, High volume + price down = distribution
            if volume_ratio > 1.5:  # 50% above average = significant
                if price_change > 0:
                    net_flow = min(25, (volume_ratio - 1) * 20)  # Scale to 0-25
                    exchange_flow = 'accumulation'
                    large_txs = 1
                else:
                    net_flow = -min(25, (volume_ratio - 1) * 20)
                    exchange_flow = 'distribution'
                    large_txs = 1
            else:
                net_flow = 0
                exchange_flow = 'neutral'
                large_txs = 0

            return WhaleActivity(
                symbol=symbol,
                net_flow=net_flow,
                large_txs=large_txs,
                exchange_flow=exchange_flow,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"CCXT whale detection error for {symbol}: {e}")
            return WhaleActivity(
                symbol=symbol,
                net_flow=0,
                large_txs=0,
                exchange_flow='neutral',
                timestamp=datetime.now().isoformat()
            )

    def _get_birdeye_whale(self, symbol: str) -> Optional[WhaleActivity]:
        """Get whale data for Solana tokens from Birdeye"""
        try:
            # Birdeye token overview
            url = f"https://public-api.birdeye.so/public/token_overview?address={symbol}"
            headers = {'X-API-KEY': self.birdeye_key}

            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            # Parse whale metrics
            return WhaleActivity(
                symbol=symbol,
                net_flow=data.get('data', {}).get('whale_net_flow', 0),
                large_txs=data.get('data', {}).get('large_tx_count', 0),
                exchange_flow='neutral',
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"Birdeye error for {symbol}: {e}")
            return None

    # =========================================================================
    # REGIME DETECTION
    # =========================================================================

    def detect_regime(self, symbol: str) -> Dict[str, Any]:
        """Detect market regime using Strategy Engine"""
        try:
            from core.strategies.strategy_engine import MarketRegimeDetector

            detector = MarketRegimeDetector()
            ohlcv = self.get_ohlcv(symbol, days=30)

            if ohlcv.empty:
                return {'regime': 'Unknown', 'adx': 0, 'atr_percentile': 50}

            return detector.detect_regime(ohlcv)

        except Exception as e:
            print(f"Regime detection error: {e}")
            return {'regime': 'Error', 'error': str(e)}

    # =========================================================================
    # UNIFIED SIGNAL GENERATION
    # =========================================================================

    def generate_signal(self, symbol: str, capital: float = 734) -> MarketSignal:
        """
        Generate unified trading signal combining all data sources

        Args:
            symbol: Asset to analyze
            capital: Available trading capital
        """
        # 1. Get live price
        prices = self.get_live_prices()
        price_data = prices.get(symbol)

        if not price_data:
            return MarketSignal(
                symbol=symbol,
                regime='Unknown',
                direction='NEUTRAL',
                confidence=0,
                entry_price=0,
                stop_loss=0,
                take_profit=0,
                position_size=0,
                reasoning='No price data available',
                sources=[],
                timestamp=datetime.now().isoformat()
            )

        current_price = price_data.price
        change_24h = price_data.change_24h

        # 2. Detect regime
        regime_data = self.detect_regime(symbol)
        regime = regime_data.get('regime', 'Unknown')

        # 3. Determine direction based on regime + momentum
        if regime in ['High Volatility Trend', 'Low Volatility Trend']:
            direction = 'LONG' if change_24h > 0 else 'SHORT'
            confidence = min(80, 50 + abs(change_24h))
        elif regime in ['High Volatility Range', 'Low Volatility Range']:
            # Mean reversion
            if change_24h > 5:
                direction = 'SHORT'  # Overbought
            elif change_24h < -5:
                direction = 'LONG'  # Oversold
            else:
                direction = 'NEUTRAL'
            confidence = min(70, 40 + abs(change_24h))
        else:
            direction = 'NEUTRAL'
            confidence = 30

        # 4. Get trading profile for this symbol (uses asset-specific or active profile)
        if get_profile_for_symbol:
            profile = get_profile_for_symbol(symbol)
        else:
            # Fallback to hardcoded sniper defaults
            profile = type('Profile', (), {
                'stop_loss_pct': 3.0, 'tp1_pct': 5.0, 'risk_per_trade_pct': 2.0
            })()

        # 5. Calculate position sizing using profile
        risk_pct = profile.risk_per_trade_pct / 100
        sl_pct = profile.stop_loss_pct / 100
        max_position = min(50, capital * risk_pct / sl_pct)
        position_size = max_position * (confidence / 100)

        # 6. Calculate levels using profile (use LONG math for NEUTRAL too since we don't short on Coinbase)
        is_long = direction in ['LONG', 'NEUTRAL']  # Default to long-biased
        stop_loss = current_price * (1 - sl_pct if is_long else 1 + sl_pct)
        take_profit = current_price * (1 + profile.tp1_pct / 100 if is_long else 1 - profile.tp1_pct / 100)

        # 7. Generate reasoning
        reasoning = f"{symbol} in {regime} regime. "
        reasoning += f"Profile: {getattr(profile, 'name', 'default')}. "
        reasoning += f"24h change: {change_24h:.1f}%. "
        reasoning += f"ADX: {regime_data.get('adx', 0):.1f}. "
        reasoning += f"Recommended: {direction} with {confidence:.0f}% confidence."

        return MarketSignal(
            symbol=symbol,
            regime=regime,
            direction=direction,
            confidence=confidence,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=round(position_size, 2),
            reasoning=reasoning,
            sources=['Coinbase/CCXT', 'StrategyEngine'],
            timestamp=datetime.now().isoformat()
        )

    # =========================================================================
    # FULL SCAN
    # =========================================================================

    def scan_all(self, capital: float = 734) -> Dict[str, Any]:
        """
        Full scan of all watched symbols

        Returns unified report with signals for each asset
        """
        print(f"\n{'='*60}")
        print("LIVE DATA PIPELINE - Full Scan")
        print(f"{'='*60}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"Capital: ${capital}")
        print(f"Symbols: {', '.join(self.symbols)}")

        results = {
            'timestamp': datetime.now().isoformat(),
            'capital': capital,
            'signals': {},
            'summary': {
                'long': [],
                'short': [],
                'neutral': []
            }
        }

        # Scan each symbol
        for symbol in self.symbols:
            print(f"\n[{symbol}]")
            signal = self.generate_signal(symbol, capital)
            results['signals'][symbol] = asdict(signal)

            print(f"  Price: ${signal.entry_price:,.2f}")
            print(f"  Regime: {signal.regime}")
            print(f"  Signal: {signal.direction} ({signal.confidence:.0f}%)")

            if signal.direction == 'LONG':
                results['summary']['long'].append(symbol)
            elif signal.direction == 'SHORT':
                results['summary']['short'].append(symbol)
            else:
                results['summary']['neutral'].append(symbol)

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"LONG signals: {results['summary']['long']}")
        print(f"SHORT signals: {results['summary']['short']}")
        print(f"NEUTRAL: {results['summary']['neutral']}")

        return results


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_scan() -> Dict[str, Any]:
    """Quick market scan"""
    pipeline = LiveDataPipeline()
    return pipeline.scan_all()


def get_signal(symbol: str) -> MarketSignal:
    """Get signal for single symbol"""
    pipeline = LiveDataPipeline()
    return pipeline.generate_signal(symbol)


if __name__ == '__main__':
    # Run full scan
    results = quick_scan()

    # Save results
    output_path = SS3_ROOT / 'data' / 'live_scan_result.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")
