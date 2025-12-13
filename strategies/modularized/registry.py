#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Strategy Registry
Manages all available modular strategies

Author: SovereignShadow Trading System
"""

import json
import logging
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass

from .base import ModularStrategy, BaseEntryModule, BaseExitModule, BaseRiskModule

logger = logging.getLogger(__name__)


@dataclass
class StrategyMetadata:
    """Strategy metadata from metadata.json"""
    strategy_name: str
    strategy_type: str  # mean_reversion, trend_following, breakout, etc.
    suitable_regimes: List[str]
    timeframes: List[str]
    assets: List[str]
    risk_per_trade: float
    max_position_size: float
    indicators_required: List[str]
    description: str = ""
    author: str = "SovereignShadow"
    version: str = "1.0.0"


class StrategyRegistry:
    """
    Central registry for all modular strategies
    
    Features:
    - Auto-discovery of strategies from directory
    - Strategy lookup by name or regime
    - Metadata management
    - Performance tracking integration
    """
    
    def __init__(self, strategies_dir: str = None):
        """
        Initialize strategy registry
        
        Args:
            strategies_dir: Path to strategies/modularized directory
        """
        if strategies_dir is None:
            strategies_dir = Path(__file__).parent
        
        self.strategies_dir = Path(strategies_dir)
        self.strategies: Dict[str, ModularStrategy] = {}
        self.metadata: Dict[str, StrategyMetadata] = {}
        
        logger.info(f"📋 Strategy Registry initialized: {self.strategies_dir}")
    
    def register(self, strategy: ModularStrategy, metadata: StrategyMetadata = None):
        """
        Register a strategy
        
        Args:
            strategy: ModularStrategy instance
            metadata: Optional StrategyMetadata
        """
        self.strategies[strategy.name] = strategy
        
        if metadata:
            self.metadata[strategy.name] = metadata
        
        logger.info(f"✅ Registered strategy: {strategy.name}")
    
    def get(self, name: str) -> Optional[ModularStrategy]:
        """Get strategy by name"""
        return self.strategies.get(name)
    
    def get_by_regime(self, regime: str) -> List[ModularStrategy]:
        """Get all strategies suitable for a regime"""
        suitable = []
        
        for name, strategy in self.strategies.items():
            if strategy.is_suitable_for_regime(regime):
                suitable.append(strategy)
        
        return suitable
    
    def get_by_type(self, strategy_type: str) -> List[ModularStrategy]:
        """Get all strategies of a type (mean_reversion, trend_following, etc.)"""
        suitable = []
        
        for name, meta in self.metadata.items():
            if meta.strategy_type == strategy_type:
                strategy = self.strategies.get(name)
                if strategy:
                    suitable.append(strategy)
        
        return suitable
    
    def list_all(self) -> List[str]:
        """List all registered strategy names"""
        return list(self.strategies.keys())
    
    def list_by_regime(self) -> Dict[str, List[str]]:
        """List strategies grouped by regime"""
        by_regime: Dict[str, List[str]] = {
            'trending_bull': [],
            'trending_bear': [],
            'choppy_volatile': [],
            'choppy_calm': []
        }
        
        for name, strategy in self.strategies.items():
            for regime in strategy.suitable_regimes:
                if regime in by_regime:
                    by_regime[regime].append(name)
        
        return by_regime
    
    def get_metadata(self, name: str) -> Optional[StrategyMetadata]:
        """Get metadata for a strategy"""
        return self.metadata.get(name)
    
    def auto_discover(self):
        """
        Auto-discover and load strategies from directory
        
        Looks for directories with __init__.py, entry.py, exit.py, risk.py
        """
        logger.info("🔍 Auto-discovering strategies...")
        
        for strategy_dir in self.strategies_dir.iterdir():
            if not strategy_dir.is_dir():
                continue
            
            if strategy_dir.name.startswith('_') or strategy_dir.name.startswith('.'):
                continue
            
            # Check for required files
            required_files = ['__init__.py', 'entry.py', 'exit.py', 'risk.py']
            has_all_files = all((strategy_dir / f).exists() for f in required_files)
            
            if not has_all_files:
                continue
            
            try:
                self._load_strategy_module(strategy_dir)
            except Exception as e:
                logger.warning(f"⚠️  Failed to load {strategy_dir.name}: {e}")
        
        logger.info(f"📋 Discovered {len(self.strategies)} strategies")
    
    def _load_strategy_module(self, strategy_dir: Path):
        """Load a strategy from its directory"""
        strategy_name = strategy_dir.name
        
        # Convert directory name to module path
        # e.g., elder_reversion -> strategies.modularized.elder_reversion
        module_base = f"strategies.modularized.{strategy_name}"
        
        # Try to import the strategy module
        try:
            strategy_module = importlib.import_module(module_base)
            
            # Look for get_strategy() function or Strategy class
            if hasattr(strategy_module, 'get_strategy'):
                strategy = strategy_module.get_strategy()
                self.register(strategy)
            elif hasattr(strategy_module, 'Strategy'):
                strategy = strategy_module.Strategy()
                self.register(strategy)
            
            # Load metadata if exists
            metadata_file = strategy_dir / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    meta_dict = json.load(f)
                    metadata = StrategyMetadata(**meta_dict)
                    self.metadata[strategy_name] = metadata
                    
        except Exception as e:
            logger.warning(f"⚠️  Could not import {module_base}: {e}")
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry information"""
        return {
            'total_strategies': len(self.strategies),
            'strategies': {
                name: {
                    'suitable_regimes': strat.suitable_regimes,
                    'timeframes': strat.timeframes,
                    'assets': strat.assets
                }
                for name, strat in self.strategies.items()
            },
            'by_regime': self.list_by_regime()
        }
    
    def __len__(self) -> int:
        return len(self.strategies)
    
    def __contains__(self, name: str) -> bool:
        return name in self.strategies
    
    def __iter__(self):
        return iter(self.strategies.values())


# Global registry instance
_global_registry = None


def get_registry() -> StrategyRegistry:
    """Get or create global strategy registry"""
    global _global_registry
    
    if _global_registry is None:
        _global_registry = StrategyRegistry()
    
    return _global_registry
