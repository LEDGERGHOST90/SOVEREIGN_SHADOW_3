#!/usr/bin/env python3
"""
FUNDING RATE ARBITRAGE - Delta-Neutral Yield Strategy
======================================================
Based on research from GitHub swarm (Jane Street style strategies)

Strategy: Long Spot + Short Perpetual = Capture Funding Payments
Expected APY: 10-25% (after fees)
Risk: Market-neutral when properly hedged

Sources:
- ynhy513/funding-rate-arbitrage (best risk management)
- aoki-h-jp/funding-rate-arbitrage (multi-exchange scanner)
- 50shadesofgwei/funding-rate-arbitrage (backtest framework)

Usage:
    from core.strategies.funding_arb import FundingArbScanner
    scanner = FundingArbScanner()
    opportunities = scanner.scan_all()
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try to import ccxt for exchange data
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False


@dataclass
class FundingOpportunity:
    """Represents a funding rate arbitrage opportunity"""
    symbol: str
    exchange: str
    funding_rate: float  # Current rate (per 8h)
    annualized_rate: float  # APY
    next_funding_time: datetime
    spot_price: float
    perp_price: float
    basis_spread: float  # % difference spot vs perp
    estimated_apy_after_fees: float
    direction: str  # "POSITIVE" (short perp) or "NEGATIVE" (long perp)
    confidence: float  # 0-1
    timestamp: datetime


@dataclass
class Position:
    """Active funding arb position"""
    symbol: str
    spot_qty: float
    perp_qty: float
    entry_spot_price: float
    entry_perp_price: float
    entry_time: datetime
    total_funding_earned: float
    fees_paid: float
    current_pnl: float


class FundingArbScanner:
    """
    Scans multiple exchanges for funding rate arbitrage opportunities.

    Key metrics:
    - Funding rate > 0.01% per 8h = ~10% APY
    - Funding rate > 0.03% per 8h = ~30% APY
    - Must account for: trading fees, spread, rebalancing costs
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()

        # Exchange clients
        self.exchanges = {}
        if CCXT_AVAILABLE:
            self._init_exchanges()

        # Thresholds
        self.min_funding_rate = 0.0001  # 0.01% per 8h (~10% APY)
        self.min_apy_after_fees = 0.10  # 10% minimum
        self.max_basis_spread = 0.005  # 0.5% max spot-perp divergence

        # Fee assumptions (conservative)
        self.fees = {
            'binance': {'maker': 0.0002, 'taker': 0.0004},
            'bybit': {'maker': 0.0001, 'taker': 0.0006},
            'okx': {'maker': 0.0002, 'taker': 0.0005},
        }

        # NTFY for alerts
        self.ntfy_topic = "sovereignshadow_dc4d2fa1"

        print("=" * 60)
        print("FUNDING RATE ARBITRAGE SCANNER")
        print("=" * 60)
        print(f"Min APY threshold: {self.min_apy_after_fees:.0%}")
        print(f"Exchanges: {list(self.fees.keys())}")
        print("=" * 60)

    def _default_config(self) -> Dict:
        return {
            'symbols': ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'AVAX', 'LINK'],
            'exchanges': ['binance', 'bybit', 'okx'],
            'check_interval': 300,  # 5 minutes
            'alert_threshold_apy': 0.15,  # Alert if >15% APY
        }

    def _init_exchanges(self):
        """Initialize CCXT exchange clients"""
        for exchange_id in self.config['exchanges']:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                self.exchanges[exchange_id] = exchange_class({
                    'enableRateLimit': True,
                })
                print(f"[OK] {exchange_id} initialized")
            except Exception as e:
                print(f"[WARN] {exchange_id} failed: {e}")

    def get_funding_rate_binance(self, symbol: str) -> Optional[Dict]:
        """Get funding rate from Binance Futures"""
        try:
            # Binance public API
            url = f"https://fapi.binance.com/fapi/v1/premiumIndex"
            params = {'symbol': f"{symbol}USDT"}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'lastFundingRate' not in data:
                return None

            funding_rate = float(data['lastFundingRate'])
            mark_price = float(data['markPrice'])
            next_funding = datetime.fromtimestamp(int(data['nextFundingTime']) / 1000)

            # Get spot price
            spot_url = f"https://api.binance.com/api/v3/ticker/price"
            spot_response = requests.get(spot_url, params={'symbol': f"{symbol}USDT"}, timeout=10)
            spot_price = float(spot_response.json()['price'])

            # Calculate basis spread
            basis_spread = (mark_price - spot_price) / spot_price

            # Annualized rate (3 funding periods per day * 365)
            annualized = funding_rate * 3 * 365

            # Estimate APY after fees (entry + exit = 4 trades)
            total_fees = self.fees['binance']['taker'] * 4  # Conservative: all taker
            apy_after_fees = annualized - total_fees

            return {
                'exchange': 'binance',
                'symbol': symbol,
                'funding_rate': funding_rate,
                'annualized_rate': annualized,
                'next_funding_time': next_funding,
                'spot_price': spot_price,
                'perp_price': mark_price,
                'basis_spread': basis_spread,
                'estimated_apy_after_fees': apy_after_fees,
            }

        except Exception as e:
            print(f"[ERROR] Binance {symbol}: {e}")
            return None

    def get_funding_rate_bybit(self, symbol: str) -> Optional[Dict]:
        """Get funding rate from Bybit"""
        try:
            # Bybit public API
            url = "https://api.bybit.com/v5/market/tickers"
            params = {'category': 'linear', 'symbol': f"{symbol}USDT"}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data['retCode'] != 0 or not data['result']['list']:
                return None

            ticker = data['result']['list'][0]
            funding_rate = float(ticker['fundingRate'])
            mark_price = float(ticker['markPrice'])

            # Get next funding time
            next_funding = datetime.now() + timedelta(hours=8 - (datetime.now().hour % 8))

            # Spot price (use mark as approximation)
            spot_price = float(ticker['lastPrice'])
            basis_spread = (mark_price - spot_price) / spot_price

            annualized = funding_rate * 3 * 365
            total_fees = self.fees['bybit']['taker'] * 4
            apy_after_fees = annualized - total_fees

            return {
                'exchange': 'bybit',
                'symbol': symbol,
                'funding_rate': funding_rate,
                'annualized_rate': annualized,
                'next_funding_time': next_funding,
                'spot_price': spot_price,
                'perp_price': mark_price,
                'basis_spread': basis_spread,
                'estimated_apy_after_fees': apy_after_fees,
            }

        except Exception as e:
            print(f"[ERROR] Bybit {symbol}: {e}")
            return None

    def scan_symbol(self, symbol: str) -> List[FundingOpportunity]:
        """Scan all exchanges for a single symbol"""
        opportunities = []

        # Binance
        binance_data = self.get_funding_rate_binance(symbol)
        if binance_data and abs(binance_data['funding_rate']) >= self.min_funding_rate:
            direction = "POSITIVE" if binance_data['funding_rate'] > 0 else "NEGATIVE"
            confidence = min(abs(binance_data['estimated_apy_after_fees']) / 0.30, 1.0)

            opp = FundingOpportunity(
                symbol=symbol,
                exchange='binance',
                funding_rate=binance_data['funding_rate'],
                annualized_rate=binance_data['annualized_rate'],
                next_funding_time=binance_data['next_funding_time'],
                spot_price=binance_data['spot_price'],
                perp_price=binance_data['perp_price'],
                basis_spread=binance_data['basis_spread'],
                estimated_apy_after_fees=binance_data['estimated_apy_after_fees'],
                direction=direction,
                confidence=confidence,
                timestamp=datetime.now()
            )
            opportunities.append(opp)

        # Bybit
        bybit_data = self.get_funding_rate_bybit(symbol)
        if bybit_data and abs(bybit_data['funding_rate']) >= self.min_funding_rate:
            direction = "POSITIVE" if bybit_data['funding_rate'] > 0 else "NEGATIVE"
            confidence = min(abs(bybit_data['estimated_apy_after_fees']) / 0.30, 1.0)

            opp = FundingOpportunity(
                symbol=symbol,
                exchange='bybit',
                funding_rate=bybit_data['funding_rate'],
                annualized_rate=bybit_data['annualized_rate'],
                next_funding_time=bybit_data['next_funding_time'],
                spot_price=bybit_data['spot_price'],
                perp_price=bybit_data['perp_price'],
                basis_spread=bybit_data['basis_spread'],
                estimated_apy_after_fees=bybit_data['estimated_apy_after_fees'],
                direction=direction,
                confidence=confidence,
                timestamp=datetime.now()
            )
            opportunities.append(opp)

        return opportunities

    def scan_all(self) -> List[FundingOpportunity]:
        """Scan all symbols across all exchanges"""
        all_opportunities = []

        print(f"\n[SCAN] {datetime.now().strftime('%H:%M:%S')} - Scanning {len(self.config['symbols'])} symbols...")

        for symbol in self.config['symbols']:
            opps = self.scan_symbol(symbol)
            all_opportunities.extend(opps)
            time.sleep(0.2)  # Rate limiting

        # Filter by minimum APY
        filtered = [o for o in all_opportunities if abs(o.estimated_apy_after_fees) >= self.min_apy_after_fees]

        # Sort by APY (absolute value for both positive and negative funding)
        filtered.sort(key=lambda x: abs(x.estimated_apy_after_fees), reverse=True)

        return filtered

    def print_opportunities(self, opportunities: List[FundingOpportunity]):
        """Print formatted opportunity table"""
        if not opportunities:
            print("\n[INFO] No opportunities above threshold")
            return

        print("\n" + "=" * 80)
        print("FUNDING ARBITRAGE OPPORTUNITIES")
        print("=" * 80)
        print(f"{'Symbol':<8} {'Exchange':<10} {'Rate/8h':<10} {'APY':<10} {'After Fees':<12} {'Direction':<10}")
        print("-" * 80)

        for opp in opportunities:
            rate_pct = f"{opp.funding_rate * 100:.4f}%"
            apy_pct = f"{opp.annualized_rate * 100:.1f}%"
            after_fees = f"{opp.estimated_apy_after_fees * 100:.1f}%"

            # Color coding (via emoji)
            if opp.estimated_apy_after_fees >= 0.20:
                icon = "🔥"
            elif opp.estimated_apy_after_fees >= 0.15:
                icon = "🟢"
            else:
                icon = "🟡"

            print(f"{icon} {opp.symbol:<6} {opp.exchange:<10} {rate_pct:<10} {apy_pct:<10} {after_fees:<12} {opp.direction:<10}")

        print("=" * 80)
        print(f"Strategy: {opportunities[0].direction} = ", end="")
        if opportunities[0].direction == "POSITIVE":
            print("Long Spot + Short Perp (receive funding)")
        else:
            print("Short Spot + Long Perp (receive funding)")

    def send_alert(self, opp: FundingOpportunity):
        """Send NTFY alert for high-APY opportunity"""
        try:
            message = f"{opp.symbol} on {opp.exchange}: {opp.estimated_apy_after_fees*100:.1f}% APY\n"
            message += f"Funding: {opp.funding_rate*100:.4f}% per 8h\n"
            message += f"Direction: {opp.direction}"

            requests.post(
                f"https://ntfy.sh/{self.ntfy_topic}",
                data=message.encode('utf-8'),
                headers={
                    "Title": f"Funding Arb: {opp.symbol} {opp.estimated_apy_after_fees*100:.0f}% APY",
                    "Priority": "high" if opp.estimated_apy_after_fees >= 0.25 else "default",
                    "Tags": "chart_with_upwards_trend,money_with_wings"
                },
                timeout=5
            )
        except Exception as e:
            print(f"[WARN] Alert failed: {e}")

    def calculate_position_size(
        self,
        capital: float,
        opp: FundingOpportunity,
        max_allocation: float = 0.15
    ) -> Dict:
        """
        Calculate optimal position size for funding arb.

        Args:
            capital: Total available capital
            opp: Funding opportunity
            max_allocation: Max % of capital per position (default 15%)

        Returns:
            Position sizing details
        """
        # Max position for this opportunity
        max_position = capital * max_allocation

        # Split between spot and perp (equal notional)
        spot_allocation = max_position / 2
        perp_allocation = max_position / 2

        # Calculate quantities
        spot_qty = spot_allocation / opp.spot_price
        perp_qty = perp_allocation / opp.perp_price

        # Estimate fees for entry
        entry_fees = (spot_allocation + perp_allocation) * self.fees.get(opp.exchange, {}).get('taker', 0.0005)

        # Expected 8h funding payment
        funding_payment = perp_allocation * abs(opp.funding_rate)

        # Break-even time (hours to recover entry fees)
        if funding_payment > 0:
            breakeven_hours = (entry_fees / funding_payment) * 8
        else:
            breakeven_hours = float('inf')

        return {
            'total_capital': max_position,
            'spot_allocation': spot_allocation,
            'perp_allocation': perp_allocation,
            'spot_qty': spot_qty,
            'perp_qty': perp_qty,
            'entry_fees': entry_fees,
            'expected_funding_8h': funding_payment,
            'breakeven_hours': breakeven_hours,
            'estimated_daily_yield': funding_payment * 3,
            'estimated_monthly_yield': funding_payment * 3 * 30,
        }

    def run_continuous(self, interval: int = 300):
        """Run continuous scanning loop"""
        print(f"\n[START] Continuous scan every {interval}s")
        print("Press Ctrl+C to stop\n")

        alert_threshold = self.config.get('alert_threshold_apy', 0.15)

        try:
            while True:
                opportunities = self.scan_all()
                self.print_opportunities(opportunities)

                # Send alerts for high-APY opportunities
                for opp in opportunities:
                    if opp.estimated_apy_after_fees >= alert_threshold:
                        self.send_alert(opp)

                # Save to log
                self._save_scan_log(opportunities)

                print(f"\n[SLEEP] Next scan in {interval}s...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[STOP] Scanner stopped")

    def _save_scan_log(self, opportunities: List[FundingOpportunity]):
        """Save scan results to log file"""
        log_dir = PROJECT_ROOT / "logs" / "funding_arb"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"scan_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        with open(log_file, 'a') as f:
            for opp in opportunities:
                record = asdict(opp)
                record['next_funding_time'] = opp.next_funding_time.isoformat()
                record['timestamp'] = opp.timestamp.isoformat()
                f.write(json.dumps(record) + '\n')


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Funding Rate Arbitrage Scanner")
    parser.add_argument("--scan", action="store_true", help="Run single scan")
    parser.add_argument("--continuous", action="store_true", help="Run continuous scanning")
    parser.add_argument("--interval", type=int, default=300, help="Scan interval in seconds")
    parser.add_argument("--symbol", type=str, help="Scan specific symbol")

    args = parser.parse_args()

    scanner = FundingArbScanner()

    if args.symbol:
        opps = scanner.scan_symbol(args.symbol.upper())
        scanner.print_opportunities(opps)
    elif args.continuous:
        scanner.run_continuous(interval=args.interval)
    else:
        # Default: single scan
        opps = scanner.scan_all()
        scanner.print_opportunities(opps)

        if opps:
            print("\n[POSITION SIZING] Example for top opportunity:")
            sizing = scanner.calculate_position_size(1000, opps[0])
            print(f"  Capital: ${sizing['total_capital']:.2f}")
            print(f"  Spot: ${sizing['spot_allocation']:.2f} ({sizing['spot_qty']:.6f} units)")
            print(f"  Perp: ${sizing['perp_allocation']:.2f} ({sizing['perp_qty']:.6f} units)")
            print(f"  Entry fees: ${sizing['entry_fees']:.2f}")
            print(f"  Expected daily yield: ${sizing['estimated_daily_yield']:.2f}")
            print(f"  Break-even: {sizing['breakeven_hours']:.1f} hours")


if __name__ == "__main__":
    main()
