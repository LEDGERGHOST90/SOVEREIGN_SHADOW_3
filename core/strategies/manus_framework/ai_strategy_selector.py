#!/usr/bin/env python3.11
"""
AI Strategy Selector
Intelligently selects the optimal strategy based on market regime
"""
import json
import pandas as pd
from typing import Dict, List, Tuple
from market_regime_detector import MarketRegimeDetector

class AIStrategySelector:
    """
    AI agent that selects the optimal trading strategy based on:
    1. Current market regime
    2. Strategy performance history
    3. Portfolio constraints
    """
    
    def __init__(self, strategy_library_path: str):
        """
        Initialize the selector with a strategy library.
        
        Args:
            strategy_library_path: Path to JSON file containing strategy data
        """
        with open(strategy_library_path, 'r') as f:
            data = json.load(f)
        
        self.strategies = data['components']['strategy_library']['strategies']
        self.regime_detector = MarketRegimeDetector()
        
        # Regime to strategy type mapping
        self.regime_map = {
            "High Volatility Trend": ["Trend Following", "Breakout", "Volatility", "Momentum"],
            "Low Volatility Trend": ["Trend Following", "Pullback", "Momentum"],
            "High Volatility Range": ["Mean Reversion", "Volatility", "Scalping", "Arbitrage"],
            "Low Volatility Range": ["Mean Reversion", "Volatility Squeeze", "Accumulation", "Band-Based"],
            "Transitioning Market": ["Divergence", "Adaptive", "Harmonic"]
        }
    
    def get_strategies_for_regime(self, regime: str) -> List[Dict]:
        """Get all strategies suitable for a given regime"""
        recommended_types = self.regime_map.get(regime, [])
        
        candidate_strategies = []
        for name, data in self.strategies.items():
            if data['type'] in recommended_types:
                candidate_strategies.append({
                    'name': name,
                    'type': data['type'],
                    'score': data.get('score', 0),
                    'source': data.get('source', 'unknown')
                })
        
        # Sort by score
        candidate_strategies.sort(key=lambda x: x['score'], reverse=True)
        return candidate_strategies
    
    def select_strategy(self, market_data: pd.DataFrame, portfolio_constraints: Dict = None) -> Dict:
        """
        Select the optimal strategy for current market conditions.
        
        Args:
            market_data: DataFrame with OHLCV data
            portfolio_constraints: Optional dict with constraints like max_risk, preferred_types, etc.
        
        Returns:
            Dict with selected strategy and reasoning
        """
        # Step 1: Detect current market regime
        regime_info = self.regime_detector.detect_regime(market_data)
        regime = regime_info['regime']
        metrics = regime_info
        
        # Step 2: Get recommended strategy types for this regime
        recommended_types = self.regime_map.get(regime, [])
        
        # Step 3: Filter strategies by type
        candidate_strategies = []
        for name, data in self.strategies.items():
            if data['type'] in recommended_types:
                candidate_strategies.append({
                    'name': name,
                    'type': data['type'],
                    'score': data.get('score', 0),
                    'source': data.get('source', 'unknown')
                })
        
        # Step 4: Apply portfolio constraints if provided
        if portfolio_constraints:
            if 'preferred_types' in portfolio_constraints:
                preferred = portfolio_constraints['preferred_types']
                candidate_strategies = [s for s in candidate_strategies if s['type'] in preferred]
            
            if 'min_score' in portfolio_constraints:
                min_score = portfolio_constraints['min_score']
                candidate_strategies = [s for s in candidate_strategies if s['score'] >= min_score]
        
        # Step 5: Rank candidates by score
        candidate_strategies.sort(key=lambda x: x['score'], reverse=True)
        
        # Step 6: Select top strategy
        if candidate_strategies:
            selected = candidate_strategies[0]
            
            # Build reasoning
            reasoning = {
                "market_regime": regime,
                "regime_metrics": metrics,
                "recommended_types": recommended_types,
                "candidates_evaluated": len(candidate_strategies),
                "selection_criteria": "Highest score among regime-compatible strategies",
                "selected_strategy": selected['name'],
                "strategy_type": selected['type'],
                "strategy_score": selected['score'],
                "alternatives": [s['name'] for s in candidate_strategies[1:6]]  # Top 5 alternatives
            }
            
            return reasoning
        else:
            # No suitable strategies found
            return {
                "market_regime": regime,
                "regime_metrics": metrics,
                "recommended_types": recommended_types,
                "candidates_evaluated": 0,
                "selected_strategy": None,
                "warning": "No strategies match current regime and constraints"
            }
    
    def get_strategy_allocation(self, market_data: pd.DataFrame, num_strategies: int = 3) -> List[Dict]:
        """
        Get a portfolio allocation of multiple strategies for diversification.
        
        Args:
            market_data: DataFrame with OHLCV data
            num_strategies: Number of strategies to allocate
        
        Returns:
            List of strategy allocations with weights
        """
        # Detect regime
        regime, metrics = self.regime_detector.detect_regime(market_data)
        recommended_types = self.regime_map.get(regime, [])
        
        # Get all compatible strategies
        candidates = []
        for name, data in self.strategies.items():
            if data['type'] in recommended_types:
                candidates.append({
                    'name': name,
                    'type': data['type'],
                    'score': data.get('score', 0)
                })
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top N strategies
        selected = candidates[:num_strategies]
        
        # Calculate weights (simple equal weight for now)
        weight = 1.0 / len(selected) if selected else 0
        
        allocation = []
        for strategy in selected:
            allocation.append({
                'strategy_name': strategy['name'],
                'strategy_type': strategy['type'],
                'weight': round(weight, 3),
                'score': strategy['score']
            })
        
        return {
            "market_regime": regime,
            "regime_metrics": metrics,
            "allocation": allocation,
            "total_strategies": len(allocation)
        }


