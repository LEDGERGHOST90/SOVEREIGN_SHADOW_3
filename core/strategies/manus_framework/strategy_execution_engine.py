#!/usr/bin/env python3.11
"""
Strategy Execution Engine
Manages the execution and monitoring of selected strategies
"""
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from market_regime_detector import MarketRegimeDetector
from ai_strategy_selector import AIStrategySelector

class StrategyExecutionEngine:
    """
    Execution engine that:
    1. Monitors market conditions continuously
    2. Detects regime changes
    3. Automatically switches strategies when regime changes
    4. Tracks performance and logs decisions
    """
    
    def __init__(self, strategy_library_path: str, config: Dict = None):
        """
        Initialize the execution engine.
        
        Args:
            strategy_library_path: Path to strategy library JSON
            config: Optional configuration dict
        """
        self.selector = AIStrategySelector(strategy_library_path)
        self.regime_detector = MarketRegimeDetector()
        
        # Default configuration
        self.config = {
            'regime_check_interval': 15,  # Check regime every N candles
            'min_regime_duration': 3,  # Require N consecutive confirmations before switching
            'enable_auto_switch': True,  # Automatically switch strategies on regime change
            'max_concurrent_strategies': 3,  # Maximum number of strategies to run simultaneously
            'log_decisions': True  # Log all decisions
        }
        
        if config:
            self.config.update(config)
        
        # State tracking
        self.current_regime = None
        self.current_strategy = None
        self.regime_confirmation_count = 0
        self.decision_log = []
    
    def analyze_and_select(self, market_data: pd.DataFrame) -> Dict:
        """
        Analyze market and select strategy.
        
        Args:
            market_data: DataFrame with OHLCV data
        
        Returns:
            Dict with analysis and selection results
        """
        # Detect current regime
        regime, metrics = self.regime_detector.detect_regime(market_data)
        
        # Check for regime change
        regime_changed = (regime != self.current_regime)
        
        if regime_changed:
            self.regime_confirmation_count = 1
            print(f"⚠️  Potential regime change detected: {self.current_regime} → {regime}")
        else:
            self.regime_confirmation_count += 1
        
        # Decide whether to switch strategy
        should_switch = False
        if regime_changed and self.regime_confirmation_count >= self.config['min_regime_duration']:
            should_switch = True
            self.current_regime = regime
        
        # Select strategy
        selection = self.selector.select_strategy(market_data)
        
        # Build decision record
        decision = {
            'timestamp': datetime.now().isoformat(),
            'regime': regime,
            'regime_metrics': metrics,
            'regime_changed': regime_changed,
            'regime_confirmations': self.regime_confirmation_count,
            'should_switch_strategy': should_switch,
            'selected_strategy': selection.get('selected_strategy'),
            'strategy_type': selection.get('strategy_type'),
            'previous_strategy': self.current_strategy
        }
        
        # Update current strategy if switching
        if should_switch and self.config['enable_auto_switch']:
            old_strategy = self.current_strategy
            self.current_strategy = selection.get('selected_strategy')
            decision['action'] = f"Switched from {old_strategy} to {self.current_strategy}"
            print(f"🔄 Strategy Switch: {old_strategy} → {self.current_strategy}")
        else:
            decision['action'] = "Maintained current strategy"
        
        # Log decision
        if self.config['log_decisions']:
            self.decision_log.append(decision)
        
        return decision
    
    def get_portfolio_execution_plan(self, market_data: pd.DataFrame) -> Dict:
        """
        Get a multi-strategy execution plan for portfolio diversification.
        
        Args:
            market_data: DataFrame with OHLCV data
        
        Returns:
            Dict with execution plan
        """
        allocation = self.selector.get_strategy_allocation(
            market_data,
            num_strategies=self.config['max_concurrent_strategies']
        )
        
        execution_plan = {
            'timestamp': datetime.now().isoformat(),
            'market_regime': allocation['market_regime'],
            'regime_metrics': allocation['regime_metrics'],
            'strategies': allocation['allocation'],
            'total_strategies': allocation['total_strategies']
        }
        
        return execution_plan
    
    def export_decision_log(self, filepath: str):
        """Export decision log to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.decision_log, indent=2, fp=f)
        print(f"✅ Decision log exported to {filepath}")
    
    def get_performance_summary(self) -> Dict:
        """Get summary of engine performance"""
        if not self.decision_log:
            return {"message": "No decisions logged yet"}
        
        regime_counts = {}
        strategy_counts = {}
        
        for decision in self.decision_log:
            regime = decision['regime']
            strategy = decision.get('selected_strategy')
            
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
            if strategy:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            'total_decisions': len(self.decision_log),
            'regime_distribution': regime_counts,
            'strategy_distribution': strategy_counts,
            'current_regime': self.current_regime,
            'current_strategy': self.current_strategy
        }


# Example usage and testing
if __name__ == "__main__":
    print("Strategy Execution Engine - Test Mode")
    print("=" * 60)
    
    try:
        # Load BTC data
        df = pd.read_csv('/home/ubuntu/upload/BTC-USD-15m.csv')
        df.columns = df.columns.str.strip().str.replace(',', '').str.lower()
        
        # Initialize engine
        config = {
            'regime_check_interval': 15,
            'min_regime_duration': 1,  # For testing, switch immediately
            'enable_auto_switch': True,
            'max_concurrent_strategies': 3
        }
        
        engine = StrategyExecutionEngine(
            '/home/ubuntu/strategy_framework_design.json',
            config=config
        )
        
        print(f"\n✅ Execution Engine Initialized")
        print(f"   Auto-Switch: {config['enable_auto_switch']}")
        print(f"   Max Concurrent Strategies: {config['max_concurrent_strategies']}")
        
        # Test 1: Single strategy selection
        print(f"\n{'='*60}")
        print("TEST 1: Analyze Market & Select Strategy")
        print("=" * 60)
        
        decision = engine.analyze_and_select(df)
        
        print(f"\n🎯 Decision Summary:")
        print(f"   Regime: {decision['regime']}")
        print(f"   Selected Strategy: {decision['selected_strategy']}")
        print(f"   Action: {decision['action']}")
        
        # Test 2: Portfolio execution plan
        print(f"\n{'='*60}")
        print("TEST 2: Portfolio Execution Plan")
        print("=" * 60)
        
        plan = engine.get_portfolio_execution_plan(df)
        
        print(f"\n💼 Execution Plan:")
        print(f"   Market Regime: {plan['market_regime']}")
        print(f"   Total Strategies: {plan['total_strategies']}")
        print(f"\n   Strategy Allocation:")
        for i, strat in enumerate(plan['strategies'], 1):
            print(f"      {i}. {strat['strategy_name']} ({strat['weight']*100:.0f}%)")
        
        # Test 3: Performance summary
        print(f"\n{'='*60}")
        print("TEST 3: Performance Summary")
        print("=" * 60)
        
        summary = engine.get_performance_summary()
        print(f"\n📊 Engine Performance:")
        print(f"   Total Decisions: {summary['total_decisions']}")
        print(f"   Current Regime: {summary['current_regime']}")
        print(f"   Current Strategy: {summary['current_strategy']}")
        
        # Export decision log
        engine.export_decision_log('/home/ubuntu/execution_decision_log.json')
        
        print(f"\n{'='*60}")
        print("✅ Strategy Execution Engine is operational!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
