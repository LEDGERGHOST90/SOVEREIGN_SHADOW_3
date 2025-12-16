"""
Portfolio Aggregator
Combines exchange balances + manual ledger entries + live prices
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .exchange_clients import CoinbaseClient, KrakenClient, OKXClient, BinanceUSClient
from .ledger import LedgerService
from .ledger_wallets import LedgerWalletClient
from ds_star.data_feeds.cex_client import CEXClient


class PortfolioAggregator:
    """Aggregates holdings from all sources with live pricing."""
    
    def __init__(self):
        self.coinbase = CoinbaseClient()
        self.kraken = KrakenClient()
        self.okx = OKXClient()
        self.binance_us = BinanceUSClient()
        self.ledger_wallet = LedgerWalletClient()
        self.ledger = LedgerService()
        self.price_cache: Dict[str, float] = {}
        self.last_refresh: Optional[str] = None
    
    def get_exchange_status(self) -> Dict[str, bool]:
        """Check which exchanges are configured."""
        return {
            'coinbase': self.coinbase.is_configured(),
            'kraken': self.kraken.is_configured(),
            'okx': self.okx.is_configured(),
            'binance_us': self.binance_us.is_configured(),
            'ledger': self.ledger_wallet.is_configured()
        }
    
    def fetch_all_holdings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch holdings from all configured exchanges and ledger."""
        holdings = {
            'coinbase': [],
            'kraken': [],
            'okx': [],
            'binance_us': [],
            'ledger': [],
            'manual': []
        }
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}
            
            if self.coinbase.is_configured():
                futures[executor.submit(self.coinbase.get_accounts)] = 'coinbase'
            if self.kraken.is_configured():
                futures[executor.submit(self.kraken.get_balances)] = 'kraken'
            if self.okx.is_configured():
                futures[executor.submit(self.okx.get_balances)] = 'okx'
            if self.binance_us.is_configured():
                futures[executor.submit(self.binance_us.get_balances)] = 'binance_us'
            if self.ledger_wallet.is_configured():
                futures[executor.submit(self.ledger_wallet.get_all_balances)] = 'ledger'
            
            for future in as_completed(futures):
                source = futures[future]
                try:
                    result = future.result()
                    holdings[source] = result
                except Exception as e:
                    print(f"Error fetching {source}: {e}")
        
        holdings['manual'] = self.ledger.get_all_entries()
        self.last_refresh = datetime.now().isoformat()
        
        return holdings
    
    def get_live_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get live prices for symbols."""
        prices = {}
        
        for symbol in symbols:
            if symbol.upper() in ['USD', 'USDC', 'USDT', 'DAI', 'BUSD']:
                prices[symbol.upper()] = 1.0
                continue
            
            try:
                price_data = CEXClient.get_coinbase_price(symbol)
                if price_data:
                    prices[symbol.upper()] = price_data['price']
                else:
                    price_data = CEXClient.get_coingecko_price(symbol)
                    if price_data:
                        prices[symbol.upper()] = price_data['price']
            except:
                pass
        
        self.price_cache.update(prices)
        return prices
    
    def get_portfolio_summary(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get complete portfolio summary with valuations."""
        holdings_by_source = self.fetch_all_holdings()
        
        all_holdings: List[Dict[str, Any]] = []
        all_symbols = set()
        
        for source, items in holdings_by_source.items():
            for item in items:
                symbol = item.get('symbol', '').upper()
                if symbol and symbol not in ['USD']:
                    all_symbols.add(symbol)
                    all_holdings.append({
                        'symbol': symbol,
                        'amount': item.get('amount', 0),
                        'source': source,
                        'cost_basis': item.get('cost_basis'),
                        'notes': item.get('notes', '')
                    })
        
        prices = self.get_live_prices(list(all_symbols))
        
        aggregated: Dict[str, Dict[str, Any]] = {}
        for holding in all_holdings:
            symbol = holding['symbol']
            price = prices.get(symbol, 0)
            amount = holding['amount']
            value = price * amount
            
            if symbol not in aggregated:
                aggregated[symbol] = {
                    'symbol': symbol,
                    'total_amount': 0,
                    'usd_value': 0,
                    'price': price,
                    'sources': [],
                    'cost_basis': 0
                }
            
            aggregated[symbol]['total_amount'] += amount
            aggregated[symbol]['usd_value'] += value
            aggregated[symbol]['sources'].append({
                'source': holding['source'],
                'amount': amount,
                'value': value
            })
            if holding.get('cost_basis'):
                aggregated[symbol]['cost_basis'] += holding['cost_basis']
        
        holdings_list = list(aggregated.values())
        holdings_list.sort(key=lambda x: x['usd_value'], reverse=True)
        
        total_value = sum(h['usd_value'] for h in holdings_list)
        total_cost_basis = sum(h['cost_basis'] for h in holdings_list)
        
        for h in holdings_list:
            h['allocation_pct'] = (h['usd_value'] / total_value * 100) if total_value > 0 else 0
            h['unrealized_pnl'] = h['usd_value'] - h['cost_basis'] if h['cost_basis'] > 0 else None
        
        source_totals = {}
        for source in ['coinbase', 'kraken', 'okx', 'binance_us', 'ledger', 'manual']:
            source_value = sum(
                s['value'] for h in holdings_list for s in h['sources'] if s['source'] == source
            )
            if source_value > 0:
                source_totals[source] = {
                    'usd_value': source_value,
                    'pct': (source_value / total_value * 100) if total_value > 0 else 0
                }
        
        exchange_status = self.get_exchange_status()
        
        return {
            'net_worth': round(total_value, 2),
            'total_cost_basis': round(total_cost_basis, 2),
            'unrealized_pnl': round(total_value - total_cost_basis, 2) if total_cost_basis > 0 else None,
            'holdings': holdings_list,
            'sources': source_totals,
            'exchange_status': exchange_status,
            'last_refresh': self.last_refresh,
            'asset_count': len(holdings_list)
        }
    
    def get_holdings_by_source(self) -> Dict[str, Any]:
        """Get raw holdings organized by source."""
        holdings = self.fetch_all_holdings()
        return {
            'holdings': holdings,
            'exchange_status': self.get_exchange_status(),
            'last_refresh': self.last_refresh
        }
