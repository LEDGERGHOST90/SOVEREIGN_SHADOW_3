#!/usr/bin/env python3
"""
Social Sentiment Scanner
Aggregates crypto sentiment from multiple sources

Sources:
- Fear & Greed Index (free)
- LunarCrush social metrics (free tier)
- Reddit trending (free)
- CoinGecko trending (free)
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

BASE_DIR = Path('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/content_ingestion')
SENTIMENT_DIR = BASE_DIR / 'sentiment'
SENTIMENT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SentimentSignal:
    """Structured sentiment data"""
    symbol: str
    score: float  # -100 to +100
    source: str
    mentions: int
    trend: str  # "rising", "falling", "stable"
    timestamp: str
    raw_data: Dict


class SentimentScanner:
    """
    Aggregates sentiment from free crypto data sources
    """

    def __init__(self):
        self.cache_file = SENTIMENT_DIR / 'latest_sentiment.json'
        self.history_file = SENTIMENT_DIR / 'sentiment_history.json'

    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Get Bitcoin Fear & Greed Index
        Free, no API key needed
        """
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get('data'):
                fng = data['data'][0]
                return {
                    'value': int(fng['value']),
                    'classification': fng['value_classification'],
                    'timestamp': fng['timestamp'],
                    'interpretation': self._interpret_fng(int(fng['value']))
                }
        except Exception as e:
            print(f"Fear & Greed error: {e}")
        return None

    def _interpret_fng(self, value: int) -> str:
        """Interpret Fear & Greed for trading"""
        if value <= 20:
            return "EXTREME_FEAR - Potential buy zone"
        elif value <= 40:
            return "FEAR - Consider accumulating"
        elif value <= 60:
            return "NEUTRAL - Wait for direction"
        elif value <= 80:
            return "GREED - Be cautious"
        else:
            return "EXTREME_GREED - Consider taking profits"

    def get_coingecko_trending(self) -> List[Dict]:
        """
        Get trending coins from CoinGecko
        Free, no API key needed
        """
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = requests.get(url, timeout=10)
            data = response.json()

            trending = []
            for item in data.get('coins', [])[:10]:
                coin = item['item']
                trending.append({
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'score': coin.get('score', 0)
                })
            return trending
        except Exception as e:
            print(f"CoinGecko trending error: {e}")
        return []

    def get_coingecko_sentiment(self, coin_id: str) -> Optional[Dict]:
        """
        Get community sentiment for a specific coin
        """
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'false',
                'community_data': 'true',
                'developer_data': 'false'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            community = data.get('community_data', {})
            sentiment = data.get('sentiment_votes_up_percentage', 50)

            return {
                'coin_id': coin_id,
                'symbol': data.get('symbol', '').upper(),
                'sentiment_up_pct': sentiment,
                'sentiment_down_pct': 100 - sentiment if sentiment else 50,
                'twitter_followers': community.get('twitter_followers', 0),
                'reddit_subscribers': community.get('reddit_subscribers', 0),
                'reddit_active_48h': community.get('reddit_accounts_active_48h', 0)
            }
        except Exception as e:
            print(f"CoinGecko sentiment error for {coin_id}: {e}")
        return None

    def calculate_aggregate_sentiment(self, symbol: str) -> SentimentSignal:
        """
        Calculate aggregate sentiment score for a symbol
        Combines multiple sources into single score
        """
        scores = []
        mentions = 0
        raw_data = {}

        # Map symbol to coingecko ID
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'PEPE': 'pepe'
        }

        coin_id = symbol_map.get(symbol.upper())

        # Get CoinGecko sentiment
        if coin_id:
            cg_sentiment = self.get_coingecko_sentiment(coin_id)
            if cg_sentiment:
                # Convert 0-100 to -100 to +100
                score = (cg_sentiment['sentiment_up_pct'] - 50) * 2
                scores.append(score)
                mentions += cg_sentiment.get('reddit_active_48h', 0)
                raw_data['coingecko'] = cg_sentiment

        # Get Fear & Greed (applies to overall market, weight for BTC)
        fng = self.get_fear_greed_index()
        if fng:
            # Convert 0-100 to -100 to +100
            fng_score = (fng['value'] - 50) * 2
            if symbol.upper() == 'BTC':
                scores.append(fng_score)  # Full weight for BTC
            else:
                scores.append(fng_score * 0.5)  # Half weight for alts
            raw_data['fear_greed'] = fng

        # Check if trending
        trending = self.get_coingecko_trending()
        trending_symbols = [t['symbol'] for t in trending]
        if symbol.upper() in trending_symbols:
            scores.append(30)  # Trending bonus
            raw_data['trending'] = True
        else:
            raw_data['trending'] = False

        # Calculate final score
        final_score = sum(scores) / len(scores) if scores else 0

        # Determine trend
        if final_score > 20:
            trend = "bullish"
        elif final_score < -20:
            trend = "bearish"
        else:
            trend = "neutral"

        return SentimentSignal(
            symbol=symbol.upper(),
            score=round(final_score, 2),
            source="aggregate",
            mentions=mentions,
            trend=trend,
            timestamp=datetime.now().isoformat(),
            raw_data=raw_data
        )

    def scan_watchlist(self, symbols: List[str] = None) -> Dict:
        """
        Scan sentiment for watchlist
        """
        if symbols is None:
            symbols = ['BTC', 'ETH', 'SOL', 'XRP']

        print(f"Scanning sentiment for: {', '.join(symbols)}")

        results = {
            'timestamp': datetime.now().isoformat(),
            'market_fear_greed': self.get_fear_greed_index(),
            'trending': self.get_coingecko_trending()[:5],
            'symbols': {}
        }

        for symbol in symbols:
            signal = self.calculate_aggregate_sentiment(symbol)
            results['symbols'][symbol] = asdict(signal)
            print(f"  {symbol}: {signal.score:+.1f} ({signal.trend})")

        # Save results
        self.cache_file.write_text(json.dumps(results, indent=2))

        # Append to history
        self._append_history(results)

        return results

    def _append_history(self, results: Dict):
        """Append to history file"""
        try:
            history = []
            if self.history_file.exists():
                history = json.loads(self.history_file.read_text())

            history.append({
                'timestamp': results['timestamp'],
                'fear_greed': results.get('market_fear_greed', {}).get('value'),
                'symbols': {
                    k: v['score'] for k, v in results.get('symbols', {}).items()
                }
            })

            # Keep last 100 entries
            history = history[-100:]
            self.history_file.write_text(json.dumps(history, indent=2))
        except Exception as e:
            print(f"History error: {e}")

    def get_trading_signals(self) -> List[Dict]:
        """
        Generate trading signals from sentiment
        """
        signals = []

        # Load latest sentiment
        if not self.cache_file.exists():
            self.scan_watchlist()

        data = json.loads(self.cache_file.read_text())

        # Check Fear & Greed extremes
        fng = data.get('market_fear_greed', {})
        if fng:
            value = fng.get('value', 50)
            if value <= 25:
                signals.append({
                    'type': 'MARKET_FEAR',
                    'action': 'CONSIDER_BUY',
                    'reason': f"Extreme Fear ({value}) - historically good buy zone",
                    'confidence': min(90, 100 - value)
                })
            elif value >= 75:
                signals.append({
                    'type': 'MARKET_GREED',
                    'action': 'CONSIDER_SELL',
                    'reason': f"Extreme Greed ({value}) - consider taking profits",
                    'confidence': value
                })

        # Check individual coins
        for symbol, sentiment in data.get('symbols', {}).items():
            score = sentiment.get('score', 0)
            if score >= 40:
                signals.append({
                    'type': 'BULLISH_SENTIMENT',
                    'symbol': symbol,
                    'action': 'WATCH_FOR_ENTRY',
                    'score': score,
                    'reason': f"{symbol} sentiment very positive ({score:+.1f})"
                })
            elif score <= -40:
                signals.append({
                    'type': 'BEARISH_SENTIMENT',
                    'symbol': symbol,
                    'action': 'AVOID_OR_SHORT',
                    'score': score,
                    'reason': f"{symbol} sentiment very negative ({score:+.1f})"
                })

        return signals


def main():
    """CLI interface"""
    import sys

    scanner = SentimentScanner()

    if len(sys.argv) > 1 and sys.argv[1] == '--signals':
        signals = scanner.get_trading_signals()
        print(f"\nTrading Signals ({len(signals)}):")
        for s in signals:
            print(f"  [{s['type']}] {s.get('symbol', 'MARKET')}: {s['action']}")
            print(f"    {s['reason']}")
    else:
        results = scanner.scan_watchlist()
        print(f"\nFear & Greed: {results['market_fear_greed']}")
        print(f"\nTrending: {[t['symbol'] for t in results['trending']]}")
        print(f"\nSaved to: {scanner.cache_file}")


if __name__ == "__main__":
    main()
