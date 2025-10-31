#!/usr/bin/env python3
"""
🐝 SWARM INTELLIGENCE BRIDGE
Connects AI trading swarms to SovereignShadow 2 profit tracking

Swarm Systems:
- Agent Swarm: Consensus-based coordination (60% threshold)
- Shadow Army: Competitive learning (5 agent types)
- Hive Mind: 6 specialized agents with 67% voting

Bridge Purpose: Aggregate P&L from all swarm systems for Unified Profit Tracker
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("swarm_intelligence_bridge")

class SwarmIntelligenceBridge:
    """
    Bridge between AI Trading Swarms and SovereignShadow 2

    Swarm Locations:
    - Agent Swarm: ClaudeSDK/agents/agent_swarm.py
    - Shadow Army: ClaudeSDK/agents/shadow_army/shadow_swarm.py
    - Hive Mind: ClaudeSDK/launch_hive_swarm.py
    """

    def __init__(self):
        # SovereignShadow 2 paths
        self.sovereign_root = Path("/Volumes/LegacySafe/SovereignShadow 2")
        self.swarm_root = self.sovereign_root / "ClaudeSDK" / "agents"
        self.logs_path = self.sovereign_root / "logs"
        self.bridge_output = self.logs_path / "swarm_intelligence_bridge.json"

        # Swarm data paths
        self.agent_swarm_data = self.swarm_root / "agent_swarm_pnl.json"
        self.shadow_army_data = self.swarm_root / "shadow_army" / "shadow_army_pnl.json"
        self.hive_mind_data = self.sovereign_root / "SwarmAgents" / "hive_mind_pnl.json"

        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)

        logger.info("🐝 Swarm Intelligence Bridge initialized")

    def check_swarm_systems_status(self) -> Dict[str, bool]:
        """Check accessibility of all swarm systems"""
        status = {
            'swarm_root_exists': self.swarm_root.exists(),
            'agent_swarm_data_exists': self.agent_swarm_data.exists(),
            'shadow_army_data_exists': self.shadow_army_data.exists(),
            'hive_mind_data_exists': self.hive_mind_data.exists()
        }

        if status['swarm_root_exists']:
            logger.info("✅ Swarm systems root directory found")
        else:
            logger.warning("⚠️  Swarm systems root directory not found")

        return status

    def read_agent_swarm_pnl(self) -> Dict[str, Any]:
        """
        Read P&L from Agent Swarm (consensus-based coordination)

        Features:
        - 60% consensus threshold
        - Performance-based capital allocation
        - Max 50 agents
        """
        try:
            if not self.agent_swarm_data.exists():
                logger.warning("⚠️  Agent Swarm data file not found")
                return {
                    'total_pnl': 0.0,
                    'agent_count': 0,
                    'consensus_rate': 0.0,
                    'status': 'data_file_not_found',
                    'swarm_type': 'agent_swarm'
                }

            with open(self.agent_swarm_data, 'r') as f:
                swarm_data = json.load(f)

            total_pnl = swarm_data.get('total_pnl', 0.0)
            agent_count = swarm_data.get('active_agents', 0)
            consensus_rate = swarm_data.get('consensus_rate', 0.0)

            logger.info(f"✅ Agent Swarm: ${total_pnl:.2f} P&L ({agent_count} agents)")

            return {
                'total_pnl': total_pnl,
                'agent_count': agent_count,
                'consensus_rate': consensus_rate,
                'status': 'success',
                'swarm_type': 'agent_swarm',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error reading Agent Swarm data: {e}")
            return {
                'total_pnl': 0.0,
                'agent_count': 0,
                'status': 'error',
                'error': str(e),
                'swarm_type': 'agent_swarm'
            }

    def read_shadow_army_pnl(self) -> Dict[str, Any]:
        """
        Read P&L from Shadow Army (competitive learning)

        Features:
        - 5 agent types (Hunter, Sniper, Whale Tracker, Ghost, Sentinel)
        - Capital reallocation based on performance
        - Top 30% get +50%, bottom 30% get -20%
        """
        try:
            if not self.shadow_army_data.exists():
                logger.warning("⚠️  Shadow Army data file not found")
                return {
                    'total_pnl': 0.0,
                    'agent_count': 0,
                    'top_performer_pnl': 0.0,
                    'status': 'data_file_not_found',
                    'swarm_type': 'shadow_army'
                }

            with open(self.shadow_army_data, 'r') as f:
                army_data = json.load(f)

            total_pnl = army_data.get('total_pnl', 0.0)
            agent_count = army_data.get('active_agents', 0)
            top_performer_pnl = army_data.get('top_performer_pnl', 0.0)

            logger.info(f"✅ Shadow Army: ${total_pnl:.2f} P&L ({agent_count} agents)")

            return {
                'total_pnl': total_pnl,
                'agent_count': agent_count,
                'top_performer_pnl': top_performer_pnl,
                'status': 'success',
                'swarm_type': 'shadow_army',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error reading Shadow Army data: {e}")
            return {
                'total_pnl': 0.0,
                'agent_count': 0,
                'status': 'error',
                'error': str(e),
                'swarm_type': 'shadow_army'
            }

    def read_hive_mind_pnl(self) -> Dict[str, Any]:
        """
        Read P&L from Hive Mind (6 specialized agents)

        Agents:
        - Volatility Hunter
        - RSI Reader
        - Technical Master
        - Pattern Master
        - Whale Watcher
        - Sentiment Scanner

        Features:
        - 67% consensus voting (4/6 agents must agree)
        - $10K starting capital
        - Specialized roles
        """
        try:
            if not self.hive_mind_data.exists():
                logger.warning("⚠️  Hive Mind data file not found")
                return {
                    'total_pnl': 0.0,
                    'agent_count': 0,
                    'consensus_rate': 0.0,
                    'status': 'data_file_not_found',
                    'swarm_type': 'hive_mind'
                }

            with open(self.hive_mind_data, 'r') as f:
                hive_data = json.load(f)

            total_pnl = hive_data.get('total_pnl', 0.0)
            agent_count = hive_data.get('active_agents', 6)  # Always 6 agents
            consensus_rate = hive_data.get('consensus_rate', 0.0)

            logger.info(f"✅ Hive Mind: ${total_pnl:.2f} P&L ({agent_count} agents)")

            return {
                'total_pnl': total_pnl,
                'agent_count': agent_count,
                'consensus_rate': consensus_rate,
                'status': 'success',
                'swarm_type': 'hive_mind',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error reading Hive Mind data: {e}")
            return {
                'total_pnl': 0.0,
                'agent_count': 0,
                'status': 'error',
                'error': str(e),
                'swarm_type': 'hive_mind'
            }

    def aggregate_swarm_pnl(self) -> Dict[str, Any]:
        """Aggregate P&L from all swarm systems"""
        logger.info("🔄 Aggregating P&L from all swarm systems...")

        # Read data from all swarms
        agent_swarm = self.read_agent_swarm_pnl()
        shadow_army = self.read_shadow_army_pnl()
        hive_mind = self.read_hive_mind_pnl()

        # Calculate totals
        total_pnl = (
            agent_swarm.get('total_pnl', 0.0) +
            shadow_army.get('total_pnl', 0.0) +
            hive_mind.get('total_pnl', 0.0)
        )

        total_agents = (
            agent_swarm.get('agent_count', 0) +
            shadow_army.get('agent_count', 0) +
            hive_mind.get('agent_count', 0)
        )

        logger.info(f"✅ Total Swarm P&L: ${total_pnl:.2f} ({total_agents} total agents)")

        return {
            'total_pnl': total_pnl,
            'agent_count': total_agents,
            'swarms': {
                'agent_swarm': agent_swarm,
                'shadow_army': shadow_army,
                'hive_mind': hive_mind
            },
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'status': 'success'
        }

    def sync_to_profit_tracker(self) -> bool:
        """
        Sync Swarm Intelligence data to Unified Profit Tracker

        Creates swarm_intelligence_bridge.json that unified_profit_tracker.py reads
        """
        try:
            logger.info("🔄 Syncing Swarm Intelligence data to Unified Profit Tracker...")

            # Check swarm systems status
            status = self.check_swarm_systems_status()

            if not status['swarm_root_exists']:
                logger.error("❌ Swarm systems not accessible")
                self._write_empty_bridge()
                return False

            # Aggregate P&L from all swarms
            aggregated_data = self.aggregate_swarm_pnl()

            # Add bridge metadata
            bridge_data = {
                'bridge_version': '1.0.0',
                'source': 'swarm_intelligence_systems',
                'source_path': str(self.swarm_root),
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                **aggregated_data
            }

            # Write to bridge file
            with open(self.bridge_output, 'w') as f:
                json.dump(bridge_data, f, indent=2)

            logger.info(f"✅ Bridge data written to: {self.bridge_output}")
            logger.info(f"   Total P&L: ${bridge_data.get('total_pnl', 0):.2f}")
            logger.info(f"   Total Agents: {bridge_data.get('agent_count', 0)}")

            return True

        except Exception as e:
            logger.error(f"❌ Error syncing Swarm Intelligence data: {e}")
            self._write_empty_bridge()
            return False

    def _write_empty_bridge(self):
        """Write empty bridge file when swarms not accessible"""
        empty_data = {
            'bridge_version': '1.0.0',
            'source': 'swarm_intelligence_systems',
            'sync_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_pnl': 0.0,
            'agent_count': 0,
            'status': 'swarms_not_accessible'
        }

        with open(self.bridge_output, 'w') as f:
            json.dump(empty_data, f, indent=2)

        logger.info(f"📝 Empty bridge file written (Swarms not accessible)")

def main():
    """Main execution"""
    print("="*70)
    print("🐝 SWARM INTELLIGENCE BRIDGE - Connecting AI Trading Swarms")
    print("="*70)
    print()

    bridge = SwarmIntelligenceBridge()

    # Check status
    status = bridge.check_swarm_systems_status()
    print(f"\n📊 SWARM SYSTEMS STATUS:")
    print(f"   Swarm Root: {'✅ Found' if status['swarm_root_exists'] else '❌ Not Found'}")
    print(f"   Agent Swarm Data: {'✅ Found' if status['agent_swarm_data_exists'] else '⚠️  Not Found'}")
    print(f"   Shadow Army Data: {'✅ Found' if status['shadow_army_data_exists'] else '⚠️  Not Found'}")
    print(f"   Hive Mind Data: {'✅ Found' if status['hive_mind_data_exists'] else '⚠️  Not Found'}")
    print()

    # Sync data
    success = bridge.sync_to_profit_tracker()

    if success:
        print("\n✅ Swarm Intelligence data successfully synced!")
        print(f"📁 Bridge file: {bridge.bridge_output}")
    else:
        print("\n⚠️  Swarm Intelligence sync completed with warnings")
        print("   Check logs above for details")

    print()
    print("="*70)

if __name__ == "__main__":
    main()
