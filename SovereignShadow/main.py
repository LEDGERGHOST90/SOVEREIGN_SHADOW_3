#!/usr/bin/env python3
"""
SovereignShadow VES System - Main Orchestrator
Coordinates Vault, Engine, and Siphon components
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from decimal import Decimal

# Add modules to path
sys.path.append(str(Path(__file__).parent))

# Import system modules
from modules.vault_manager import VaultManager
from modules.engine_manager import EngineManager
from modules.siphon_distributor import SiphonDistributor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VESOrchestrator:
    """
    Main orchestrator for the Vault-Engine-Siphon system
    Coordinates all components and manages system lifecycle
    """
    
    def __init__(self, config_path: str = "config/ves_architecture.yaml"):
        """Initialize the VES orchestrator"""
        logger.info("Initializing SovereignShadow VES System...")
        
        # Create necessary directories
        self._setup_directories()
        
        # Initialize components
        try:
            self.vault = VaultManager(config_path)
            self.engine = EngineManager(config_path)
            self.siphon = SiphonDistributor(
                config_path=config_path,
                vault_manager=self.vault,
                engine_manager=self.engine
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
            
        # System state
        self.running = False
        self.cycle_count = 0
        self.start_time = datetime.now()
        
    def _setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'data', 'data/vault', 'data/engine', 'data/siphon',
            'logs', 'backups', 'tmp'
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
    def run_cycle(self) -> Dict[str, Any]:
        """
        Run a complete VES cycle
        
        Returns:
            Dictionary with cycle results
        """
        self.cycle_count += 1
        logger.info(f"Starting VES cycle #{self.cycle_count}")
        
        cycle_results = {
            'cycle_number': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'vault_status': None,
            'engine_status': None,
            'siphon_status': None,
            'errors': []
        }
        
        # Step 1: Update Vault status
        try:
            logger.info("Checking vault health...")
            vault_health = self.vault.check_health()
            cycle_results['vault_status'] = {
                'health_score': vault_health.health_score,
                'total_value': float(vault_health.total_value_usd),
                'warnings': len(vault_health.warnings),
                'critical_alerts': len(vault_health.critical_alerts)
            }
            
            if vault_health.critical_alerts:
                logger.warning(f"Vault critical alerts: {vault_health.critical_alerts}")
                
        except Exception as e:
            logger.error(f"Vault check failed: {e}")
            cycle_results['errors'].append(f"Vault: {str(e)}")
            
        # Step 2: Execute Engine trading
        try:
            logger.info("Executing engine trading cycle...")
            engine_results = self.engine.execute_trading_cycle()
            cycle_results['engine_status'] = engine_results
            
            # Get performance metrics
            metrics = self.engine.get_performance_metrics()
            logger.info(
                f"Engine metrics - Open positions: {metrics['open_positions']}, "
                f"Daily P&L: ${metrics['daily_pnl']:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Engine cycle failed: {e}")
            cycle_results['errors'].append(f"Engine: {str(e)}")
            
        # Step 3: Process Siphon distributions
        try:
            logger.info("Processing siphon distributions...")
            siphon_results = self.siphon.run_siphon_cycle()
            cycle_results['siphon_status'] = siphon_results
            
            if siphon_results['total_distributed'] > 0:
                logger.info(
                    f"Siphon distributed ${siphon_results['total_distributed']:.2f}"
                )
                
        except Exception as e:
            logger.error(f"Siphon cycle failed: {e}")
            cycle_results['errors'].append(f"Siphon: {str(e)}")
            
        # Save cycle results
        self._save_cycle_results(cycle_results)
        
        # Log summary
        if cycle_results['errors']:
            logger.warning(f"Cycle #{self.cycle_count} completed with {len(cycle_results['errors'])} errors")
        else:
            logger.info(f"Cycle #{self.cycle_count} completed successfully")
            
        return cycle_results
        
    def run_continuous(self, interval_minutes: int = 15):
        """
        Run the system continuously with specified interval
        
        Args:
            interval_minutes: Minutes between cycles
        """
        logger.info(f"Starting continuous operation (interval: {interval_minutes} minutes)")
        self.running = True
        
        try:
            while self.running:
                # Run cycle
                cycle_results = self.run_cycle()
                
                # Check for critical issues
                if self._has_critical_issues(cycle_results):
                    logger.critical("Critical issues detected, stopping system")
                    self.shutdown()
                    break
                    
                # Wait for next cycle
                logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.shutdown()
            
        except Exception as e:
            logger.error(f"Unexpected error in continuous operation: {e}")
            self.shutdown()
            
    def _has_critical_issues(self, cycle_results: Dict) -> bool:
        """Check if there are critical issues requiring shutdown"""
        # Check for multiple errors
        if len(cycle_results.get('errors', [])) >= 3:
            return True
            
        # Check vault health
        vault_status = cycle_results.get('vault_status', {})
        if vault_status and vault_status.get('health_score', 100) < 50:
            return True
            
        # Check for critical alerts
        if vault_status and vault_status.get('critical_alerts', 0) > 0:
            return True
            
        return False
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        uptime = datetime.now() - self.start_time
        
        status = {
            'running': self.running,
            'uptime_hours': uptime.total_seconds() / 3600,
            'cycles_completed': self.cycle_count,
            'start_time': self.start_time.isoformat(),
            'components': {
                'vault': 'OK',
                'engine': 'OK', 
                'siphon': 'OK'
            }
        }
        
        # Get component summaries
        try:
            status['vault_summary'] = self.vault.get_summary()
        except:
            status['components']['vault'] = 'ERROR'
            
        try:
            status['engine_metrics'] = self.engine.get_performance_metrics()
        except:
            status['components']['engine'] = 'ERROR'
            
        try:
            status['siphon_stats'] = self.siphon.get_statistics()
        except:
            status['components']['siphon'] = 'ERROR'
            
        return status
        
    def manual_rebalance(self, force: bool = False) -> Dict[str, Any]:
        """
        Manually trigger system rebalancing
        
        Args:
            force: Force rebalancing even if within tolerance
            
        Returns:
            Rebalancing results
        """
        logger.info("Manual rebalancing triggered")
        
        # Get rebalancing needs
        actions = self.siphon.check_rebalancing_needs()
        
        if not actions and not force:
            logger.info("No rebalancing needed")
            return {'status': 'no_action_needed', 'actions': []}
            
        if force:
            logger.warning("Force rebalancing activated")
            # Would implement force logic here
            
        # Execute rebalancing
        results = self.siphon.execute_rebalancing(actions)
        
        logger.info(f"Rebalancing completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
        
    def emergency_stop(self):
        """Emergency stop - close all positions and halt trading"""
        logger.critical("EMERGENCY STOP ACTIVATED")
        
        try:
            # Close all engine positions
            positions = self.engine.positions.copy()
            for symbol in positions:
                logger.info(f"Closing position: {symbol}")
                self.engine.close_position(symbol, reason="EMERGENCY_STOP")
                
            # Save emergency state
            emergency_file = Path('data/emergency_stop.json')
            with open(emergency_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'Manual emergency stop',
                    'positions_closed': list(positions.keys()),
                    'system_state': self.get_system_status()
                }, f, indent=2)
                
            logger.info("Emergency stop completed - all positions closed")
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Graceful system shutdown"""
        logger.info("Initiating system shutdown...")
        
        self.running = False
        
        # Save final state
        try:
            final_status = self.get_system_status()
            shutdown_file = Path('data/shutdown_state.json')
            
            with open(shutdown_file, 'w') as f:
                json.dump(final_status, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save shutdown state: {e}")
            
        logger.info("SovereignShadow VES System shutdown complete")
        
    def _save_cycle_results(self, results: Dict):
        """Save cycle results to file"""
        cycle_file = Path(f"data/cycles_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(cycle_file, 'a') as f:
            f.write(json.dumps(results, default=str) + '\n')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SovereignShadow VES System Orchestrator'
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'continuous', 'status', 'rebalance', 'emergency'],
        default='single',
        help='Operation mode'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Interval in minutes for continuous mode (default: 15)'
    )
    
    parser.add_argument(
        '--config',
        default='config/ves_architecture.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ['COINBASE_API_KEY', 'COINBASE_API_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please copy .env.template to .env and fill in your credentials")
        sys.exit(1)
        
    # Initialize orchestrator
    orchestrator = VESOrchestrator(args.config)
    
    # Execute based on mode
    if args.mode == 'single':
        logger.info("Running single cycle...")
        results = orchestrator.run_cycle()
        print(json.dumps(results, indent=2, default=str))
        
    elif args.mode == 'continuous':
        logger.info(f"Starting continuous mode (interval: {args.interval} minutes)")
        orchestrator.run_continuous(args.interval)
        
    elif args.mode == 'status':
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2, default=str))
        
    elif args.mode == 'rebalance':
        results = orchestrator.manual_rebalance()
        print(json.dumps(results, indent=2, default=str))
        
    elif args.mode == 'emergency':
        confirm = input("⚠️  EMERGENCY STOP - This will close all positions. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            orchestrator.emergency_stop()
        else:
            logger.info("Emergency stop cancelled")


if __name__ == "__main__":
    main()