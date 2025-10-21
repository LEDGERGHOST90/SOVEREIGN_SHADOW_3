"""
Siphon Distributor Module
Intelligent profit routing system between Vault and Engine layers
"""

import logging
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfitCategory(Enum):
    """Categorization of profit amounts"""
    SMALL = "SMALL"      # < $100
    MEDIUM = "MEDIUM"    # $100 - $500
    LARGE = "LARGE"      # > $500


class TransferStatus(Enum):
    """Status of fund transfers"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class ProfitDistribution:
    """Represents a profit distribution event"""
    timestamp: datetime
    total_amount: Decimal
    category: ProfitCategory
    vault_amount: Decimal
    engine_amount: Decimal
    buffer_amount: Decimal
    source: str  # "ENGINE" or "VAULT"
    status: TransferStatus


@dataclass
class RebalanceAction:
    """Represents a rebalancing action needed"""
    asset: str
    from_layer: str  # "VAULT" or "ENGINE"
    to_layer: str
    amount: Decimal
    reason: str
    priority: int  # 1-5, 1 being highest


class SiphonDistributor:
    """
    Manages intelligent profit routing between Vault and Engine
    Implements distribution rules and triggers rebalancing
    """
    
    def __init__(
        self, 
        config_path: str = "../config/ves_architecture.yaml",
        vault_manager=None,
        engine_manager=None
    ):
        """
        Initialize siphon distributor
        
        Args:
            config_path: Path to configuration file
            vault_manager: VaultManager instance
            engine_manager: EngineManager instance
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.vault_manager = vault_manager
        self.engine_manager = engine_manager
        
        # Track distributions
        self.distributions: List[ProfitDistribution] = []
        self.pending_transfers: List[ProfitDistribution] = []
        
        # Metrics
        self.total_distributed = Decimal('0')
        self.distribution_count = 0
        
        # Create data directory
        self.data_dir = Path("../data/siphon")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load historical data
        self._load_distribution_history()
        
        logger.info("Siphon Distributor initialized")
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            config_path = self.config_path
            if not config_path.is_absolute():
                config_path = Path(__file__).parent / config_path
                
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f)
            return full_config['siphon']
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
            
    def categorize_profit(self, amount: Decimal) -> ProfitCategory:
        """
        Categorize profit amount based on thresholds
        
        Args:
            amount: Profit amount in USD
            
        Returns:
            ProfitCategory enum value
        """
        # Get thresholds from config
        small_range = self.config['distribution_rules']['small_win']['threshold_usd']
        medium_range = self.config['distribution_rules']['medium_win']['threshold_usd']
        
        if amount < Decimal(str(small_range[1])):
            return ProfitCategory.SMALL
        elif amount < Decimal(str(medium_range[1])):
            return ProfitCategory.MEDIUM
        else:
            return ProfitCategory.LARGE
            
    def calculate_distribution(
        self, 
        profit_amount: Decimal, 
        source: str = "ENGINE"
    ) -> ProfitDistribution:
        """
        Calculate how to distribute profits based on rules
        
        Args:
            profit_amount: Amount of profit to distribute
            source: Source of profit (ENGINE or VAULT)
            
        Returns:
            ProfitDistribution object with calculated amounts
        """
        # Categorize the profit
        category = self.categorize_profit(profit_amount)
        
        # Get distribution percentages based on category
        if category == ProfitCategory.SMALL:
            rules = self.config['distribution_rules']['small_win']
        elif category == ProfitCategory.MEDIUM:
            rules = self.config['distribution_rules']['medium_win']
        else:
            rules = self.config['distribution_rules']['large_win']
            
        # Calculate amounts
        vault_percent = Decimal(str(rules['vault_percent'])) / 100
        engine_percent = Decimal(str(rules['engine_percent'])) / 100
        buffer_percent = Decimal(str(rules['buffer_percent'])) / 100
        
        vault_amount = profit_amount * vault_percent
        engine_amount = profit_amount * engine_percent
        buffer_amount = profit_amount * buffer_percent
        
        # Create distribution object
        distribution = ProfitDistribution(
            timestamp=datetime.now(),
            total_amount=profit_amount,
            category=category,
            vault_amount=vault_amount,
            engine_amount=engine_amount,
            buffer_amount=buffer_amount,
            source=source,
            status=TransferStatus.PENDING
        )
        
        logger.info(
            f"Calculated distribution for ${profit_amount:.2f} ({category.value}): "
            f"Vault=${vault_amount:.2f}, Engine=${engine_amount:.2f}, Buffer=${buffer_amount:.2f}"
        )
        
        return distribution
        
    def execute_distribution(self, distribution: ProfitDistribution) -> bool:
        """
        Execute the actual fund transfers for a distribution
        
        Args:
            distribution: ProfitDistribution to execute
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check minimum transfer amount
            min_transfer = Decimal(str(self.config['triggers']['min_transfer_amount_usd']))
            
            if distribution.total_amount < min_transfer:
                logger.info(f"Distribution ${distribution.total_amount} below minimum ${min_transfer}")
                return False
                
            # Update status
            distribution.status = TransferStatus.PROCESSING
            
            # In production, would execute actual transfers via exchange APIs
            # For now, we'll simulate the transfers
            
            # Log transfers to vault
            if distribution.vault_amount > 0:
                logger.info(f"Transferring ${distribution.vault_amount:.2f} to Vault")
                # self.vault_manager.receive_funds(distribution.vault_amount)
                
            # Log transfers to engine
            if distribution.engine_amount > 0:
                logger.info(f"Transferring ${distribution.engine_amount:.2f} to Engine")
                # self.engine_manager.receive_funds(distribution.engine_amount)
                
            # Log transfers to buffer
            if distribution.buffer_amount > 0:
                logger.info(f"Transferring ${distribution.buffer_amount:.2f} to Buffer")
                
            # Update status and metrics
            distribution.status = TransferStatus.COMPLETED
            self.distributions.append(distribution)
            self.total_distributed += distribution.total_amount
            self.distribution_count += 1
            
            # Save to history
            self._save_distribution(distribution)
            
            logger.info(f"Distribution executed successfully: ${distribution.total_amount:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Distribution execution failed: {e}")
            distribution.status = TransferStatus.FAILED
            return False
            
    def process_engine_profits(self) -> Optional[ProfitDistribution]:
        """
        Process profits from Engine trading
        
        Returns:
            ProfitDistribution if profits available, None otherwise
        """
        if not self.engine_manager:
            logger.warning("Engine manager not connected")
            return None
            
        # Get current P&L from engine
        metrics = self.engine_manager.get_performance_metrics()
        daily_pnl = Decimal(str(metrics.get('daily_pnl', 0)))
        
        # Only distribute positive P&L
        if daily_pnl <= 0:
            logger.info(f"No profits to distribute (P&L: ${daily_pnl:.2f})")
            return None
            
        # Calculate distribution
        distribution = self.calculate_distribution(daily_pnl, source="ENGINE")
        
        # Execute if above minimum
        if self.execute_distribution(distribution):
            return distribution
            
        return None
        
    def process_vault_yield(self) -> Optional[ProfitDistribution]:
        """
        Process yield from Vault assets
        
        Returns:
            ProfitDistribution if yield available, None otherwise
        """
        if not self.vault_manager:
            logger.warning("Vault manager not connected")
            return None
            
        # Trigger vault siphon
        siphon_amounts = self.vault_manager.trigger_siphon()
        
        if not siphon_amounts:
            logger.info("No vault yield to distribute")
            return None
            
        # Calculate total yield in USD
        total_yield = sum(siphon_amounts.values())
        
        # Calculate distribution
        distribution = self.calculate_distribution(total_yield, source="VAULT")
        
        # Execute distribution
        if self.execute_distribution(distribution):
            return distribution
            
        return None
        
    def check_rebalancing_needs(self) -> List[RebalanceAction]:
        """
        Check if rebalancing is needed between layers
        
        Returns:
            List of rebalancing actions needed
        """
        rebalance_actions = []
        
        if not self.config['rebalancing']['enabled']:
            return rebalance_actions
            
        # Check if enough time has passed
        frequency_days = self.config['rebalancing']['frequency_days']
        last_rebalance = self._get_last_rebalance_date()
        
        if last_rebalance and (datetime.now() - last_rebalance).days < frequency_days:
            logger.info("Too soon for rebalancing check")
            return rebalance_actions
            
        # Get current allocations
        vault_value = Decimal('0')
        engine_value = Decimal('0')
        
        if self.vault_manager:
            vault_summary = self.vault_manager.get_summary()
            vault_value = Decimal(str(vault_summary['total_value_usd']))
            
        if self.engine_manager:
            engine_metrics = self.engine_manager.get_performance_metrics()
            engine_value = Decimal(str(engine_metrics['total_position_value']))
            
        total_value = vault_value + engine_value
        
        if total_value == 0:
            return rebalance_actions
            
        # Calculate current percentages
        vault_percent = (vault_value / total_value) * 100
        engine_percent = (engine_value / total_value) * 100
        
        # Get target allocations (simplified - would be more complex in production)
        target_vault_percent = 70  # 70% in vault
        target_engine_percent = 30  # 30% in engine
        
        # Check tolerance
        tolerance = Decimal(str(self.config['rebalancing']['tolerance_percent']))
        
        vault_deviation = abs(vault_percent - target_vault_percent)
        engine_deviation = abs(engine_percent - target_engine_percent)
        
        if vault_deviation > tolerance or engine_deviation > tolerance:
            # Calculate rebalancing amounts
            target_vault_value = total_value * Decimal(str(target_vault_percent / 100))
            target_engine_value = total_value * Decimal(str(target_engine_percent / 100))
            
            vault_difference = target_vault_value - vault_value
            
            if vault_difference > 0:
                # Need to move funds from Engine to Vault
                action = RebalanceAction(
                    asset="USDC",
                    from_layer="ENGINE",
                    to_layer="VAULT",
                    amount=abs(vault_difference),
                    reason=f"Vault allocation {vault_percent:.1f}% below target {target_vault_percent}%",
                    priority=1 if vault_deviation > tolerance * 2 else 2
                )
                rebalance_actions.append(action)
                
            elif vault_difference < 0:
                # Need to move funds from Vault to Engine
                action = RebalanceAction(
                    asset="USDC",
                    from_layer="VAULT",
                    to_layer="ENGINE",
                    amount=abs(vault_difference),
                    reason=f"Engine allocation {engine_percent:.1f}% below target {target_engine_percent}%",
                    priority=1 if engine_deviation > tolerance * 2 else 2
                )
                rebalance_actions.append(action)
                
        if rebalance_actions:
            logger.info(f"Identified {len(rebalance_actions)} rebalancing actions needed")
            self._save_rebalance_actions(rebalance_actions)
            
        return rebalance_actions
        
    def execute_rebalancing(self, actions: List[RebalanceAction]) -> Dict[str, Any]:
        """
        Execute rebalancing actions
        
        Args:
            actions: List of rebalancing actions to execute
            
        Returns:
            Summary of execution results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_actions': len(actions),
            'successful': 0,
            'failed': 0,
            'total_rebalanced': Decimal('0')
        }
        
        # Sort by priority
        sorted_actions = sorted(actions, key=lambda x: x.priority)
        
        for action in sorted_actions:
            try:
                logger.info(
                    f"Executing rebalance: {action.amount:.2f} {action.asset} "
                    f"from {action.from_layer} to {action.to_layer}"
                )
                
                # In production, would execute actual transfers
                # For now, simulate success
                
                results['successful'] += 1
                results['total_rebalanced'] += action.amount
                
            except Exception as e:
                logger.error(f"Rebalancing action failed: {e}")
                results['failed'] += 1
                
        # Save rebalancing results
        self._save_rebalance_results(results)
        
        return results
        
    def run_siphon_cycle(self) -> Dict[str, Any]:
        """
        Run a complete siphon cycle checking all sources
        
        Returns:
            Summary of siphon cycle results
        """
        cycle_results = {
            'timestamp': datetime.now().isoformat(),
            'engine_distribution': None,
            'vault_distribution': None,
            'rebalancing_needed': False,
            'total_distributed': Decimal('0')
        }
        
        # Process engine profits
        engine_dist = self.process_engine_profits()
        if engine_dist:
            cycle_results['engine_distribution'] = {
                'amount': float(engine_dist.total_amount),
                'category': engine_dist.category.value,
                'status': engine_dist.status.value
            }
            cycle_results['total_distributed'] += engine_dist.total_amount
            
        # Process vault yield
        vault_dist = self.process_vault_yield()
        if vault_dist:
            cycle_results['vault_distribution'] = {
                'amount': float(vault_dist.total_amount),
                'category': vault_dist.category.value,
                'status': vault_dist.status.value
            }
            cycle_results['total_distributed'] += vault_dist.total_amount
            
        # Check for rebalancing needs
        rebalance_actions = self.check_rebalancing_needs()
        if rebalance_actions:
            cycle_results['rebalancing_needed'] = True
            cycle_results['rebalance_actions'] = len(rebalance_actions)
            
            # Optionally execute rebalancing
            if self.config['rebalancing']['enabled']:
                rebalance_results = self.execute_rebalancing(rebalance_actions)
                cycle_results['rebalancing_executed'] = rebalance_results
                
        # Save cycle results
        self._save_cycle_results(cycle_results)
        
        logger.info(f"Siphon cycle completed: ${cycle_results['total_distributed']:.2f} distributed")
        
        return cycle_results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get siphon statistics"""
        # Calculate distribution by category
        category_stats = {
            'SMALL': {'count': 0, 'total': Decimal('0')},
            'MEDIUM': {'count': 0, 'total': Decimal('0')},
            'LARGE': {'count': 0, 'total': Decimal('0')}
        }
        
        for dist in self.distributions:
            category = dist.category.value
            category_stats[category]['count'] += 1
            category_stats[category]['total'] += dist.total_amount
            
        # Calculate average distribution
        avg_distribution = (
            self.total_distributed / self.distribution_count 
            if self.distribution_count > 0 
            else Decimal('0')
        )
        
        stats = {
            'total_distributed': float(self.total_distributed),
            'distribution_count': self.distribution_count,
            'average_distribution': float(avg_distribution),
            'category_breakdown': {
                cat: {
                    'count': data['count'],
                    'total': float(data['total']),
                    'average': float(data['total'] / data['count']) if data['count'] > 0 else 0
                }
                for cat, data in category_stats.items()
            },
            'last_distribution': (
                self.distributions[-1].timestamp.isoformat() 
                if self.distributions 
                else None
            )
        }
        
        return stats
        
    def _save_distribution(self, distribution: ProfitDistribution) -> None:
        """Save distribution to file"""
        dist_file = self.data_dir / "distributions.jsonl"
        
        dist_data = {
            'timestamp': distribution.timestamp.isoformat(),
            'total_amount': str(distribution.total_amount),
            'category': distribution.category.value,
            'vault_amount': str(distribution.vault_amount),
            'engine_amount': str(distribution.engine_amount),
            'buffer_amount': str(distribution.buffer_amount),
            'source': distribution.source,
            'status': distribution.status.value
        }
        
        with open(dist_file, 'a') as f:
            f.write(json.dumps(dist_data) + '\n')
            
    def _save_rebalance_actions(self, actions: List[RebalanceAction]) -> None:
        """Save rebalancing actions to file"""
        rebalance_file = self.data_dir / f"rebalance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        actions_data = []
        for action in actions:
            actions_data.append({
                'asset': action.asset,
                'from_layer': action.from_layer,
                'to_layer': action.to_layer,
                'amount': str(action.amount),
                'reason': action.reason,
                'priority': action.priority
            })
            
        with open(rebalance_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'actions': actions_data
            }, f, indent=2)
            
    def _save_rebalance_results(self, results: Dict) -> None:
        """Save rebalancing results"""
        results_file = self.data_dir / "rebalance_results.jsonl"
        
        # Convert Decimal to float for JSON serialization
        results['total_rebalanced'] = float(results['total_rebalanced'])
        
        with open(results_file, 'a') as f:
            f.write(json.dumps(results) + '\n')
            
    def _save_cycle_results(self, results: Dict) -> None:
        """Save siphon cycle results"""
        cycle_file = self.data_dir / f"cycles_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Convert Decimal to float for JSON serialization
        results['total_distributed'] = float(results['total_distributed'])
        
        with open(cycle_file, 'a') as f:
            f.write(json.dumps(results) + '\n')
            
    def _load_distribution_history(self) -> None:
        """Load historical distributions from file"""
        dist_file = self.data_dir / "distributions.jsonl"
        
        if not dist_file.exists():
            return
            
        try:
            with open(dist_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    
                    distribution = ProfitDistribution(
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        total_amount=Decimal(data['total_amount']),
                        category=ProfitCategory[data['category']],
                        vault_amount=Decimal(data['vault_amount']),
                        engine_amount=Decimal(data['engine_amount']),
                        buffer_amount=Decimal(data['buffer_amount']),
                        source=data['source'],
                        status=TransferStatus[data['status']]
                    )
                    
                    self.distributions.append(distribution)
                    self.total_distributed += distribution.total_amount
                    self.distribution_count += 1
                    
            logger.info(f"Loaded {len(self.distributions)} historical distributions")
            
        except Exception as e:
            logger.error(f"Failed to load distribution history: {e}")
            
    def _get_last_rebalance_date(self) -> Optional[datetime]:
        """Get the date of last rebalancing"""
        results_file = self.data_dir / "rebalance_results.jsonl"
        
        if not results_file.exists():
            return None
            
        try:
            with open(results_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_result = json.loads(lines[-1])
                    return datetime.fromisoformat(last_result['timestamp'])
                    
        except Exception as e:
            logger.error(f"Failed to get last rebalance date: {e}")
            
        return None


# Example usage and testing
if __name__ == "__main__":
    # Initialize siphon distributor
    siphon = SiphonDistributor()
    
    # Test profit categorization
    test_amounts = [50, 250, 750]
    for amount in test_amounts:
        category = siphon.categorize_profit(Decimal(str(amount)))
        print(f"${amount} -> {category.value}")
        
    # Test distribution calculation
    distribution = siphon.calculate_distribution(Decimal('350'), source="ENGINE")
    print(f"\nDistribution for $350:")
    print(f"  Vault: ${distribution.vault_amount:.2f}")
    print(f"  Engine: ${distribution.engine_amount:.2f}")
    print(f"  Buffer: ${distribution.buffer_amount:.2f}")
    
    # Execute distribution
    success = siphon.execute_distribution(distribution)
    print(f"Distribution executed: {success}")
    
    # Get statistics
    stats = siphon.get_statistics()
    print(f"\nSiphon Statistics: {json.dumps(stats, indent=2)}")