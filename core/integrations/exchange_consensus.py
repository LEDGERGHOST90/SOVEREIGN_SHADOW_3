#!/usr/bin/env python3
"""
Exchange Consensus - Real-time data from YOUR exchanges
No stale web research. Direct from Coinbase, Kraken, Binance, OKX.
"""

import os
import ccxt
from typing import Dict, List, Optional
from statistics import median, mean
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')


class ExchangeConsensus:
    """
    Pull real-time data from all your exchanges and aggregate.
    No bullshit web research - direct from the source.
    """

    def __init__(self):
        self.exchanges = {}
        self._init_exchanges()

    def _init_exchanges(self):
        """Initialize all exchange connections."""

        # Coinbase
        try:
            self.exchanges['coinbase'] = ccxt.coinbase({
                'apiKey': os.getenv('COINBASE_API_KEY'),
                'secret': os.getenv('COINBASE_API_SECRET'),
                'enableRateLimit': True,
            })
            print("✓ Coinbase connected")
        except Exception as e:
            print(f"✗ Coinbase: {e}")

        # Kraken
        try:
            self.exchanges['kraken'] = ccxt.kraken({
                'apiKey': os.getenv('KRAKEN_API_KEY'),
                'secret': os.getenv('KRAKEN_API_SECRET'),
                'enableRateLimit': True,
            })
            print("✓ Kraken connected")
        except Exception as e:
            print(f"✗ Kraken: {e}")

        # Binance US
        try:
            self.exchanges['binance'] = ccxt.binanceus({
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_API_SECRET'),
                'enableRateLimit': True,
            })
            print("✓ Binance US connected")
        except Exception as e:
            print(f"✗ Binance US: {e}")

        # OKX
        try:
            self.exchanges['okx'] = ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_API_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'enableRateLimit': True,
            })
            print("✓ OKX connected")
        except Exception as e:
            print(f"✗ OKX: {e}")

    def get_consensus_price(self, symbol: str = 'BTC/USDT') -> Dict:
        """
        Get consensus price from all exchanges.

        Returns:
            {
                'symbol': 'BTC/USDT',
                'consensus_price': 88500.0,  # median of all
                'prices': {'coinbase': 88510, 'kraken': 88490, ...},
                'spread': 0.02,  # % difference between high and low
                'exchanges_reporting': 4
            }
        """
        prices = {}

        for name, exchange in self.exchanges.items():
            try:
                # Map symbol for each exchange if needed
                ticker = exchange.fetch_ticker(symbol)
                if ticker and ticker.get('last'):
                    prices[name] = ticker['last']
            except Exception as e:
                print(f"  {name}: {e}")
                continue

        if not prices:
            return {'error': 'No prices available', 'symbol': symbol}

        price_list = list(prices.values())
        consensus = median(price_list)
        spread = (max(price_list) - min(price_list)) / consensus * 100

        return {
            'symbol': symbol,
            'consensus_price': consensus,
            'mean_price': mean(price_list),
            'prices': prices,
            'spread_pct': round(spread, 4),
            'exchanges_reporting': len(prices)
        }

    def get_all_prices(self, symbols: List[str] = None) -> Dict:
        """Get consensus prices for multiple symbols."""
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']

        results = {}
        for symbol in symbols:
            results[symbol] = self.get_consensus_price(symbol)

        return results

    def get_total_balance(self) -> Dict:
        """Get aggregated balance across all exchanges."""
        total = {}
        by_exchange = {}

        for name, exchange in self.exchanges.items():
            try:
                balance = exchange.fetch_balance()
                by_exchange[name] = {}

                for currency, amount in balance['total'].items():
                    if amount and amount > 0:
                        by_exchange[name][currency] = amount
                        total[currency] = total.get(currency, 0) + amount
            except Exception as e:
                print(f"  {name} balance error: {e}")

        return {
            'total': total,
            'by_exchange': by_exchange
        }


# Quick test
if __name__ == '__main__':
    print("=== EXCHANGE CONSENSUS ===\n")

    ec = ExchangeConsensus()

    print("\n=== BTC CONSENSUS PRICE ===")
    btc = ec.get_consensus_price('BTC/USDT')
    print(f"Consensus: ${btc.get('consensus_price', 'N/A'):,.2f}")
    print(f"Spread: {btc.get('spread_pct', 'N/A')}%")
    print(f"By exchange: {btc.get('prices', {})}")

    print("\n=== ALL PRICES ===")
    all_prices = ec.get_all_prices()
    for sym, data in all_prices.items():
        print(f"{sym}: ${data.get('consensus_price', 0):,.2f} (spread: {data.get('spread_pct', 0)}%)")
