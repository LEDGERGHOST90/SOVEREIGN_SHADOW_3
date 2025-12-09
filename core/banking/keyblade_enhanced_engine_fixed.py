#!/usr/bin/env python3
"""
🔥 KEYBLADE ENHANCED TACTICAL ENGINE - ROI EXECUTION MODE (FIXED)
Advanced tactical intelligence with KeybladeAI fortress protocols
Optimized for $1000+ quarterly ROI with autonomous wealth multiplication
"""

import json
import sqlite3
import logging
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KeybladeFlipRecommendation:
    """Enhanced flip recommendation with KeybladeAI logic"""
    symbol: str
    action: str
    entry_price: float
    tp1_price: float
    tp2_price: float
    tp3_price: float
    stop_loss_price: float
    expected_roi: float
    confidence_score: float
    ray_score: float
    priority: str
    reasoning: str

@dataclass
class KeybladeWhaleSignal:
    """Enhanced whale signal with MENACE integration"""
    symbol: str
    whale_activity_type: str
    signal_strength: float
    menace_score: float
    accumulation_pattern: str
    risk_level: str
    recommended_action: str

@dataclass
class KeybladeVaultAlert:
    """Enhanced vault alert with aging analysis"""
    symbol: str
    aging_status: str
    current_roi: float
    days_in_vault: int
    suggested_action: str
    reallocation_urgency: float

@dataclass
class KeybladeTileHeat:
    """Enhanced tile heatmap with correlation analysis"""
    symbol: str
    heat_score: float
    urgency_level: str
    correlation_risk: float
    sector_exposure: str

