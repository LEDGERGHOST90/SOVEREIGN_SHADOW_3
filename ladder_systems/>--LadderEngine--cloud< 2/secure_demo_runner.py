#!/usr/bin/env python3
"""
ΣIGMA-ΩSNIPER Secure Demonstration Runner
Demonstrates full ladder execution capabilities without exposing live credentials
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

# Import our ΣIGMA-ΩSNIPER components
from src.execution.sigma_omega_sniper import sigma_omega_sniper, deploy_sigma_ladder
from src.execution.paper_trading_engine import paper_trading_engine
from src.utils.ray_score_engine import ray_score_engine, validate_roi
from src.utils.vault_router import vault_router

class SecureDemoRunner:
    """Secure demonstration of ΣIGMA-ΩSNIPER capabilities"""
    
    def __init__(self):
        self.demo_results = []
        
    async def run_secure_demo(self, token: str, entry_low: float, entry_high: float,
                            tp1: float, tp2: float, sl: float, capital: float) -> Dict[str, Any]:
        """
        Run secure demonstration of ΣIGMA-ΩSNIPER ladder execution
        
        Args:
            token: Token symbol (e.g., 'BONK')
            entry_low: Lower entry price
            entry_high: Higher entry price
            tp1: Take profit 1 price
            tp2: Take profit 2 price
            sl: Stop loss price
            capital: Capital allocation
            
        Returns:
            Complete execution demonstration results
        """
        print("🎯 ΣIGMA-ΩSNIPER SECURE DEMONSTRATION INITIATED")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 1. Security Check
            print("🛡️  SECURITY PROTOCOL: API credentials protected - using paper trading mode")
            
            # 2. Ray Score Analysis
            print(f"\n🧠 RAY SCORE ANALYSIS for {token}USDT")
            signal_data = {
                'symbol': f'{token}USDT',
                'action': 'buy',
                'entry_price': (entry_low + entry_high) / 2,
                'quantity': capital / ((entry_low + entry_high) / 2),
                'tp1_price': tp1,
                'tp2_price': tp2,
                'sl_price': sl,
                'priority': 8,
                'source': 'sigma_demo'
            }
            
            ray_analysis = ray_score_engine.get_detailed_ray_analysis(signal_data)
            print(f"   Ray Score: {ray_analysis['ray_score']:.1f}/100")
            print(f"   Validation: {ray_analysis['validation']['action']}")
            
            if ray_analysis['ray_score'] < 60:
                return {
                    'success': False,
                    'rejection_reason': f"Ray Score {ray_analysis['ray_score']:.1f} below threshold 60",
                    'ray_analysis': ray_analysis
                }
            
            # 3. ROI Validation
            print(f"\n💰 ROI VALIDATION")
            entry_prices = [entry_low + i * (entry_high - entry_low) / 5 for i in range(6)]
            roi_validation = validate_roi(entry_prices, tp1, tp2, sl)
            
            print(f"   TP1 ROI: {roi_validation['tp1_roi']:.1f}% (req: ≥20%)")
            print(f"   TP2 ROI: {roi_validation['tp2_roi']:.1f}% (req: ≥30%)")
            print(f"   Max Drawdown: {roi_validation['drawdown']:.1f}% (req: ≤7%)")
            print(f"   Validation: {'✅ PASS' if roi_validation['valid'] else '❌ FAIL'}")
            
            if not roi_validation['valid']:
                return {
                    'success': False,
                    'rejection_reason': "ROI requirements not met",
                    'roi_validation': roi_validation,
                    'ray_analysis': ray_analysis
                }
            
            # 4. Spread Check
            spread = abs(entry_high - entry_low) / entry_low * 100
            print(f"\n📊 SPREAD ANALYSIS")
            print(f"   Entry Spread: {spread:.2f}% (req: ≤1.25%)")
            
            if spread > 1.25:
                return {
                    'success': False,
                    'rejection_reason': f"Spread {spread:.2f}% exceeds 1.25% limit",
                    'spread': spread
                }
            
            # 5. Execute ΣIGMA-ΩSNIPER Ladder
            print(f"\n⚡ EXECUTING ΣIGMA-ΩSNIPER LADDER")
            print(f"   Mode: SECURE PAPER TRADING")
            print(f"   Target: {token}USDT")
            print(f"   Capital: ${capital}")
            
            execution_result = await deploy_sigma_ladder(
                token=token,
                entry_min=entry_low,
                entry_max=entry_high,
                tp1=tp1,
                tp2=tp2,
                sl=sl,
                capital=capital,
                ray_score=ray_analysis['ray_score'],
                mode='paper',
                exchange='binance_us'
            )
            
            # 6. Vault Siphon Projection
            print(f"\n💎 VAULT SIPHON PROJECTION")
            vault_projection = execution_result.get('vault_siphon_projection', {})
            if vault_projection:
                print(f"   TP1 Profit Projection: ${vault_projection.get('tp1_profit', 0):.2f}")
                print(f"   TP2 Profit Projection: ${vault_projection.get('tp2_profit', 0):.2f}")
                print(f"   Total Siphon (30%): ${vault_projection.get('total_siphon', 0):.2f}")
                print(f"   Target SLEEP Asset: {vault_projection.get('target_asset', 'AUTO')}")
            
            # 7. Execution Diagnostics
            execution_time = time.time() - start_time
            print(f"\n🔧 EXECUTION DIAGNOSTICS")
            print(f"   Total Execution Time: {execution_time*1000:.0f}ms")
            print(f"   Ladder Tiers: {execution_result.get('ladder_fill_plan', {}).get('entry_tiers', 0)}")
            print(f"   Order IDs: {len(execution_result.get('order_ids', []))}")
            
            # 8. Start Monitoring (demo)
            print(f"\n👁️  COGNITIVE MONITORING ACTIVE")
            print(f"   Ray Score Threshold: 40 (force exit)")
            print(f"   Monitoring Interval: 30 seconds")
            
            # 9. Generate Summary Report
            demo_result = {
                'success': True,
                'token': token,
                'execution_mode': 'secure_paper_trading',
                'ray_analysis': ray_analysis,
                'roi_validation': roi_validation,
                'spread_check': {'spread_percentage': spread, 'valid': spread <= 1.25},
                'execution_result': execution_result,
                'vault_projection': vault_projection,
                'execution_time_ms': int(execution_time * 1000),
                'security_status': 'credentials_protected',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.demo_results.append(demo_result)
            
            print(f"\n✅ ΣIGMA-ΩSNIPER DEMONSTRATION COMPLETE")
            print(f"   Status: {execution_result['execution_status']}")
            print(f"   Ray Score: {ray_analysis['ray_score']:.1f}")
            print(f"   ROI: TP1 {roi_validation['tp1_roi']:.1f}% | TP2 {roi_validation['tp2_roi']:.1f}%")
            
            return demo_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'execution_time_ms': int((time.time() - start_time) * 1000),
                'timestamp': datetime.utcnow().isoformat()
            }
            print(f"\n❌ DEMONSTRATION FAILED: {e}")
            return error_result
    
    def save_demo_report(self, filename: str = None):
        """Save demonstration results to file"""
        if not filename:
            filename = f"sigma_demo_report_{int(time.time())}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'demo_summary': {
                    'total_demonstrations': len(self.demo_results),
                    'successful_demos': len([r for r in self.demo_results if r.get('success')]),
                    'generated_at': datetime.utcnow().isoformat()
                },
                'demonstrations': self.demo_results
            }, f, indent=2, default=str)
        
        print(f"\n📄 Demo report saved: {filename}")
        return filename

# Example demonstration scenarios
DEMO_SCENARIOS = {
    'bonk_conservative': {
        'token': 'BONK',
        'entry_low': 0.000030,
        'entry_high': 0.000032,
        'tp1': 0.000036,
        'tp2': 0.000040,
        'sl': 0.000028,
        'capital': 500.0
    },
    'wif_aggressive': {
        'token': 'WIF',
        'entry_low': 2.40,
        'entry_high': 2.50,
        'tp1': 3.00,
        'tp2': 3.50,
        'sl': 2.20,
        'capital': 300.0
    },
    'rndr_balanced': {
        'token': 'RNDR',
        'entry_low': 8.20,
        'entry_high': 8.50,
        'tp1': 10.20,
        'tp2': 11.50,
        'sl': 7.50,
        'capital': 400.0
    }
}

async def run_demo_scenario(scenario_name: str):
    """Run a specific demo scenario"""
    if scenario_name not in DEMO_SCENARIOS:
        print(f"❌ Unknown scenario: {scenario_name}")
        return
    
    scenario = DEMO_SCENARIOS[scenario_name]
    demo_runner = SecureDemoRunner()
    
    print(f"🎯 Running {scenario_name.upper()} scenario...")
    
    result = await demo_runner.run_secure_demo(**scenario)
    demo_runner.save_demo_report(f"{scenario_name}_demo_report.json")
    
    return result

async def main():
    """Main demonstration runner"""
    print("🎯 ΣIGMA-ΩSNIPER SECURE DEMONSTRATION SUITE")
    print("=" * 60)
    print("Available scenarios:")
    for name, scenario in DEMO_SCENARIOS.items():
        print(f"  - {name}: {scenario['token']} ${scenario['capital']}")
    
    # Run all scenarios
    demo_runner = SecureDemoRunner()
    
    for scenario_name, scenario in DEMO_SCENARIOS.items():
        print(f"\n{'='*60}")
        result = await demo_runner.run_secure_demo(**scenario)
        
        if result['success']:
            print(f"✅ {scenario_name.upper()} DEMONSTRATION SUCCESSFUL")
        else:
            print(f"❌ {scenario_name.upper()} DEMONSTRATION FAILED")
    
    # Save comprehensive report
    demo_runner.save_demo_report("comprehensive_sigma_demo_report.json")

if __name__ == "__main__":
    asyncio.run(main())

