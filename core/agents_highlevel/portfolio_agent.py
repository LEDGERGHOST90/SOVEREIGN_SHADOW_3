#!/usr/bin/env python3
"""
🏴 Portfolio Agent - Sovereign Shadow II
Uses: existing database + unified_portfolio_api.py
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add core/portfolio to path
sys.path.append(str(Path(__file__).parent.parent / 'core' / 'portfolio'))

class PortfolioAgent:
    """Portfolio analysis using existing infrastructure"""

    def __init__(self):
        self.name = "Portfolio Deep Agent"
        print(f"✅ {self.name} initialized")

    def get_live_portfolio(self):
        """Fetch from mcp_portfolio_context.json (already generated)"""
        try:
            # Read the MCP portfolio context file
            context_file = Path(__file__).parent.parent / 'core' / 'portfolio' / 'logs' / 'mcp_portfolio_context.json'

            with open(context_file, 'r') as f:
                data = json.load(f)

            snapshot = data['portfolio_snapshot']

            return {
                'total_value': snapshot['total_portfolio_value_usd'],
                'ledger_value': snapshot['breakdown']['ledger_hardware_wallet'],
                'metamask_value': snapshot['breakdown']['metamask_hot_wallet'],
                'exchange_value': snapshot['breakdown']['exchange_wallets'],
                'aave_health': snapshot['components']['defi_positions']['health_factor'],
                'aave_net_value': snapshot['components']['defi_positions']['position_value_usd'],
                'btc_cold_storage': snapshot['components']['ledger_cold_storage']['balances']['btc']['value_usd'],
                'timestamp': datetime.now().isoformat()
            }

        except FileNotFoundError:
            print(f"⚠️ MCP context file not found. Running unified_portfolio_api.py...")
            # Run the API to generate fresh data
            import subprocess
            subprocess.run(['python3', 'core/portfolio/unified_portfolio_api.py'], check=True)
            # Try again
            return self.get_live_portfolio()

        except Exception as e:
            print(f"❌ Portfolio fetch error: {e}")
            return None

    def analyze_allocation(self, portfolio):
        """Analyze current vs target allocation"""
        if not portfolio:
            return []

        total_value = portfolio['total_value']

        # Current allocation
        current = {
            'BTC': portfolio['btc_cold_storage'],
            'AAVE': portfolio['aave_net_value'],
            'ETH': portfolio['ledger_value'] - portfolio['btc_cold_storage'] - portfolio['aave_net_value'],
            'Exchanges': portfolio['exchange_value']
        }

        # Target allocation: 40% BTC, 30% ETH, 20% SOL, 10% XRP
        target = {
            'BTC': total_value * 0.40,
            'ETH': total_value * 0.30,
            'SOL': total_value * 0.20,
            'XRP': total_value * 0.10
        }

        recommendations = []

        for asset, target_value in target.items():
            current_value = current.get(asset, 0)
            delta = target_value - current_value
            delta_pct = (delta / total_value) * 100 if total_value > 0 else 0

            if abs(delta_pct) > 5:  # >5% difference
                action = 'BUY' if delta > 0 else 'SELL'
                recommendations.append({
                    'asset': asset,
                    'action': action,
                    'amount_usd': abs(delta),
                    'delta_pct': abs(delta_pct),
                    'current_allocation_pct': (current_value / total_value * 100) if total_value > 0 else 0,
                    'target_allocation_pct': (target_value / total_value * 100) if total_value > 0 else 0,
                    'priority': abs(delta_pct) / 100  # Higher % difference = higher priority
                })

        # Sort by priority (highest first)
        recommendations.sort(key=lambda x: x['priority'], reverse=True)

        return recommendations

    def calculate_metrics(self, portfolio):
        """Calculate portfolio metrics"""
        if not portfolio:
            return None

        total_value = portfolio['total_value']

        # Diversification score (0-1, higher = more diversified)
        allocations = [
            portfolio['btc_cold_storage'] / total_value if total_value > 0 else 0,
            portfolio['aave_net_value'] / total_value if total_value > 0 else 0,
            (portfolio['ledger_value'] - portfolio['btc_cold_storage'] - portfolio['aave_net_value']) / total_value if total_value > 0 else 0,
            portfolio['exchange_value'] / total_value if total_value > 0 else 0
        ]

        # Herfindahl index (concentration measure)
        herfindahl = sum(a**2 for a in allocations)
        diversification_score = 1 - herfindahl

        return {
            'total_value_usd': total_value,
            'diversification_score': diversification_score,
            'cold_storage_pct': (portfolio['ledger_value'] / total_value * 100) if total_value > 0 else 0,
            'hot_exchange_pct': (portfolio['exchange_value'] / total_value * 100) if total_value > 0 else 0,
            'defi_exposure_pct': (portfolio['aave_net_value'] / total_value * 100) if total_value > 0 else 0,
            'aave_health_factor': portfolio['aave_health'],
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self):
        """Complete portfolio analysis report"""
        print(f"\n{'='*70}")
        print(f"📊 {self.name.upper()} - PORTFOLIO ANALYSIS")
        print(f"{'='*70}\n")

        # Get live data
        portfolio = self.get_live_portfolio()
        if not portfolio:
            print("❌ Unable to fetch portfolio data")
            return None

        # Calculate metrics
        metrics = self.calculate_metrics(portfolio)

        # Get recommendations
        recommendations = self.analyze_allocation(portfolio)

        # Display report
        print(f"💰 Total Portfolio Value: ${portfolio['total_value']:,.2f}")
        print(f"🔐 Ledger Cold Storage: ${portfolio['ledger_value']:,.2f} ({metrics['cold_storage_pct']:.1f}%)")
        print(f"💱 Exchange Wallets: ${portfolio['exchange_value']:,.2f} ({metrics['hot_exchange_pct']:.1f}%)")
        print(f"🏦 AAVE DeFi: ${portfolio['aave_net_value']:,.2f} ({metrics['defi_exposure_pct']:.1f}%)")
        print(f"📊 AAVE Health Factor: {portfolio['aave_health']}")
        print(f"🎯 Diversification Score: {metrics['diversification_score']:.2f}/1.00")

        print(f"\n💡 REBALANCING RECOMMENDATIONS:")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec['action']} ${rec['amount_usd']:,.2f} {rec['asset']}")
                print(f"     Current: {rec['current_allocation_pct']:.1f}% → Target: {rec['target_allocation_pct']:.1f}%")
                print(f"     Delta: {rec['delta_pct']:.1f}% | Priority: {rec['priority']:.2f}")
        else:
            print("  ✅ Portfolio is well-balanced")

        print(f"\n{'='*70}")

        return {
            'portfolio': portfolio,
            'metrics': metrics,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    agent = PortfolioAgent()
    report = agent.generate_report()

    if report:
        # Save report to file
        output_file = Path(__file__).parent.parent / 'logs' / 'portfolio_agent_report.json'
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Report saved to: {output_file}")