class KeybladeEnhancedEngineFixed:
    """
    🔥 KEYBLADE ENHANCED TACTICAL ENGINE (FIXED VERSION)
    Advanced tactical intelligence with fortress-class protection
    """
    
    def __init__(self, llf_beta_path: str = "/home/ubuntu/LLF-Beta"):
        self.llf_beta_path = Path(llf_beta_path)
        self.keyblade_path = self.llf_beta_path / "keyblade_ai_integration"
        
        # Load KeybladeAI configurations
        self._load_keyblade_configs()
        
        # ROI optimization parameters
        self.roi_targets = {
            'daily_minimum': 0.005,     # 0.5% daily minimum
            'weekly_target': 0.035,     # 3.5% weekly target
            'monthly_target': 0.15,     # 15% monthly target
            'quarterly_target': 0.50    # 50% quarterly target ($1000+ ROI)
        }
        
        # Enhanced risk management
        self.fortress_limits = {
            'max_position_size': 0.15,      # 15% max per position
            'max_daily_risk': 0.02,         # 2% max daily risk
            'correlation_threshold': 0.7,    # 70% correlation limit
            'ray_rules_minimum': 60.0,      # Minimum Ray Score (float)
            'confidence_threshold': 0.80,   # 80% minimum confidence
            'emergency_halt_signal': '🔴'   # Emergency halt trigger
        }
        
        logger.info("🔥 KeybladeAI Enhanced Tactical Engine (Fixed) initialized")
    
    def _load_keyblade_configs(self):
        """Load KeybladeAI configuration files"""
        
        try:
            # Load flip template
            template_path = self.keyblade_path / "Commander_30-50%_Flip_Template.json"
            if template_path.exists():
                with open(template_path, 'r') as f:
                    self.keyblade_template = json.load(f)
                logger.info("✅ KeybladeAI flip template loaded")
            else:
                logger.warning("⚠️ KeybladeAI flip template not found - using defaults")
                self.keyblade_template = {}
            
            # Load correlation matrix
            matrix_path = self.keyblade_path / "omega_correlation_matrix.json"
            if matrix_path.exists():
                with open(matrix_path, 'r') as f:
                    self.keyblade_matrix = json.load(f)
                logger.info("✅ KeybladeAI correlation matrix loaded")
            else:
                logger.warning("⚠️ KeybladeAI correlation matrix not found - using defaults")
                self.keyblade_matrix = {}
            
        except Exception as e:
            logger.error(f"Error loading KeybladeAI configs: {e}")
            self.keyblade_template = {}
            self.keyblade_matrix = {}
    
    def generate_keyblade_flip_recommendations(self, market_data: Dict, 
                                             vaultlog_intelligence: Dict) -> List[KeybladeFlipRecommendation]:
        """Generate enhanced flip recommendations with KeybladeAI logic"""
        
        recommendations = []
        
        # Analyze each asset with KeybladeAI enhancement
        for symbol, data in market_data.items():
            try:
                # KeybladeAI risk assessment
                risk_assessment = self._keyblade_risk_analysis(symbol, data)
                
                # Skip if risk too high
                if risk_assessment.get('risk_level') == 'CRITICAL':
                    continue
                
                # Calculate enhanced pricing
                pricing = self._calculate_keyblade_pricing(symbol, data)
                
                # KeybladeAI signal analysis
                keyblade_signals = self._analyze_keyblade_signals(symbol, data, risk_assessment)
                
                # Generate recommendation
                recommendation = KeybladeFlipRecommendation(
                    symbol=symbol,
                    action=self._determine_action(keyblade_signals),
                    entry_price=pricing['entry_price'],
                    tp1_price=pricing['tp1_price'],
                    tp2_price=pricing['tp2_price'],
                    tp3_price=pricing['tp3_price'],
                    stop_loss_price=pricing['stop_loss_price'],
                    expected_roi=pricing['expected_roi'],
                    confidence_score=keyblade_signals['confidence_score'],
                    ray_score=keyblade_signals['ray_score'],
                    priority=risk_assessment['priority'],
                    reasoning=keyblade_signals['reasoning']
                )
                
                # Only add high-quality recommendations
                if (recommendation.confidence_score >= self.fortress_limits['confidence_threshold'] and
                    recommendation.ray_score >= self.fortress_limits['ray_rules_minimum']):
                    recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error generating recommendation for {symbol}: {e}")
                continue
        
        # Sort by expected ROI and confidence
        recommendations.sort(key=lambda x: (x.expected_roi * x.confidence_score), reverse=True)
        
        logger.info(f"🎯 Generated {len(recommendations)} KeybladeAI flip recommendations")
        return recommendations[:6]  # Top 6 recommendations
    
    def _keyblade_risk_analysis(self, symbol: str, data: Dict) -> Dict:
        """Perform KeybladeAI risk analysis"""
        
        # Base risk factors
        volatility_risk = min(data.get('volatility', 0.5), 1.0)
        volume_risk = 1.0 - min(data.get('volume_ratio', 0.5), 1.0)
        
        # Composite risk score
        composite_risk = (volatility_risk + volume_risk) / 2.0
        
        # Determine risk level
        if composite_risk > 0.8:
            risk_level = 'CRITICAL'
            priority = 'AVOID'
        elif composite_risk > 0.6:
            risk_level = 'HIGH'
            priority = 'LOW'
        elif composite_risk > 0.4:
            risk_level = 'MEDIUM'
            priority = 'MEDIUM'
        else:
            risk_level = 'LOW'
            priority = 'HIGH'
        
        return {
            'risk_level': risk_level,
            'priority': priority,
            'composite_risk': composite_risk
        }
    
    def _calculate_keyblade_pricing(self, symbol: str, data: Dict) -> Dict:
        """Calculate KeybladeAI enhanced pricing"""
        
        current_price = data.get('current_price', 100.0)
        
        # Entry price (slightly below current for better entry)
        entry_price = current_price * 0.98
        
        # Target prices based on KeybladeAI template
        tp1_price = entry_price * 1.15  # 15% gain
        tp2_price = entry_price * 1.30  # 30% gain
        tp3_price = entry_price * 1.45  # 45% gain
        
        # Stop loss
        stop_loss_price = entry_price * 0.92  # 8% stop loss
        
        # Expected ROI calculation
        expected_roi = (tp2_price - entry_price) / entry_price
        
        return {
            'entry_price': entry_price,
            'tp1_price': tp1_price,
            'tp2_price': tp2_price,
            'tp3_price': tp3_price,
            'stop_loss_price': stop_loss_price,
            'expected_roi': expected_roi
        }
    
    def _analyze_keyblade_signals(self, symbol: str, data: Dict, risk_assessment: Dict) -> Dict:
        """Analyze KeybladeAI signals"""
        
        # Base signal strength
        price_momentum = abs(data.get('price_change_24h', 0.0))
        volume_strength = min(data.get('volume_ratio', 1.0), 2.0) / 2.0
        
        # Technical confluence
        technical_confluence = self._calculate_technical_confluence(symbol, data)
        
        # Ray Score calculation (KeybladeAI clarity metric)
        ray_score = (technical_confluence * 40.0 + 
                    volume_strength * 30.0 + 
                    price_momentum * 100.0 * 20.0 + 
                    (1.0 - risk_assessment['composite_risk']) * 10.0)
        
        # Confidence score
        confidence_score = (technical_confluence + volume_strength) / 2.0
        
        # Reasoning
        reasoning = self._generate_reasoning(symbol, data, risk_assessment, ray_score, confidence_score)
        
        return {
            'ray_score': ray_score,
            'confidence_score': confidence_score,
            'technical_confluence': technical_confluence,
            'volume_strength': volume_strength,
            'reasoning': reasoning
        }
    
    def _calculate_technical_confluence(self, symbol: str, data: Dict) -> float:
        """Calculate technical confluence score"""
        
        # Simulate technical indicators
        volume_ratio = data.get('volume_ratio', 1.0)
        price_change = data.get('price_change_24h', 0.0)
        
        confluence_score = 0.0
        
        # Volume confluence
        if volume_ratio > 1.2:  # Above average volume
            confluence_score += 0.5
        
        # Price momentum confluence
        if abs(price_change) > 0.03:  # Significant movement
            confluence_score += 0.3
        
        # Volatility confluence
        volatility = data.get('volatility', 0.1)
        if 0.1 <= volatility <= 0.3:  # Healthy volatility range
            confluence_score += 0.2
        
        return min(confluence_score, 1.0)
    
    def _generate_reasoning(self, symbol: str, data: Dict, risk_assessment: Dict, 
                          ray_score: float, confidence_score: float) -> str:
        """Generate KeybladeAI reasoning"""
        
        reasoning_parts = []
        
        # Ray Score assessment
        if ray_score >= 80.0:
            reasoning_parts.append(f"High Ray Score ({ray_score:.1f}) indicates strong clarity")
        elif ray_score >= 60.0:
            reasoning_parts.append(f"Moderate Ray Score ({ray_score:.1f}) suggests caution")
        else:
            reasoning_parts.append(f"Low Ray Score ({ray_score:.1f}) - avoid trade")
        
        # Risk assessment
        risk_level = risk_assessment['risk_level']
        if risk_level == 'LOW':
            reasoning_parts.append("Low risk profile with fortress protection")
        elif risk_level == 'MEDIUM':
            reasoning_parts.append("Medium risk - enhanced monitoring required")
        else:
            reasoning_parts.append("High risk - consider avoiding")
        
        # Market conditions
        price_change = data.get('price_change_24h', 0.0)
        if price_change > 0.05:
            reasoning_parts.append("Strong upward momentum detected")
        elif price_change < -0.05:
            reasoning_parts.append("Downward pressure - wait for reversal")
        
        return ". ".join(reasoning_parts)
    
    def _determine_action(self, keyblade_signals: Dict) -> str:
        """Determine recommended action based on KeybladeAI signals"""
        
        ray_score = keyblade_signals['ray_score']
        confidence_score = keyblade_signals['confidence_score']
        
        if ray_score >= 80.0 and confidence_score >= 0.8:
            return "STRONG_BUY"
        elif ray_score >= 70.0 and confidence_score >= 0.7:
            return "BUY"
        elif ray_score >= 60.0 and confidence_score >= 0.6:
            return "MODERATE_BUY"
        else:
            return "MONITOR"
    
    def generate_keyblade_whale_signals(self, market_data: Dict) -> List[KeybladeWhaleSignal]:
        """Generate enhanced whale signals with KeybladeAI MENACE integration"""
        
        whale_signals = []
        
        for symbol, data in market_data.items():
            try:
                # MENACE score calculation
                menace_score = self._calculate_menace_score(symbol, data)
                
                # Whale activity analysis
                whale_activity = self._analyze_whale_activity(symbol, data, menace_score)
                
                whale_signal = KeybladeWhaleSignal(
                    symbol=symbol,
                    whale_activity_type=whale_activity['activity_type'],
                    signal_strength=whale_activity['signal_strength'],
                    menace_score=menace_score,
                    accumulation_pattern=whale_activity['pattern'],
                    risk_level=whale_activity['risk_level'],
                    recommended_action=whale_activity['recommended_action']
                )
                
                whale_signals.append(whale_signal)
                
            except Exception as e:
                logger.error(f"Error generating whale signal for {symbol}: {e}")
                continue
        
        # Sort by MENACE score and signal strength
        whale_signals.sort(key=lambda x: (x.menace_score * x.signal_strength), reverse=True)
        
        logger.info(f"🐋 Generated {len(whale_signals)} KeybladeAI whale signals")
        return whale_signals[:6]  # Top 6 signals
    
    def _calculate_menace_score(self, symbol: str, data: Dict) -> float:
        """Calculate MENACE (Market ENhanced ACcumulation Engine) score"""
        
        # Volume analysis
        volume_ratio = data.get('volume_ratio', 1.0)
        volume_score = min(volume_ratio / 2.0, 1.0)  # Normalize to 0-1
        
        # Price stability during accumulation
        volatility = data.get('volatility', 0.5)
        stability_score = 1.0 - min(volatility, 1.0)
        
        # Market cap considerations
        market_cap = data.get('market_cap', 100000000)
        cap_score = 0.8 if market_cap > 1000000000 else 0.6  # Large cap bonus
        
        # Composite MENACE score
        menace_score = (volume_score * 0.4 + stability_score * 0.3 + cap_score * 0.3)
        
        return menace_score
    
    def _analyze_whale_activity(self, symbol: str, data: Dict, menace_score: float) -> Dict:
        """Analyze whale activity patterns"""
        
        volume_ratio = data.get('volume_ratio', 1.0)
        price_change = data.get('price_change_24h', 0.0)
        
        # Determine activity type
        if volume_ratio > 1.5 and abs(price_change) < 0.05:
            activity_type = "ACCUMULATION"
            signal_strength = menace_score * 0.9
            pattern = "STEALTH_ACCUMULATION"
            risk_level = "LOW"
            recommended_action = "FOLLOW"
        elif volume_ratio > 2.0 and price_change > 0.1:
            activity_type = "PUMP_PREPARATION"
            signal_strength = menace_score * 0.8
            pattern = "AGGRESSIVE_ACCUMULATION"
            risk_level = "MEDIUM"
            recommended_action = "FOLLOW"
        elif volume_ratio > 1.5 and price_change < -0.05:
            activity_type = "DISTRIBUTION"
            signal_strength = menace_score * 0.6
            pattern = "CONTROLLED_DISTRIBUTION"
            risk_level = "HIGH"
            recommended_action = "AVOID"
        else:
            activity_type = "NEUTRAL"
            signal_strength = menace_score * 0.4
            pattern = "NO_CLEAR_PATTERN"
            risk_level = "MEDIUM"
            recommended_action = "MONITOR"
        
        return {
            'activity_type': activity_type,
            'signal_strength': signal_strength,
            'pattern': pattern,
            'risk_level': risk_level,
            'recommended_action': recommended_action
        }
    
    def generate_keyblade_vault_alerts(self, vaultlog_intelligence: Dict) -> List[KeybladeVaultAlert]:
        """Generate enhanced vault alerts with KeybladeAI optimization"""
        
        vault_alerts = []
        
        # Analyze vault positions
        for symbol, vault_data in vaultlog_intelligence.get('vault_positions', {}).items():
            try:
                # Aging analysis
                days_held = vault_data.get('days_held', 0)
                current_roi = vault_data.get('current_roi', 0.0)
                
                # Determine aging status
                aging_status = self._determine_aging_status(days_held, current_roi)
                
                # Reallocation urgency
                urgency = self._calculate_reallocation_urgency(days_held, current_roi)
                
                # Suggested action
                suggested_action = self._determine_vault_action(aging_status, urgency)
                
                vault_alert = KeybladeVaultAlert(
                    symbol=symbol,
                    aging_status=aging_status,
                    current_roi=current_roi,
                    days_in_vault=days_held,
                    suggested_action=suggested_action,
                    reallocation_urgency=urgency
                )
                
                vault_alerts.append(vault_alert)
                
            except Exception as e:
                logger.error(f"Error generating vault alert for {symbol}: {e}")
                continue
        
        # Sort by urgency
        vault_alerts.sort(key=lambda x: x.reallocation_urgency, reverse=True)
        
        logger.info(f"🏛️ Generated {len(vault_alerts)} KeybladeAI vault alerts")
        return vault_alerts
    
    def _determine_aging_status(self, days_held: int, current_roi: float) -> str:
        """Determine vault position aging status"""
        
        if days_held < 7:
            return "FRESH"
        elif days_held < 30:
            if current_roi > 0.1:  # 10%+ in under 30 days
                return "MATURE"
            else:
                return "DEVELOPING"
        elif days_held < 90:
            if current_roi > 0.2:  # 20%+ in under 90 days
                return "MATURE"
            else:
                return "STALE"
        else:
            if current_roi > 0.3:  # 30%+ in 90+ days
                return "VINTAGE"
            else:
                return "STAGNANT"
    
    def _calculate_reallocation_urgency(self, days_held: int, current_roi: float) -> float:
        """Calculate reallocation urgency score"""
        
        # Daily ROI calculation
        daily_roi = current_roi / max(days_held, 1)
        
        # Target daily ROI (0.3% = 0.003)
        target_daily_roi = 0.003
        
        # Performance urgency
        performance_urgency = max(0.0, 1.0 - (daily_roi / target_daily_roi))
        
        # Time urgency (increases with time)
        time_urgency = min(days_held / 90.0, 1.0)
        
        # Composite urgency
        urgency = (performance_urgency * 0.7 + time_urgency * 0.3)
        
        return min(urgency, 1.0)
    
    def _determine_vault_action(self, aging_status: str, urgency: float) -> str:
        """Determine recommended vault action"""
        
        if urgency > 0.8:
            return "LIQUIDATE"
        elif urgency > 0.6:
            return "ROTATE"
        elif urgency > 0.4:
            return "REBALANCE"
        elif aging_status in ["MATURE", "VINTAGE"]:
            return "PARTIAL_PROFIT"
        else:
            return "HOLD"
    
    def generate_keyblade_tile_heatmap(self, market_data: Dict, flip_recommendations: List, 
                                     whale_signals: List) -> List[KeybladeTileHeat]:
        """Generate enhanced tile heatmap with KeybladeAI correlation analysis"""
        
        tile_heatmap = []
        
        for symbol, data in market_data.items():
            try:
                # Base heat calculation
                base_heat = self._calculate_base_heat(symbol, data)
                
                # Enhancement from recommendations
                recommendation_boost = self._get_recommendation_boost(symbol, flip_recommendations)
                
                # Enhancement from whale signals
                whale_boost = self._get_whale_boost(symbol, whale_signals)
                
                # Correlation risk (simplified)
                correlation_risk = 0.3  # Default moderate correlation risk
                
                # Sector exposure
                sector_exposure = self._analyze_sector_exposure(symbol)
                
                # Composite heat score
                heat_score = min(base_heat + recommendation_boost + whale_boost - correlation_risk * 0.3, 1.0)
                
                # Urgency level
                urgency_level = self._determine_urgency_level(heat_score, correlation_risk)
                
                tile_heat = KeybladeTileHeat(
                    symbol=symbol,
                    heat_score=heat_score,
                    urgency_level=urgency_level,
                    correlation_risk=correlation_risk,
                    sector_exposure=sector_exposure
                )
                
                tile_heatmap.append(tile_heat)
                
            except Exception as e:
                logger.error(f"Error generating tile heat for {symbol}: {e}")
                continue
        
        # Sort by heat score
        tile_heatmap.sort(key=lambda x: x.heat_score, reverse=True)
        
        logger.info(f"🔥 Generated {len(tile_heatmap)} KeybladeAI tile heatmap entries")
        return tile_heatmap
    
    def _calculate_base_heat(self, symbol: str, data: Dict) -> float:
        """Calculate base heat score"""
        
        # Volume heat
        volume_ratio = data.get('volume_ratio', 1.0)
        volume_heat = min(volume_ratio / 2.0, 0.4)  # Max 0.4 from volume
        
        # Price momentum heat
        price_change = abs(data.get('price_change_24h', 0.0))
        momentum_heat = min(price_change * 2, 0.3)  # Max 0.3 from momentum
        
        # Volatility heat
        volatility = data.get('volatility', 0.1)
        volatility_heat = min(volatility, 0.3)  # Max 0.3 from volatility
        
        return volume_heat + momentum_heat + volatility_heat
    
    def _get_recommendation_boost(self, symbol: str, recommendations: List) -> float:
        """Get heat boost from flip recommendations"""
        
        for rec in recommendations:
            if rec.symbol == symbol:
                if rec.priority == 'HIGH':
                    return 0.3
                elif rec.priority == 'MEDIUM':
                    return 0.2
                else:
                    return 0.1
        return 0.0
    
    def _get_whale_boost(self, symbol: str, whale_signals: List) -> float:
        """Get heat boost from whale signals"""
        
        for whale in whale_signals:
            if whale.symbol == symbol:
                if whale.recommended_action == 'FOLLOW':
                    return whale.signal_strength * 0.2
                elif whale.recommended_action == 'MONITOR':
                    return whale.signal_strength * 0.1
        return 0.0
    
    def _analyze_sector_exposure(self, symbol: str) -> str:
        """Analyze sector exposure"""
        
        # Sector mapping
        sectors = {
            'BTC': 'STORE_OF_VALUE',
            'ETH': 'SMART_CONTRACTS',
            'ADA': 'PROOF_OF_STAKE',
            'XRP': 'PAYMENTS',
            'WIF': 'MEME_TOKENS',
            'BONK': 'MEME_TOKENS',
            'POLYX': 'SECURITY_TOKENS'
        }
        
        return sectors.get(symbol, 'UNKNOWN')
    
    def _determine_urgency_level(self, heat_score: float, correlation_risk: float) -> str:
        """Determine urgency level for tile"""
        
        # Adjust heat score for correlation risk
        adjusted_heat = heat_score * (1.0 - correlation_risk * 0.3)
        
        if adjusted_heat > 0.8:
            return "CRITICAL"
        elif adjusted_heat > 0.6:
            return "HIGH"
        elif adjusted_heat > 0.4:
            return "MEDIUM"
        else:
            return "LOW"

