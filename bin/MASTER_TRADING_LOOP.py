#!/usr/bin/env python3
"""
🏴 MASTER TRADING LOOP - Sovereign Shadow Empire
The eternal heartbeat that orchestrates all trading operations

This is the ONE loop that rules them all:
- Monitors markets 24/7
- Executes strategies based on conditions
- Enforces safety rules ruthlessly
- Handles crises automatically
- Logs every decision
- Never sleeps, never stops

Capital: $8,153.14 → Target: $50,000 by Q4 2025
"""

import asyncio
import aiohttp
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import traceback

# Add project paths
REPO_ROOT = Path("/Volumes/LegacySafe/SovereignShadow")
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "core" / "orchestration"))
sys.path.insert(0, str(REPO_ROOT / "core" / "monitoring"))
sys.path.insert(0, str(REPO_ROOT / "core" / "trading"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import your engines
try:
    from core.orchestration.sovereign_shadow_orchestrator import SovereignShadowOrchestrator
    from core.orchestration.SAFETY_RULES_IMPLEMENTATION import SafetyRulesImplementation
    from core.orchestration.CRISIS_MANAGEMENT_PLAYBOOK import CrisisManagementPlaybook
    from core.trading.strategy_knowledge_base import StrategyKnowledgeBase
except ImportError as e:
    logging.warning(f"Import warning: {e}")

# Configure structured logging
LOG_DIR = REPO_ROOT / "logs" / "master_loop"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"master_loop_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("MasterLoop")

def jlog(event: str, **fields):
    """Structured JSON logging"""
    log_entry = {
        "event": event,
        "timestamp": datetime.utcnow().isoformat(),
        **fields
    }
    log.info(json.dumps(log_entry))

    # Also write to JSON log
    json_log_path = LOG_DIR / f"events_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_log_path, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

@dataclass
class LoopConfig:
    """Master loop configuration"""
    # Operating mode
    mode: str = "paper"  # paper, live, monitor_only

    # Timing
    scan_interval_seconds: int = 60  # How often to scan markets
    strategy_check_seconds: int = 300  # How often to check strategy performance
    health_check_seconds: int = 600  # How often to check system health

    # Capital
    total_capital: float = 8153.14
    active_capital: float = 1638.49  # Coinbase hot wallet
    vault_capital: float = 6514.65  # Ledger vault (READ-ONLY)

    # Safety
    max_concurrent_trades: int = 3
    max_daily_trades: int = 50
    emergency_stop_loss: float = 1000  # Total daily loss limit

    # Exchanges
    active_exchanges: List[str] = None

    def __post_init__(self):
        if self.active_exchanges is None:
            self.active_exchanges = ["coinbase", "okx", "kraken"]

class MasterTradingLoop:
    """The eternal trading loop that orchestrates your empire"""

    def __init__(self, config: Optional[LoopConfig] = None):
        self.config = config or LoopConfig()

        # Initialize core systems
        self.orchestrator = None
        self.safety_rules = None
        self.crisis_playbook = None
        self.strategy_kb = None

        # Loop state
        self.running = False
        self.paused = False
        self.loop_count = 0
        self.start_time = None

        # Performance tracking
        self.stats = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "total_profit": 0.0,
            "total_loss": 0.0,
            "net_profit": 0.0,
            "daily_trades": 0,
            "daily_profit": 0.0,
            "last_trade_time": None,
            "last_reset_time": datetime.now()
        }

        # Market state
        self.market_state = {
            "btc_price": 0,
            "eth_price": 0,
            "volatility": "normal",
            "trend": "neutral",
            "last_update": None
        }

        # Active trades tracking
        self.active_trades = []

        jlog("MASTER_LOOP_INIT",
             mode=self.config.mode,
             capital=self.config.total_capital,
             exchanges=self.config.active_exchanges)

    async def initialize_systems(self):
        """Initialize all trading systems"""
        jlog("SYSTEMS_INIT_START")

        try:
            # Initialize orchestrator
            log.info("🎯 Initializing Sovereign Shadow Orchestrator...")
            self.orchestrator = SovereignShadowOrchestrator()

            # Initialize safety rules
            log.info("🛡️ Initializing Safety Rules System...")
            self.safety_rules = SafetyRulesImplementation()

            # Initialize crisis playbook
            log.info("🚨 Initializing Crisis Management Playbook...")
            self.crisis_playbook = CrisisManagementPlaybook()

            # Initialize strategy knowledge base
            log.info("📚 Initializing Strategy Knowledge Base...")
            self.strategy_kb = StrategyKnowledgeBase()

            # Test system health
            log.info("🏥 Testing system health...")
            health_ok = await self.check_system_health()

            if health_ok:
                jlog("SYSTEMS_INIT_SUCCESS", status="all_systems_operational")
                log.info("✅ All systems initialized successfully")
                return True
            else:
                jlog("SYSTEMS_INIT_WARNING", status="partial_operational")
                log.warning("⚠️ Some systems may not be fully operational")
                return False

        except Exception as e:
            jlog("SYSTEMS_INIT_ERROR", error=str(e), traceback=traceback.format_exc())
            log.error(f"❌ System initialization error: {e}")
            return False

    async def check_system_health(self) -> bool:
        """Check health of all systems"""
        try:
            if self.orchestrator:
                health = await self.orchestrator.test_unified_system()
                jlog("HEALTH_CHECK", systems_operational=health)
                return health
            return False
        except Exception as e:
            jlog("HEALTH_CHECK_ERROR", error=str(e))
            return False

    async def scan_markets(self) -> List[Dict[str, Any]]:
        """Scan all markets for opportunities"""
        opportunities = []

        try:
            # This would integrate with your live_market_scanner.py
            # For now, return mock opportunities based on time

            current_time = datetime.now()

            # Mock BTC/ETH prices (in production, fetch real data)
            self.market_state = {
                "btc_price": 106000 + (hash(str(current_time)) % 1000),
                "eth_price": 4800 + (hash(str(current_time)) % 100),
                "volatility": "normal",
                "trend": "neutral",
                "last_update": current_time.isoformat()
            }

            # Check for arbitrage opportunities
            if self.loop_count % 5 == 0:  # Every 5 scans
                opportunities.append({
                    "type": "arbitrage",
                    "pair": "BTC/USDT",
                    "exchanges": ["coinbase", "okx"],
                    "spread": 0.00125,
                    "amount": 100,
                    "confidence": 0.85,
                    "expires_at": (current_time + timedelta(seconds=30)).isoformat()
                })

            # Check for sniping opportunities
            if self.loop_count % 10 == 0:  # Every 10 scans
                opportunities.append({
                    "type": "sniping",
                    "pair": "ETH/USDT",
                    "exchange": "coinbase",
                    "entry_price": self.market_state["eth_price"],
                    "target_price": self.market_state["eth_price"] * 1.05,
                    "amount": 50,
                    "confidence": 0.75,
                    "expires_at": (current_time + timedelta(minutes=5)).isoformat()
                })

            jlog("MARKET_SCAN_COMPLETE",
                 opportunities_found=len(opportunities),
                 btc_price=self.market_state["btc_price"],
                 eth_price=self.market_state["eth_price"])

            return opportunities

        except Exception as e:
            jlog("MARKET_SCAN_ERROR", error=str(e))
            log.error(f"Market scan error: {e}")
            return []

    async def evaluate_opportunity(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate if opportunity meets all criteria"""

        try:
            # Step 1: Safety rules validation
            exchange = opportunity.get("exchanges", [opportunity.get("exchange", "coinbase")])[0]
            amount = opportunity.get("amount", 100)
            trade_type = opportunity.get("type", "unknown")

            is_safe, safety_message = self.safety_rules.validate_trade_request(
                exchange, amount, trade_type
            )

            if not is_safe:
                jlog("OPPORTUNITY_REJECTED_SAFETY",
                     opportunity=opportunity,
                     reason=safety_message)
                return None

            # Step 2: Crisis playbook validation
            trade_description = f"{trade_type} {opportunity.get('pair', 'unknown')}"
            crisis_check = self.crisis_playbook.override_system_suggestions(trade_description)

            if crisis_check.get("override"):
                jlog("OPPORTUNITY_REJECTED_CRISIS",
                     opportunity=opportunity,
                     reason=crisis_check["violation_message"])
                return None

            # Step 3: Check concurrent trades limit
            if len(self.active_trades) >= self.config.max_concurrent_trades:
                jlog("OPPORTUNITY_REJECTED_LIMIT",
                     opportunity=opportunity,
                     reason=f"Max concurrent trades reached: {len(self.active_trades)}")
                return None

            # Step 4: Check daily trades limit
            if self.stats["daily_trades"] >= self.config.max_daily_trades:
                jlog("OPPORTUNITY_REJECTED_DAILY_LIMIT",
                     opportunity=opportunity,
                     reason=f"Daily trade limit reached: {self.stats['daily_trades']}")
                return None

            # All checks passed
            jlog("OPPORTUNITY_APPROVED",
                 opportunity=opportunity,
                 confidence=opportunity.get("confidence", 0))

            return opportunity

        except Exception as e:
            jlog("OPPORTUNITY_EVALUATION_ERROR", error=str(e))
            return None

    async def execute_trade(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute approved trade through orchestrator"""

        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.loop_count}"

        jlog("TRADE_EXECUTION_START",
             trade_id=trade_id,
             opportunity=opportunity,
             mode=self.config.mode)

        try:
            # Add to active trades
            self.active_trades.append({
                "trade_id": trade_id,
                "opportunity": opportunity,
                "start_time": datetime.now(),
                "status": "executing"
            })

            # Execute through orchestrator
            if self.orchestrator:
                # Convert opportunity to trade signal
                trade_signal = {
                    **opportunity,
                    "btc_price": self.market_state.get("btc_price"),
                    "market_flags": {
                        "volatility": self.market_state.get("volatility"),
                        "trend": self.market_state.get("trend")
                    }
                }

                success = await self.orchestrator.execute_unified_trade(trade_signal)

                # Simulate result (in production, get real result)
                if success:
                    strategy_type = opportunity.get("type", "arbitrage")
                    amount = opportunity.get("amount", 100)

                    # Calculate profit based on strategy
                    if strategy_type == "arbitrage":
                        profit = amount * 0.00125  # 0.125%
                    elif strategy_type == "sniping":
                        profit = amount * 0.05  # 5%
                    elif strategy_type == "scalping":
                        profit = amount * 0.0005  # 0.05%
                    else:
                        profit = amount * 0.001  # 0.1%

                    result = {
                        "trade_id": trade_id,
                        "success": True,
                        "profit": profit,
                        "loss": 0,
                        "amount": amount,
                        "strategy": strategy_type,
                        "exchange": opportunity.get("exchanges", [opportunity.get("exchange", "unknown")])[0],
                        "execution_time": datetime.now().isoformat(),
                        "mode": self.config.mode
                    }
                else:
                    result = {
                        "trade_id": trade_id,
                        "success": False,
                        "profit": 0,
                        "loss": opportunity.get("amount", 100) * 0.001,  # Small loss
                        "strategy": opportunity.get("type"),
                        "reason": "execution_failed"
                    }

                # Update stats
                self.update_stats(result)

                # Remove from active trades
                self.active_trades = [t for t in self.active_trades if t["trade_id"] != trade_id]

                jlog("TRADE_EXECUTION_COMPLETE",
                     trade_id=trade_id,
                     success=result["success"],
                     profit=result.get("profit", 0),
                     mode=self.config.mode)

                return result
            else:
                # No orchestrator, simulation mode
                jlog("TRADE_SIMULATION", trade_id=trade_id)
                return {
                    "trade_id": trade_id,
                    "success": True,
                    "profit": 0,
                    "mode": "simulation"
                }

        except Exception as e:
            jlog("TRADE_EXECUTION_ERROR",
                 trade_id=trade_id,
                 error=str(e),
                 traceback=traceback.format_exc())

            # Remove from active trades
            self.active_trades = [t for t in self.active_trades if t["trade_id"] != trade_id]

            return {
                "trade_id": trade_id,
                "success": False,
                "error": str(e)
            }

    def update_stats(self, trade_result: Dict[str, Any]):
        """Update loop statistics"""
        self.stats["total_trades"] += 1
        self.stats["daily_trades"] += 1
        self.stats["last_trade_time"] = datetime.now()

        if trade_result.get("success"):
            self.stats["successful_trades"] += 1
            profit = trade_result.get("profit", 0)
            self.stats["total_profit"] += profit
            self.stats["daily_profit"] += profit
            self.stats["net_profit"] += profit
        else:
            self.stats["failed_trades"] += 1
            loss = trade_result.get("loss", 0)
            self.stats["total_loss"] += loss
            self.stats["daily_profit"] -= loss
            self.stats["net_profit"] -= loss

        # Update safety rules
        if self.safety_rules:
            self.safety_rules.update_trade_result({
                "pnl": trade_result.get("profit", 0) - trade_result.get("loss", 0)
            })

    def reset_daily_stats(self):
        """Reset daily statistics"""
        now = datetime.now()
        if now.date() > self.stats["last_reset_time"].date():
            jlog("DAILY_STATS_RESET",
                 daily_trades=self.stats["daily_trades"],
                 daily_profit=self.stats["daily_profit"])

            self.stats["daily_trades"] = 0
            self.stats["daily_profit"] = 0.0
            self.stats["last_reset_time"] = now

    def display_status(self):
        """Display current loop status"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        win_rate = (self.stats["successful_trades"] / max(self.stats["total_trades"], 1)) * 100

        print(f"""
╔════════════════════════════════════════════════════════════════════╗
║ 🏴 MASTER TRADING LOOP - SOVEREIGN SHADOW EMPIRE                  ║
╠════════════════════════════════════════════════════════════════════╣
║ Status: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}    Mode: {self.config.mode.upper():8s}    Loop: {self.loop_count:6d} ║
║ Uptime: {str(uptime).split('.')[0]:20s}    Capital: ${self.config.total_capital:,.2f}     ║
╠════════════════════════════════════════════════════════════════════╣
║ 📊 PERFORMANCE                                                     ║
║   Total Trades: {self.stats['total_trades']:6d}  Win Rate: {win_rate:5.1f}%  Active: {len(self.active_trades):2d}    ║
║   Today Trades: {self.stats['daily_trades']:6d}  Today P&L: ${self.stats['daily_profit']:+8.2f}         ║
║   Net Profit:   ${self.stats['net_profit']:+8.2f}                                  ║
╠════════════════════════════════════════════════════════════════════╣
║ 🌐 MARKET STATE                                                    ║
║   BTC: ${self.market_state.get('btc_price', 0):,.2f}   ETH: ${self.market_state.get('eth_price', 0):,.2f}             ║
║   Volatility: {self.market_state.get('volatility', 'unknown'):10s}  Trend: {self.market_state.get('trend', 'unknown'):10s}  ║
╠════════════════════════════════════════════════════════════════════╣
║ 🛡️ SAFETY STATUS                                                   ║
║   Emergency Stop: {'🚨 ACTIVE' if self.safety_rules and self.safety_rules.current_status.get('emergency_stop_active') else '🟢 NORMAL':10s}                            ║
║   Daily Loss Limit: ${self.config.emergency_stop_loss:,.2f} remaining          ║
╚════════════════════════════════════════════════════════════════════╝
        """)

    async def run_forever(self):
        """Run the master trading loop forever"""
        self.running = True
        self.start_time = datetime.now()

        jlog("MASTER_LOOP_START",
             mode=self.config.mode,
             capital=self.config.total_capital)

        log.info("🚀 MASTER TRADING LOOP STARTED")
        log.info(f"Mode: {self.config.mode.upper()}")
        log.info(f"Capital: ${self.config.total_capital:,.2f}")
        log.info(f"Scan Interval: {self.config.scan_interval_seconds}s")

        try:
            while self.running:
                self.loop_count += 1

                try:
                    # Reset daily stats if needed
                    self.reset_daily_stats()

                    # Health check every N loops
                    if self.loop_count % (self.config.health_check_seconds // self.config.scan_interval_seconds) == 0:
                        log.info("🏥 Running system health check...")
                        await self.check_system_health()

                    # Scan markets for opportunities
                    opportunities = await self.scan_markets()

                    # Evaluate and execute each opportunity
                    for opportunity in opportunities:
                        if not self.running:
                            break

                        # Evaluate
                        approved = await self.evaluate_opportunity(opportunity)

                        if approved:
                            # Execute
                            result = await self.execute_trade(approved)

                            # Log result
                            if result.get("success"):
                                log.info(f"✅ Trade successful: {result.get('trade_id')} - Profit: ${result.get('profit', 0):.2f}")
                            else:
                                log.warning(f"❌ Trade failed: {result.get('trade_id')}")

                    # Display status every 10 loops
                    if self.loop_count % 10 == 0:
                        self.display_status()

                    # Wait for next scan
                    await asyncio.sleep(self.config.scan_interval_seconds)

                except Exception as e:
                    jlog("LOOP_ITERATION_ERROR",
                         loop_count=self.loop_count,
                         error=str(e),
                         traceback=traceback.format_exc())
                    log.error(f"Loop iteration error: {e}")
                    await asyncio.sleep(60)  # Wait longer on error

        except KeyboardInterrupt:
            log.info("🛑 Keyboard interrupt received")
            jlog("MASTER_LOOP_INTERRUPTED", reason="keyboard_interrupt")
        except Exception as e:
            log.critical(f"💥 Fatal error in master loop: {e}")
            jlog("MASTER_LOOP_FATAL_ERROR",
                 error=str(e),
                 traceback=traceback.format_exc())
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown the loop"""
        log.info("🛑 Shutting down master trading loop...")
        jlog("MASTER_LOOP_SHUTDOWN",
             total_loops=self.loop_count,
             total_trades=self.stats["total_trades"],
             net_profit=self.stats["net_profit"])

        self.running = False

        # Close orchestrator
        if self.orchestrator:
            await self.orchestrator.close()

        # Save final stats
        stats_file = LOG_DIR / f"final_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump({
                "stats": self.stats,
                "config": asdict(self.config),
                "loop_count": self.loop_count,
                "shutdown_time": datetime.now().isoformat()
            }, f, indent=2)

        log.info(f"✅ Shutdown complete. Stats saved to {stats_file}")
        print("\n🏴 MASTER TRADING LOOP STOPPED")
        print(f"Total Loops: {self.loop_count}")
        print(f"Total Trades: {self.stats['total_trades']}")
        print(f"Net Profit: ${self.stats['net_profit']:.2f}")
        print(f"Stats saved to: {stats_file}")

async def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        🏴  SOVEREIGN SHADOW EMPIRE - MASTER TRADING LOOP  🏴       ║
║                                                                    ║
║                  The Heart That Never Stops Beating                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Master Trading Loop")
    parser.add_argument("--mode", choices=["paper", "live", "monitor"],
                       default="paper", help="Operating mode")
    parser.add_argument("--interval", type=int, default=60,
                       help="Scan interval in seconds")
    args = parser.parse_args()

    # Create config
    config = LoopConfig(
        mode=args.mode,
        scan_interval_seconds=args.interval
    )

    # Create and initialize loop
    loop = MasterTradingLoop(config)

    log.info("Initializing systems...")
    initialized = await loop.initialize_systems()

    if not initialized:
        log.warning("⚠️ System initialization incomplete - proceeding anyway")

    # Run forever
    await loop.run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Your empire awaits your return.")
