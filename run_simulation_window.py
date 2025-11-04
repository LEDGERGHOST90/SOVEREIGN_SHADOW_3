#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - 5-HOUR SIMULATION RUN
Time Window: Nov 4, 2025 12:00 AM → 5:00 AM
Mode: Simulation with live API keys
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'modules' / 'safety'))
sys.path.insert(0, str(Path(__file__).parent / 'agents'))
sys.path.insert(0, str(Path(__file__).parent / 'core' / 'portfolio'))

def get_current_time():
    """Get current time in PST"""
    from datetime import datetime
    return datetime.now()

def is_in_simulation_window():
    """Check if current time is within simulation window"""
    now = get_current_time()

    # Simulation window: Nov 4, 2025 00:00 - 05:00
    if now.month == 11 and now.day == 4 and now.year == 2025:
        if 0 <= now.hour < 5:
            return True
    return False

def run_full_system_check():
    """Run all monitoring systems"""
    print(f"\n{'='*70}")
    print(f"🏴 SOVEREIGN SHADOW II - SYSTEM CHECK")
    print(f"{'='*70}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    results = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'checks': {}
    }

    # 1. AAVE Monitor
    print("🏦 Running AAVE Monitor...")
    try:
        from aave_monitor_v2 import AaveMonitor

        monitor = AaveMonitor()
        report = monitor.generate_report()

        results['checks']['aave'] = {
            'status': 'success',
            'health_factor': report['position']['health_factor'],
            'collateral_usd': report['position']['collateral_usd'],
            'debt_usd': report['position']['debt_usd'],
            'risk_level': report['risk']['level']
        }

        print(f"   ✅ Health Factor: {report['position']['health_factor']:.2f}")
        print(f"   ✅ Collateral: ${report['position']['collateral_usd']:,.2f}")
        print(f"   ✅ Debt: ${report['position']['debt_usd']:,.2f}")

    except Exception as e:
        print(f"   ❌ AAVE Error: {e}")
        results['checks']['aave'] = {'status': 'error', 'error': str(e)}

    print()

    # 2. Portfolio Agent
    print("📊 Running Portfolio Agent...")
    try:
        from portfolio_agent import PortfolioAgent

        agent = PortfolioAgent()
        portfolio_report = agent.generate_report()

        results['checks']['portfolio'] = {
            'status': 'success',
            'total_value': portfolio_report['portfolio']['total_value'],
            'diversification_score': portfolio_report['metrics']['diversification_score'],
            'recommendations_count': len(portfolio_report['recommendations'])
        }

        print(f"   ✅ Portfolio Value: ${portfolio_report['portfolio']['total_value']:,.2f}")
        print(f"   ✅ Diversification: {portfolio_report['metrics']['diversification_score']:.2f}/1.0")
        print(f"   ✅ Recommendations: {len(portfolio_report['recommendations'])}")

    except Exception as e:
        print(f"   ❌ Portfolio Error: {e}")
        results['checks']['portfolio'] = {'status': 'error', 'error': str(e)}

    print()

    # 3. Risk Agent
    print("🛡️ Running Risk Agent...")
    try:
        from risk_agent import RiskAgent

        agent = RiskAgent()
        risk_report = agent.generate_report()

        results['checks']['risk'] = {
            'status': 'success',
            'risk_score': risk_report.get('risk_score', 0),
            'warnings_count': len(risk_report.get('warnings', []))
        }

        print(f"   ✅ Risk Score: {risk_report.get('risk_score', 0)}/100")
        print(f"   ✅ Warnings: {len(risk_report.get('warnings', []))}")

    except Exception as e:
        print(f"   ❌ Risk Error: {e}")
        results['checks']['risk'] = {'status': 'error', 'error': str(e)}

    print()

    # Save unified report
    output_file = Path(__file__).parent / 'logs' / 'simulation_run.json'
    output_file.parent.mkdir(exist_ok=True)

    # Load existing data or create new
    if output_file.exists():
        with open(output_file, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = {'runs': []}

    all_data['runs'].append(results)

    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"{'='*70}")
    print(f"✅ System check completed")
    print(f"📁 Saved to: {output_file}")
    print(f"{'='*70}\n")

    return results

def main():
    """Main simulation loop"""
    print(f"\n{'='*70}")
    print(f"🏴 SOVEREIGN SHADOW II - 5 HOUR SIMULATION")
    print(f"{'='*70}")
    print(f"⏰ Simulation Window: Nov 4, 2025 00:00 - 05:00")
    print(f"🔄 Check Interval: Every 15 minutes")
    print(f"📍 Mode: SIMULATION (Live APIs, No Execution)")
    print(f"{'='*70}\n")

    # Check if we're in the simulation window
    if not is_in_simulation_window():
        print(f"⏰ Current time: {get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚠️  Outside simulation window (Nov 4, 2025 00:00-05:00)")
        print(f"✅ Running ONE check anyway for testing...\n")

        # Run once for testing
        run_full_system_check()

        print(f"\n💡 To run continuous monitoring during window:")
        print(f"   Set system time to Nov 4, 2025 00:00-05:00")
        print(f"   Or modify is_in_simulation_window() to return True\n")

        return

    # We're in the simulation window
    run_count = 0

    try:
        while is_in_simulation_window():
            run_count += 1

            print(f"\n{'='*70}")
            print(f"🔄 RUN #{run_count}")
            print(f"{'='*70}\n")

            # Run system check
            run_full_system_check()

            # Wait 15 minutes
            print(f"⏳ Waiting 15 minutes until next check...")
            print(f"   (Press Ctrl+C to stop)\n")

            time.sleep(15 * 60)  # 15 minutes

        # Exited simulation window
        print(f"\n{'='*70}")
        print(f"✅ SIMULATION COMPLETE")
        print(f"{'='*70}")
        print(f"⏰ Exited simulation window")
        print(f"🔄 Total Runs: {run_count}")
        print(f"📁 Results saved to: logs/simulation_run.json")
        print(f"{'='*70}\n")

    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print(f"⚠️  SIMULATION STOPPED BY USER")
        print(f"{'='*70}")
        print(f"🔄 Completed Runs: {run_count}")
        print(f"📁 Results saved to: logs/simulation_run.json")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
