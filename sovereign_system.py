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
from safety import AAVEMonitor, SafetyRulesImplementation, RealPortfolioBridge
from execution import UniversalExchangeManager, RealPortfolioConnector

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
        print("👑 SOVEREIGNSHADOW v2.5a - SAFETY ENABLED")
        print("="*70)

        # Initialize components
        self.ladder = UnifiedLadderSystem()
        self.profit_extraction = TieredLadderSystem()
        self.profit_tracker = UnifiedProfitTracker()
        self.capital_tracker = IncomeCapitalTracker()
        self.injection_manager = InjectionManager()

        # Initialize AAVE monitor (optional - requires INFURA_URL)
        try:
            self.aave_monitor = AAVEMonitor()
            print("✅ AAVE monitor initialized")
        except ValueError as e:
            print(f"⚠️  AAVE monitor disabled: {e}")
            self.aave_monitor = None

        # Initialize safety systems
        self.safety_rules = SafetyRulesImplementation()
        self.portfolio_bridge = RealPortfolioBridge()

        # Initialize exchange management
        self.exchange_manager = UniversalExchangeManager()
        self.portfolio_connector = RealPortfolioConnector()

        print("✅ All systems initialized")
        print("🛡️  Safety systems ACTIVE")
        print("🔗 Exchange management READY")
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
        if self.aave_monitor:
            return self.aave_monitor.get_position_summary()
        return {"status": "disabled", "message": "AAVE monitor not initialized"}

    def check_safety_limits(self):
        """Check all safety rules and limits"""
        return self.safety_rules.check_all_safety_rules()

    def validate_trade(self, trade_params):
        """Validate trade against safety rules before execution"""
        return self.portfolio_bridge.validate_trade(trade_params)

    def get_portfolio_limits(self):
        """Get current portfolio limits and risk parameters"""
        return self.portfolio_bridge.get_portfolio_limits()

    def connect_to_exchanges(self):
        """Auto-detect and connect to all configured exchanges"""
        return self.exchange_manager.connect_all()

    def get_connected_exchanges(self):
        """Get list of successfully connected exchanges"""
        return list(self.exchange_manager.exchanges.keys())

    def get_portfolio_status(self):
        """Get real portfolio status and capital allocation"""
        return self.portfolio_connector.display_portfolio_status()

    def get_system_status(self):
        """Get complete system status"""
        return {
            'ladder': self.ladder.get_active_ladders(),
            'profit': self.get_total_profit(),
            'aave': self.get_aave_health(),
            'extraction': self.profit_extraction.get_tier_summary(),
            'safety': self.safety_rules.get_safety_status(),
            'portfolio_limits': self.get_portfolio_limits(),
            'connected_exchanges': self.get_connected_exchanges(),
            'portfolio': self.portfolio_connector.portfolio
        }


def main():
    """Demo execution"""
    system = SovereignShadow()

    print("🎯 System ready for operation")
    print()
    print("Available methods:")
    print("  Trading:")
    print("    - system.deploy_ladder(signal, capital)")
    print("    - system.check_extraction_milestones()")
    print("  Monitoring:")
    print("    - system.get_total_profit()")
    print("    - system.inject_all_exchanges()")
    print("    - system.get_system_status()")
    print("  Safety:")
    print("    - system.check_safety_limits()")
    print("    - system.validate_trade(trade_params)")
    print("    - system.get_portfolio_limits()")
    print("  Exchange Management:")
    print("    - system.connect_to_exchanges()")
    print("    - system.get_connected_exchanges()")
    print("    - system.get_portfolio_status()")
    print()

if __name__ == "__main__":
    main()