# Example usage and testing
if __name__ == "__main__":
    print("AI Strategy Selector - Test Mode")
    print("=" * 60)
    
    try:
        # Load BTC data
        df = pd.read_csv('/home/ubuntu/upload/BTC-USD-15m.csv')
        df.columns = df.columns.str.strip().str.replace(',', '').str.lower()
        
        # Initialize selector
        selector = AIStrategySelector('/home/ubuntu/strategy_framework_design.json')
        
        print(f"\n📚 Strategy Library Loaded: {len(selector.strategies)} unique strategies")
        
        # Test 1: Select single optimal strategy
        print(f"\n{'='*60}")
        print("TEST 1: Select Optimal Strategy")
        print("=" * 60)
        
        result = selector.select_strategy(df)
        
        print(f"\n🎯 Selected Strategy: {result['selected_strategy']}")
        print(f"   Type: {result['strategy_type']}")
        print(f"   Score: {result['strategy_score']}")
        print(f"\n📊 Market Regime: {result['market_regime']}")
        print(f"   ADX: {result['regime_metrics']['adx']}")
        print(f"   ATR Percentile: {result['regime_metrics']['atr_percentile']}%")
        print(f"\n💡 Reasoning:")
        print(f"   - Recommended Types: {', '.join(result['recommended_types'])}")
        print(f"   - Candidates Evaluated: {result['candidates_evaluated']}")
        print(f"   - Selection Criteria: {result['selection_criteria']}")
        
        if result['alternatives']:
            print(f"\n🔄 Top Alternatives:")
            for i, alt in enumerate(result['alternatives'][:3], 1):
                print(f"   {i}. {alt}")
        
        # Test 2: Get portfolio allocation
        print(f"\n{'='*60}")
        print("TEST 2: Portfolio Allocation (Top 3 Strategies)")
        print("=" * 60)
        
        allocation = selector.get_strategy_allocation(df, num_strategies=3)
        
        print(f"\n📊 Market Regime: {allocation['market_regime']}")
        print(f"\n💼 Recommended Portfolio Allocation:")
        for i, strat in enumerate(allocation['allocation'], 1):
            print(f"   {i}. {strat['strategy_name']}")
            print(f"      Type: {strat['strategy_type']}")
            print(f"      Weight: {strat['weight']*100:.1f}%")
            print(f"      Score: {strat['score']}")
            print()
        
        print("=" * 60)
        print("✅ AI Strategy Selector is operational!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
