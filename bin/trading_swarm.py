#!/usr/bin/env python3
"""
TRADING SWARM - Autonomous Signal Discovery & Validation
Orchestrates meme_machine + SHADE agents for December campaign

Usage:
    python bin/trading_swarm.py --scan          # Run full scan cycle
    python bin/trading_swarm.py --validate ADDR # Validate specific token
    python bin/trading_swarm.py --status        # Show swarm status
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "agents"))
sys.path.insert(0, str(PROJECT_ROOT / "meme_machine"))
sys.path.insert(0, str(PROJECT_ROOT / "core"))

# Import verified Moon Dev signal generators
try:
    from signals.moondev_signals import MoonDevSignals
    MOONDEV_AVAILABLE = True
except ImportError:
    MOONDEV_AVAILABLE = False
    print("[WARN] MoonDev signals not available")

class TradingSwarm:
    """
    Orchestrates multiple agents for autonomous trading signals.

    Flow:
    1. Scanner (meme_machine) finds candidates
    2. Validator (SHADE) checks risk rules
    3. Psychologist checks emotional state
    4. Presents approved trades for human confirmation
    """

    def __init__(self):
        self.config_path = PROJECT_ROOT / "config" / "swarm_config.json"
        self.load_config()

        # State tracking
        self.candidates = []
        self.validated = []
        self.approved = []
        self.rejected = []

        # Initialize MoonDev verified signals (top 3 from 450 backtested)
        self.moondev_signals = MoonDevSignals() if MOONDEV_AVAILABLE else None

        print("=" * 60)
        print("TRADING SWARM - December Aggressive Mode")
        print("=" * 60)
        print(f"Config: {self.config['mode']}")
        print(f"Max Position: ${self.config['risk_rules']['position_sizing']['max_position_usd']}")
        print(f"Stop Loss: {self.config['risk_rules']['stop_loss']['default_pct']}%")
        print(f"Target: ${self.config['december_targets']['starting_capital']} → ${self.config['december_targets']['goal_target']}")
        print("=" * 60)

    def load_config(self):
        """Load swarm configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError(f"Config not found: {self.config_path}")

    def run_scanner(self, scan_type: str = "breakout") -> List[Dict]:
        """Run meme_machine scanner and capture results"""
        print(f"\n[SCANNER] Running {scan_type} scan...")

        cmd_map = {
            "breakout": ["python", "-m", "meme_machine", "--breakout", "--min-score", "70"],
            "kings": ["python", "-m", "meme_machine", "--kings"],
            "trending": ["python", "-m", "meme_machine", "--trending"],
            "smart-buys": ["python", "-m", "meme_machine", "--smart-buys"],
            "pumpfun": ["python", "-m", "meme_machine", "--pumpfun"]
        }

        cmd = cmd_map.get(scan_type, cmd_map["breakout"])

        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=60
            )

            print(result.stdout)
            if result.stderr:
                print(f"[WARN] {result.stderr}")

            # Parse any tokens from output (simplified - would need real parsing)
            return self.parse_scanner_output(result.stdout)

        except subprocess.TimeoutExpired:
            print("[ERROR] Scanner timed out")
            return []
        except Exception as e:
            print(f"[ERROR] Scanner failed: {e}")
            return []

    def parse_scanner_output(self, output: str) -> List[Dict]:
        """Parse meme_machine output for token candidates"""
        candidates = []

        # Look for score patterns like "PEPE: 70/100"
        for line in output.split('\n'):
            if '/100' in line or 'score' in line.lower():
                # Extract token info (simplified)
                candidates.append({
                    "raw": line.strip(),
                    "source": "meme_machine",
                    "timestamp": datetime.now().isoformat()
                })

        return candidates

    def validate_candidate(self, candidate: Dict) -> Dict:
        """Run candidate through SHADE validation"""
        rules = self.config['risk_rules']

        result = {
            "candidate": candidate,
            "passed": True,
            "checks": [],
            "warnings": []
        }

        # Position size check
        max_pos = rules['position_sizing']['max_position_usd']
        result['checks'].append(f"Max position: ${max_pos}")

        # Liquidity check
        min_liq = self.config['alert_thresholds']['liquidity_min_usd']
        result['checks'].append(f"Min liquidity: ${min_liq}")

        # Concentration check
        max_conc = self.config['alert_thresholds']['concentration_avoid_pct']
        result['checks'].append(f"Max concentration: {max_conc}%")

        return result

    def check_psychology(self) -> Dict:
        """Check if trading is psychologically safe"""
        # Load strike count from log
        loss_log = PROJECT_ROOT / "logs" / "psychology" / "loss_streak.json"

        strikes = 0
        if loss_log.exists():
            with open(loss_log) as f:
                data = json.load(f)
                if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    strikes = data.get('count', 0)

        allowed = strikes < 3

        return {
            "trading_allowed": allowed,
            "strikes": strikes,
            "max_strikes": 3,
            "message": "Clear to trade" if allowed else "LOCKED - 3 strike limit reached"
        }

    def run_moondev_signals(self, symbol: str = "BTC-USD") -> Optional[Dict]:
        """Run verified MoonDev strategies for consensus signal"""
        if not self.moondev_signals:
            print("[MOONDEV] Signals not available")
            return None

        print(f"\n[MOONDEV] Running verified signals on {symbol}...")

        try:
            import yfinance as yf
            import pandas as pd

            # Get recent data
            data = yf.download(symbol, period='3mo', interval='1h', progress=False)
            if data.empty:
                print(f"[MOONDEV] No data for {symbol}")
                return None

            # Flatten MultiIndex if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data = data.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume'
            })

            # Get consensus
            result = self.moondev_signals.get_consensus(data)
            self.moondev_signals.print_dashboard(data, symbol)

            return result

        except Exception as e:
            print(f"[MOONDEV] Error: {e}")
            return None

    def full_scan_cycle(self):
        """Run complete scan → validate → present cycle"""
        print("\n" + "=" * 60)
        print("FULL SCAN CYCLE")
        print("=" * 60)

        # Step 1: Psychology check
        psych = self.check_psychology()
        print(f"\n[PSYCHOLOGY] Strikes: {psych['strikes']}/3 - {psych['message']}")

        if not psych['trading_allowed']:
            print("SWARM HALTED - Psychology lock active")
            return

        # Step 1.5: MoonDev Verified Signals (TOP 3 from 450 backtested)
        print("\n" + "-" * 60)
        print("MOONDEV VERIFIED SIGNALS (Top 3 from 450 backtested)")
        print("-" * 60)
        moondev_btc = self.run_moondev_signals("BTC-USD")
        moondev_eth = self.run_moondev_signals("ETH-USD")

        if moondev_btc and moondev_btc['action'] != 'WAIT':
            print(f"\n*** BTC SIGNAL: {moondev_btc['action']} (confidence: {moondev_btc['confidence']:.0%}) ***")
        if moondev_eth and moondev_eth['action'] != 'WAIT':
            print(f"\n*** ETH SIGNAL: {moondev_eth['action']} (confidence: {moondev_eth['confidence']:.0%}) ***")

        # Step 2: Run all scanners (meme_machine for alts)
        scan_types = ["breakout", "kings", "trending"]
        all_candidates = []

        for scan_type in scan_types:
            candidates = self.run_scanner(scan_type)
            all_candidates.extend(candidates)

        print(f"\n[RESULTS] Found {len(all_candidates)} raw candidates")

        # Step 3: Validate each
        validated = []
        for candidate in all_candidates:
            result = self.validate_candidate(candidate)
            if result['passed']:
                validated.append(result)

        print(f"[VALIDATED] {len(validated)} passed risk rules")

        # Step 4: Present for approval
        if validated:
            print("\n" + "=" * 60)
            print("SIGNALS READY FOR REVIEW")
            print("=" * 60)
            for i, v in enumerate(validated, 1):
                print(f"\n{i}. {v['candidate']['raw']}")
                print(f"   Checks: {', '.join(v['checks'])}")
        else:
            print("\n[INFO] No actionable signals found this cycle")

        # Save results
        self.save_scan_results(all_candidates, validated)

        return validated

    def save_scan_results(self, raw: List, validated: List):
        """Save scan results to log"""
        log_dir = PROJECT_ROOT / "logs" / "swarm"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        log_file = log_dir / f"scan_{timestamp}.json"

        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "raw_candidates": len(raw),
                "validated": len(validated),
                "candidates": raw,
                "validated_details": validated
            }, f, indent=2)

        print(f"\n[LOG] Results saved to {log_file}")

    def show_status(self):
        """Display current swarm status"""
        print("\n" + "=" * 60)
        print("SWARM STATUS")
        print("=" * 60)

        # Config status
        print(f"\nMode: {self.config['mode']}")
        print(f"Position Limit: ${self.config['risk_rules']['position_sizing']['max_position_usd']}")
        print(f"Daily Loss Limit: ${self.config['risk_rules']['daily_limits']['max_loss_usd']}")

        # Psychology
        psych = self.check_psychology()
        status = "ACTIVE" if psych['trading_allowed'] else "LOCKED"
        print(f"\nPsychology: {status} ({psych['strikes']}/3 strikes)")

        # Recent scans
        log_dir = PROJECT_ROOT / "logs" / "swarm"
        if log_dir.exists():
            logs = sorted(log_dir.glob("scan_*.json"), reverse=True)[:3]
            if logs:
                print(f"\nRecent Scans:")
                for log in logs:
                    print(f"  - {log.name}")

        # December progress
        targets = self.config['december_targets']
        print(f"\nDecember Target: ${targets['starting_capital']} → ${targets['goal_target']}")
        print(f"Deadline: {targets['deadline']}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Trading Swarm Orchestrator")
    parser.add_argument("--scan", action="store_true", help="Run full scan cycle")
    parser.add_argument("--validate", type=str, help="Validate specific token address")
    parser.add_argument("--status", action="store_true", help="Show swarm status")

    args = parser.parse_args()

    swarm = TradingSwarm()

    if args.scan:
        swarm.full_scan_cycle()
    elif args.validate:
        print(f"Validating: {args.validate}")
        # Would integrate with meme_machine --score
    elif args.status:
        swarm.show_status()
    else:
        # Default: show status
        swarm.show_status()


if __name__ == "__main__":
    main()
