#!/usr/bin/env python3
"""
👑 SOVEREIGNSHADOW v2.5a - Unified Interface
============================================

Single entry point for all system components.

Usage:
    from sovereign_system import SovereignShadow

    system = SovereignShadow()
    system.deploy_ladder(signal, capital)
    system.check_profit_milestones()
"""

import sys
from pathlib import Path

# Add modules to path
MODULES_PATH = Path(__file__).parent / "modules"
sys.path.insert(0, str(MODULES_PATH))

# Import all components
from ladder import UnifiedLadderSystem, TieredLadderSystem
from tracking import UnifiedProfitTracker, IncomeCapitalTracker, InjectionManager
from safety import AAVEMonitor

class SovereignShadow:
    """
    Unified SovereignShadow trading system

    Complete integration of:
    - Ladder trading (entry + exit + extraction)
    - Profit tracking (all exchanges)
    - Safety monitoring (AAVE health)
    - Capital management (income separation)
    """

    def __init__(self):
        print("\n" + "="*70)
        print("👑 SOVEREIGNSHADOW v2.5a")
        print("="*70)

        # Initialize components
        self.ladder = UnifiedLadderSystem()
        self.profit_extraction = TieredLadderSystem()
        self.profit_tracker = UnifiedProfitTracker()
        self.capital_tracker = IncomeCapitalTracker()
        self.injection_manager = InjectionManager()
        self.aave_monitor = AAVEMonitor()

        print("✅ All systems initialized")
        print("="*70 + "\n")

    def deploy_ladder(self, signal, capital, mode='paper'):
        """Deploy complete ladder trading system"""
        return self.ladder.deploy_ladder(signal, capital, mode)

    def check_extraction_milestones(self):
        """Check if profit extraction milestone reached"""
        return self.profit_extraction.run_ladder_check()

    def get_total_profit(self):
        """Get unified profit across all sources"""
        return self.profit_tracker.get_total_profit()

    def inject_all_exchanges(self):
        """Inject data from all 5 exchanges"""
        return self.injection_manager.inject_all()

    def get_aave_health(self):
        """Get AAVE position health"""
        return self.aave_monitor.get_position_summary()

    def get_system_status(self):
        """Get complete system status"""
        return {
            'ladder': self.ladder.get_active_ladders(),
            'profit': self.get_total_profit(),
            'aave': self.get_aave_health(),
            'extraction': self.profit_extraction.get_tier_summary()
        }


def main():
    """Demo execution"""
    system = SovereignShadow()

    print("🎯 System ready for operation")
    print()
    print("Available methods:")
    print("  - system.deploy_ladder(signal, capital)")
    print("  - system.check_extraction_milestones()")
    print("  - system.get_total_profit()")
    print("  - system.inject_all_exchanges()")
    print("  - system.get_system_status()")
    print()

if __name__ == "__main__":
    main()
