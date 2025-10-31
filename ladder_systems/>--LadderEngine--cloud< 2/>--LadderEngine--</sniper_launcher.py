#!/usr/bin/env python3
"""
ΣIGMA-ΩSNIPER Ladder Execution System - Main Launcher
==================================================

Author: Manus AI
Version: 1.0.0
Date: 2025-01-07
Classification: Production Trading System

Description:
Main entry point for the ΣIGMA-ΩSNIPER ladder execution system.
Provides unified interface for paper trading, live execution, and system monitoring.

Security Level: MAXIMUM
Structure Lock: STRUCTURE_LOCK_0712_SIGMAΩ_FINALIZED
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.execution.sniper_engine_core import SniperEngineCore
from src.utils.secure_config_loader import SecureConfigLoader
from src.utils.cognitive_filter_ray import CognitiveFilterRay
from src.utils.vault_siphon_router import VaultSiphonRouter
from src.execution.simulated_ladder_engine import SimulatedLadderEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sniper_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SniperLauncher:
    """
    Main launcher for ΣIGMA-ΩSNIPER system
    Coordinates all subsystems and provides unified interface
    """
    
    def __init__(self):
        self.config_loader = SecureConfigLoader()
        self.cognitive_filter = CognitiveFilterRay()
        self.vault_router = VaultSiphonRouter()
        self.sniper_engine = None
        self.simulator = None
        
    async def initialize_system(self, config_path: str = None) -> bool:
        """Initialize all system components"""
        try:
            logger.info("🎯 ΣIGMA-ΩSNIPER System Initialization")
            
            # Load configuration
            if not await self.config_loader.load_config(config_path):
                logger.error("❌ Failed to load system configuration")
                return False
            
            # Initialize core engine
            self.sniper_engine = SniperEngineCore(self.config_loader)
            
            # Initialize simulator
            self.simulator = SimulatedLadderEngine(self.config_loader)
            
            # Validate system integrity
            if not await self._validate_system():
                logger.error("❌ System validation failed")
                return False
            
            logger.info("✅ ΣIGMA-ΩSNIPER System Ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def _validate_system(self) -> bool:
        """Validate system components and configuration"""
        try:
            # Check cognitive filter
            test_signal = {
                'symbol': 'BTCUSDT',
                'action': 'buy',
                'entry_price': 45000.0,
                'tp1_price': 50000.0,
                'sl_price': 42000.0
            }
            
            ray_score = await self.cognitive_filter.calculate_ray_score(test_signal)
            if ray_score < 0 or ray_score > 100:
                logger.error("❌ Cognitive filter validation failed")
                return False
            
            # Check vault router
            if not await self.vault_router.validate_sleep_assets():
                logger.error("❌ Vault router validation failed")
                return False
            
            logger.info("✅ System validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ System validation error: {e}")
            return False
    
    async def execute_ladder_deployment(self, signal: Dict[str, Any], mode: str = 'paper') -> Dict[str, Any]:
        """
        Execute ladder deployment with full ΣIGMA-ΩSNIPER protocol
        
        Args:
            signal: Trading signal with entry, TP, SL parameters
            mode: 'paper' or 'live' execution mode
            
        Returns:
            Execution result with status and metrics
        """
        try:
            logger.info(f"🚀 Executing ladder deployment: {signal.get('symbol', 'UNKNOWN')}")
            
            # Phase 1: Cognitive Filtering
            ray_analysis = await self.cognitive_filter.analyze_signal(signal)
            
            if ray_analysis['ray_score'] < 60:
                return {
                    'success': False,
                    'rejection_reason': f"Ray Score {ray_analysis['ray_score']:.1f} below threshold 60",
                    'ray_analysis': ray_analysis
                }
            
            # Phase 2: ROI Validation
            roi_validation = await self._validate_roi(signal)
            if not roi_validation['valid']:
                return {
                    'success': False,
                    'rejection_reason': "ROI requirements not met",
                    'roi_validation': roi_validation
                }
            
            # Phase 3: Execute Ladder
            if mode == 'paper':
                result = await self.simulator.execute_ladder(signal, ray_analysis['ray_score'])
            else:
                result = await self.sniper_engine.execute_ladder(signal, ray_analysis['ray_score'])
            
            # Phase 4: Vault Siphon (if profitable)
            if result.get('success') and result.get('profit_projection', 0) > 0:
                vault_result = await self.vault_router.process_profit_siphon(
                    result['profit_projection'],
                    signal.get('symbol', 'UNKNOWN')
                )
                result['vault_siphon'] = vault_result
            
            logger.info(f"✅ Ladder deployment complete: {result.get('execution_status', 'UNKNOWN')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ladder deployment failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _validate_roi(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ROI requirements for signal"""
        try:
            entry = signal.get('entry_price', 0)
            tp1 = signal.get('tp1_price', 0)
            tp2 = signal.get('tp2_price', 0)
            sl = signal.get('sl_price', 0)
            
            if not all([entry, tp1, sl]):
                return {'valid': False, 'reason': 'Missing price parameters'}
            
            # Calculate ROI percentages
            tp1_roi = ((tp1 - entry) / entry) * 100
            tp2_roi = ((tp2 - entry) / entry) * 100 if tp2 else tp1_roi
            drawdown = ((entry - sl) / entry) * 100
            
            # Apply requirements: TP1 ≥ 20%, TP2 ≥ 30%, drawdown ≤ 7%
            valid = (tp1_roi >= 20.0 and 
                    tp2_roi >= 30.0 and 
                    drawdown <= 7.0)
            
            return {
                'valid': valid,
                'tp1_roi': round(tp1_roi, 2),
                'tp2_roi': round(tp2_roi, 2),
                'drawdown': round(drawdown, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ ROI validation error: {e}")
            return {'valid': False, 'error': str(e)}
    
    async def monitor_system(self, duration_minutes: int = 60) -> None:
        """Monitor system performance and cognitive state"""
        try:
            logger.info(f"👁️  Starting system monitoring for {duration_minutes} minutes")
            
            start_time = datetime.utcnow()
            
            while True:
                # Check system health
                health_status = await self._check_system_health()
                
                if not health_status['healthy']:
                    logger.warning(f"⚠️  System health issue: {health_status['issues']}")
                
                # Check for cognitive degradation
                cognitive_status = await self.cognitive_filter.get_system_status()
                
                if cognitive_status.get('ray_score_avg', 100) < 40:
                    logger.warning("🧠 Cognitive degradation detected - consider system pause")
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # 30 second intervals
                
                # Check if monitoring duration exceeded
                elapsed = (datetime.utcnow() - start_time).total_seconds() / 60
                if elapsed >= duration_minutes:
                    break
            
            logger.info("✅ System monitoring complete")
            
        except Exception as e:
            logger.error(f"❌ System monitoring error: {e}")
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            issues = []
            
            # Check configuration
            if not self.config_loader.is_valid():
                issues.append("Invalid configuration")
            
            # Check cognitive filter
            if not await self.cognitive_filter.is_operational():
                issues.append("Cognitive filter offline")
            
            # Check vault router
            if not await self.vault_router.is_operational():
                issues.append("Vault router offline")
            
            return {
                'healthy': len(issues) == 0,
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f"Health check error: {e}"],
                'timestamp': datetime.utcnow().isoformat()
            }

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ΣIGMA-ΩSNIPER Ladder Execution System')
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper',
                       help='Execution mode (default: paper)')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--monitor', type=int, help='Monitor system for N minutes')
    parser.add_argument('--signal', type=str, help='JSON signal file to execute')
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = SniperLauncher()
    
    if not await launcher.initialize_system(args.config):
        logger.error("❌ Failed to initialize ΣIGMA-ΩSNIPER system")
        sys.exit(1)
    
    # Execute based on arguments
    if args.monitor:
        await launcher.monitor_system(args.monitor)
    elif args.signal:
        # Load and execute signal
        try:
            import json
            with open(args.signal, 'r') as f:
                signal_data = json.load(f)
            
            result = await launcher.execute_ladder_deployment(signal_data, args.mode)
            print(json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            logger.error(f"❌ Signal execution failed: {e}")
            sys.exit(1)
    else:
        logger.info("🎯 ΣIGMA-ΩSNIPER System Ready - Use --help for options")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 System shutdown requested")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        sys.exit(1)

