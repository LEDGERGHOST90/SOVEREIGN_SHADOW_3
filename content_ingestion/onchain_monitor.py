#!/usr/bin/env python3
"""
On-Chain Analytics & Sniper Monitor
Tracks whale movements, DEX activity, and new token launches

Features:
- Whale wallet tracking
- DEX volume spikes
- New token detection (for sniping)
- Large transaction alerts
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

BASE_DIR = Path('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/content_ingestion')
ONCHAIN_DIR = BASE_DIR / 'onchain'
ONCHAIN_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class WhaleAlert:
    """Large transaction alert"""
    chain: str
    tx_hash: str
    amount_usd: float
    token: str
    from_type: str  # "exchange", "whale", "unknown"
    to_type: str
    timestamp: str
    signal: str  # "accumulation", "distribution", "transfer"


@dataclass
class NewToken:
    """New token for potential sniping"""
    chain: str
    address: str
    name: str
    symbol: str
    liquidity_usd: float
    created_at: str
    risk_score: int  # 0-100 (higher = riskier)
    honeypot_check: bool
    snipe_eligible: bool


class OnChainMonitor:
    """
    Monitor on-chain activity for trading signals
    Uses free APIs: DeFiLlama, Etherscan, DEXScreener
    """

    def __init__(self):
        self.cache_dir = ONCHAIN_DIR
        self.etherscan_key = os.getenv('ETHERSCAN_API_KEY', '')

    # =========================================================================
    # DEX ACTIVITY (via DeFiLlama - FREE)
    # =========================================================================

    def get_dex_volumes(self) -> Dict:
        """
        Get DEX trading volumes from DeFiLlama
        Free, no API key needed
        """
        try:
            url = "https://api.llama.fi/overview/dexs"
            response = requests.get(url, timeout=15)
            data = response.json()

            # Get top DEXes by 24h volume
            dexes = []
            for protocol in data.get('protocols', [])[:20]:
                dexes.append({
                    'name': protocol.get('name'),
                    'volume_24h': protocol.get('total24h', 0),
                    'change_24h': protocol.get('change_1d', 0),
                    'chains': protocol.get('chains', [])
                })

            return {
                'timestamp': datetime.now().isoformat(),
                'total_volume_24h': data.get('total24h', 0),
                'total_change_24h': data.get('change_1d', 0),
                'top_dexes': sorted(dexes, key=lambda x: x['volume_24h'], reverse=True)[:10]
            }
        except Exception as e:
            print(f"DEX volumes error: {e}")
            return {}

    def get_chain_tvl(self) -> Dict:
        """
        Get TVL by chain from DeFiLlama
        Shows where money is flowing
        """
        try:
            url = "https://api.llama.fi/v2/chains"
            response = requests.get(url, timeout=15)
            data = response.json()

            chains = []
            for chain in data[:15]:
                chains.append({
                    'name': chain.get('name'),
                    'tvl': chain.get('tvl', 0),
                    'change_1d': chain.get('change_1d', 0),
                    'change_7d': chain.get('change_7d', 0)
                })

            # Find chains with biggest inflows
            hot_chains = [c for c in chains if c.get('change_1d', 0) > 5]
            cold_chains = [c for c in chains if c.get('change_1d', 0) < -5]

            return {
                'timestamp': datetime.now().isoformat(),
                'chains': chains,
                'hot_chains': hot_chains,  # TVL increasing
                'cold_chains': cold_chains  # TVL decreasing
            }
        except Exception as e:
            print(f"Chain TVL error: {e}")
            return {}

    # =========================================================================
    # NEW TOKEN SCANNER (for sniping) - via DEXScreener
    # =========================================================================

    def scan_new_tokens(self, chain: str = 'solana', min_liquidity: float = 1000) -> List[NewToken]:
        """
        Scan for newly created tokens on DEXScreener
        For snipe opportunities

        Args:
            chain: 'solana', 'ethereum', 'bsc'
            min_liquidity: Minimum liquidity in USD
        """
        try:
            # DEXScreener API - free
            url = f"https://api.dexscreener.com/latest/dex/tokens/new/{chain}"
            response = requests.get(url, timeout=15)

            # If that endpoint doesn't work, try search
            if response.status_code != 200:
                url = f"https://api.dexscreener.com/latest/dex/search?q={chain}"
                response = requests.get(url, timeout=15)

            data = response.json()
            pairs = data.get('pairs', [])

            new_tokens = []
            for pair in pairs[:50]:
                # Filter by liquidity
                liquidity = pair.get('liquidity', {}).get('usd', 0)
                if liquidity < min_liquidity:
                    continue

                # Calculate age
                created = pair.get('pairCreatedAt')
                if created:
                    age_hours = (datetime.now().timestamp() * 1000 - created) / (1000 * 60 * 60)
                else:
                    age_hours = 999

                # Only tokens < 24 hours old
                if age_hours > 24:
                    continue

                # Risk assessment
                risk_score = self._calculate_risk_score(pair)

                token = NewToken(
                    chain=chain,
                    address=pair.get('baseToken', {}).get('address', ''),
                    name=pair.get('baseToken', {}).get('name', 'Unknown'),
                    symbol=pair.get('baseToken', {}).get('symbol', '???'),
                    liquidity_usd=liquidity,
                    created_at=datetime.fromtimestamp(created/1000).isoformat() if created else 'unknown',
                    risk_score=risk_score,
                    honeypot_check=risk_score < 70,  # Basic check
                    snipe_eligible=liquidity >= min_liquidity and risk_score < 80
                )
                new_tokens.append(token)

            return sorted(new_tokens, key=lambda x: x.liquidity_usd, reverse=True)

        except Exception as e:
            print(f"New token scan error: {e}")
            return []

    def _calculate_risk_score(self, pair: Dict) -> int:
        """
        Calculate risk score for new token (0-100)
        Higher = riskier
        """
        score = 50  # Base risk

        liquidity = pair.get('liquidity', {}).get('usd', 0)
        volume_24h = pair.get('volume', {}).get('h24', 0)
        price_change = pair.get('priceChange', {}).get('h24', 0)
        txns = pair.get('txns', {}).get('h24', {})
        buys = txns.get('buys', 0)
        sells = txns.get('sells', 0)

        # Low liquidity = higher risk
        if liquidity < 5000:
            score += 20
        elif liquidity < 10000:
            score += 10

        # Very high price increase = pump risk
        if price_change and price_change > 500:
            score += 15

        # Buy/sell ratio (lots of buys, few sells = potential rug)
        if buys > 0 and sells > 0:
            ratio = buys / sells
            if ratio > 10:  # 10x more buys than sells
                score += 20

        # No sells at all = red flag
        if sells == 0 and buys > 10:
            score += 25

        return min(100, max(0, score))

    # =========================================================================
    # WHALE TRACKING
    # =========================================================================

    def get_whale_transactions(self, min_usd: float = 100000) -> List[Dict]:
        """
        Get large transactions from Whale Alert API
        Free tier: limited calls
        """
        try:
            # Use whale-alert.io free API or alternative
            url = "https://api.whale-alert.io/v1/transactions"
            params = {
                'api_key': os.getenv('WHALE_ALERT_KEY', ''),
                'min_value': min_usd,
                'limit': 20
            }

            # If no API key, use alternative data source
            if not params['api_key']:
                return self._get_whale_transactions_alternative()

            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            transactions = []
            for tx in data.get('transactions', []):
                transactions.append({
                    'blockchain': tx.get('blockchain'),
                    'symbol': tx.get('symbol'),
                    'amount': tx.get('amount'),
                    'amount_usd': tx.get('amount_usd'),
                    'from': tx.get('from', {}).get('owner_type', 'unknown'),
                    'to': tx.get('to', {}).get('owner_type', 'unknown'),
                    'timestamp': tx.get('timestamp'),
                    'hash': tx.get('hash')
                })

            return transactions

        except Exception as e:
            print(f"Whale transactions error: {e}")
            return []

    def _get_whale_transactions_alternative(self) -> List[Dict]:
        """
        Alternative whale tracking using public blockchain explorers
        """
        # Placeholder - would scrape from blockchain explorers
        return [{
            'note': 'Whale Alert API key not configured',
            'suggestion': 'Add WHALE_ALERT_KEY to .env for live whale tracking'
        }]

    # =========================================================================
    # TRADING SIGNALS
    # =========================================================================

    def get_onchain_signals(self) -> Dict:
        """
        Generate trading signals from on-chain data
        """
        signals = []

        # DEX volume analysis
        dex_data = self.get_dex_volumes()
        if dex_data.get('total_change_24h', 0) > 20:
            signals.append({
                'type': 'DEX_VOLUME_SPIKE',
                'action': 'INCREASED_ACTIVITY',
                'change': dex_data['total_change_24h'],
                'reason': 'DEX volume up significantly - market active'
            })

        # Chain TVL flows
        tvl_data = self.get_chain_tvl()
        for chain in tvl_data.get('hot_chains', []):
            signals.append({
                'type': 'TVL_INFLOW',
                'chain': chain['name'],
                'change': chain['change_1d'],
                'action': 'WATCH_CHAIN',
                'reason': f"{chain['name']} seeing TVL inflows"
            })

        # New token opportunities
        new_tokens = self.scan_new_tokens('solana', min_liquidity=5000)
        snipeable = [t for t in new_tokens if t.snipe_eligible]
        if snipeable:
            signals.append({
                'type': 'SNIPE_OPPORTUNITIES',
                'count': len(snipeable),
                'tokens': [asdict(t) for t in snipeable[:5]],
                'action': 'EVALUATE_FOR_SNIPE'
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'signals': signals,
            'dex_summary': {
                'total_volume_24h': dex_data.get('total_volume_24h', 0),
                'volume_change': dex_data.get('total_change_24h', 0)
            },
            'snipe_candidates': len(snipeable)
        }

    def run_full_scan(self) -> Dict:
        """
        Run complete on-chain analysis
        """
        print("Running on-chain scan...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'dex_volumes': self.get_dex_volumes(),
            'chain_tvl': self.get_chain_tvl(),
            'new_tokens_solana': [asdict(t) for t in self.scan_new_tokens('solana')[:10]],
            'signals': self.get_onchain_signals()
        }

        # Save results
        cache_file = self.cache_dir / 'latest_onchain.json'
        cache_file.write_text(json.dumps(results, indent=2, default=str))

        print(f"Saved to: {cache_file}")
        return results


def main():
    """CLI interface"""
    import sys

    monitor = OnChainMonitor()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == '--snipe':
            chain = sys.argv[2] if len(sys.argv) > 2 else 'solana'
            print(f"\nScanning {chain} for snipe opportunities...")
            tokens = monitor.scan_new_tokens(chain, min_liquidity=5000)
            print(f"Found {len(tokens)} new tokens")
            for t in tokens[:10]:
                status = "SNIPE" if t.snipe_eligible else "RISKY"
                print(f"  [{status}] {t.symbol}: ${t.liquidity_usd:,.0f} liq, risk={t.risk_score}")

        elif cmd == '--signals':
            signals = monitor.get_onchain_signals()
            print(f"\nOn-Chain Signals ({len(signals['signals'])}):")
            for s in signals['signals']:
                print(f"  [{s['type']}] {s.get('action', '')}")
                print(f"    {s.get('reason', '')}")

        elif cmd == '--dex':
            dex = monitor.get_dex_volumes()
            print(f"\nDEX Volume 24h: ${dex.get('total_volume_24h', 0):,.0f}")
            print(f"Change: {dex.get('total_change_24h', 0):+.1f}%")

    else:
        results = monitor.run_full_scan()
        print(f"\nDEX Volume 24h: ${results['dex_volumes'].get('total_volume_24h', 0):,.0f}")
        print(f"Snipe Candidates: {len(results['new_tokens_solana'])}")
        print(f"Signals: {len(results['signals'].get('signals', []))}")


if __name__ == "__main__":
    main()
