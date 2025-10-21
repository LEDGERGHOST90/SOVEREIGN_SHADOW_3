#!/usr/bin/env python3
"""
🚀 Deploy Tactical Scalps - Launcher for position-aware range trading

Integrates:
- Tactical scalp config (LSR guards, funding divergence, liquidation bands)
- Risk gate validator (enforces all safety rules)
- Market data feeds (positioning, funding, OI, Aave HF)
- Sovereign Shadow orchestrator (execution layer)

Usage:
    python3 scripts/deploy_tactical_scalps.py --mode paper
    python3 scripts/deploy_tactical_scalps.py --mode test --max-trades 3
    python3 scripts/deploy_tactical_scalps.py --mode live --validate-only

Part of the Sovereign Shadow Trading System
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.trading.tactical_risk_gate import TacticalRiskGate, TradeRequest, ValidationResult

logger = logging.getLogger(__name__)


class TacticalScalpDeployment:
    """
    Main deployment coordinator for tactical scalping strategies.
    
    Responsibilities:
    - Load and validate config
    - Initialize risk gate
    - Connect market data feeds
    - Monitor positioning/funding/OI
    - Execute approved trades
    - Track session performance
    """
    
    def __init__(self, mode: str = "paper", config_path: Optional[str] = None):
        self.mode = mode  # paper | test | live
        self.config_path = config_path or "/Volumes/LegacySafe/SovereignShadow/config/tactical_scalp_config.json"
        
        logger.info(f"🏴 Initializing Tactical Scalp Deployment (mode: {mode})")
        
        # Load config
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        if not self.config.get("enabled", False):
            logger.error("❌ Tactical scalping is disabled in config")
            sys.exit(1)
        
        logger.info(f"✅ Loaded config: {self.config.get('session_name', 'unknown')}")
        logger.info(f"📊 Regime: {self.config.get('regime', 'unknown')}")
        logger.info(f"💭 Thesis: {self.config.get('thesis', 'N/A')[:100]}...")
        
        # Initialize risk gate
        self.risk_gate = TacticalRiskGate(config_path=self.config_path)
        
        # Strategy tracking
        self.active_strategies = []
        self.enabled_strategies = [
            name for name, config in self.config.get("strategies", {}).items()
            if config.get("enabled", False)
        ]
        
        logger.info(f"🎯 Enabled strategies: {', '.join(self.enabled_strategies)}")
        
        # Market context
        self.market_context = self.config.get("market_context", {})
        self.bias = self.config.get("bias", {})
        
        logger.info(f"🎲 Base case ({self.bias.get('base_case_pct', 0)}%): {self.bias.get('base_case', 'N/A')}")
        logger.info(f"🎲 Alt path ({self.bias.get('alt_path_pct', 0)}%): {self.bias.get('alt_path', 'N/A')}")
    
    def initialize_market_data(self):
        """Initialize risk gate with current market positioning"""
        
        logger.info("📡 Initializing market data feeds...")
        
        # Load positioning data from config
        positioning = self.market_context.get("positioning", {})
        for asset, data in positioning.items():
            if isinstance(data, dict) and "long_pct" in data and "short_pct" in data:
                self.risk_gate.update_positioning(
                    asset=asset,
                    long_pct=data["long_pct"],
                    short_pct=data["short_pct"]
                )
                logger.info(f"  {asset}: {data['long_pct']:.1f}% L / {data['short_pct']:.1f}% S")
        
        # Load funding rates
        funding = self.market_context.get("funding_rates_bps", {})
        if "binance_btc" in funding and "okx_btc" in funding:
            self.risk_gate.update_funding(
                asset="BTC",
                binance_bps=funding["binance_btc"],
                okx_bps=funding["okx_btc"]
            )
            spread = funding["binance_btc"] - funding["okx_btc"]
            logger.info(f"  BTC funding: Binance {funding['binance_btc']:.2f} bps, OKX {funding['okx_btc']:.2f} bps (spread: {spread:+.2f})")
        
        # Load OI change
        oi_change = self.market_context.get("open_interest_change_24h_pct")
        if oi_change is not None:
            self.risk_gate.update_oi_change(oi_change)
            logger.info(f"  OI 24h change: {oi_change:+.2f}%")
        
        logger.info("✅ Market data initialized")
    
    async def update_aave_health_factor(self):
        """Fetch and update Aave health factor"""
        try:
            # In production, this would call Aave API
            # For now, use a safe default
            hf = 2.50  # Conservative default
            self.risk_gate.update_aave_health_factor(hf)
            logger.debug(f"💊 Aave HF updated: {hf:.2f}")
            return hf
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch Aave HF: {e}")
            return None
    
    async def monitor_market_feeds(self):
        """
        Continuous monitoring loop for market data updates.
        
        Updates:
        - Positioning (every 60s)
        - Funding rates (every 300s)
        - OI changes (every 120s)
        - Aave HF (every 30s)
        """
        
        logger.info("👁️ Starting market feed monitoring...")
        
        while True:
            try:
                # In production, these would call real APIs
                # For demo, we just log that we're monitoring
                
                # Update Aave HF
                await self.update_aave_health_factor()
                
                # Check kill switch
                should_halt, reason = self.risk_gate.should_halt_trading()
                if should_halt:
                    logger.error(f"🛑 KILL SWITCH ACTIVATED: {reason}")
                    await self.emergency_flatten_all()
                    break
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Market feed monitor error: {e}")
                await asyncio.sleep(60)
    
    async def emergency_flatten_all(self):
        """Emergency: flatten all positions immediately"""
        logger.critical("🚨 EMERGENCY FLATTEN ALL POSITIONS")
        
        stats = self.risk_gate.get_session_stats()
        open_trades = stats.get("open_trades", 0)
        
        if open_trades > 0:
            logger.critical(f"🚨 Closing {open_trades} open positions at market")
            # In production, would send market close orders
        
        logger.critical("🛑 All trading halted. Manual intervention required.")
    
    def validate_setup(self) -> bool:
        """Pre-flight validation checks"""
        
        logger.info("🔍 Running pre-flight validation...")
        
        checks = []
        
        # 1. Config loaded
        checks.append(("Config loaded", self.config is not None))
        
        # 2. Risk gate initialized
        checks.append(("Risk gate initialized", self.risk_gate is not None))
        
        # 3. At least one strategy enabled
        checks.append(("Strategies enabled", len(self.enabled_strategies) > 0))
        
        # 4. Market data initialized
        has_positioning = len(self.risk_gate.positioning_cache) > 0
        checks.append(("Market positioning loaded", has_positioning))
        
        # 5. Safety limits configured
        safety_overrides = self.config.get("sovereign_shadow_safety_overrides", {})
        respects_limits = safety_overrides.get("respect_global_limits", False)
        checks.append(("Respects global safety limits", respects_limits))
        
        # 6. Kill switch configured
        kill_switch = self.config.get("kill_switch", {})
        has_kill_switch = len(kill_switch) > 0
        checks.append(("Kill switch configured", has_kill_switch))
        
        # Print results
        logger.info("Pre-flight checklist:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            logger.info("🟢 All pre-flight checks passed")
        else:
            logger.error("🔴 Pre-flight checks failed")
        
        return all_passed
    
    def display_operator_checklist(self):
        """Display operator checklist from config"""
        
        checklist = self.config.get("operator_checklist", [])
        if not checklist:
            return
        
        logger.info("\n" + "="*70)
        logger.info("📋 OPERATOR CHECKLIST")
        logger.info("="*70)
        
        for i, item in enumerate(checklist, 1):
            logger.info(f"{i}. {item}")
        
        logger.info("="*70 + "\n")
    
    def display_liquidation_map(self):
        """Display liquidation bands for reference"""
        
        liq_bands = self.market_context.get("liquidation_bands", {})
        if not liq_bands:
            return
        
        logger.info("\n" + "="*70)
        logger.info("🎯 LIQUIDATION BANDS")
        logger.info("="*70)
        
        for asset, bands in liq_bands.items():
            current = bands.get("current", 0)
            upper = bands.get("upper", [])
            lower = bands.get("lower", [])
            
            logger.info(f"\n{asset} @ ${current:,.0f}")
            logger.info(f"  Upper targets: {', '.join([f'${x:,.0f}' for x in upper])}")
            logger.info(f"  Lower targets: {', '.join([f'${x:,.0f}' for x in lower])}")
        
        logger.info("="*70 + "\n")
    
    def display_capital_rules(self):
        """Display capital deployment rules"""
        
        cap_config = self.config.get("capital_deployment", {})
        if not cap_config:
            return
        
        logger.info("\n" + "="*70)
        logger.info("💰 CAPITAL DEPLOYMENT RULES")
        logger.info("="*70)
        
        logger.info(f"Per-trade notional: ${cap_config.get('per_trade_notional_usd_range', [0,0])[0]:.0f}-${cap_config.get('per_trade_notional_usd_range', [0,0])[1]:.0f}")
        logger.info(f"Daily trade cap: {cap_config.get('daily_cap_trades', 0)} trades")
        logger.info(f"Stop conditions: {', '.join(cap_config.get('stop_conditions', []))}")
        
        logger.info("="*70 + "\n")
    
    async def run(self, validate_only: bool = False, max_trades: Optional[int] = None):
        """Main execution loop"""
        
        # Pre-flight checks
        if not self.validate_setup():
            logger.error("❌ Pre-flight validation failed. Aborting.")
            return
        
        # Display operator info
        self.display_operator_checklist()
        self.display_liquidation_map()
        self.display_capital_rules()
        
        if validate_only:
            logger.info("✅ Validation complete. Exiting (--validate-only mode)")
            return
        
        if self.mode == "paper":
            logger.warning("📝 PAPER TRADING MODE - No real capital at risk")
        elif self.mode == "test":
            logger.warning("🧪 TEST MODE - Small real capital ($100 max)")
        elif self.mode == "live":
            logger.warning("🔴 LIVE TRADING MODE - Real capital at risk")
            logger.warning("⚠️  Press Ctrl+C within 5 seconds to abort...")
            await asyncio.sleep(5)
        
        logger.info(f"🚀 Tactical scalping deployment started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🎯 Max trades: {max_trades or 'unlimited (per daily cap)'}")
        
        # Start market monitoring in background
        monitor_task = asyncio.create_task(self.monitor_market_feeds())
        
        try:
            # Main trading loop would go here
            # For now, just demonstrate the risk gate with a sample trade
            
            logger.info("\n" + "="*70)
            logger.info("🎮 DEMO: Validating sample BTC long entry at lower band")
            logger.info("="*70 + "\n")
            
            sample_request = TradeRequest(
                strategy_name="BTC_range_scalp",
                asset="BTC",
                side="long",
                notional_usd=25.0,
                stop_loss_bps=28,
                entry_price=106800,
                conditions_met={"reclaim": True, "delta_positive": True},
                timestamp=datetime.now()
            )
            
            result = self.risk_gate.validate_trade(sample_request)
            
            logger.info(f"Validation result:")
            logger.info(f"  Approved: {result.approved}")
            logger.info(f"  Reason: {result.reason}")
            logger.info(f"  Size adjustment: {result.size_adjustment:.2f}×")
            logger.info(f"  Adjusted notional: ${sample_request.notional_usd * result.size_adjustment:.2f}")
            logger.info(f"  Stop: {result.stop_adjustment_bps or sample_request.stop_loss_bps} bps")
            
            if result.warnings:
                logger.info(f"  Warnings:")
                for warning in result.warnings:
                    logger.info(f"    {warning}")
            
            # In production, if approved, would execute trade here
            if result.approved:
                logger.info("\n✅ Trade would be executed (demo mode - no actual execution)")
            
            logger.info("\n" + "="*70)
            logger.info("Session stats:")
            logger.info("="*70)
            stats = self.risk_gate.get_session_stats()
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
            logger.info("="*70 + "\n")
            
            # Keep monitoring running
            logger.info("👁️ Market monitoring active. Press Ctrl+C to stop.")
            await monitor_task
            
        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutdown signal received")
            monitor_task.cancel()
        
        except Exception as e:
            logger.error(f"❌ Critical error: {e}", exc_info=True)
            monitor_task.cancel()
        
        finally:
            logger.info("🛑 Tactical scalping deployment stopped")
            
            # Final stats
            final_stats = self.risk_gate.get_session_stats()
            logger.info(f"\nFinal session stats:")
            logger.info(f"  Total trades: {final_stats.get('total_trades', 0)}")
            logger.info(f"  Session P&L: ${final_stats.get('session_pnl_usd', 0):+.2f}")
            logger.info(f"  Duration: {final_stats.get('session_duration_min', 0):.1f} minutes")


def main():
    parser = argparse.ArgumentParser(
        description="🏴 Deploy Tactical Scalps - Position-aware range trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Paper trading (safe testing)
  python3 scripts/deploy_tactical_scalps.py --mode paper
  
  # Validation only (no execution)
  python3 scripts/deploy_tactical_scalps.py --validate-only
  
  # Test mode with max 3 trades
  python3 scripts/deploy_tactical_scalps.py --mode test --max-trades 3
  
  # Live production (real capital)
  python3 scripts/deploy_tactical_scalps.py --mode live
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['paper', 'test', 'live'],
        default='paper',
        help='Trading mode (paper/test/live)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Run validation checks only, no execution'
    )
    
    parser.add_argument(
        '--max-trades',
        type=int,
        help='Maximum number of trades to execute'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to tactical scalp config (default: config/tactical_scalp_config.json)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_dir = Path("/Volumes/LegacySafe/SovereignShadow/logs/tactical_scalps")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )
    
    # Create deployment
    deployment = TacticalScalpDeployment(
        mode=args.mode,
        config_path=args.config
    )
    
    # Initialize market data
    deployment.initialize_market_data()
    
    # Run
    asyncio.run(deployment.run(
        validate_only=args.validate_only,
        max_trades=args.max_trades
    ))


if __name__ == "__main__":
    main()

