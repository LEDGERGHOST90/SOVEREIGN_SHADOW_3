#!/usr/bin/env python3
"""
🛡️ AAVE GUARDIAN - Automated Health Factor Monitor with Alerts
Runs continuously, sends alerts when HF drops below thresholds
"""

import os
import sys
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal

# Add aave monitor to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules' / 'safety'))

from aave_monitor_v2 import AaveMonitor

# Alert thresholds
CRITICAL_HF = Decimal('1.8')  # Emergency repay needed
WARNING_HF = Decimal('2.0')   # Prepare to act
CAUTION_HF = Decimal('2.5')   # Monitor closely

# Check interval (seconds)
CHECK_INTERVAL = 300  # 5 minutes

class AAVEGuardian:
    """Automated AAVE position guardian with alerts"""

    def __init__(self):
        self.monitor = AaveMonitor()
        self.logs_dir = Path(__file__).parent.parent / 'logs' / 'guardian'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.alert_log = self.logs_dir / 'alert_history.json'
        self.hf_history = self.logs_dir / 'hf_history.json'

        self.last_alert_level = None

        print(f"🛡️ AAVE Guardian initialized")
        print(f"   Alert thresholds:")
        print(f"   🚨 CRITICAL: < {CRITICAL_HF}")
        print(f"   🔴 WARNING: < {WARNING_HF}")
        print(f"   🟠 CAUTION: < {CAUTION_HF}")
        print(f"   Check interval: {CHECK_INTERVAL}s ({CHECK_INTERVAL/60:.0f} min)")
        print(f"   Logs: {self.logs_dir}")
        print()

    def load_hf_history(self):
        """Load HF history"""
        if self.hf_history.exists():
            with open(self.hf_history, 'r') as f:
                return json.load(f)
        return []

    def save_hf_snapshot(self, position):
        """Save HF snapshot to history"""
        history = self.load_hf_history()

        snapshot = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'block_number': self.monitor.w3.eth.block_number,
            'health_factor': float(position.health_factor) if position.health_factor != Decimal('Infinity') else None,
            'collateral_usd': float(position.collateral_usd),
            'debt_usd': float(position.debt_usd),
            'collateral_base': position.collateral_base,
            'debt_base': position.debt_base
        }

        history.append(snapshot)

        # Keep last 1000 snapshots
        if len(history) > 1000:
            history = history[-1000:]

        with open(self.hf_history, 'w') as f:
            json.dump(history, f, indent=2)

        return snapshot

    def log_alert(self, level, message, position, recommended_action):
        """Log alert to file"""
        if self.alert_log.exists():
            with open(self.alert_log, 'r') as f:
                alerts = json.load(f)
        else:
            alerts = []

        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': level,
            'message': message,
            'health_factor': float(position.health_factor) if position.health_factor != Decimal('Infinity') else None,
            'collateral_usd': float(position.collateral_usd),
            'debt_usd': float(position.debt_usd),
            'recommended_action': recommended_action
        }

        alerts.append(alert)

        # Keep last 500 alerts
        if len(alerts) > 500:
            alerts = alerts[-500:]

        with open(self.alert_log, 'w') as f:
            json.dump(alerts, f, indent=2)

    def check_and_alert(self):
        """Check HF and send alerts if needed"""
        try:
            # Get current position
            position = self.monitor.get_position()
            hf = position.health_factor

            # Save snapshot
            snapshot = self.save_hf_snapshot(position)

            # Determine alert level
            alert_level = None
            alert_message = None
            recommended_action = None

            if hf == Decimal('Infinity'):
                alert_level = 'SAFE'
                alert_message = '✅ No debt - no liquidation risk'
                recommended_action = 'Continue monitoring'
            elif hf < CRITICAL_HF:
                alert_level = 'CRITICAL'
                alert_message = f'🚨 CRITICAL: HF {hf:.2f} < {CRITICAL_HF}'
                repay_amount = self.monitor.calculate_repay_to_target(position, Decimal('2.5'))
                recommended_action = f'URGENT: Repay ${repay_amount:.2f} USDC IMMEDIATELY'
            elif hf < WARNING_HF:
                alert_level = 'WARNING'
                alert_message = f'🔴 WARNING: HF {hf:.2f} < {WARNING_HF}'
                repay_amount = self.monitor.calculate_repay_to_target(position, Decimal('2.5'))
                recommended_action = f'Repay ${repay_amount:.2f} USDC within 24 hours'
            elif hf < CAUTION_HF:
                alert_level = 'CAUTION'
                alert_message = f'🟠 CAUTION: HF {hf:.2f} < {CAUTION_HF}'
                repay_amount = self.monitor.calculate_repay_to_target(position, Decimal('3.0'))
                recommended_action = f'Consider repaying ${repay_amount:.2f} USDC to reach HF 3.0'
            else:
                alert_level = 'SAFE'
                alert_message = f'✅ SAFE: HF {hf:.2f} > {CAUTION_HF}'
                recommended_action = 'Continue monitoring'

            # Print status
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {alert_message}")
            print(f"   Collateral: ${position.collateral_usd:,.2f}")
            print(f"   Debt: ${position.debt_usd:,.2f}")

            # Log alert if level changed
            if alert_level != self.last_alert_level and alert_level in ['CRITICAL', 'WARNING', 'CAUTION']:
                print(f"   ⚠️  ALERT LEVEL CHANGED: {self.last_alert_level} → {alert_level}")
                print(f"   Action: {recommended_action}")
                self.log_alert(alert_level, alert_message, position, recommended_action)

            self.last_alert_level = alert_level

            # Return status
            return {
                'success': True,
                'alert_level': alert_level,
                'health_factor': float(hf) if hf != Decimal('Infinity') else None,
                'snapshot': snapshot
            }

        except Exception as e:
            print(f"❌ Check failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def run_continuous(self):
        """Run continuous monitoring"""
        print(f"🛡️ Starting continuous monitoring...")
        print(f"   Press Ctrl+C to stop\n")

        check_count = 0

        try:
            while True:
                check_count += 1
                print(f"{'='*70}")
                print(f"CHECK #{check_count}")
                print(f"{'='*70}")

                result = self.check_and_alert()

                if result['success']:
                    print(f"✅ Check complete")
                else:
                    print(f"❌ Check failed: {result['error']}")

                print(f"\n⏳ Next check in {CHECK_INTERVAL/60:.0f} minutes...\n")
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print(f"🛡️ Guardian stopped by user")
            print(f"{'='*70}")
            print(f"Total checks: {check_count}")
            print(f"Alert log: {self.alert_log}")
            print(f"HF history: {self.hf_history}")
            print(f"{'='*70}\n")

    def run_once(self):
        """Run single check"""
        print(f"🛡️ Running single check...\n")
        result = self.check_and_alert()
        print(f"\n{'='*70}")
        if result['success']:
            print(f"✅ Check complete")
            print(f"   Alert level: {result['alert_level']}")
            if result['health_factor']:
                print(f"   Health Factor: {result['health_factor']:.2f}")
        else:
            print(f"❌ Check failed: {result['error']}")
        print(f"{'='*70}\n")
        return result

def main():
    """Main entry point"""
    import sys

    guardian = AAVEGuardian()

    if '--once' in sys.argv:
        guardian.run_once()
    else:
        guardian.run_continuous()

if __name__ == '__main__':
    main()
