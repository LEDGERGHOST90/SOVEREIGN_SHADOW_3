#!/usr/bin/env python3
"""
🚀 SWARM DEPLOYMENT - Deploy all AI trading swarms
Activates Agent Swarm, Shadow Army, and Hive Mind systems
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add modules to path
MODULES_PATH = Path(__file__).parent / "modules"
sys.path.insert(0, str(MODULES_PATH))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("swarm_deployment")


def create_mock_swarm_data():
    """Create mock P&L data files for swarms until they're fully deployed"""

    swarm_root = Path("/Volumes/LegacySafe/SovereignShadow 2")

    # Agent Swarm mock data
    agent_swarm_data = {
        'total_pnl': 0.0,
        'active_agents': 0,
        'consensus_rate': 0.0,
        'swarm_type': 'agent_swarm',
        'status': 'initialized',
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

    agent_swarm_path = swarm_root / "ClaudeSDK" / "agents" / "agent_swarm_pnl.json"
    agent_swarm_path.parent.mkdir(parents=True, exist_ok=True)
    with open(agent_swarm_path, 'w') as f:
        json.dump(agent_swarm_data, f, indent=2)
    logger.info(f"✅ Created Agent Swarm data: {agent_swarm_path}")

    # Shadow Army mock data
    shadow_army_data = {
        'total_pnl': 0.0,
        'active_agents': 0,
        'top_performer_pnl': 0.0,
        'swarm_type': 'shadow_army',
        'status': 'initialized',
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

    shadow_army_path = swarm_root / "ClaudeSDK" / "agents" / "shadow_army" / "shadow_army_pnl.json"
    shadow_army_path.parent.mkdir(parents=True, exist_ok=True)
    with open(shadow_army_path, 'w') as f:
        json.dump(shadow_army_data, f, indent=2)
    logger.info(f"✅ Created Shadow Army data: {shadow_army_path}")

    # Hive Mind mock data
    hive_mind_data = {
        'total_pnl': 0.0,
        'active_agents': 6,  # Always 6 agents
        'consensus_rate': 0.0,
        'swarm_type': 'hive_mind',
        'status': 'initialized',
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

    hive_mind_path = swarm_root / "SwarmAgents" / "hive_mind_pnl.json"
    hive_mind_path.parent.mkdir(parents=True, exist_ok=True)
    with open(hive_mind_path, 'w') as f:
        json.dump(hive_mind_data, f, indent=2)
    logger.info(f"✅ Created Hive Mind data: {hive_mind_path}")

    return {
        'agent_swarm': agent_swarm_path,
        'shadow_army': shadow_army_path,
        'hive_mind': hive_mind_path
    }


def deploy_swarms(total_capital: float = 1000.0):
    """
    Deploy all three swarm systems with capital allocation

    Capital Allocation:
    - Agent Swarm: 40% ($400) - Consensus-based coordination
    - Shadow Army: 40% ($400) - Competitive learning
    - Hive Mind: 20% ($200) - Specialized 6-agent voting
    """

    print("\n" + "="*70)
    print("🚀 SWARM DEPLOYMENT - Activating AI Trading Agents")
    print("="*70)
    print()

    # Capital allocation
    agent_swarm_capital = total_capital * 0.40
    shadow_army_capital = total_capital * 0.40
    hive_mind_capital = total_capital * 0.20

    print(f"💰 Total Capital: ${total_capital:.2f}")
    print(f"   Agent Swarm: ${agent_swarm_capital:.2f} (40%)")
    print(f"   Shadow Army: ${shadow_army_capital:.2f} (40%)")
    print(f"   Hive Mind: ${hive_mind_capital:.2f} (20%)")
    print()

    # Step 1: Create mock data files
    print("📊 Step 1: Initializing swarm data files...")
    data_files = create_mock_swarm_data()
    print("✅ All swarm data files created")
    print()

    # Step 2: Test bridge connectivity
    print("🔌 Step 2: Testing bridge connectivity...")
    from hybrid_system.swarm_intelligence_bridge import SwarmIntelligenceBridge
    bridge = SwarmIntelligenceBridge()

    status = bridge.check_swarm_systems_status()
    if all(status.values()):
        print("✅ Bridge connectivity verified")
    else:
        print("⚠️  Some swarm systems not accessible:")
        for system, accessible in status.items():
            symbol = "✅" if accessible else "❌"
            print(f"   {symbol} {system}")
    print()

    # Step 3: Sync bridge
    print("🔄 Step 3: Syncing swarm data to profit tracker...")
    bridge.sync_to_profit_tracker()
    print("✅ Bridge sync complete")
    print()

    # Step 4: Summary
    print("="*70)
    print("✅ SWARM DEPLOYMENT COMPLETE")
    print("="*70)
    print()
    print("Next Steps:")
    print("1. Connect swarms to signal generation (signal_aggregator.py)")
    print("2. Deploy test capital to each swarm")
    print("3. Monitor performance via Unified Profit Tracker")
    print("4. Activate autonomous trading loop")
    print()
    print("Swarm Status:")
    print("  🐝 Agent Swarm: Initialized (0 active agents)")
    print("  🏴‍☠️ Shadow Army: Initialized (0 active agents)")
    print("  🧠 Hive Mind: Initialized (6 specialized agents)")
    print()
    print("Data Files:")
    for swarm_name, data_path in data_files.items():
        print(f"  📁 {swarm_name}: {data_path}")
    print()
    print("="*70)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Deploy AI trading swarms')
    parser.add_argument(
        '--capital',
        type=float,
        default=1000.0,
        help='Total capital to allocate across swarms (default: $1000)'
    )

    args = parser.parse_args()

    deploy_swarms(total_capital=args.capital)


if __name__ == "__main__":
    main()
