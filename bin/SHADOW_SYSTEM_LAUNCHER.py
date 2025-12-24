#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW - MASTER SYSTEM LAUNCHER
The ONE command to launch entire trading empire

Usage:
    python3 SHADOW_SYSTEM_LAUNCHER.py [mode]

Modes:
    monitor     - Portfolio monitoring only (safe, default)
    trade       - Enable live trading (requires confirmation)
    full        - Launch everything (orchestrator + MCP + monitoring)
    check       - System health check
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Project paths
SHADOW_ROOT = Path(__file__).parent
sys.path.insert(0, str(SHADOW_ROOT))

from dotenv import load_dotenv
load_dotenv()

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ShadowSystemLauncher:
    """Master launcher for Sovereign Shadow system"""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False

    def print_banner(self):
        """Print startup banner"""
        print(f"\n{Colors.CYAN}{'='*70}")
        print(f"🏴 SOVEREIGN SHADOW TRADING SYSTEM")
        print(f"{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Philosophy:{Colors.ENDC} Fearless. Bold. Smiling through chaos.")
        print(f"{Colors.BOLD}Initialized:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def check_environment(self) -> Dict[str, bool]:
        """Verify environment setup"""
        print(f"{Colors.YELLOW}🔍 ENVIRONMENT CHECK{Colors.ENDC}")
        print("-" * 70)

        checks = {}

        # Check Python environment
        venv_path = SHADOW_ROOT / ".venv"
        checks['venv'] = venv_path.exists()
        print(f"  {'✅' if checks['venv'] else '❌'} Virtual environment: {venv_path}")

        # Check .env file
        env_path = SHADOW_ROOT / ".env"
        checks['env_file'] = env_path.exists()
        print(f"  {'✅' if checks['env_file'] else '❌'} Environment file: {env_path}")

        # Check API keys
        checks['coinbase_api'] = bool(os.getenv('COINBASE_API_KEY'))
        print(f"  {'✅' if checks['coinbase_api'] else '❌'} Coinbase API configured")

        checks['okx_api'] = bool(os.getenv('OKX_API_KEY'))
        print(f"  {'✅' if checks['okx_api'] else '❌'} OKX API configured")

        checks['kraken_api'] = bool(os.getenv('KRAKEN_API_KEY'))
        print(f"  {'✅' if checks['kraken_api'] else '❌'} Kraken API configured")

        # Check key modules
        modules = [
            'core/portfolio/unified_portfolio_api.py',
            'core/portfolio/cold_vault_monitor.py',
            'core/portfolio/COLD_VAULT_KNOWLEDGE_BASE.py',
            'core/trading/EXECUTE_MANUAL_TRADE.py',
            'shadow_sdk/simple_mcp_server.py'
        ]

        for module in modules:
            path = SHADOW_ROOT / module
            checks[module] = path.exists()
            status = '✅' if checks[module] else '❌'
            print(f"  {status} {module}")

        print()
        return checks

    def check_portfolio_health(self):
        """Check portfolio status"""
        print(f"{Colors.YELLOW}💰 PORTFOLIO HEALTH CHECK{Colors.ENDC}")
        print("-" * 70)

        try:
            from core.portfolio.unified_portfolio_api import UnifiedPortfolioAPI

            api = UnifiedPortfolioAPI()
            portfolio = api.get_complete_portfolio(force_refresh=True)

            print(f"  Total Value: ${portfolio['total_portfolio_value_usd']:,.2f}")
            print(f"  Cold Storage: ${portfolio['components']['cold_storage']['total_value_usd']:,.2f} (🔒 LOCKED)")
            print(f"  Trading Capital: ${portfolio['components']['hot_wallet_velocity']['available_for_trading']:,.2f}")
            print(f"  AAVE Health Factor: {portfolio['components']['defi_positions']['health_factor']}")

            # Safety checks
            safety = portfolio['safety_checks']
            print(f"\n  Safety Status:")
            print(f"    {'✅' if safety['cold_vault_secure'] else '❌'} Cold Vault Secure")
            print(f"    {'✅' if safety['health_factor_safe'] else '❌'} AAVE Safe")
            print(f"    {'✅' if safety['trading_capital_available'] else '❌'} Capital Available")

            return True

        except Exception as e:
            print(f"  {Colors.RED}❌ Error: {e}{Colors.ENDC}")
            return False

        finally:
            print()

    def launch_component(self, name: str, command: List[str], description: str) -> Optional[subprocess.Popen]:
        """Launch a system component"""
        print(f"  🚀 Starting {name}... ", end='', flush=True)

        try:
            process = subprocess.Popen(
                command,
                cwd=SHADOW_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a moment to check if it crashes immediately
            time.sleep(1)
            if process.poll() is None:
                print(f"{Colors.GREEN}✅ Running (PID {process.pid}){Colors.ENDC}")
                self.processes.append(process)
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"{Colors.RED}❌ Failed{Colors.ENDC}")
                if stderr:
                    print(f"     Error: {stderr[:200]}")
                return None

        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")
            return None

    def launch_monitor_mode(self):
        """Launch in monitor-only mode (safe)"""
        print(f"\n{Colors.CYAN}📊 LAUNCHING MONITOR MODE{Colors.ENDC}")
        print("-" * 70)

        # Launch portfolio monitoring
        self.launch_component(
            "Portfolio Monitor",
            [sys.executable, "core/portfolio/unified_portfolio_api.py"],
            "Real-time portfolio tracking"
        )

        print(f"\n{Colors.GREEN}✅ Monitor mode active{Colors.ENDC}")
        print(f"{Colors.YELLOW}ℹ️  Read-only mode - No trading will occur{Colors.ENDC}\n")

    def launch_full_system(self):
        """Launch complete system"""
        print(f"\n{Colors.CYAN}🚀 LAUNCHING FULL SYSTEM{Colors.ENDC}")
        print("-" * 70)

        # 1. Launch MCP Server
        mcp_cmd = [
            sys.executable,
            "shadow_sdk/simple_mcp_server.py"
        ]
        self.launch_component(
            "MCP Server",
            mcp_cmd,
            "Claude Desktop integration"
        )

        # 2. Launch Portfolio API
        self.launch_component(
            "Portfolio API",
            [sys.executable, "core/portfolio/unified_portfolio_api.py"],
            "Unified portfolio monitoring"
        )

        # 3. Check if orchestrator should launch
        # (Commented out for safety - uncomment when ready)
        # self.launch_component(
        #     "AI Orchestrator",
        #     [sys.executable, "core/orchestration/sovereign_shadow_orchestrator.py"],
        #     "AI trading coordination"
        # )

        print(f"\n{Colors.GREEN}✅ Full system operational{Colors.ENDC}\n")

    def shutdown(self):
        """Gracefully shutdown all components"""
        print(f"\n{Colors.YELLOW}🛑 SHUTTING DOWN{Colors.ENDC}")
        print("-" * 70)

        for process in self.processes:
            try:
                print(f"  Stopping PID {process.pid}... ", end='', flush=True)
                process.terminate()
                process.wait(timeout=5)
                print(f"{Colors.GREEN}✅{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}⚠️  Force killing{Colors.ENDC}")
                process.kill()
            except Exception as e:
                print(f"{Colors.RED}❌ {e}{Colors.ENDC}")

        print(f"\n{Colors.GREEN}✅ Shutdown complete{Colors.ENDC}\n")

    def run(self, mode: str = 'monitor'):
        """Main entry point"""
        self.print_banner()

        # Environment check
        checks = self.check_environment()
        if not all(checks.values()):
            print(f"{Colors.RED}⚠️  Environment check failed!{Colors.ENDC}")
            print(f"{Colors.YELLOW}ℹ️  Some components may not work properly{Colors.ENDC}\n")

        # Portfolio health check
        self.check_portfolio_health()

        # Launch based on mode
        if mode == 'check':
            print(f"{Colors.GREEN}✅ System check complete{Colors.ENDC}\n")
            return

        elif mode == 'monitor':
            self.launch_monitor_mode()

        elif mode == 'full':
            print(f"{Colors.YELLOW}⚠️  WARNING: Full system mode{Colors.ENDC}")
            print(f"This will launch all components including trading systems.\n")
            response = input("Continue? (yes/no): ")
            if response.lower() != 'yes':
                print(f"{Colors.RED}Cancelled{Colors.ENDC}\n")
                return

            self.launch_full_system()

        elif mode == 'trade':
            print(f"{Colors.RED}⚠️  ⚠️  ⚠️  LIVE TRADING MODE ⚠️  ⚠️  ⚠️{Colors.ENDC}")
            print(f"This mode enables REAL trading with REAL money!\n")
            response = input("Type 'ENABLE TRADING' to confirm: ")
            if response != 'ENABLE TRADING':
                print(f"{Colors.RED}Cancelled{Colors.ENDC}\n")
                return

            # Set trading mode environment variable
            os.environ['ALLOW_LIVE_EXCHANGE'] = '1'
            os.environ['SOVEREIGN_READONLY'] = '0'

            self.launch_full_system()

        else:
            print(f"{Colors.RED}❌ Unknown mode: {mode}{Colors.ENDC}\n")
            return

        # Keep running until interrupted
        try:
            self.running = True
            print(f"{Colors.CYAN}Press Ctrl+C to shutdown{Colors.ENDC}\n")

            while self.running:
                time.sleep(1)

                # Check if any process died
                for process in self.processes[:]:
                    if process.poll() is not None:
                        print(f"{Colors.RED}⚠️  Process {process.pid} exited{Colors.ENDC}")
                        self.processes.remove(process)

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Received interrupt signal{Colors.ENDC}")

        finally:
            self.shutdown()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='🏴 Sovereign Shadow Master Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 SHADOW_SYSTEM_LAUNCHER.py check       # Health check only
  python3 SHADOW_SYSTEM_LAUNCHER.py monitor     # Safe monitoring mode
  python3 SHADOW_SYSTEM_LAUNCHER.py full        # Launch full system (read-only)
  python3 SHADOW_SYSTEM_LAUNCHER.py trade       # Enable live trading (dangerous!)
        """
    )

    parser.add_argument(
        'mode',
        nargs='?',
        default='monitor',
        choices=['check', 'monitor', 'full', 'trade'],
        help='Launch mode (default: monitor)'
    )

    args = parser.parse_args()

    launcher = ShadowSystemLauncher()
    launcher.run(args.mode)


if __name__ == "__main__":
    main()
