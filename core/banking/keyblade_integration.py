#!/usr/bin/env python3
"""
KeybladeAI Integration Module - Advanced Tactical Logic for ShadowCommander
Integrates risk evaluation, flip strategy confidence, ladder structures, and tile heat map scoring

This module transforms the ShadowCommander from basic strategy generation into
a sophisticated wealth multiplication engine with KeybladeAI intelligence.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeybladeFlipTemplate:
    """30-50% Flip Template Structure"""
    template_id: str
    target_profit_range: Tuple[float, float]  # (0.30, 0.50) for 30-50%
    ladder_structure: List[Dict[str, float]]  # TP/SL ladder points
    risk_parameters: Dict[str, float]
    confidence_threshold: float
    max_position_size: float
    stop_loss_levels: List[float]
    take_profit_levels: List[float]

@dataclass
class LadderStrategy:
    """Sniper TP/SL Ladder Structure"""
    ladder_id: str
    symbol: str
    entry_price: float
    ladder_depth: int  # Number of ladder rungs
    spread_ratio: float  # % between each rung
    tp_levels: List[float]  # Take profit levels
    sl_levels: List[float]  # Stop loss levels
    position_sizes: List[float]  # Position size for each level
    aggression_mode: str  # STEALTH, STANDARD, ALPHA, SCALP

@dataclass
class RiskEvaluation:
    """Enhanced Risk Evaluation with Emotional State"""
    risk_score: float  # 0.0 to 1.0
    emotional_state: str  # 🟢🟡🔴
    risk_factors: List[str]
    confidence_level: float
    market_phase_risk: float
    portfolio_risk: float
    volatility_risk: float
    correlation_risk: float
    recommendation: str  # PROCEED, CAUTION, HALT

@dataclass
class TileHeatMap:
    """Asset Correlation and Heat Map Scoring"""
    symbol: str
    heat_score: float  # 0.0 to 1.0 (cold to hot)
    correlation_matrix: Dict[str, float]  # Correlation with other assets
    urgency_score: float  # How urgent is action needed
    opportunity_score: float  # How good is the opportunity
    risk_score: float  # How risky is the asset
    momentum_score: float  # Price momentum indicator

class KeybladeAIEngine:
    """
    Advanced KeybladeAI Integration Engine
    Provides sophisticated tactical analysis for wealth multiplication
    """
    
    def __init__(self, llf_beta_path: str = "/home/ubuntu/LLF-Beta"):
        self.llf_beta_path = Path(llf_beta_path)
        self.flip_templates = self._load_flip_templates()
        self.correlation_matrix = self._load_correlation_matrix()
        self.risk_thresholds = self._load_risk_thresholds()
        
    def _load_flip_templates(self) -> Dict[str, KeybladeFlipTemplate]:
        """Load 30-50% flip templates"""
        
        # Default 30-50% flip template
        default_template = KeybladeFlipTemplate(
            template_id="COMMANDER_30_50_FLIP",
            target_profit_range=(0.30, 0.50),
            ladder_structure=[
                {"level": 1, "tp_percent": 0.15, "position_percent": 0.4},
                {"level": 2, "tp_percent": 0.25, "position_percent": 0.3},
                {"level": 3, "tp_percent": 0.35, "position_percent": 0.2},
                {"level": 4, "tp_percent": 0.50, "position_percent": 0.1}
            ],
            risk_parameters={
                "max_drawdown": 0.08,  # 8% max loss
                "position_size_limit": 0.15,  # 15% max position
                "volatility_threshold": 0.06,  # 6% daily volatility limit
                "correlation_limit": 0.7  # Max 70% correlation with existing positions
            },
            confidence_threshold=0.75,
            max_position_size=0.15,
            stop_loss_levels=[0.05, 0.08, 0.12],  # 5%, 8%, 12% stop losses
            take_profit_levels=[0.15, 0.25, 0.35, 0.50]  # TP levels
        )
        
        return {"default": default_template}
    
    def _load_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Load asset correlation matrix for heat map scoring"""
        
        # Sample correlation matrix (in real implementation, load from file)
        correlation_matrix = {
            "BTC": {"ETH": 0.85, "WIF": 0.65, "BONK": 0.45, "XRP": 0.55},
            "ETH": {"BTC": 0.85, "WIF": 0.70, "BONK": 0.50, "XRP": 0.60},
            "WIF": {"BTC": 0.65, "ETH": 0.70, "BONK": 0.80, "XRP": 0.40},
            "BONK": {"BTC": 0.45, "ETH": 0.50, "WIF": 0.80, "XRP": 0.35},
            "XRP": {"BTC": 0.55, "ETH": 0.60, "WIF": 0.40, "BONK": 0.35}
        }
        
        return correlation_matrix
    
    def _load_risk_thresholds(self) -> Dict[str, float]:
        """Load risk evaluation thresholds"""
        
        return {
            "green_threshold": 0.25,    # Risk < 25% = 🟢
            "yellow_threshold": 0.60,   # Risk 25-60% = 🟡  
            "red_threshold": 1.0,       # Risk > 60% = 🔴
            "volatility_limit": 0.08,   # 8% daily volatility limit
            "correlation_limit": 0.75,  # 75% max correlation
            "drawdown_limit": 0.10,     # 10% max drawdown
            "confidence_minimum": 0.60  # 60% minimum confidence
        }
    
    def evaluate_risk_level(self, portfolio_data: Dict, market_data: Dict) -> RiskEvaluation:
        """Enhanced risk evaluation with emotional state determination"""
        
        risk_factors = []
        risk_scores = []
        
        # Market volatility risk
        market_volatility = market_data.get('volatility', 0.04)
        volatility_risk = min(market_volatility / self.risk_thresholds['volatility_limit'], 1.0)
        risk_scores.append(volatility_risk)
        
        if volatility_risk > 0.7:
            risk_factors.append(f"High market volatility: {market_volatility:.1%}")
        
        # Portfolio concentration risk
        holdings = portfolio_data.get('holdings', [])
        if holdings:
            max_allocation = max([h.get('allocation_percent', 0) for h in holdings]) / 100
            concentration_risk = max_allocation if max_allocation > 0.3 else 0.0
            risk_scores.append(concentration_risk)
            
            if concentration_risk > 0.4:
                risk_factors.append(f"High concentration risk: {max_allocation:.1%} in single asset")
        
        # Portfolio performance risk (recent losses)
        portfolio_change = portfolio_data.get('change_24h', 0.0)
        performance_risk = max(-portfolio_change, 0.0) if portfolio_change < 0 else 0.0
        risk_scores.append(performance_risk)
        
        if performance_risk > 0.05:
            risk_factors.append(f"Recent portfolio decline: {abs(portfolio_change):.1%}")
        
        # Correlation risk (how correlated are holdings)
        correlation_risk = self._calculate_correlation_risk(holdings)
        risk_scores.append(correlation_risk)
        
        if correlation_risk > 0.6:
            risk_factors.append("High asset correlation detected")
        
        # Calculate overall risk score
        overall_risk = np.mean(risk_scores) if risk_scores else 0.0
        
        # Determine emotional state
        if overall_risk < self.risk_thresholds['green_threshold']:
            emotional_state = "🟢"
            recommendation = "PROCEED"
        elif overall_risk < self.risk_thresholds['yellow_threshold']:
            emotional_state = "🟡"
            recommendation = "CAUTION"
        else:
            emotional_state = "🔴"
            recommendation = "HALT"
        
        # Calculate confidence level
        confidence_level = max(1.0 - overall_risk, 0.1)
        
        return RiskEvaluation(
            risk_score=overall_risk,
            emotional_state=emotional_state,
            risk_factors=risk_factors,
            confidence_level=confidence_level,
            market_phase_risk=volatility_risk,
            portfolio_risk=concentration_risk,
            volatility_risk=volatility_risk,
            correlation_risk=correlation_risk,
            recommendation=recommendation
        )
    
    def _calculate_correlation_risk(self, holdings: List[Dict]) -> float:
        """Calculate portfolio correlation risk"""
        
        if len(holdings) < 2:
            return 0.0
        
        correlations = []
        symbols = [h.get('symbol', '') for h in holdings]
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                if symbol1 in self.correlation_matrix and symbol2 in self.correlation_matrix[symbol1]:
                    correlation = abs(self.correlation_matrix[symbol1][symbol2])
                    correlations.append(correlation)
        
        if correlations:
            avg_correlation = np.mean(correlations)
            return min(avg_correlation, 1.0)
        
        return 0.5  # Default moderate correlation
    
    def generate_ladder_strategy(self, symbol: str, entry_price: float, 
                                confidence_score: float, risk_level: float) -> LadderStrategy:
        """Generate sniper TP/SL ladder strategy"""
        
        # Determine aggression mode based on confidence and risk
        if confidence_score > 0.8 and risk_level < 0.3:
            aggression_mode = "ALPHA"
            ladder_depth = 5
            spread_ratio = 0.008  # 0.8% between levels
        elif confidence_score > 0.6 and risk_level < 0.5:
            aggression_mode = "STANDARD"
            ladder_depth = 4
            spread_ratio = 0.012  # 1.2% between levels
        else:
            aggression_mode = "STEALTH"
            ladder_depth = 3
            spread_ratio = 0.015  # 1.5% between levels
        
        # Generate TP levels based on 30-50% template
        template = self.flip_templates["default"]
        tp_levels = []
        sl_levels = []
        position_sizes = []
        
        for i, level_data in enumerate(template.ladder_structure[:ladder_depth]):
            tp_percent = level_data["tp_percent"]
            position_percent = level_data["position_percent"]
            
            tp_price = entry_price * (1 + tp_percent)
            tp_levels.append(tp_price)
            
            # Stop loss at 5% below entry for all levels
            sl_price = entry_price * 0.95
            sl_levels.append(sl_price)
            
            position_sizes.append(position_percent)
        
        return LadderStrategy(
            ladder_id=f"LADDER_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            entry_price=entry_price,
            ladder_depth=ladder_depth,
            spread_ratio=spread_ratio,
            tp_levels=tp_levels,
            sl_levels=sl_levels,
            position_sizes=position_sizes,
            aggression_mode=aggression_mode
        )
    
    def calculate_tile_heat_map(self, symbols: List[str], market_data: Dict) -> Dict[str, TileHeatMap]:
        """Calculate tile heat map scoring for assets"""
        
        heat_maps = {}
        
        for symbol in symbols:
            # Calculate heat score based on multiple factors
            price_change = market_data.get(f'{symbol}_change_24h', 0.0)
            volume_change = market_data.get(f'{symbol}_volume_change', 0.0)
            volatility = market_data.get(f'{symbol}_volatility', 0.04)
            
            # Heat score calculation
            momentum_score = min(abs(price_change) * 2, 1.0)  # Price momentum
            volume_score = min(volume_change / 2.0, 1.0) if volume_change > 0 else 0.0
            volatility_score = min(volatility / 0.1, 1.0)  # Normalize to 10% volatility
            
            heat_score = (momentum_score * 0.4 + volume_score * 0.3 + volatility_score * 0.3)
            
            # Opportunity score (higher for oversold quality assets)
            if price_change < -0.05 and symbol in ['BTC', 'ETH', 'XRP']:  # Quality assets down 5%+
                opportunity_score = min(abs(price_change) * 3, 1.0)
            elif price_change > 0.1:  # Assets up 10%+ (profit taking opportunity)
                opportunity_score = min(price_change * 2, 1.0)
            else:
                opportunity_score = 0.3  # Neutral opportunity
            
            # Risk score (higher volatility = higher risk)
            risk_score = min(volatility / 0.08, 1.0)  # Normalize to 8% volatility
            
            # Urgency score (how urgent is action needed)
            if abs(price_change) > 0.1:  # 10%+ move
                urgency_score = 0.9
            elif abs(price_change) > 0.05:  # 5%+ move
                urgency_score = 0.6
            else:
                urgency_score = 0.2
            
            # Get correlations
            correlations = self.correlation_matrix.get(symbol, {})
            
            heat_maps[symbol] = TileHeatMap(
                symbol=symbol,
                heat_score=heat_score,
                correlation_matrix=correlations,
                urgency_score=urgency_score,
                opportunity_score=opportunity_score,
                risk_score=risk_score,
                momentum_score=momentum_score
            )
        
        return heat_maps
    
    def calculate_flip_confidence(self, symbol: str, entry_price: float, 
                                 market_conditions: Dict, portfolio_context: Dict) -> float:
        """Calculate flip strategy confidence score"""
        
        confidence_factors = []
        
        # Technical analysis confidence
        price_change_24h = market_conditions.get(f'{symbol}_change_24h', 0.0)
        if symbol in ['BTC', 'ETH', 'XRP'] and price_change_24h < -0.05:
            # Quality assets oversold
            confidence_factors.append(0.8)
        elif price_change_24h > 0.15:
            # Overbought - lower confidence for new entries
            confidence_factors.append(0.3)
        else:
            confidence_factors.append(0.6)
        
        # Volume analysis confidence
        volume_change = market_conditions.get(f'{symbol}_volume_change', 0.0)
        if volume_change > 1.5:  # 150%+ volume increase
            confidence_factors.append(0.8)
        elif volume_change > 1.0:  # 100%+ volume increase
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Portfolio diversification confidence
        current_allocation = portfolio_context.get(f'{symbol}_allocation', 0.0)
        if current_allocation < 0.1:  # Less than 10% allocation
            confidence_factors.append(0.8)
        elif current_allocation < 0.2:  # Less than 20% allocation
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)  # Already heavily allocated
        
        # Market phase confidence
        market_sentiment = market_conditions.get('sentiment', 'NEUTRAL')
        if market_sentiment in ['BULLISH', 'NEUTRAL_BULLISH']:
            confidence_factors.append(0.8)
        elif market_sentiment == 'NEUTRAL':
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # Calculate weighted confidence score
        confidence_score = np.mean(confidence_factors)
        
        # Apply Ray Rules adjustment (if available)
        ray_score = portfolio_context.get('ray_score', 70.0)
        ray_adjustment = (ray_score / 100.0) * 0.2  # Up to 20% adjustment
        confidence_score = min(confidence_score + ray_adjustment, 1.0)
        
        return confidence_score
    
    def generate_wealth_multiplication_plan(self, portfolio_data: Dict, 
                                          market_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive wealth multiplication plan using KeybladeAI logic"""
        
        # Risk evaluation
        risk_eval = self.evaluate_risk_level(portfolio_data, market_data)
        
        # Get symbols from portfolio
        symbols = [h.get('symbol', '') for h in portfolio_data.get('holdings', [])]
        if not symbols:
            symbols = ['BTC', 'ETH', 'WIF', 'BONK', 'XRP']  # Default watchlist
        
        # Calculate heat maps
        heat_maps = self.calculate_tile_heat_map(symbols, market_data)
        
        # Generate ladder strategies for high-opportunity assets
        ladder_strategies = {}
        for symbol, heat_map in heat_maps.items():
            if heat_map.opportunity_score > 0.6:  # High opportunity threshold
                current_price = market_data.get(f'{symbol}_price', 1.0)
                confidence = self.calculate_flip_confidence(
                    symbol, current_price, market_data, portfolio_data
                )
                
                if confidence > 0.6:  # Minimum confidence threshold
                    ladder_strategies[symbol] = self.generate_ladder_strategy(
                        symbol, current_price, confidence, risk_eval.risk_score
                    )
        
        # ROI projections
        roi_projections = self._calculate_roi_projections(
            portfolio_data, ladder_strategies, risk_eval
        )
        
        return {
            'risk_evaluation': asdict(risk_eval),
            'heat_maps': {k: asdict(v) for k, v in heat_maps.items()},
            'ladder_strategies': {k: asdict(v) for k, v in ladder_strategies.items()},
            'roi_projections': roi_projections,
            'wealth_multiplication_score': self._calculate_wealth_score(
                risk_eval, heat_maps, ladder_strategies
            ),
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_roi_projections(self, portfolio_data: Dict, 
                                  ladder_strategies: Dict, 
                                  risk_eval: RiskEvaluation) -> Dict[str, float]:
        """Calculate ROI projections for wealth multiplication"""
        
        total_value = portfolio_data.get('total_value', 1000.0)
        
        # Conservative projections based on risk level
        if risk_eval.emotional_state == "🟢":
            monthly_multiplier = 1.15  # 15% monthly growth potential
            confidence_multiplier = 0.9
        elif risk_eval.emotional_state == "🟡":
            monthly_multiplier = 1.08  # 8% monthly growth potential
            confidence_multiplier = 0.7
        else:
            monthly_multiplier = 1.03  # 3% monthly growth potential
            confidence_multiplier = 0.5
        
        # Factor in number of active strategies
        strategy_bonus = min(len(ladder_strategies) * 0.02, 0.1)  # Up to 10% bonus
        
        projections = {}
        for month in range(1, 5):  # 4-month projection
            base_growth = (monthly_multiplier ** month - 1) * total_value
            strategy_enhancement = base_growth * strategy_bonus
            confidence_adjustment = (base_growth + strategy_enhancement) * confidence_multiplier
            
            projections[f'month_{month}'] = round(confidence_adjustment, 2)
        
        return projections
    
    def _calculate_wealth_score(self, risk_eval: RiskEvaluation, 
                               heat_maps: Dict[str, TileHeatMap],
                               ladder_strategies: Dict) -> float:
        """Calculate overall wealth multiplication score"""
        
        # Base score from risk evaluation (lower risk = higher score)
        risk_score = 1.0 - risk_eval.risk_score
        
        # Opportunity score from heat maps
        if heat_maps:
            avg_opportunity = np.mean([hm.opportunity_score for hm in heat_maps.values()])
        else:
            avg_opportunity = 0.5
        
        # Strategy score from number and quality of strategies
        strategy_score = min(len(ladder_strategies) / 3.0, 1.0)  # Normalize to 3 strategies
        
        # Confidence score
        confidence_score = risk_eval.confidence_level
        
        # Weighted combination
        wealth_score = (
            risk_score * 0.3 +
            avg_opportunity * 0.25 +
            strategy_score * 0.25 +
            confidence_score * 0.2
        )
        
        return round(wealth_score, 3)

def main():
    """Test KeybladeAI integration"""
    
    engine = KeybladeAIEngine()
    
    # Sample data
    portfolio_data = {
        'total_value': 1543.40,
        'change_24h': 0.0567,
        'holdings': [
            {'symbol': 'WIF', 'value': 464.69, 'allocation_percent': 30.1},
            {'symbol': 'BONK', 'value': 205.58, 'allocation_percent': 13.3},
            {'symbol': 'XRP', 'value': 202.06, 'allocation_percent': 13.1}
        ]
    }
    
    market_data = {
        'volatility': 0.045,
        'sentiment': 'NEUTRAL_BULLISH',
        'WIF_change_24h': 0.12,
        'WIF_volume_change': 1.8,
        'WIF_price': 2.89,
        'BONK_change_24h': -0.08,
        'BONK_volume_change': 1.2,
        'BONK_price': 0.000025,
        'XRP_change_24h': 0.05,
        'XRP_volume_change': 1.4,
        'XRP_price': 0.58
    }
    
    # Generate wealth multiplication plan
    plan = engine.generate_wealth_multiplication_plan(portfolio_data, market_data)
    
    print("🔥 KEYBLADEAI WEALTH MULTIPLICATION PLAN")
    print(f"Risk Level: {plan['risk_evaluation']['emotional_state']} ({plan['risk_evaluation']['recommendation']})")
    print(f"Wealth Score: {plan['wealth_multiplication_score']:.3f}")
    print(f"Active Strategies: {len(plan['ladder_strategies'])}")
    
    print("\n💰 ROI PROJECTIONS:")
    for month, roi in plan['roi_projections'].items():
        print(f"  {month.replace('_', ' ').title()}: +${roi:.2f}")
    
    print(f"\n🎯 TOTAL 4-MONTH PROJECTION: +${plan['roi_projections']['month_4']:.2f}")

if __name__ == "__main__":
    main()

