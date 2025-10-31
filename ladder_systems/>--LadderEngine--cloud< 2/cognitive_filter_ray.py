#!/usr/bin/env python3
"""
Cognitive Filter Ray Score Engine
================================

Author: Manus AI
Version: 1.0.0
Date: 2025-01-07
Classification: Production Trading System

Description:
Advanced cognitive filtering system using Ray Score methodology.
Provides multi-factor analysis for signal validation and cognitive rejection monitoring.

Security Level: MAXIMUM
Structure Lock: STRUCTURE_LOCK_0712_SIGMAΩ_FINALIZED
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class CognitiveFilterRay:
    """
    Advanced cognitive filtering system using Ray Score methodology
    Implements multi-factor analysis for signal validation
    """
    
    def __init__(self):
        self.score_history = []
        self.rejection_threshold = 60.0
        self.cognitive_exit_threshold = 40.0
        
        # Scoring weights (must sum to 100)
        self.weights = {
            'signal_quality': 20.0,      # Signal completeness and validity
            'risk_reward': 25.0,         # Risk/reward ratio analysis
            'market_conditions': 15.0,   # Market environment assessment
            'position_sizing': 15.0,     # Capital allocation appropriateness
            'long_term_alignment': 25.0  # Strategic alignment with goals
        }
        
        # Performance tracking
        self.metrics = {
            'total_analyses': 0,
            'approved_signals': 0,
            'rejected_signals': 0,
            'cognitive_exits': 0,
            'average_ray_score': 0.0
        }
    
    async def calculate_ray_score(self, signal: Dict[str, Any]) -> float:
        """
        Calculate Ray Score for a trading signal
        
        Args:
            signal: Trading signal with price and metadata
            
        Returns:
            Ray Score (0-100 scale)
        """
        try:
            # Component scores
            signal_quality_score = await self._assess_signal_quality(signal)
            risk_reward_score = await self._assess_risk_reward(signal)
            market_conditions_score = await self._assess_market_conditions(signal)
            position_sizing_score = await self._assess_position_sizing(signal)
            alignment_score = await self._assess_long_term_alignment(signal)
            
            # Weighted composite score
            ray_score = (
                signal_quality_score * (self.weights['signal_quality'] / 100) +
                risk_reward_score * (self.weights['risk_reward'] / 100) +
                market_conditions_score * (self.weights['market_conditions'] / 100) +
                position_sizing_score * (self.weights['position_sizing'] / 100) +
                alignment_score * (self.weights['long_term_alignment'] / 100)
            )
            
            # Ensure score is within bounds
            ray_score = max(0.0, min(100.0, ray_score))
            
            # Update metrics
            self.metrics['total_analyses'] += 1
            self.score_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'signal': signal.get('symbol', 'UNKNOWN'),
                'ray_score': ray_score,
                'components': {
                    'signal_quality': signal_quality_score,
                    'risk_reward': risk_reward_score,
                    'market_conditions': market_conditions_score,
                    'position_sizing': position_sizing_score,
                    'long_term_alignment': alignment_score
                }
            })
            
            # Update average
            total_score = sum(entry['ray_score'] for entry in self.score_history)
            self.metrics['average_ray_score'] = total_score / len(self.score_history)
            
            if ray_score >= self.rejection_threshold:
                self.metrics['approved_signals'] += 1
            else:
                self.metrics['rejected_signals'] += 1
            
            logger.info(f"🧠 Ray Score calculated: {ray_score:.1f} for {signal.get('symbol', 'UNKNOWN')}")
            return ray_score
            
        except Exception as e:
            logger.error(f"❌ Ray Score calculation failed: {e}")
            return 0.0
    
    async def analyze_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive signal analysis with detailed breakdown
        
        Args:
            signal: Trading signal to analyze
            
        Returns:
            Detailed analysis with Ray Score and component breakdown
        """
        try:
            ray_score = await self.calculate_ray_score(signal)
            
            # Determine validation action
            if ray_score >= self.rejection_threshold:
                validation_action = "APPROVED"
                validation_reason = f"Ray Score {ray_score:.1f} meets threshold {self.rejection_threshold}"
            else:
                validation_action = "REJECTED"
                validation_reason = f"Ray Score {ray_score:.1f} below threshold {self.rejection_threshold}"
            
            # Get latest component scores
            latest_analysis = self.score_history[-1] if self.score_history else {}
            
            return {
                'ray_score': ray_score,
                'validation': {
                    'action': validation_action,
                    'reason': validation_reason,
                    'threshold': self.rejection_threshold
                },
                'component_scores': latest_analysis.get('components', {}),
                'cognitive_exit_threshold': self.cognitive_exit_threshold,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Signal analysis failed: {e}")
            return {
                'ray_score': 0.0,
                'validation': {
                    'action': "ERROR",
                    'reason': f"Analysis failed: {e}",
                    'threshold': self.rejection_threshold
                },
                'error': str(e)
            }
    
    async def _assess_signal_quality(self, signal: Dict[str, Any]) -> float:
        """Assess signal quality and completeness (0-100 scale)"""
        try:
            score = 50.0  # Base score
            
            # Required fields check
            required_fields = ['symbol', 'action', 'entry_price', 'tp1_price', 'sl_price']
            present_fields = sum(1 for field in required_fields if field in signal and signal[field])
            field_completeness = (present_fields / len(required_fields)) * 30.0
            score += field_completeness
            
            # Signal metadata quality
            if signal.get('source'):
                score += 5.0
            if signal.get('priority', 0) > 5:
                score += 5.0
            if signal.get('confidence', 0) > 0.7:
                score += 10.0
            
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"❌ Signal quality assessment failed: {e}")
            return 0.0
    
    async def _assess_risk_reward(self, signal: Dict[str, Any]) -> float:
        """Assess risk/reward ratio (0-100 scale)"""
        try:
            entry = signal.get('entry_price', 0)
            tp1 = signal.get('tp1_price', 0)
            tp2 = signal.get('tp2_price', tp1)
            sl = signal.get('sl_price', 0)
            
            if not all([entry, tp1, sl]):
                return 0.0
            
            # Calculate risk and reward
            risk = abs(entry - sl)
            reward1 = abs(tp1 - entry)
            reward2 = abs(tp2 - entry) if tp2 else reward1
            avg_reward = (reward1 + reward2) / 2
            
            if risk <= 0:
                return 0.0
            
            rr_ratio = avg_reward / risk
            
            # Score based on risk/reward ratio
            if rr_ratio >= 4.0:
                return 100.0
            elif rr_ratio >= 3.0:
                return 90.0
            elif rr_ratio >= 2.5:
                return 80.0
            elif rr_ratio >= 2.0:
                return 70.0
            elif rr_ratio >= 1.5:
                return 60.0
            elif rr_ratio >= 1.0:
                return 40.0
            else:
                return 20.0
            
        except Exception as e:
            logger.error(f"❌ Risk/reward assessment failed: {e}")
            return 0.0
    
    async def _assess_market_conditions(self, signal: Dict[str, Any]) -> float:
        """Assess market conditions (0-100 scale)"""
        try:
            score = 60.0  # Base score for neutral conditions
            
            # Symbol-based market assessment
            symbol = signal.get('symbol', '').upper()
            
            # Major pairs get higher base score
            if any(major in symbol for major in ['BTC', 'ETH']):
                score += 15.0
            elif any(alt in symbol for alt in ['ADA', 'ATOM', 'INJ', 'RNDR']):
                score += 10.0
            elif any(meme in symbol for meme in ['BONK', 'WIF', 'DOGE']):
                score += 5.0  # Higher volatility, moderate score
            
            # Time-based factors (simplified)
            current_hour = datetime.utcnow().hour
            
            # Favor trading during active market hours
            if 8 <= current_hour <= 20:  # Active hours
                score += 10.0
            elif 21 <= current_hour <= 23 or 6 <= current_hour <= 7:  # Moderate hours
                score += 5.0
            # Overnight hours get no bonus
            
            # Volatility assessment (simplified)
            entry = signal.get('entry_price', 0)
            tp1 = signal.get('tp1_price', 0)
            
            if entry and tp1:
                price_move_pct = abs(tp1 - entry) / entry * 100
                
                # Optimal price moves get higher scores
                if 5.0 <= price_move_pct <= 25.0:
                    score += 15.0
                elif 2.0 <= price_move_pct < 5.0 or 25.0 < price_move_pct <= 40.0:
                    score += 10.0
                elif price_move_pct > 40.0:
                    score -= 10.0  # Too volatile
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Market conditions assessment failed: {e}")
            return 50.0  # Neutral score on error
    
    async def _assess_position_sizing(self, signal: Dict[str, Any]) -> float:
        """Assess position sizing appropriateness (0-100 scale)"""
        try:
            capital = signal.get('capital', 0)
            entry_price = signal.get('entry_price', 0)
            
            if not capital or not entry_price:
                return 50.0  # Neutral if no sizing info
            
            # Assume $10,000 account for percentage calculations
            account_size = 10000.0
            position_pct = (capital / account_size) * 100
            
            # Optimal position sizing: 2-5% of account
            if 2.0 <= position_pct <= 5.0:
                return 100.0
            elif 1.0 <= position_pct < 2.0 or 5.0 < position_pct <= 8.0:
                return 80.0
            elif 0.5 <= position_pct < 1.0 or 8.0 < position_pct <= 12.0:
                return 60.0
            elif position_pct < 0.5:
                return 40.0  # Too small
            else:
                return 20.0  # Too large
            
        except Exception as e:
            logger.error(f"❌ Position sizing assessment failed: {e}")
            return 50.0
    
    async def _assess_long_term_alignment(self, signal: Dict[str, Any]) -> float:
        """Assess alignment with long-term strategy (0-100 scale)"""
        try:
            symbol = signal.get('symbol', '').upper()
            action = signal.get('action', '').lower()
            
            score = 50.0  # Base score
            
            # SLEEP tier assets (long-term holds)
            sleep_assets = ['ADA', 'KAVA', 'INJ', 'COTI', 'ALGO', 'XTZ', 'ATOM', 'FLOW', 'NEAR']
            
            # FLIP tier assets (active trading)
            flip_assets = ['BTC', 'ETH', 'BONK', 'WIF', 'RNDR', 'STMX']
            
            if any(asset in symbol for asset in sleep_assets):
                # SLEEP assets: favor buy and hold strategies
                if action == 'buy':
                    score += 25.0
                else:
                    score += 10.0  # Selling SLEEP assets is less aligned
            elif any(asset in symbol for asset in flip_assets):
                # FLIP assets: favor active trading
                score += 20.0
            else:
                # Unknown assets: moderate score
                score += 10.0
            
            # Strategy alignment based on signal characteristics
            entry = signal.get('entry_price', 0)
            tp1 = signal.get('tp1_price', 0)
            
            if entry and tp1:
                # Calculate expected return
                expected_return = ((tp1 - entry) / entry) * 100
                
                # Favor reasonable returns (10-50%)
                if 10.0 <= expected_return <= 50.0:
                    score += 15.0
                elif 5.0 <= expected_return < 10.0 or 50.0 < expected_return <= 100.0:
                    score += 10.0
                elif expected_return > 100.0:
                    score -= 10.0  # Unrealistic expectations
            
            # Time horizon alignment
            signal_type = signal.get('type', '').lower()
            if signal_type in ['swing', 'position']:
                score += 10.0  # Aligned with longer-term approach
            elif signal_type in ['scalp', 'day']:
                score += 5.0   # Moderate alignment
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Long-term alignment assessment failed: {e}")
            return 50.0
    
    async def is_operational(self) -> bool:
        """Check if cognitive filter is operational"""
        try:
            # Test with a simple signal
            test_signal = {
                'symbol': 'BTCUSDT',
                'action': 'buy',
                'entry_price': 45000.0,
                'tp1_price': 50000.0,
                'sl_price': 42000.0
            }
            
            ray_score = await self.calculate_ray_score(test_signal)
            return 0 <= ray_score <= 100
            
        except Exception as e:
            logger.error(f"❌ Cognitive filter operational check failed: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get cognitive filter system status"""
        try:
            return {
                'operational': await self.is_operational(),
                'metrics': self.metrics,
                'thresholds': {
                    'rejection_threshold': self.rejection_threshold,
                    'cognitive_exit_threshold': self.cognitive_exit_threshold
                },
                'recent_scores': self.score_history[-10:] if self.score_history else [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {
                'operational': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def save_analysis_history(self, filename: str = 'ray_score_history.json') -> None:
        """Save analysis history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'metrics': self.metrics,
                    'score_history': self.score_history,
                    'weights': self.weights,
                    'thresholds': {
                        'rejection_threshold': self.rejection_threshold,
                        'cognitive_exit_threshold': self.cognitive_exit_threshold
                    },
                    'saved_at': datetime.utcnow().isoformat()
                }, f, indent=2, default=str)
            
            logger.info(f"✅ Ray Score history saved to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis history: {e}")

# Utility functions for external use
async def validate_signal_ray_score(signal: Dict[str, Any], threshold: float = 60.0) -> bool:
    """
    Quick validation function for external use
    
    Args:
        signal: Trading signal to validate
        threshold: Minimum Ray Score threshold
        
    Returns:
        True if signal meets Ray Score threshold
    """
    try:
        cognitive_filter = CognitiveFilterRay()
        ray_score = await cognitive_filter.calculate_ray_score(signal)
        return ray_score >= threshold
        
    except Exception as e:
        logger.error(f"❌ Ray Score validation failed: {e}")
        return False

def get_ray_score_breakdown(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed Ray Score breakdown for analysis
    
    Args:
        signal: Trading signal to analyze
        
    Returns:
        Detailed breakdown of Ray Score components
    """
    try:
        cognitive_filter = CognitiveFilterRay()
        return asyncio.run(cognitive_filter.analyze_signal(signal))
        
    except Exception as e:
        logger.error(f"❌ Ray Score breakdown failed: {e}")
        return {
            'ray_score': 0.0,
            'error': str(e)
        }

