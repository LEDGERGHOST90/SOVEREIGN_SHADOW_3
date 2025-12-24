#!/usr/bin/env python3
"""
🎯 SHADOW SNIPER BRIDGE
Connects desktop Shadow Sniper system to SovereignShadow 2 profit tracking

Desktop Location: /Users/memphis/Desktop/Claude/shadow-sniper/
Bridge Purpose: Pull P&L data from Shadow Sniper and make it available to Unified Profit Tracker
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("shadow_sniper_bridge")

class ShadowSniperBridge:
    """
    Bridge between desktop Shadow Sniper and SovereignShadow 2

    Shadow Sniper Location: /Users/memphis/Desktop/Claude/shadow-sniper/
    Output Format: JSON file readable by unified_profit_tracker.py
    """

    def __init__(self):
        # Desktop Shadow Sniper paths
        self.shadow_sniper_root = Path("/Users/memphis/Desktop/Claude/shadow-sniper")
        self.shadow_sniper_trades = self.shadow_sniper_root / "trades.json"
        self.shadow_sniper_pnl = self.shadow_sniper_root / "pnl_summary.json"

        # SovereignShadow 2 paths
        self.sovereign_root = Path("/Volumes/LegacySafe/SovereignShadow 2")
        self.logs_path = self.sovereign_root / "logs"
        self.bridge_output = self.logs_path / "shadow_sniper_bridge.json"

        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)

        logger.info("🎯 Shadow Sniper Bridge initialized")

    def check_shadow_sniper_status(self) -> Dict[str, Any]:
        """Check if Shadow Sniper system is accessible"""
        status = {
            'accessible': False,
            'root_exists': self.shadow_sniper_root.exists(),
            'trades_file_exists': self.shadow_sniper_trades.exists(),
            'pnl_file_exists': self.shadow_sniper_pnl.exists()
        }

        if status['root_exists']:
            logger.info("✅ Shadow Sniper root directory found")
            status['accessible'] = True
        else:
            logger.warning("⚠️  Shadow Sniper root directory not found")
            logger.warning(f"   Expected: {self.shadow_sniper_root}")

        return status

    def read_shadow_sniper_trades(self) -> Dict[str, Any]:
        """Read trade history from Shadow Sniper"""
        try:
            if not self.shadow_sniper_trades.exists():
                logger.warning("⚠️  Shadow Sniper trades.json not found")
                return {
                    'total_pnl': 0.0,
                    'trade_count': 0,
                    'status': 'trades_file_not_found'
                }

            with open(self.shadow_sniper_trades, 'r') as f:
                trades_data = json.load(f)

            # Calculate total P&L from trades
            total_pnl = sum(trade.get('profit', 0.0) for trade in trades_data.get('trades', []))
            trade_count = len(trades_data.get('trades', []))

            logger.info(f"✅ Read {trade_count} trades from Shadow Sniper")
            logger.info(f"   Total P&L: ${total_pnl:.2f}")

            return {
                'total_pnl': total_pnl,
                'trade_count': trade_count,
                'trades': trades_data.get('trades', []),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'success'
            }

        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing Shadow Sniper trades.json: {e}")
            return {
                'total_pnl': 0.0,
                'trade_count': 0,
                'status': 'parse_error',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"❌ Error reading Shadow Sniper trades: {e}")
            return {
                'total_pnl': 0.0,
                'trade_count': 0,
                'status': 'error',
                'error': str(e)
            }

    def read_shadow_sniper_pnl(self) -> Dict[str, Any]:
        """Read P&L summary from Shadow Sniper"""
        try:
            if not self.shadow_sniper_pnl.exists():
                logger.warning("⚠️  Shadow Sniper pnl_summary.json not found")
                logger.info("   Falling back to trades.json")
                return self.read_shadow_sniper_trades()

            with open(self.shadow_sniper_pnl, 'r') as f:
                pnl_data = json.load(f)

            total_pnl = pnl_data.get('total_pnl', 0.0)
            win_rate = pnl_data.get('win_rate', 0.0)
            trade_count = pnl_data.get('total_trades', 0)

            logger.info(f"✅ Read Shadow Sniper P&L summary")
            logger.info(f"   Total P&L: ${total_pnl:.2f}")
            logger.info(f"   Win Rate: {win_rate:.1f}%")
            logger.info(f"   Total Trades: {trade_count}")

            return {
                'total_pnl': total_pnl,
                'trade_count': trade_count,
                'win_rate': win_rate,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'success',
                'source': 'pnl_summary'
            }

        except Exception as e:
            logger.error(f"❌ Error reading Shadow Sniper P&L: {e}")
            logger.info("   Falling back to trades.json")
            return self.read_shadow_sniper_trades()

    def sync_to_profit_tracker(self) -> bool:
        """
        Sync Shadow Sniper data to Unified Profit Tracker

        Creates shadow_sniper_bridge.json that unified_profit_tracker.py reads
        """
        try:
            logger.info("🔄 Syncing Shadow Sniper data to Unified Profit Tracker...")

            # Check Shadow Sniper status
            status = self.check_shadow_sniper_status()

            if not status['accessible']:
                logger.error("❌ Shadow Sniper system not accessible")
                # Write empty bridge file
                self._write_empty_bridge()
                return False

            # Read P&L data
            pnl_data = self.read_shadow_sniper_pnl()

            # Add bridge metadata
            bridge_data = {
                'bridge_version': '1.0.0',
                'source': 'shadow_sniper_desktop',
                'source_path': str(self.shadow_sniper_root),
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                **pnl_data
            }

            # Write to bridge file
            with open(self.bridge_output, 'w') as f:
                json.dump(bridge_data, f, indent=2)

            logger.info(f"✅ Bridge data written to: {self.bridge_output}")
            logger.info(f"   Total P&L: ${bridge_data.get('total_pnl', 0):.2f}")

            return True

        except Exception as e:
            logger.error(f"❌ Error syncing Shadow Sniper data: {e}")
            self._write_empty_bridge()
            return False

    def _write_empty_bridge(self):
        """Write empty bridge file when Shadow Sniper not accessible"""
        empty_data = {
            'bridge_version': '1.0.0',
            'source': 'shadow_sniper_desktop',
            'sync_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_pnl': 0.0,
            'trade_count': 0,
            'status': 'shadow_sniper_not_accessible'
        }

        with open(self.bridge_output, 'w') as f:
            json.dump(empty_data, f, indent=2)

        logger.info(f"📝 Empty bridge file written (Shadow Sniper not accessible)")

def main():
    """Main execution"""
    print("="*70)
    print("🎯 SHADOW SNIPER BRIDGE - Connecting Desktop System")
    print("="*70)
    print()

    bridge = ShadowSniperBridge()

    # Check status
    status = bridge.check_shadow_sniper_status()
    print(f"\n📊 SHADOW SNIPER STATUS:")
    print(f"   Root Directory: {'✅ Found' if status['root_exists'] else '❌ Not Found'}")
    print(f"   Trades File: {'✅ Found' if status['trades_file_exists'] else '⚠️  Not Found'}")
    print(f"   P&L File: {'✅ Found' if status['pnl_file_exists'] else '⚠️  Not Found'}")
    print()

    # Sync data
    success = bridge.sync_to_profit_tracker()

    if success:
        print("\n✅ Shadow Sniper data successfully synced!")
        print(f"📁 Bridge file: {bridge.bridge_output}")
    else:
        print("\n⚠️  Shadow Sniper sync completed with warnings")
        print("   Check logs above for details")

    print()
    print("="*70)

if __name__ == "__main__":
    main()
