#!/usr/bin/env python3
"""
🛡️ Risk Agent - Sovereign Shadow II
Uses: existing AAVE monitor + exchange APIs
"""

import os
import sys
import ccxt
import json
from datetime import datetime
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent / 'modules' / 'safety'))

class RiskAgent:
    """Risk monitoring using existing infrastructure"""

    def __init__(self):
        self.name = "Risk Deep Agent"
        self.max_position_size = 0.25  # 25%
        self.max_daily_exposure = 100  # $100
        self.aave_safe_hf = 1.5  # Health factor threshold

        # Initialize exchanges (use existing API keys)
        self.exchanges = {}
        self._init_exchanges()

        print(f"✅ {self.name} initialized")

    def _init_exchanges(self):
        """Initialize exchange connections"""
        try:
            # OKX
            if os.getenv('OKX_API_KEY'):
                self.exchanges['okx'] = ccxt.okx({
                    'apiKey': os.getenv('OKX_API_KEY'),
                    'secret': os.getenv('OKX_SECRET_KEY'),
                    'password': os.getenv('OKX_PASSPHRASE'),
                    'enableRateLimit': True
                })
                print("  ✅ OKX connected")

            # Binance US
            if os.getenv('BINANCE_US_API_KEY'):
                self.exchanges['binance'] = ccxt.binanceus({
                    'apiKey': os.getenv('BINANCE_US_API_KEY'),
                    'secret': os.getenv('BINANCE_US_SECRET_KEY'),
                    'enableRateLimit': True
                })
                print("  ✅ Binance US connected")

        except Exception as e:
            print(f"  ⚠️ Exchange init warning: {e}")

    def check_aave_risk(self):
        """Monitor AAVE health factor"""
        try:
            from aave_monitor import get_aave_position

            position = get_aave_position()
            health_factor = position.get('health_factor', 0)

            # Risk levels
            if health_factor >= 2.0:
                risk_level = 'SAFE'
                alert_level = '✅'
            elif health_factor >= 1.5:
                risk_level = 'LOW'
                alert_level = '⚠️'
            elif health_factor >= 1.3:
                risk_level = 'WARNING'
                alert_level = '🟠'
            elif health_factor >= 1.1:
                risk_level = 'DANGER'
                alert_level = '🔴'
            else:
                risk_level = 'CRITICAL'
                alert_level = '🚨'

            return {
                'health_factor': health_factor,
                'risk_level': risk_level,
                'alert_level': alert_level,
                'collateral_usd': position.get('collateral_usd', 0),
                'debt_usd': position.get('debt_usd', 0),
                'net_value_usd': position.get('net_value_usd', 0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ AAVE risk check error: {e}")
            return {
                'health_factor': 0,
                'risk_level': 'UNKNOWN',
                'alert_level': '❓',
                'error': str(e)
            }

    def check_exchange_exposure(self):
        """Check balances on hot exchanges"""
        exposure = {
            'exchanges': {},
            'total_usd': 0
        }

        for name, exchange in self.exchanges.items():
            try:
                balance = exchange.fetch_balance()
                total = balance.get('total', {})

                # Convert to USD
                usd_value = 0
                for asset, amount in total.items():
                    if amount > 0:
                        try:
                            ticker = exchange.fetch_ticker(f'{asset}/USDT')
                            usd_value += amount * ticker['last']
                        except:
                            pass  # Asset not traded vs USDT

                exposure['exchanges'][name] = {
                    'usd_value': usd_value,
                    'assets': {k: v for k, v in total.items() if v > 0}
                }
                exposure['total_usd'] += usd_value

            except Exception as e:
                exposure['exchanges'][name] = {
                    'error': str(e),
                    'usd_value': 0
                }

        return exposure

    def calculate_risk_score(self, aave_risk, exchange_exposure, portfolio_value):
        """Calculate overall risk score (0-100, higher = riskier)"""
        score = 0

        # AAVE component (0-40 points)
        hf = aave_risk.get('health_factor', 0)
        if hf < 1.1:
            score += 40
        elif hf < 1.3:
            score += 30
        elif hf < 1.5:
            score += 20
        elif hf < 2.0:
            score += 10

        # Exchange exposure component (0-30 points)
        exchange_pct = (exchange_exposure['total_usd'] / portfolio_value * 100) if portfolio_value > 0 else 0
        if exchange_pct > 50:
            score += 30
        elif exchange_pct > 30:
            score += 20
        elif exchange_pct > 20:
            score += 10

        # Diversification component (0-30 points)
        # Would need portfolio breakdown for this
        # Placeholder for now
        score += 0

        return min(score, 100)

    def generate_warnings(self, aave_risk, exchange_exposure, risk_score):
        """Generate risk warnings"""
        warnings = []

        # AAVE warnings
        hf = aave_risk.get('health_factor', 0)
        if hf < 1.3:
            warnings.append({
                'level': 'CRITICAL',
                'message': f"🚨 AAVE Health Factor critically low: {hf:.2f}",
                'action': 'Add collateral or reduce debt IMMEDIATELY'
            })
        elif hf < 1.5:
            warnings.append({
                'level': 'WARNING',
                'message': f"⚠️ AAVE Health Factor below safe threshold: {hf:.2f}",
                'action': 'Consider adding collateral or reducing debt'
            })

        # Exchange exposure warnings
        if exchange_exposure['total_usd'] > 2000:
            warnings.append({
                'level': 'WARNING',
                'message': f"⚠️ High exchange exposure: ${exchange_exposure['total_usd']:,.2f}",
                'action': 'Move excess funds to cold storage'
            })

        # Overall risk warnings
        if risk_score > 70:
            warnings.append({
                'level': 'HIGH',
                'message': f"🔴 Overall risk score high: {risk_score}/100",
                'action': 'Review all positions and reduce exposure'
            })
        elif risk_score > 50:
            warnings.append({
                'level': 'MODERATE',
                'message': f"🟠 Overall risk score moderate: {risk_score}/100",
                'action': 'Monitor closely and consider rebalancing'
            })

        return warnings

    def generate_report(self, portfolio_value=None):
        """Complete risk assessment report"""
        print(f"\n{'='*70}")
        print(f"🛡️ {self.name.upper()} - RISK ASSESSMENT")
        print(f"{'='*70}\n")

        # Check AAVE risk
        aave_risk = self.check_aave_risk()
        print(f"🏦 AAVE DeFi Position:")
        print(f"   Health Factor: {aave_risk.get('health_factor', 0):.2f}")
        print(f"   Risk Level: {aave_risk.get('alert_level')} {aave_risk.get('risk_level')}")
        print(f"   Collateral: ${aave_risk.get('collateral_usd', 0):,.2f}")
        print(f"   Debt: ${aave_risk.get('debt_usd', 0):,.2f}")

        # Check exchange exposure
        print(f"\n💱 Exchange Exposure:")
        exchange_exposure = self.check_exchange_exposure()
        for name, data in exchange_exposure['exchanges'].items():
            if 'error' not in data:
                print(f"   {name.upper()}: ${data['usd_value']:,.2f}")
        print(f"   Total: ${exchange_exposure['total_usd']:,.2f}")

        # Calculate risk score
        if portfolio_value is None:
            portfolio_value = 6167.43  # Default from mcp_portfolio_context.json

        risk_score = self.calculate_risk_score(aave_risk, exchange_exposure, portfolio_value)
        print(f"\n📊 Overall Risk Score: {risk_score}/100")

        # Generate warnings
        warnings = self.generate_warnings(aave_risk, exchange_exposure, risk_score)

        if warnings:
            print(f"\n⚠️  RISK WARNINGS:")
            for i, warning in enumerate(warnings, 1):
                print(f"\n  {i}. [{warning['level']}] {warning['message']}")
                print(f"     Action: {warning['action']}")
        else:
            print(f"\n✅ No risk warnings - portfolio is healthy")

        print(f"\n{'='*70}")

        return {
            'aave_risk': aave_risk,
            'exchange_exposure': exchange_exposure,
            'risk_score': risk_score,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    agent = RiskAgent()
    report = agent.generate_report()

    # Save report to file
    output_file = Path(__file__).parent.parent / 'logs' / 'risk_agent_report.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Report saved to: {output_file}")
