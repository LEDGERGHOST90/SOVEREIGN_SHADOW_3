#!/usr/bin/env python3
"""
💰 INCOME & CAPITAL INJECTION TRACKER
Tracks recurring income and capital injections to separate from trading profits

This is CRITICAL for accurate profit calculation:
- Capital injections are NOT profits (just new money added)
- Trading profits are REAL gains
- Siphon should only extract TRADING PROFITS, not injected capital
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Import centralized portfolio config
try:
    sys.path.insert(0, '/Volumes/LegacySafe/SS_III')
    from core.config.portfolio_config import get_initial_capital
except ImportError:
    def get_initial_capital(exchange=None):
        return 5438 if exchange is None else 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("income_capital_tracker")

class IncomeCapitalTracker:
    """
    Track all income and capital injections

    Purpose:
    - Separate trading profits from injected capital
    - Track monthly recurring income
    - Prevent siphoning of injected capital (only siphon REAL profits)
    """

    def __init__(self):
        self.base_path = Path("/Volumes/LegacySafe/SovereignShadow 2")
        self.logs_path = self.base_path / "logs"
        self.tracker_file = self.logs_path / "income_capital_tracker.json"

        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Load existing tracker data
        self.data = self._load_tracker()

        logger.info("💰 Income & Capital Tracker initialized")

    def _load_tracker(self) -> Dict[str, Any]:
        """Load existing tracker data or create new"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r') as f:
                return json.load(f)

        # Initialize new tracker
        return {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'recurring_income': {
                'va_caregiving': {
                    'amount': 2188.0,
                    'frequency': 'monthly',
                    'description': 'VA caregiving for father',
                    'active': True
                }
            },
            'capital_injections': [],
            'total_income_received': 0.0,
            'total_capital_injected': 0.0,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    def _save_tracker(self):
        """Save tracker data to file"""
        self.data['last_updated'] = datetime.now(timezone.utc).isoformat()

        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)

        logger.debug(f"📁 Tracker saved to: {self.tracker_file}")

    def add_capital_injection(self, amount: float, source: str = "manual", note: str = "") -> Dict[str, Any]:
        """
        Record a capital injection

        Args:
            amount: USD amount injected
            source: Where capital came from (manual, VA income, etc.)
            note: Optional description

        Returns:
            Injection record
        """
        injection = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'amount': amount,
            'source': source,
            'note': note
        }

        self.data['capital_injections'].append(injection)
        self.data['total_capital_injected'] += amount

        self._save_tracker()

        logger.info(f"💉 Capital injection recorded: ${amount:.2f} from {source}")

        return injection

    def record_income_received(self, source: str, amount: float, note: str = "") -> Dict[str, Any]:
        """
        Record income received (not yet injected into trading)

        Args:
            source: Income source (va_caregiving, etc.)
            amount: USD amount received
            note: Optional description

        Returns:
            Income record
        """
        income = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': source,
            'amount': amount,
            'note': note
        }

        if 'income_received' not in self.data:
            self.data['income_received'] = []

        self.data['income_received'].append(income)
        self.data['total_income_received'] += amount

        self._save_tracker()

        logger.info(f"💵 Income received: ${amount:.2f} from {source}")

        return income

    def get_total_capital_injected(self, since_date: str = None) -> float:
        """
        Get total capital injected (optionally since a date)

        This is CRITICAL for profit calculation:
        True Profit = Portfolio Value - Initial Capital - Capital Injected - Withdrawn
        """
        if since_date is None:
            return self.data.get('total_capital_injected', 0.0)

        # Filter by date
        total = 0.0
        for injection in self.data.get('capital_injections', []):
            if injection['timestamp'] >= since_date:
                total += injection['amount']

        return total

    def get_monthly_income_projection(self) -> Dict[str, float]:
        """Get projected monthly income from all recurring sources"""
        projection = {}

        for source, details in self.data.get('recurring_income', {}).items():
            if details.get('active', False) and details.get('frequency') == 'monthly':
                projection[source] = details.get('amount', 0.0)

        return projection

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive income & capital summary"""
        monthly_income = self.get_monthly_income_projection()

        return {
            'recurring_income': {
                'monthly_total': sum(monthly_income.values()),
                'sources': monthly_income
            },
            'capital_injections': {
                'total_all_time': self.data.get('total_capital_injected', 0.0),
                'count': len(self.data.get('capital_injections', [])),
                'typical_range': '500-1000 per month'
            },
            'income_received': {
                'total_all_time': self.data.get('total_income_received', 0.0),
                'count': len(self.data.get('income_received', []))
            },
            'last_updated': self.data.get('last_updated')
        }

    def calculate_true_profit(self, current_portfolio: float, initial_capital: float,
                            total_withdrawn: float = 0.0) -> Dict[str, Any]:
        """
        Calculate TRUE trading profit (excluding capital injections)

        Formula:
        True Profit = Current Portfolio - Initial Capital - Capital Injected - Withdrawn

        This ensures we only siphon REAL GAINS, not injected capital!
        """
        total_injected = self.get_total_capital_injected()

        # Adjusted initial capital includes all injections
        adjusted_initial = initial_capital + total_injected

        # True profit is what's left after accounting for all capital sources
        true_profit = current_portfolio - adjusted_initial - total_withdrawn

        return {
            'current_portfolio': current_portfolio,
            'initial_capital': initial_capital,
            'total_capital_injected': total_injected,
            'adjusted_initial_capital': adjusted_initial,
            'total_withdrawn': total_withdrawn,
            'true_trading_profit': true_profit,
            'calculation': f"${current_portfolio:.2f} - ${adjusted_initial:.2f} - ${total_withdrawn:.2f} = ${true_profit:.2f}"
        }


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("💰 INCOME & CAPITAL INJECTION TRACKER")
    print("="*70)
    print()

    tracker = IncomeCapitalTracker()

    # Show summary
    summary = tracker.get_summary()

    print("📊 RECURRING INCOME:")
    print(f"   Monthly Total: ${summary['recurring_income']['monthly_total']:,.2f}")
    for source, amount in summary['recurring_income']['sources'].items():
        print(f"   ├─ {source.replace('_', ' ').title()}: ${amount:,.2f}/month")

    print()
    print("💉 CAPITAL INJECTIONS:")
    print(f"   Total Injected: ${summary['capital_injections']['total_all_time']:,.2f}")
    print(f"   Injection Count: {summary['capital_injections']['count']}")
    print(f"   Typical: {summary['capital_injections']['typical_range']}")

    print()
    print("💵 INCOME RECEIVED:")
    print(f"   Total Received: ${summary['income_received']['total_all_time']:,.2f}")

    print()
    print("="*70)
    print("📝 Example: Calculate True Trading Profit")
    print("="*70)

    # Example calculation - uses centralized config
    example = tracker.calculate_true_profit(
        current_portfolio=4761.73,
        initial_capital=get_initial_capital(),  # From portfolio_config.py
        total_withdrawn=0.0
    )

    print()
    print(f"Current Portfolio:        ${example['current_portfolio']:,.2f}")
    print(f"Initial Capital:          ${example['initial_capital']:,.2f}")
    print(f"Total Capital Injected:   ${example['total_capital_injected']:,.2f}")
    print(f"Adjusted Initial Capital: ${example['adjusted_initial_capital']:,.2f}")
    print(f"Total Withdrawn:          ${example['total_withdrawn']:,.2f}")
    print(f"─────────────────────────────────────────")
    print(f"TRUE TRADING PROFIT:      ${example['true_trading_profit']:,.2f}")
    print()
    print(f"Calculation: {example['calculation']}")

    print()
    print("="*70)
    print(f"📁 Tracker saved to: {tracker.tracker_file}")
    print("="*70)
    print()

if __name__ == "__main__":
    main()
