import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class RayScoreComponents:
    """Ray Score component breakdown"""
    signal_quality: float = 0.0
    risk_reward_ratio: float = 0.0
    market_conditions: float = 0.0
    position_sizing: float = 0.0
    long_term_alignment: float = 0.0
    volatility_score: float = 0.0
    volume_score: float = 0.0
    trend_score: float = 0.0
    total_score: float = 0.0

@dataclass
class MarketIndicators:
    """Market technical indicators for Ray Score calculation"""
    rsi: Optional[float] = None
    bollinger_width: Optional[float] = None
    volume_ratio: Optional[float] = None
    trend_velocity: Optional[float] = None
    volatility: Optional[float] = None
    price_momentum: Optional[float] = None

class RayScoreEngine:
    """
    Advanced Ray Score calculation engine using multi-factor analysis
    Incorporates technical indicators, risk metrics, and cognitive alignment
    """
    
    def __init__(self):
        # Ray Rules weights (total = 100)
        self.weights = {
            'signal_quality': 20.0,        # Complete signal data, TP/SL levels
            'risk_reward_ratio': 25.0,     # Risk/reward analysis
            'market_conditions': 15.0,     # Technical indicators
            'position_sizing': 15.0,       # Appropriate sizing
            'long_term_alignment': 25.0    # "No regret in 10 years" test
        }
        
        # Technical indicator weights for market conditions
        self.technical_weights = {
            'volatility': 0.25,
            'trend_velocity': 0.25,
            'volume_burst': 0.20,
            'bollinger_width': 0.15,
            'rsi_divergence': 0.15
        }
        
        # Minimum thresholds
        self.min_ray_score = 60.0  # Mental stop loss threshold
        self.exit_threshold = 40.0  # Force exit threshold
        
        # Market data cache for technical analysis
        self.market_cache = {}
        
    def calculate_ray_score(self, signal_data: Dict[str, Any], 
                           market_data: Optional[Dict[str, Any]] = None) -> RayScoreComponents:
        """
        Calculate comprehensive Ray Score for a trading signal
        
        Args:
            signal_data: Trading signal information
            market_data: Optional market data for technical analysis
            
        Returns:
            RayScoreComponents with detailed breakdown
        """
        try:
            components = RayScoreComponents()
            
            # 1. Signal Quality Score (20%)
            components.signal_quality = self._calculate_signal_quality(signal_data)
            
            # 2. Risk/Reward Ratio Score (25%)
            components.risk_reward_ratio = self._calculate_risk_reward_score(signal_data)
            
            # 3. Market Conditions Score (15%)
            components.market_conditions = self._calculate_market_conditions_score(
                signal_data, market_data
            )
            
            # 4. Position Sizing Score (15%)
            components.position_sizing = self._calculate_position_sizing_score(signal_data)
            
            # 5. Long-term Alignment Score (25%)
            components.long_term_alignment = self._calculate_long_term_alignment_score(signal_data)
            
            # Calculate weighted total
            components.total_score = (
                components.signal_quality * self.weights['signal_quality'] / 100 +
                components.risk_reward_ratio * self.weights['risk_reward_ratio'] / 100 +
                components.market_conditions * self.weights['market_conditions'] / 100 +
                components.position_sizing * self.weights['position_sizing'] / 100 +
                components.long_term_alignment * self.weights['long_term_alignment'] / 100
            )
            
            # Ensure score is within bounds
            components.total_score = max(0.0, min(100.0, components.total_score))
            
            logger.info(f"Ray Score calculated: {components.total_score:.1f} for {signal_data.get('symbol', 'Unknown')}")
            
            return components
            
        except Exception as e:
            logger.error(f"Ray Score calculation failed: {e}")
            return RayScoreComponents()
    
    def _calculate_signal_quality(self, signal_data: Dict[str, Any]) -> float:
        """Calculate signal quality score (0-100)"""
        score = 0.0
        
        # Base score for having required fields
        required_fields = ['symbol', 'action', 'entry_price', 'quantity']
        for field in required_fields:
            if signal_data.get(field):
                score += 15.0
        
        # Bonus for TP levels
        if signal_data.get('tp1_price'):
            score += 10.0
        if signal_data.get('tp2_price'):
            score += 10.0
        
        # Bonus for stop loss
        if signal_data.get('sl_price'):
            score += 15.0
        
        # Bonus for priority level
        priority = signal_data.get('priority', 5)
        if priority >= 7:
            score += 10.0
        elif priority >= 5:
            score += 5.0
        
        # Bonus for source reliability
        source = signal_data.get('source', '').lower()
        if source in ['tradingview', 'premium', 'verified']:
            score += 5.0
        
        return min(100.0, score)
    
    def _calculate_risk_reward_score(self, signal_data: Dict[str, Any]) -> float:
        """Calculate risk/reward ratio score (0-100)"""
        try:
            entry_price = float(signal_data.get('entry_price', 0))
            tp1_price = signal_data.get('tp1_price')
            tp2_price = signal_data.get('tp2_price')
            sl_price = signal_data.get('sl_price')
            
            if not all([entry_price, tp1_price, sl_price]):
                return 30.0  # Base score for incomplete data
            
            tp1_price = float(tp1_price)
            sl_price = float(sl_price)
            
            # Calculate risk and reward
            action = signal_data.get('action', 'buy').lower()
            
            if action == 'buy':
                risk = entry_price - sl_price
                reward_tp1 = tp1_price - entry_price
                reward_tp2 = float(tp2_price) - entry_price if tp2_price else reward_tp1
            else:  # sell/short
                risk = sl_price - entry_price
                reward_tp1 = entry_price - tp1_price
                reward_tp2 = entry_price - float(tp2_price) if tp2_price else reward_tp1
            
            if risk <= 0:
                return 0.0  # Invalid risk setup
            
            # Calculate risk/reward ratios
            rr_tp1 = reward_tp1 / risk
            rr_tp2 = reward_tp2 / risk if tp2_price else rr_tp1
            
            # Score based on risk/reward ratio
            avg_rr = (rr_tp1 + rr_tp2) / 2
            
            if avg_rr >= 3.0:
                score = 100.0
            elif avg_rr >= 2.5:
                score = 90.0
            elif avg_rr >= 2.0:
                score = 80.0
            elif avg_rr >= 1.5:
                score = 70.0
            elif avg_rr >= 1.0:
                score = 50.0
            else:
                score = 20.0
            
            # Bonus for having TP2
            if tp2_price:
                score += 10.0
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Risk/reward calculation failed: {e}")
            return 30.0
    
    def _calculate_market_conditions_score(self, signal_data: Dict[str, Any], 
                                         market_data: Optional[Dict[str, Any]]) -> float:
        """Calculate market conditions score using technical indicators"""
        if not market_data:
            return 50.0  # Neutral score without market data
        
        try:
            indicators = self._extract_market_indicators(market_data)
            score = 0.0
            
            # Volatility score (0-25 points)
            if indicators.volatility is not None:
                vol_score = self._score_volatility(indicators.volatility)
                score += vol_score * self.technical_weights['volatility']
            
            # Trend velocity score (0-25 points)
            if indicators.trend_velocity is not None:
                trend_score = self._score_trend_velocity(indicators.trend_velocity)
                score += trend_score * self.technical_weights['trend_velocity']
            
            # Volume burst score (0-20 points)
            if indicators.volume_ratio is not None:
                volume_score = self._score_volume_burst(indicators.volume_ratio)
                score += volume_score * self.technical_weights['volume_burst']
            
            # Bollinger width score (0-15 points)
            if indicators.bollinger_width is not None:
                bb_score = self._score_bollinger_width(indicators.bollinger_width)
                score += bb_score * self.technical_weights['bollinger_width']
            
            # RSI divergence score (0-15 points)
            if indicators.rsi is not None:
                rsi_score = self._score_rsi_divergence(indicators.rsi)
                score += rsi_score * self.technical_weights['rsi_divergence']
            
            return min(100.0, score * 100)  # Convert to 0-100 scale
            
        except Exception as e:
            logger.error(f"Market conditions calculation failed: {e}")
            return 50.0
    
    def _extract_market_indicators(self, market_data: Dict[str, Any]) -> MarketIndicators:
        """Extract technical indicators from market data"""
        return MarketIndicators(
            rsi=market_data.get('rsi'),
            bollinger_width=market_data.get('bollinger_width'),
            volume_ratio=market_data.get('volume_ratio'),
            trend_velocity=market_data.get('trend_velocity'),
            volatility=market_data.get('volatility'),
            price_momentum=market_data.get('price_momentum')
        )
    
    def _score_volatility(self, volatility: float) -> float:
        """Score volatility (optimal range: 2-8%)"""
        if 0.02 <= volatility <= 0.08:  # 2-8% is optimal
            return 1.0
        elif 0.01 <= volatility <= 0.12:  # 1-12% is acceptable
            return 0.7
        else:
            return 0.3  # Too low or too high volatility
    
    def _score_trend_velocity(self, velocity: float) -> float:
        """Score trend velocity (higher is better for momentum)"""
        abs_velocity = abs(velocity)
        if abs_velocity >= 0.05:  # Strong trend
            return 1.0
        elif abs_velocity >= 0.02:  # Moderate trend
            return 0.7
        else:  # Weak trend
            return 0.4
    
    def _score_volume_burst(self, volume_ratio: float) -> float:
        """Score volume burst (volume vs average)"""
        if volume_ratio >= 2.0:  # 2x average volume
            return 1.0
        elif volume_ratio >= 1.5:  # 1.5x average volume
            return 0.8
        elif volume_ratio >= 1.2:  # 1.2x average volume
            return 0.6
        else:
            return 0.3
    
    def _score_bollinger_width(self, bb_width: float) -> float:
        """Score Bollinger Band width (expansion indicates volatility)"""
        if bb_width >= 0.08:  # Wide bands (high volatility)
            return 0.8
        elif bb_width >= 0.04:  # Medium bands
            return 1.0
        else:  # Narrow bands (low volatility)
            return 0.5
    
    def _score_rsi_divergence(self, rsi: float) -> float:
        """Score RSI for overbought/oversold conditions"""
        if 30 <= rsi <= 70:  # Neutral zone
            return 1.0
        elif 20 <= rsi <= 80:  # Acceptable range
            return 0.7
        else:  # Extreme overbought/oversold
            return 0.3
    
    def _calculate_position_sizing_score(self, signal_data: Dict[str, Any]) -> float:
        """Calculate position sizing appropriateness score"""
        try:
            entry_price = float(signal_data.get('entry_price', 0))
            quantity = float(signal_data.get('quantity', 0))
            
            if not entry_price or not quantity:
                return 30.0
            
            position_value = entry_price * quantity
            
            # Score based on position size (assuming $10k account)
            account_size = 10000.0  # Default account size
            position_percentage = position_value / account_size
            
            if 0.01 <= position_percentage <= 0.05:  # 1-5% of account
                score = 100.0
            elif 0.005 <= position_percentage <= 0.10:  # 0.5-10% of account
                score = 80.0
            elif position_percentage <= 0.15:  # Up to 15%
                score = 60.0
            elif position_percentage <= 0.20:  # Up to 20%
                score = 40.0
            else:  # Too large
                score = 20.0
            
            # Bonus for reasonable absolute position size
            if 50 <= position_value <= 1000:  # $50-$1000 position
                score += 10.0
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Position sizing calculation failed: {e}")
            return 50.0
    
    def _calculate_long_term_alignment_score(self, signal_data: Dict[str, Any]) -> float:
        """Calculate long-term alignment score (Rule 5: No regret in 10 years)"""
        try:
            score = 50.0  # Base score
            
            # Asset quality assessment
            symbol = signal_data.get('symbol', '').upper()
            
            # Blue chip cryptos get higher scores
            if any(asset in symbol for asset in ['BTC', 'ETH']):
                score += 30.0
            elif any(asset in symbol for asset in ['ADA', 'ATOM', 'INJ', 'ALGO']):
                score += 20.0  # SLEEP tier assets
            elif any(asset in symbol for asset in ['SOL', 'AVAX', 'MATIC']):
                score += 15.0  # Established alts
            else:
                score += 5.0   # Other assets
            
            # Strategy alignment
            action = signal_data.get('action', 'buy').lower()
            if action == 'buy':  # Long-term bias towards buying quality assets
                score += 10.0
            
            # Time horizon consideration
            tp1_price = signal_data.get('tp1_price')
            tp2_price = signal_data.get('tp2_price')
            entry_price = signal_data.get('entry_price')
            
            if all([tp1_price, tp2_price, entry_price]):
                # Conservative targets get higher scores
                tp1_gain = abs(float(tp1_price) - float(entry_price)) / float(entry_price)
                tp2_gain = abs(float(tp2_price) - float(entry_price)) / float(entry_price)
                
                avg_gain = (tp1_gain + tp2_gain) / 2
                
                if 0.10 <= avg_gain <= 0.50:  # 10-50% targets (reasonable)
                    score += 10.0
                elif avg_gain <= 0.10:  # Conservative targets
                    score += 5.0
                else:  # Aggressive targets
                    score -= 5.0
            
            # Vault siphon alignment
            if signal_data.get('vault_siphon_enabled'):
                score += 5.0
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Long-term alignment calculation failed: {e}")
            return 50.0
    
    def validate_ray_score(self, ray_score: float, phase: str = 'entry') -> Dict[str, Any]:
        """
        Validate Ray Score against thresholds
        
        Args:
            ray_score: Calculated Ray Score
            phase: 'entry' or 'monitoring'
            
        Returns:
            Validation result with action recommendation
        """
        if phase == 'entry':
            if ray_score >= self.min_ray_score:
                return {
                    'valid': True,
                    'action': 'proceed',
                    'message': f'Ray Score {ray_score:.1f} meets entry threshold {self.min_ray_score}'
                }
            else:
                return {
                    'valid': False,
                    'action': 'reject',
                    'message': f'Ray Score {ray_score:.1f} below entry threshold {self.min_ray_score}'
                }
        
        elif phase == 'monitoring':
            if ray_score < self.exit_threshold:
                return {
                    'valid': False,
                    'action': 'force_exit',
                    'message': f'Ray Score {ray_score:.1f} below exit threshold {self.exit_threshold}'
                }
            elif ray_score < self.min_ray_score:
                return {
                    'valid': True,
                    'action': 'monitor_closely',
                    'message': f'Ray Score {ray_score:.1f} in warning zone'
                }
            else:
                return {
                    'valid': True,
                    'action': 'continue',
                    'message': f'Ray Score {ray_score:.1f} healthy'
                }
    
    def get_ray_score(self, signal_data: Dict[str, Any], 
                     market_data: Optional[Dict[str, Any]] = None) -> float:
        """
        Main interface function for Ray Score calculation
        
        Args:
            signal_data: Trading signal information
            market_data: Optional market data
            
        Returns:
            Ray Score (0-100)
        """
        components = self.calculate_ray_score(signal_data, market_data)
        return components.total_score
    
    def get_detailed_ray_analysis(self, signal_data: Dict[str, Any], 
                                 market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get detailed Ray Score analysis with component breakdown"""
        components = self.calculate_ray_score(signal_data, market_data)
        validation = self.validate_ray_score(components.total_score, 'entry')
        
        return {
            'ray_score': components.total_score,
            'components': {
                'signal_quality': components.signal_quality,
                'risk_reward_ratio': components.risk_reward_ratio,
                'market_conditions': components.market_conditions,
                'position_sizing': components.position_sizing,
                'long_term_alignment': components.long_term_alignment
            },
            'validation': validation,
            'weights': self.weights,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global Ray Score engine instance
ray_score_engine = RayScoreEngine()

def validate_roi(entry_prices: List[float], tp1: float, tp2: float, sl: float, fees: float = 0.002) -> Dict[str, Any]:
    """
    Validate ROI spread according to ΣIGMA-ΩSNIPER requirements
    
    Args:
        entry_prices: List of entry prices for ladder
        tp1: Take profit 1 price
        tp2: Take profit 2 price
        sl: Stop loss price
        fees: Trading fees (default 0.2%)
        
    Returns:
        ROI validation result
    """
    try:
        avg_entry = sum(entry_prices) / len(entry_prices)
        
        # Calculate ROI percentages
        tp1_roi = ((tp1 - avg_entry) / avg_entry) - fees
        tp2_roi = ((tp2 - avg_entry) / avg_entry) - fees
        drawdown = (avg_entry - sl) / avg_entry
        
        # Validate against requirements
        tp1_valid = tp1_roi >= 0.20  # TP1 ≥ 20%
        tp2_valid = tp2_roi >= 0.30  # TP2 ≥ 30%
        drawdown_valid = drawdown <= 0.07  # Max drawdown ≤ 7%
        
        return {
            "tp1_roi": round(tp1_roi * 100, 2),
            "tp2_roi": round(tp2_roi * 100, 2),
            "drawdown": round(drawdown * 100, 2),
            "valid": tp1_valid and tp2_valid and drawdown_valid,
            "requirements_met": {
                "tp1_20_percent": tp1_valid,
                "tp2_30_percent": tp2_valid,
                "max_drawdown_7_percent": drawdown_valid
            },
            "avg_entry": avg_entry,
            "fees_included": fees * 100
        }
        
    except Exception as e:
        logger.error(f"ROI validation failed: {e}")
        return {
            "error": str(e),
            "valid": False
        }