def main():
    """Test the KeybladeAI Enhanced Engine (Fixed)"""
    
    print("🔥 KEYBLADE ENHANCED TACTICAL ENGINE - ROI EXECUTION MODE (FIXED)")
    
    # Initialize engine
    engine = KeybladeEnhancedEngineFixed()
    
    # Test market data
    test_market_data = {
        'BTC': {
            'current_price': 45000.0,
            'price_change_24h': 0.03,
            'volume_ratio': 1.2,
            'volatility': 0.15,
            'volume_24h': 2000000000,
            'market_cap': 900000000000
        },
        'WIF': {
            'current_price': 2.5,
            'price_change_24h': 0.08,
            'volume_ratio': 1.8,
            'volatility': 0.25,
            'volume_24h': 50000000,
            'market_cap': 2500000000
        }
    }
    
    test_vaultlog = {
        'vault_positions': {
            'BTC': {
                'days_held': 45,
                'current_roi': 0.12
            },
            'WIF': {
                'days_held': 15,
                'current_roi': 0.25
            }
        }
    }
    
    print("\n🎯 Testing KeybladeAI flip recommendations...")
    flip_recs = engine.generate_keyblade_flip_recommendations(test_market_data, test_vaultlog)
    print(f"Generated {len(flip_recs)} flip recommendations")
    for rec in flip_recs:
        print(f"  {rec.symbol}: {rec.action} - ROI: {rec.expected_roi:.2%} - Ray: {rec.ray_score:.1f}")
    
    print("\n🐋 Testing KeybladeAI whale signals...")
    whale_signals = engine.generate_keyblade_whale_signals(test_market_data)
    print(f"Generated {len(whale_signals)} whale signals")
    for whale in whale_signals:
        print(f"  {whale.symbol}: {whale.whale_activity_type} - MENACE: {whale.menace_score:.2f}")
    
    print("\n🏛️ Testing KeybladeAI vault alerts...")
    vault_alerts = engine.generate_keyblade_vault_alerts(test_vaultlog)
    print(f"Generated {len(vault_alerts)} vault alerts")
    for alert in vault_alerts:
        print(f"  {alert.symbol}: {alert.aging_status} - {alert.suggested_action} - Urgency: {alert.reallocation_urgency:.2f}")
    
    print("\n🔥 Testing KeybladeAI tile heatmap...")
    tile_heatmap = engine.generate_keyblade_tile_heatmap(test_market_data, flip_recs, whale_signals)
    print(f"Generated {len(tile_heatmap)} tile heat entries")
    for tile in tile_heatmap:
        print(f"  {tile.symbol}: Heat {tile.heat_score:.2f} - {tile.urgency_level}")
    
    print("\n🚀 KEYBLADE ENHANCED ENGINE (FIXED) - READY FOR ROI EXECUTION!")

if __name__ == "__main__":
    main()

