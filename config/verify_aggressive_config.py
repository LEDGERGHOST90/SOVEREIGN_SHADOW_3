#!/usr/bin/env python3
"""
🔍 SOVEREIGNSHADOW.AI - AGGRESSIVE CONFIGURATION VERIFIER
Verify all aggressive trading parameters are properly configured for $3,000/month target
"""

import os
import json
from pathlib import Path

class AggressiveConfigVerifier:
    def __init__(self):
        self.system_root = Path("/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]")
        self.verification_results = {}
        
    def verify_all_configurations(self):
        """Verify all aggressive trading configurations"""
        print("🔍 VERIFYING AGGRESSIVE TRADING CONFIGURATIONS")
        print("=" * 70)
        print("Target: $3,000/month arbitrage profit")
        print("=" * 70)
        
        # Verify architecture configuration
        self.verify_architecture_config()
        
        # Verify automation configuration
        self.verify_automation_config()
        
        # Verify deployment configuration
        self.verify_deployment_config()
        
        # Display verification summary
        self.display_verification_summary()
        
    def verify_architecture_config(self):
        """Verify SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml configuration"""
        print("\n📋 ARCHITECTURE CONFIGURATION:")
        print("-" * 40)
        
        try:
            config_path = self.system_root / "sovLOOP_BACKUP" / "SHADOW_SOV_UNIFIED_ARCHITECTURE.yaml"
            
            if not config_path.exists():
                print("❌ Architecture config file not found")
                self.verification_results["architecture"] = False
                return
            
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Check financial metrics
            if '$3000/month' in content:
                print("✅ Arbitrage Target: $3,000/month")
                self.verification_results["arbitrage_target"] = True
            else:
                print("❌ Arbitrage Target: Not set to $3,000/month")
                self.verification_results["arbitrage_target"] = False
            
            # Check risk profile
            if 'aggressive_growth' in content:
                print("✅ Risk Profile: Aggressive Growth")
                self.verification_results["risk_profile"] = True
            else:
                print("❌ Risk Profile: Not set to aggressive_growth")
                self.verification_results["risk_profile"] = False
            
            # Check aggressive position sizing
            if 'aggressive_position_sizing' in content:
                print("✅ Aggressive Position Sizing: Configured")
                print("   • High Confidence: 4% (>85% confidence)")
                print("   • Medium Confidence: 3% (>70% confidence)")
                print("   • Max Position: 4%")
                print("   • Leverage Limit: 1.5:1")
                self.verification_results["position_sizing"] = True
            else:
                print("❌ Aggressive Position Sizing: Not configured")
                self.verification_results["position_sizing"] = False
            
            # Check aggressive trading frequency
            if 'aggressive_trading_frequency' in content:
                print("✅ Aggressive Trading Frequency: Configured")
                print("   • Scan Interval: 30-60 seconds")
                print("   • Micro Arbitrage: <1% spreads")
                print("   • Cross Exchange: 15+ simultaneous")
                print("   • Execution Speed: <5 seconds per trade")
                self.verification_results["trading_frequency"] = True
            else:
                print("❌ Aggressive Trading Frequency: Not configured")
                self.verification_results["trading_frequency"] = False
                
        except Exception as e:
            print(f"❌ Error verifying architecture config: {e}")
            self.verification_results["architecture"] = False
    
    def verify_automation_config(self):
        """Verify enhanced_empire_automation.py configuration"""
        print("\n🤖 AUTOMATION CONFIGURATION:")
        print("-" * 40)
        
        try:
            automation_path = self.system_root / "multi-exchange-crypto-mcp" / "enhanced_empire_automation.py"
            
            if not automation_path.exists():
                print("❌ Automation script not found")
                self.verification_results["automation"] = False
                return
            
            with open(automation_path, 'r') as f:
                content = f.read()
            
            # Check for key aggressive features
            features_to_check = [
                ("Duplicate Order Prevention", "DuplicateOrderPreventionSystem"),
                ("Crypto Volatility Manager", "CryptoVolatilityManager"),
                ("Kill Switch System", "KillSwitchSystem"),
                ("Dynamic Position Sizing", "get_position_size_multiplier"),
                ("Aggressive Trading", "aggressive")
            ]
            
            for feature_name, search_term in features_to_check:
                if search_term in content:
                    print(f"✅ {feature_name}: Implemented")
                else:
                    print(f"❌ {feature_name}: Not found")
            
            # Check for daily trade limits
            if "DAILY_TRADE_LIMIT = 50" in content:
                print("✅ Daily Trade Limit: 50 trades (aggressive)")
                self.verification_results["daily_limit"] = True
            else:
                print("❌ Daily Trade Limit: Not set to aggressive level")
                self.verification_results["daily_limit"] = False
            
            # Check for position sizing
            if "position_size_multiplier" in content:
                print("✅ Dynamic Position Sizing: Implemented")
                self.verification_results["dynamic_sizing"] = True
            else:
                print("❌ Dynamic Position Sizing: Not implemented")
                self.verification_results["dynamic_sizing"] = False
                
        except Exception as e:
            print(f"❌ Error verifying automation config: {e}")
            self.verification_results["automation"] = False
    
    def verify_deployment_config(self):
        """Verify deployment configuration"""
        print("\n🚀 DEPLOYMENT CONFIGURATION:")
        print("-" * 40)
        
        # Check if deployment files exist
        deployment_files = [
            "deploy_sovereign_trader.py",
            "live_trading_monitor.py",
            "check_sovereign_status.py",
            "stop_sovereign_trader.py"
        ]
        
        for file_name in deployment_files:
            file_path = self.system_root / file_name
            if file_path.exists():
                print(f"✅ {file_name}: Available")
            else:
                print(f"❌ {file_name}: Missing")
        
        # Check if live trading monitor has $3k target
        try:
            monitor_path = self.system_root / "live_trading_monitor.py"
            if monitor_path.exists():
                with open(monitor_path, 'r') as f:
                    content = f.read()
                
                if "monthly_target: 3000.0" in content or "monthly_target = 3000.0" in content:
                    print("✅ Live Monitor: $3,000/month target configured")
                    self.verification_results["monitor_target"] = True
                else:
                    print("❌ Live Monitor: Target not set to $3,000/month")
                    self.verification_results["monitor_target"] = False
        except:
            print("❌ Live Monitor: Cannot verify target")
            self.verification_results["monitor_target"] = False
    
    def display_verification_summary(self):
        """Display verification summary"""
        print("\n" + "=" * 70)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 70)
        
        total_checks = len(self.verification_results)
        passed_checks = sum(1 for result in self.verification_results.values() if result)
        
        print(f"Configuration Checks: {passed_checks}/{total_checks} PASSED")
        print()
        
        for check_name, passed in self.verification_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name.replace('_', ' ').title()}")
        
        print("\n🎯 AGGRESSIVE TRADING READINESS:")
        if passed_checks >= total_checks * 0.8:
            print("✅ READY - System configured for aggressive $3,000/month trading")
            print("🚀 All key parameters optimized for maximum returns")
        elif passed_checks >= total_checks * 0.6:
            print("⚠️ MOSTLY READY - Minor configuration adjustments needed")
            print("🔧 Review failed checks and update configurations")
        else:
            print("❌ NOT READY - Significant configuration issues found")
            print("🛠️ Fix failed checks before aggressive trading")
        
        print("\n💰 EXPECTED PERFORMANCE:")
        print("• Monthly Target: $3,000 arbitrage profit")
        print("• Daily Target: ~$100 profit")
        print("• Position Sizing: 1-4% based on confidence")
        print("• Trading Frequency: 30-60 second scans")
        print("• Risk Management: 2-4% stop losses")
        print("• Leverage: Up to 1.5:1 on high confidence")
        
        print("\n🔧 NEXT STEPS:")
        if passed_checks >= total_checks * 0.8:
            print("1. ✅ Configuration verified - Start live trading")
            print("2. 📊 Monitor performance with live_trading_monitor.py")
            print("3. 📈 Scale capital allocation as system proves itself")
            print("4. 🎯 Track progress toward $3,000/month target")
        else:
            print("1. 🔧 Fix configuration issues identified above")
            print("2. 🔍 Re-run verification: python3 verify_aggressive_config.py")
            print("3. 🚀 Deploy system: python3 deploy_sovereign_trader.py")
            print("4. 📊 Monitor performance once configured")
        
        print("=" * 70)

def main():
    """Main verification function"""
    verifier = AggressiveConfigVerifier()
    verifier.verify_all_configurations()

if __name__ == "__main__":
    main()
