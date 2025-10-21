"""
Vault Manager Module
Handles Ledger tracking, yield generation, and collateral health monitoring
"""

import logging
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AssetPosition:
    """Represents a single asset position in the vault"""
    symbol: str
    balance: Decimal
    value_usd: Decimal
    apy: float
    last_updated: datetime
    allocation_percent: float
    yield_generated: Decimal = Decimal('0')
    

@dataclass
class VaultHealth:
    """Vault health metrics"""
    total_value_usd: Decimal
    collateral_ratio: float
    health_score: float  # 0-100
    last_check: datetime
    warnings: List[str]
    critical_alerts: List[str]


class VaultManager:
    """
    Manages cold storage assets on Ledger
    Tracks yield, monitors health, and triggers siphon distributions
    """
    
    def __init__(self, config_path: str = "../config/ves_architecture.yaml"):
        """Initialize vault manager with configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.positions: Dict[str, AssetPosition] = {}
        self.health: Optional[VaultHealth] = None
        self.last_harvest = datetime.now()
        
        # Create data directory for vault state
        self.data_dir = Path("../data/vault")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Vault Manager initialized")
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config['vault']
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
            
    def update_positions(self, positions_data: Dict[str, dict]) -> None:
        """
        Update vault positions from external data source
        
        Args:
            positions_data: Dictionary of asset positions
                {
                    'ETH': {'balance': 1.5, 'value_usd': 3750},
                    'stETH': {'balance': 2.0, 'value_usd': 5000},
                    ...
                }
        """
        total_value = Decimal('0')
        
        # First pass: update positions and calculate total
        for symbol, data in positions_data.items():
            balance = Decimal(str(data['balance']))
            value_usd = Decimal(str(data['value_usd']))
            
            # Get APY from config
            apy = self.config['assets'].get(symbol, {}).get('yield_apy', 0)
            
            self.positions[symbol] = AssetPosition(
                symbol=symbol,
                balance=balance,
                value_usd=value_usd,
                apy=apy,
                last_updated=datetime.now(),
                allocation_percent=0  # Will calculate next
            )
            total_value += value_usd
            
        # Second pass: calculate allocation percentages
        if total_value > 0:
            for position in self.positions.values():
                position.allocation_percent = float(
                    (position.value_usd / total_value) * 100
                )
                
        self._save_positions()
        logger.info(f"Updated {len(self.positions)} vault positions")
        
    def calculate_yield(self, days: int = 7) -> Dict[str, Decimal]:
        """
        Calculate yield generated over specified period
        
        Returns:
            Dictionary of yield by asset
        """
        yield_by_asset = {}
        
        for symbol, position in self.positions.items():
            if position.apy > 0:
                # Calculate daily yield rate
                daily_rate = position.apy / 365 / 100
                
                # Calculate yield for period
                yield_amount = position.value_usd * Decimal(str(daily_rate)) * days
                yield_by_asset[symbol] = yield_amount
                position.yield_generated += yield_amount
                
        total_yield = sum(yield_by_asset.values())
        logger.info(f"Total yield generated ({days} days): ${total_yield:.2f}")
        
        return yield_by_asset
        
    def check_health(self) -> VaultHealth:
        """
        Check vault health and collateral ratios
        
        Returns:
            VaultHealth object with current metrics
        """
        warnings = []
        critical_alerts = []
        
        # Calculate total vault value
        total_value = sum(p.value_usd for p in self.positions.values())
        
        # Check collateral ratio (simplified - would need lending data)
        collateral_ratio = 2.0  # Placeholder - implement actual calculation
        
        # Check against thresholds
        warning_threshold = self.config['health_monitoring']['collateral_ratio_warning']
        critical_threshold = self.config['health_monitoring']['collateral_ratio_critical']
        
        if collateral_ratio < warning_threshold:
            warnings.append(f"Collateral ratio below warning: {collateral_ratio:.2f}")
            
        if collateral_ratio < critical_threshold:
            critical_alerts.append(f"CRITICAL: Collateral ratio dangerously low: {collateral_ratio:.2f}")
            
        # Check allocation deviations
        for symbol, position in self.positions.items():
            target_allocation = self.config['assets'].get(symbol, {}).get('allocation_percent', 0)
            deviation = abs(position.allocation_percent - target_allocation)
            
            if deviation > 10:
                warnings.append(
                    f"{symbol} allocation off target: {position.allocation_percent:.1f}% "
                    f"(target: {target_allocation}%)"
                )
                
        # Calculate health score (0-100)
        health_score = self._calculate_health_score(collateral_ratio, warnings, critical_alerts)
        
        self.health = VaultHealth(
            total_value_usd=total_value,
            collateral_ratio=collateral_ratio,
            health_score=health_score,
            last_check=datetime.now(),
            warnings=warnings,
            critical_alerts=critical_alerts
        )
        
        self._save_health_report()
        return self.health
        
    def _calculate_health_score(
        self, 
        collateral_ratio: float, 
        warnings: List[str], 
        critical_alerts: List[str]
    ) -> float:
        """Calculate overall health score from 0-100"""
        score = 100.0
        
        # Deduct for collateral ratio
        if collateral_ratio < 2.0:
            score -= (2.0 - collateral_ratio) * 20
            
        # Deduct for warnings and alerts
        score -= len(warnings) * 5
        score -= len(critical_alerts) * 15
        
        return max(0, min(100, score))
        
    def trigger_siphon(self) -> Optional[Dict[str, Decimal]]:
        """
        Calculate and trigger siphon distribution of yield
        
        Returns:
            Dictionary of amounts to siphon by asset, or None if below threshold
        """
        # Check if enough time has passed since last harvest
        harvest_frequency = self.config['yield_management']['harvest_frequency_days']
        if (datetime.now() - self.last_harvest).days < harvest_frequency:
            logger.info("Too soon for harvest, skipping siphon trigger")
            return None
            
        # Calculate accumulated yield
        yield_amounts = self.calculate_yield(days=harvest_frequency)
        total_yield_usd = sum(yield_amounts.values())
        
        # Check minimum threshold
        min_harvest = Decimal(str(self.config['yield_management']['min_harvest_value_usd']))
        if total_yield_usd < min_harvest:
            logger.info(f"Yield ${total_yield_usd:.2f} below minimum ${min_harvest}")
            return None
            
        # Calculate siphon amount (percentage of yield)
        siphon_percentage = self.config['yield_management']['siphon_percentage'] / 100
        siphon_amounts = {}
        
        for symbol, yield_amount in yield_amounts.items():
            siphon_amount = yield_amount * Decimal(str(siphon_percentage))
            siphon_amounts[symbol] = siphon_amount
            
            # Update position to reflect siphon
            if symbol in self.positions:
                self.positions[symbol].yield_generated -= siphon_amount
                
        self.last_harvest = datetime.now()
        self._save_siphon_trigger(siphon_amounts)
        
        total_siphon = sum(siphon_amounts.values())
        logger.info(f"Triggered siphon of ${total_siphon:.2f} from vault yield")
        
        return siphon_amounts
        
    def get_rebalancing_targets(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Calculate rebalancing targets based on configured allocations
        
        Returns:
            Dictionary of rebalancing actions needed
        """
        if not self.positions:
            logger.warning("No positions to rebalance")
            return {}
            
        total_value = sum(p.value_usd for p in self.positions.values())
        rebalancing_targets = {}
        
        for symbol, config in self.config['assets'].items():
            target_percent = config['allocation_percent']
            target_value = total_value * Decimal(str(target_percent / 100))
            
            current_value = self.positions.get(symbol, AssetPosition(
                symbol=symbol, 
                balance=Decimal('0'), 
                value_usd=Decimal('0'),
                apy=0,
                last_updated=datetime.now(),
                allocation_percent=0
            )).value_usd
            
            difference = target_value - current_value
            
            if abs(difference) > total_value * Decimal('0.05'):  # 5% tolerance
                rebalancing_targets[symbol] = {
                    'current_value': current_value,
                    'target_value': target_value,
                    'difference': difference,
                    'action': 'BUY' if difference > 0 else 'SELL'
                }
                
        return rebalancing_targets
        
    def _save_positions(self) -> None:
        """Save current positions to file"""
        positions_file = self.data_dir / "positions.json"
        
        positions_data = {}
        for symbol, position in self.positions.items():
            positions_data[symbol] = {
                'balance': str(position.balance),
                'value_usd': str(position.value_usd),
                'apy': position.apy,
                'last_updated': position.last_updated.isoformat(),
                'allocation_percent': position.allocation_percent,
                'yield_generated': str(position.yield_generated)
            }
            
        with open(positions_file, 'w') as f:
            json.dump(positions_data, f, indent=2)
            
    def _save_health_report(self) -> None:
        """Save health report to file"""
        if not self.health:
            return
            
        health_file = self.data_dir / "health_report.json"
        
        health_data = {
            'total_value_usd': str(self.health.total_value_usd),
            'collateral_ratio': self.health.collateral_ratio,
            'health_score': self.health.health_score,
            'last_check': self.health.last_check.isoformat(),
            'warnings': self.health.warnings,
            'critical_alerts': self.health.critical_alerts
        }
        
        with open(health_file, 'w') as f:
            json.dump(health_data, f, indent=2)
            
    def _save_siphon_trigger(self, siphon_amounts: Dict[str, Decimal]) -> None:
        """Save siphon trigger details"""
        siphon_file = self.data_dir / f"siphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        siphon_data = {
            'timestamp': datetime.now().isoformat(),
            'amounts': {k: str(v) for k, v in siphon_amounts.items()},
            'total_usd': str(sum(siphon_amounts.values()))
        }
        
        with open(siphon_file, 'w') as f:
            json.dump(siphon_data, f, indent=2)
            
    def load_positions(self) -> None:
        """Load positions from saved file"""
        positions_file = self.data_dir / "positions.json"
        
        if not positions_file.exists():
            logger.info("No saved positions found")
            return
            
        try:
            with open(positions_file, 'r') as f:
                positions_data = json.load(f)
                
            for symbol, data in positions_data.items():
                self.positions[symbol] = AssetPosition(
                    symbol=symbol,
                    balance=Decimal(data['balance']),
                    value_usd=Decimal(data['value_usd']),
                    apy=data['apy'],
                    last_updated=datetime.fromisoformat(data['last_updated']),
                    allocation_percent=data['allocation_percent'],
                    yield_generated=Decimal(data['yield_generated'])
                )
                
            logger.info(f"Loaded {len(self.positions)} positions from file")
            
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
            
    def get_summary(self) -> Dict:
        """Get vault summary for reporting"""
        total_value = sum(p.value_usd for p in self.positions.values())
        total_yield = sum(p.yield_generated for p in self.positions.values())
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_value_usd': float(total_value),
            'total_yield_generated': float(total_yield),
            'positions': len(self.positions),
            'health_score': self.health.health_score if self.health else 0,
            'last_harvest': self.last_harvest.isoformat(),
            'assets': {}
        }
        
        for symbol, position in self.positions.items():
            summary['assets'][symbol] = {
                'balance': float(position.balance),
                'value_usd': float(position.value_usd),
                'allocation_percent': position.allocation_percent,
                'apy': position.apy
            }
            
        return summary


# Example usage and testing
if __name__ == "__main__":
    # Initialize vault manager
    vault = VaultManager()
    
    # Example position update
    example_positions = {
        'ETH': {'balance': 1.5, 'value_usd': 3750},
        'stETH': {'balance': 2.0, 'value_usd': 5000},
        'AAVE': {'balance': 50, 'value_usd': 4500},
        'BTC': {'balance': 0.1, 'value_usd': 6500}
    }
    
    vault.update_positions(example_positions)
    
    # Check health
    health = vault.check_health()
    print(f"Vault Health Score: {health.health_score:.1f}")
    
    # Calculate yield
    yield_amounts = vault.calculate_yield(days=7)
    print(f"Weekly Yield: {yield_amounts}")
    
    # Check for siphon trigger
    siphon = vault.trigger_siphon()
    if siphon:
        print(f"Siphon triggered: {siphon}")
        
    # Get summary
    summary = vault.get_summary()
    print(f"Vault Summary: {json.dumps(summary, indent=2)}")