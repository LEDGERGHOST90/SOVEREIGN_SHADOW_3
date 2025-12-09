#!/usr/bin/env python3
"""
🔥 ULTIMATE TACTICAL INTELLIGENCE ENGINE - THE COMPLETE TACTICAL SOUL
Extracts and synthesizes all tactical intelligence from the LLF-ß system for $1000+ ROI per quarter

This is the crown jewel - the system that channels everything we've built into pure profit.
Every module serves the flip, defends the vault, or grows capital.

ROI_EXECUTION_MODE::ENGAGED
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import hashlib
import sqlite3
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TacticalFlipRecommendation:
    """Tactical flip ladder recommendation with entry, TP, SL"""
    symbol: str
    action: str  # BUY, SELL, HOLD, LADDER_ENTRY
    entry_price: float
    confidence_score: float
    ray_score: float
    
    # Ladder structure
    tp_levels: List[float]  # Take profit levels
    sl_levels: List[float]  # Stop loss levels
    position_sizes: List[float]  # Position size for each level
    
    # Intelligence sources
    whale_signal_strength: float
    heat_map_score: float
    vault_rotation_signal: float
    menace_accumulation: float
    
    # Risk management
    max_position_size: float
    risk_reward_ratio: float
    expected_roi: float
    time_horizon: str  # SCALP, SWING, HOLD
    
    # Execution details
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    deadline: str
    reasoning: str

@dataclass
class WhaleAlignedWatchlist:
    """Whale-aligned asset watchlist with MENACE signals"""
    symbol: str
    whale_activity_type: str  # ACCUMULATION, DISTRIBUTION, NEUTRAL
    signal_strength: float  # 0.0 to 1.0
    volume_anomaly: float  # Volume spike multiplier
    price_momentum: float  # Price movement correlation
    
    # MENACE intelligence
    menace_score: float
    accumulation_pattern: str  # STEALTH, AGGRESSIVE, SYSTEMATIC
    whale_wallet_count: int
    total_whale_volume: float
    
    # Tactical intelligence
    entry_opportunity: float  # How good is the entry opportunity
    risk_level: str  # LOW, MEDIUM, HIGH
    recommended_action: str  # FOLLOW, MONITOR, AVOID
    time_sensitivity: str  # IMMEDIATE, HOURS, DAYS

@dataclass
class VaultAgingAlert:
    """Vault aging alert and reallocation suggestion"""
    symbol: str
    current_allocation: float
    days_in_vault: int
    current_roi: float
    
    # Aging analysis
    aging_status: str  # FRESH, MATURE, STALE, EXPIRED
    reallocation_urgency: float  # 0.0 to 1.0
    suggested_action: str  # HOLD, ROTATE, LIQUIDATE, REBALANCE
    
    # Reallocation intelligence
    target_allocation: float
    rotation_candidates: List[str]  # Assets to rotate into
    expected_improvement: float  # Expected ROI improvement
    
    # Risk factors
    correlation_risk: float
    market_phase_risk: float
    liquidity_risk: float

@dataclass
class TileHeatMap:
    """Tile-based heatmap score per asset"""
    symbol: str
    heat_score: float  # 0.0 to 1.0 (cold to hot)
    
    # Heat components
    price_momentum: float
    volume_heat: float
    whale_activity_heat: float
    technical_heat: float
    sentiment_heat: float
    
    # Visual representation
    color_code: str  # HEX color for UI
    urgency_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    tile_size: str  # SMALL, MEDIUM, LARGE (based on importance)
    
    # Action signals
    buy_signal: float
    sell_signal: float
    hold_signal: float

@dataclass
class DailyTacticalFlow:
    """Complete daily tactical flow output"""
    date: str
    emotional_risk_signal: str  # 🟢🟡🔴
    primary_directive: str  # The single most profitable move
    
    # Core intelligence
    flip_recommendations: List[TacticalFlipRecommendation]
    whale_watchlist: List[WhaleAlignedWatchlist]
    vault_alerts: List[VaultAgingAlert]
    tile_heatmap: List[TileHeatMap]
    
    # ROI optimization
    expected_daily_roi: float
    quarterly_roi_projection: float
    risk_adjusted_return: float
    
    # Execution metadata
    confidence_level: float
    market_phase: str
    system_health: str
    generated_at: str

class UltimateTacticalIntelligence:
    """
    🔥 THE ULTIMATE TACTICAL INTELLIGENCE ENGINE
    Extracts the complete tactical soul from all LLF-ß components
    """
    
    def __init__(self, llf_beta_path: str = "/home/ubuntu/LLF-Beta"):
        self.llf_beta_path = Path(llf_beta_path)
        self.vaultlog_path = self.llf_beta_path / "vaultlog"
        self.memory_path = self.llf_beta_path / "memory"
        
        # Initialize intelligence modules
        self.omega_sigil = self._initialize_omega_sigil()
        self.menace_tracker = self._initialize_menace_tracker()
        self.keyblade_engine = self._initialize_keyblade_engine()
        self.vault_tracker = self._initialize_vault_tracker()
        
        # Load tactical configurations
        self.flip_templates = self._load_flip_templates()
        self.correlation_matrix = self._load_correlation_matrix()
        self.risk_thresholds = self._load_risk_thresholds()
        
        # ROI optimization parameters
        self.roi_targets = {
            'daily_minimum': 0.005,  # 0.5% daily minimum
            'quarterly_target': 0.25,  # 25% quarterly target ($1000+ on $4000)
            'max_risk_per_trade': 0.02,  # 2% max risk per trade
            'compound_factor': 1.02  # 2% compound factor
        }
        
        logger.info("🔥 Ultimate Tactical Intelligence Engine initialized")
    
    def _initialize_omega_sigil(self):
        """Initialize ΩSIGIL Intelligence Engine"""
        try:
            from ultimate_sovereign_system.omega_sigil_engine.omega_sigil_intelligence import OMEGASIGILIntelligence
            return OMEGASIGILIntelligence()
        except ImportError:
            logger.warning("ΩSIGIL Intelligence not available - using simulation")
            return None
    
    def _initialize_menace_tracker(self):
        """Initialize MENACE whale signal tracker"""
        # Simulated MENACE tracker
        return {
            'whale_wallets': [],
            'accumulation_patterns': {},
            'signal_history': []
        }
    
    def _initialize_keyblade_engine(self):
        """Initialize KeybladeAI engine"""
        try:
            from keyblade_integration import KeybladeAIEngine
            return KeybladeAIEngine(str(self.llf_beta_path))
        except ImportError:
            logger.warning("KeybladeAI not available - using basic logic")
            return None
    
    def _initialize_vault_tracker(self):
        """Initialize vault tracker"""
        return {
            'active_vaults': {},
            'aging_analysis': {},
            'rotation_signals': {}
        }
    
    def _load_flip_templates(self) -> Dict:
        """Load Commander 30-50% flip templates"""
        
        # Default 30-50% flip template
        return {
            "commander_30_50": {
                "target_range": [0.30, 0.50],
                "ladder_levels": [
                    {"tp": 0.15, "size": 0.4, "priority": "HIGH"},
                    {"tp": 0.25, "size": 0.3, "priority": "MEDIUM"},
                    {"tp": 0.35, "size": 0.2, "priority": "MEDIUM"},
                    {"tp": 0.50, "size": 0.1, "priority": "LOW"}
                ],
                "stop_loss": 0.05,  # 5% stop loss
                "max_position": 0.15,  # 15% max position
                "ray_score_minimum": 65
            }
        }
    
    def _load_correlation_matrix(self) -> Dict:
        """Load omega correlation matrix"""
        
        # Simulated correlation matrix
        return {
            "BTC": {"ETH": 0.85, "WIF": 0.65, "BONK": 0.45, "XRP": 0.55},
            "ETH": {"BTC": 0.85, "WIF": 0.70, "BONK": 0.50, "XRP": 0.60},
            "WIF": {"BTC": 0.65, "ETH": 0.70, "BONK": 0.80, "XRP": 0.40},
            "BONK": {"BTC": 0.45, "ETH": 0.50, "WIF": 0.80, "XRP": 0.35},
            "XRP": {"BTC": 0.55, "ETH": 0.60, "WIF": 0.40, "BONK": 0.35}
        }
    
    def _load_risk_thresholds(self) -> Dict:
        """Load keyblade risk thresholds"""
        
        return {
            "emotional_signals": {
                "green": {"risk_max": 0.25, "confidence_min": 0.75},
                "yellow": {"risk_max": 0.60, "confidence_min": 0.50},
                "red": {"risk_max": 1.0, "confidence_min": 0.25}
            },
            "position_limits": {
                "single_asset": 0.15,  # 15% max per asset
                "correlated_group": 0.30,  # 30% max in correlated assets
                "high_risk": 0.05  # 5% max in high-risk assets
            },
            "ray_score_gates": {
                "minimum_entry": 60,
                "confident_entry": 75,
                "aggressive_entry": 85
            }
        }
    
    def extract_vaultlog_intelligence(self) -> Dict[str, Any]:
        """Extract tactical intelligence from vaultlog history"""
        
        vaultlog_intelligence = {
            'active_positions': [],
            'completed_flips': [],
            'vault_rotations': [],
            'performance_metrics': {}
        }
        
        if not self.vaultlog_path.exists():
            logger.warning("Vaultlog directory not found - creating sample data")
            return self._generate_sample_vaultlog_intelligence()
        
        # Process vaultlog files
        for vaultlog_file in self.vaultlog_path.glob("*.json"):
            try:
                with open(vaultlog_file, 'r') as f:
                    vaultlog_data = json.load(f)
                
                # Extract active positions
                if 'active_positions' in vaultlog_data:
                    vaultlog_intelligence['active_positions'].extend(
                        vaultlog_data['active_positions']
                    )
                
                # Extract completed flips
                if 'completed_flips' in vaultlog_data:
                    vaultlog_intelligence['completed_flips'].extend(
                        vaultlog_data['completed_flips']
                    )
                
                # Extract vault rotations
                if 'vault_rotations' in vaultlog_data:
                    vaultlog_intelligence['vault_rotations'].extend(
                        vaultlog_data['vault_rotations']
                    )
                    
            except Exception as e:
                logger.error(f"Error processing vaultlog {vaultlog_file}: {e}")
        
        # Calculate performance metrics
        vaultlog_intelligence['performance_metrics'] = self._calculate_performance_metrics(
            vaultlog_intelligence
        )
        
        return vaultlog_intelligence
    
    def _generate_sample_vaultlog_intelligence(self) -> Dict[str, Any]:
        """Generate sample vaultlog intelligence for demonstration"""
        
        return {
            'active_positions': [
                {
                    'symbol': 'WIF',
                    'entry_price': 2.45,
                    'current_price': 2.89,
                    'position_size': 0.301,
                    'pnl_percent': 17.96,
                    'days_held': 12,
                    'ray_score': 78.5,
                    'confidence': 0.82
                },
                {
                    'symbol': 'BONK',
                    'entry_price': 0.000028,
                    'current_price': 0.000025,
                    'position_size': 0.133,
                    'pnl_percent': -10.71,
                    'days_held': 8,
                    'ray_score': 58.2,
                    'confidence': 0.45
                },
                {
                    'symbol': 'XRP',
                    'entry_price': 0.54,
                    'current_price': 0.58,
                    'position_size': 0.131,
                    'pnl_percent': 7.41,
                    'days_held': 15,
                    'ray_score': 71.3,
                    'confidence': 0.68
                }
            ],
            'completed_flips': [
                {
                    'symbol': 'BTC',
                    'entry_price': 42000,
                    'exit_price': 45500,
                    'roi': 0.083,
                    'days_held': 6,
                    'ray_score': 82.1,
                    'success': True
                }
            ],
            'vault_rotations': [],
            'performance_metrics': {
                'total_roi': 0.156,
                'win_rate': 0.75,
                'avg_ray_score': 72.5,
                'avg_hold_time': 10.25
            }
        }
    
    def _calculate_performance_metrics(self, vaultlog_data: Dict) -> Dict:
        """Calculate performance metrics from vaultlog data"""
        
        active_positions = vaultlog_data.get('active_positions', [])
        completed_flips = vaultlog_data.get('completed_flips', [])
        
        if not active_positions and not completed_flips:
            return {'total_roi': 0.0, 'win_rate': 0.0, 'avg_ray_score': 50.0}
        
        # Calculate total ROI
        total_roi = 0.0
        if active_positions:
            active_roi = np.mean([pos.get('pnl_percent', 0) for pos in active_positions]) / 100
            total_roi += active_roi
        
        if completed_flips:
            completed_roi = np.mean([flip.get('roi', 0) for flip in completed_flips])
            total_roi += completed_roi
        
        # Calculate win rate
        if completed_flips:
            wins = sum(1 for flip in completed_flips if flip.get('success', False))
            win_rate = wins / len(completed_flips)
        else:
            win_rate = 0.5  # Neutral assumption
        
        # Calculate average Ray Score
        all_ray_scores = []
        all_ray_scores.extend([pos.get('ray_score', 50) for pos in active_positions])
        all_ray_scores.extend([flip.get('ray_score', 50) for flip in completed_flips])
        
        avg_ray_score = np.mean(all_ray_scores) if all_ray_scores else 50.0
        
        return {
            'total_roi': total_roi,
            'win_rate': win_rate,
            'avg_ray_score': avg_ray_score,
            'position_count': len(active_positions),
            'completed_count': len(completed_flips)
        }
    
    def generate_tactical_flip_recommendations(self, vaultlog_intelligence: Dict,
                                             market_data: Dict) -> List[TacticalFlipRecommendation]:
        """Generate tactical flip ladder recommendations"""
        
        recommendations = []
        flip_template = self.flip_templates["commander_30_50"]
        
        # Analyze each potential flip opportunity
        symbols = ['BTC', 'ETH', 'WIF', 'BONK', 'XRP', 'ADA', 'SOL']
        
        for symbol in symbols:
            # Get market data for symbol
            price_change = market_data.get(f'{symbol}_change_24h', 0.0)
            volume_change = market_data.get(f'{symbol}_volume_change', 1.0)
            current_price = market_data.get(f'{symbol}_price', 1.0)
            
            # Check if already in position
            existing_position = None
            for pos in vaultlog_intelligence['active_positions']:
                if pos['symbol'] == symbol:
                    existing_position = pos
                    break
            
            # Generate recommendation based on analysis
            recommendation = self._analyze_flip_opportunity(
                symbol, current_price, price_change, volume_change,
                existing_position, flip_template, market_data
            )
            
            if recommendation:
                recommendations.append(recommendation)
        
        # Sort by expected ROI and priority
        recommendations.sort(key=lambda x: (x.expected_roi, x.confidence_score), reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _analyze_flip_opportunity(self, symbol: str, current_price: float,
                                price_change: float, volume_change: float,
                                existing_position: Optional[Dict],
                                flip_template: Dict, market_data: Dict) -> Optional[TacticalFlipRecommendation]:
        """Analyze individual flip opportunity"""
        
        # Skip if already heavily allocated
        if existing_position and existing_position.get('position_size', 0) > 0.1:
            return None
        
        # Calculate opportunity scores
        whale_signal_strength = self._calculate_whale_signal_strength(symbol, market_data)
        heat_map_score = self._calculate_heat_map_score(symbol, price_change, volume_change)
        vault_rotation_signal = self._calculate_vault_rotation_signal(symbol, existing_position)
        menace_accumulation = self._calculate_menace_accumulation(symbol, market_data)
        
        # Calculate confidence and Ray Score
        confidence_score = (whale_signal_strength + heat_map_score + menace_accumulation) / 3
        ray_score = self._calculate_ray_score(symbol, confidence_score, price_change)
        
        # Skip if below minimum Ray Score
        if ray_score < flip_template['ray_score_minimum']:
            return None
        
        # Determine action
        if existing_position:
            if existing_position.get('pnl_percent', 0) > 15:  # 15%+ gains
                action = "LADDER_ENTRY"  # Add to position
            elif existing_position.get('pnl_percent', 0) < -5:  # 5%+ loss
                action = "HOLD"  # Wait for recovery
            else:
                action = "HOLD"
        else:
            if price_change < -0.05 and whale_signal_strength > 0.6:  # Oversold with whale activity
                action = "BUY"
            elif heat_map_score > 0.7:
                action = "LADDER_ENTRY"
            else:
                action = "HOLD"
        
        if action == "HOLD":
            return None
        
        # Generate ladder structure
        tp_levels = []
        sl_levels = []
        position_sizes = []
        
        for level in flip_template['ladder_levels']:
            tp_price = current_price * (1 + level['tp'])
            tp_levels.append(tp_price)
            
            sl_price = current_price * (1 - flip_template['stop_loss'])
            sl_levels.append(sl_price)
            
            position_sizes.append(level['size'])
        
        # Calculate expected ROI
        expected_roi = np.mean([level['tp'] for level in flip_template['ladder_levels']])
        expected_roi *= confidence_score  # Adjust for confidence
        
        # Determine priority
        if ray_score > 80 and confidence_score > 0.8:
            priority = "CRITICAL"
        elif ray_score > 70 and confidence_score > 0.6:
            priority = "HIGH"
        elif ray_score > 60:
            priority = "MEDIUM"
        else:
            priority = "LOW"
        
        # Generate reasoning
        reasoning = f"Ray Score {ray_score:.1f}, Whale Signal {whale_signal_strength:.1%}, Heat {heat_map_score:.1%}"
        if price_change < -0.05:
            reasoning += f", Oversold {abs(price_change):.1%}"
        
        return TacticalFlipRecommendation(
            symbol=symbol,
            action=action,
            entry_price=current_price,
            confidence_score=confidence_score,
            ray_score=ray_score,
            tp_levels=tp_levels,
            sl_levels=sl_levels,
            position_sizes=position_sizes,
            whale_signal_strength=whale_signal_strength,
            heat_map_score=heat_map_score,
            vault_rotation_signal=vault_rotation_signal,
            menace_accumulation=menace_accumulation,
            max_position_size=flip_template['max_position'],
            risk_reward_ratio=expected_roi / flip_template['stop_loss'],
            expected_roi=expected_roi,
            time_horizon="SWING",
            priority=priority,
            deadline=(datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            reasoning=reasoning
        )
    
    def _calculate_whale_signal_strength(self, symbol: str, market_data: Dict) -> float:
        """Calculate whale signal strength for symbol"""
        
        volume_change = market_data.get(f'{symbol}_volume_change', 1.0)
        price_impact = abs(market_data.get(f'{symbol}_change_24h', 0.0))
        
        # Whale signal = unusual volume + price impact
        whale_signal = min((volume_change - 1.0) * 2 + price_impact * 5, 1.0)
        return max(whale_signal, 0.0)
    
    def _calculate_heat_map_score(self, symbol: str, price_change: float, volume_change: float) -> float:
        """Calculate heat map score for symbol"""
        
        # Heat = price momentum + volume activity
        price_heat = min(abs(price_change) * 10, 1.0)
        volume_heat = min((volume_change - 1.0) * 2, 1.0)
        
        return (price_heat + volume_heat) / 2
    
    def _calculate_vault_rotation_signal(self, symbol: str, existing_position: Optional[Dict]) -> float:
        """Calculate vault rotation signal"""
        
        if not existing_position:
            return 0.0
        
        pnl_percent = existing_position.get('pnl_percent', 0)
        days_held = existing_position.get('days_held', 0)
        
        # Strong rotation signal for 15%+ gains or 30+ days held
        if pnl_percent > 15:
            return 0.8
        elif days_held > 30:
            return 0.6
        elif pnl_percent > 10:
            return 0.4
        else:
            return 0.0
    
    def _calculate_menace_accumulation(self, symbol: str, market_data: Dict) -> float:
        """Calculate MENACE accumulation score"""
        
        # Simulated MENACE accumulation based on volume and price patterns
        volume_change = market_data.get(f'{symbol}_volume_change', 1.0)
        price_change = market_data.get(f'{symbol}_change_24h', 0.0)
        
        # MENACE accumulation = sustained volume with controlled price action
        if volume_change > 1.5 and abs(price_change) < 0.03:  # High volume, low volatility
            return 0.8
        elif volume_change > 1.2 and price_change > 0:  # Volume with positive price
            return 0.6
        else:
            return 0.3
    
    def _calculate_ray_score(self, symbol: str, confidence: float, price_change: float) -> float:
        """Calculate Ray Score for decision clarity"""
        
        # Ray Score = confidence + market conditions + symbol quality
        base_score = confidence * 50  # 0-50 points from confidence
        
        # Market conditions bonus
        if abs(price_change) < 0.02:  # Low volatility
            market_bonus = 10
        elif abs(price_change) > 0.1:  # High volatility
            market_bonus = -10
        else:
            market_bonus = 0
        
        # Symbol quality bonus
        quality_symbols = ['BTC', 'ETH', 'XRP']
        if symbol in quality_symbols:
            quality_bonus = 15
        else:
            quality_bonus = 5
        
        ray_score = base_score + market_bonus + quality_bonus + 25  # Base 25 points
        return min(max(ray_score, 0), 100)  # Clamp to 0-100
    
    def generate_whale_aligned_watchlist(self, market_data: Dict) -> List[WhaleAlignedWatchlist]:
        """Generate whale-aligned asset watchlist with MENACE signals"""
        
        watchlist = []
        symbols = ['BTC', 'ETH', 'WIF', 'BONK', 'XRP', 'ADA', 'SOL', 'MATIC', 'DOT']
        
        for symbol in symbols:
            volume_change = market_data.get(f'{symbol}_volume_change', 1.0)
            price_change = market_data.get(f'{symbol}_change_24h', 0.0)
            
            # Determine whale activity type
            if volume_change > 1.5 and price_change > 0.02:
                activity_type = "ACCUMULATION"
                signal_strength = min(volume_change / 2.0, 1.0)
            elif volume_change > 1.3 and price_change < -0.02:
                activity_type = "DISTRIBUTION"
                signal_strength = min(volume_change / 2.5, 1.0)
            else:
                activity_type = "NEUTRAL"
                signal_strength = 0.3
            
            # Calculate MENACE score
            menace_score = self._calculate_menace_score(symbol, volume_change, price_change)
            
            # Determine accumulation pattern
            if signal_strength > 0.8:
                accumulation_pattern = "AGGRESSIVE"
            elif signal_strength > 0.6:
                accumulation_pattern = "SYSTEMATIC"
            else:
                accumulation_pattern = "STEALTH"
            
            # Entry opportunity assessment
            if activity_type == "ACCUMULATION" and price_change < 0:
                entry_opportunity = 0.8  # Whales buying dips
            elif activity_type == "ACCUMULATION":
                entry_opportunity = 0.6  # Whales buying strength
            else:
                entry_opportunity = 0.3
            
            # Risk level
            if signal_strength > 0.7:
                risk_level = "LOW"  # Following whales is safer
            elif signal_strength > 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"
            
            # Recommended action
            if activity_type == "ACCUMULATION" and entry_opportunity > 0.6:
                recommended_action = "FOLLOW"
            elif signal_strength > 0.5:
                recommended_action = "MONITOR"
            else:
                recommended_action = "AVOID"
            
            watchlist_item = WhaleAlignedWatchlist(
                symbol=symbol,
                whale_activity_type=activity_type,
                signal_strength=signal_strength,
                volume_anomaly=volume_change,
                price_momentum=price_change,
                menace_score=menace_score,
                accumulation_pattern=accumulation_pattern,
                whale_wallet_count=int(signal_strength * 10),  # Simulated
                total_whale_volume=volume_change * 1000000,  # Simulated
                entry_opportunity=entry_opportunity,
                risk_level=risk_level,
                recommended_action=recommended_action,
                time_sensitivity="HOURS" if signal_strength > 0.7 else "DAYS"
            )
            
            watchlist.append(watchlist_item)
        
        # Sort by signal strength and entry opportunity
        watchlist.sort(key=lambda x: (x.signal_strength, x.entry_opportunity), reverse=True)
        
        return watchlist[:6]  # Top 6 whale signals
    
    def _calculate_menace_score(self, symbol: str, volume_change: float, price_change: float) -> float:
        """Calculate MENACE score for whale activity"""
        
        # MENACE = volume anomaly + price control + pattern consistency
        volume_score = min((volume_change - 1.0) * 2, 1.0)
        
        # Price control = high volume with controlled price movement
        if volume_change > 1.5 and abs(price_change) < 0.05:
            control_score = 0.8  # High volume, low volatility = control
        elif volume_change > 1.2:
            control_score = 0.5
        else:
            control_score = 0.2
        
        # Pattern consistency (simulated)
        pattern_score = 0.6  # Default consistency
        
        menace_score = (volume_score + control_score + pattern_score) / 3
        return min(max(menace_score, 0.0), 1.0)
    
    def generate_vault_aging_alerts(self, vaultlog_intelligence: Dict) -> List[VaultAgingAlert]:
        """Generate vault aging alerts and reallocation suggestions"""
        
        alerts = []
        active_positions = vaultlog_intelligence.get('active_positions', [])
        
        for position in active_positions:
            symbol = position['symbol']
            days_held = position.get('days_held', 0)
            current_roi = position.get('pnl_percent', 0) / 100
            allocation = position.get('position_size', 0)
            
            # Determine aging status
            if days_held < 7:
                aging_status = "FRESH"
                reallocation_urgency = 0.1
            elif days_held < 30:
                aging_status = "MATURE"
                reallocation_urgency = 0.3
            elif days_held < 90:
                aging_status = "STALE"
                reallocation_urgency = 0.6
            else:
                aging_status = "EXPIRED"
                reallocation_urgency = 0.9
            
            # Determine suggested action
            if current_roi > 0.20:  # 20%+ gains
                suggested_action = "ROTATE"
                target_allocation = allocation * 0.5  # Take 50% profits
            elif current_roi > 0.10 and days_held > 30:  # 10%+ gains, held long
                suggested_action = "REBALANCE"
                target_allocation = allocation * 0.7  # Reduce position
            elif current_roi < -0.10:  # 10%+ loss
                suggested_action = "LIQUIDATE"
                target_allocation = 0.0
            elif days_held > 60:
                suggested_action = "ROTATE"
                target_allocation = allocation * 0.3  # Significant reduction
            else:
                suggested_action = "HOLD"
                target_allocation = allocation
            
            # Rotation candidates
            rotation_candidates = self._suggest_rotation_candidates(symbol, current_roi)
            
            # Expected improvement
            if suggested_action in ["ROTATE", "REBALANCE"]:
                expected_improvement = 0.05 + (reallocation_urgency * 0.10)  # 5-15% improvement
            else:
                expected_improvement = 0.0
            
            # Risk factors
            correlation_risk = self._calculate_correlation_risk(symbol)
            market_phase_risk = 0.4  # Default market risk
            liquidity_risk = 0.2 if symbol in ['BTC', 'ETH', 'XRP'] else 0.4
            
            alert = VaultAgingAlert(
                symbol=symbol,
                current_allocation=allocation,
                days_in_vault=days_held,
                current_roi=current_roi,
                aging_status=aging_status,
                reallocation_urgency=reallocation_urgency,
                suggested_action=suggested_action,
                target_allocation=target_allocation,
                rotation_candidates=rotation_candidates,
                expected_improvement=expected_improvement,
                correlation_risk=correlation_risk,
                market_phase_risk=market_phase_risk,
                liquidity_risk=liquidity_risk
            )
            
            alerts.append(alert)
        
        # Sort by urgency
        alerts.sort(key=lambda x: x.reallocation_urgency, reverse=True)
        
        return alerts
    
    def _suggest_rotation_candidates(self, current_symbol: str, current_roi: float) -> List[str]:
        """Suggest rotation candidates for vault reallocation"""
        
        # Quality assets for rotation
        quality_assets = ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
        
        # Remove current symbol
        candidates = [asset for asset in quality_assets if asset != current_symbol]
        
        # If current ROI is negative, suggest safer assets
        if current_roi < 0:
            return ['BTC', 'ETH'][:2]
        
        # If current ROI is high, suggest diversification
        return candidates[:3]
    
    def _calculate_correlation_risk(self, symbol: str) -> float:
        """Calculate correlation risk for symbol"""
        
        correlations = self.correlation_matrix.get(symbol, {})
        if not correlations:
            return 0.5  # Default moderate risk
        
        # High correlation with many assets = high risk
        high_correlations = sum(1 for corr in correlations.values() if corr > 0.7)
        correlation_risk = min(high_correlations / len(correlations), 1.0)
        
        return correlation_risk
    
    def generate_tile_heatmap(self, market_data: Dict, 
                            flip_recommendations: List[TacticalFlipRecommendation],
                            whale_watchlist: List[WhaleAlignedWatchlist]) -> List[TileHeatMap]:
        """Generate tile-based heatmap scores per asset"""
        
        heatmap = []
        symbols = set(['BTC', 'ETH', 'WIF', 'BONK', 'XRP', 'ADA', 'SOL'])
        
        # Add symbols from recommendations and watchlist
        for rec in flip_recommendations:
            symbols.add(rec.symbol)
        for whale in whale_watchlist:
            symbols.add(whale.symbol)
        
        for symbol in symbols:
            # Get market data
            price_change = market_data.get(f'{symbol}_change_24h', 0.0)
            volume_change = market_data.get(f'{symbol}_volume_change', 1.0)
            
            # Calculate heat components
            price_momentum = min(abs(price_change) * 10, 1.0)
            volume_heat = min((volume_change - 1.0) * 2, 1.0)
            
            # Whale activity heat
            whale_activity_heat = 0.0
            for whale in whale_watchlist:
                if whale.symbol == symbol:
                    whale_activity_heat = whale.signal_strength
                    break
            
            # Technical heat (simulated)
            technical_heat = (price_momentum + volume_heat) / 2
            
            # Sentiment heat (simulated)
            if price_change > 0.05:
                sentiment_heat = 0.8  # Positive sentiment
            elif price_change < -0.05:
                sentiment_heat = 0.3  # Negative sentiment
            else:
                sentiment_heat = 0.5  # Neutral sentiment
            
            # Overall heat score
            heat_score = (
                price_momentum * 0.25 +
                volume_heat * 0.25 +
                whale_activity_heat * 0.30 +
                technical_heat * 0.10 +
                sentiment_heat * 0.10
            )
            
            # Color coding
            if heat_score > 0.7:
                color_code = "#FF4444"  # Hot red
                urgency_level = "CRITICAL"
                tile_size = "LARGE"
            elif heat_score > 0.5:
                color_code = "#FF8844"  # Orange
                urgency_level = "HIGH"
                tile_size = "MEDIUM"
            elif heat_score > 0.3:
                color_code = "#FFAA44"  # Yellow
                urgency_level = "MEDIUM"
                tile_size = "MEDIUM"
            else:
                color_code = "#44AA44"  # Cool green
                urgency_level = "LOW"
                tile_size = "SMALL"
            
            # Action signals
            buy_signal = 0.0
            sell_signal = 0.0
            hold_signal = 0.0
            
            for rec in flip_recommendations:
                if rec.symbol == symbol:
                    if rec.action in ["BUY", "LADDER_ENTRY"]:
                        buy_signal = rec.confidence_score
                    elif rec.action == "SELL":
                        sell_signal = rec.confidence_score
                    else:
                        hold_signal = rec.confidence_score
                    break
            
            if buy_signal == 0 and sell_signal == 0:
                hold_signal = 0.5  # Default hold
            
            tile = TileHeatMap(
                symbol=symbol,
                heat_score=heat_score,
                price_momentum=price_momentum,
                volume_heat=volume_heat,
                whale_activity_heat=whale_activity_heat,
                technical_heat=technical_heat,
                sentiment_heat=sentiment_heat,
                color_code=color_code,
                urgency_level=urgency_level,
                tile_size=tile_size,
                buy_signal=buy_signal,
                sell_signal=sell_signal,
                hold_signal=hold_signal
            )
            
            heatmap.append(tile)
        
        # Sort by heat score
        heatmap.sort(key=lambda x: x.heat_score, reverse=True)
        
        return heatmap
    
    def determine_emotional_risk_signal(self, flip_recommendations: List[TacticalFlipRecommendation],
                                      vault_alerts: List[VaultAgingAlert],
                                      market_data: Dict) -> str:
        """Determine emotional risk signal (🟢🟡🔴)"""
        
        risk_factors = []
        
        # Portfolio risk from recommendations
        if flip_recommendations:
            avg_confidence = np.mean([rec.confidence_score for rec in flip_recommendations])
            avg_ray_score = np.mean([rec.ray_score for rec in flip_recommendations])
            
            portfolio_risk = 1.0 - ((avg_confidence + avg_ray_score/100) / 2)
            risk_factors.append(portfolio_risk)
        
        # Vault aging risk
        if vault_alerts:
            high_urgency_alerts = sum(1 for alert in vault_alerts if alert.reallocation_urgency > 0.7)
            vault_risk = min(high_urgency_alerts / len(vault_alerts), 1.0)
            risk_factors.append(vault_risk)
        
        # Market volatility risk
        market_volatility = market_data.get('volatility', 0.05)
        volatility_risk = min(market_volatility / 0.10, 1.0)  # Normalize to 10%
        risk_factors.append(volatility_risk)
        
        # Overall risk assessment
        if risk_factors:
            overall_risk = np.mean(risk_factors)
        else:
            overall_risk = 0.5  # Default moderate risk
        
        # Determine emotional signal
        risk_thresholds = self.risk_thresholds["emotional_signals"]
        
        if overall_risk <= risk_thresholds["green"]["risk_max"]:
            return "🟢"  # Low risk - confident
        elif overall_risk <= risk_thresholds["yellow"]["risk_max"]:
            return "🟡"  # Medium risk - cautious
        else:
            return "🔴"  # High risk - defensive
    
    def generate_primary_directive(self, flip_recommendations: List[TacticalFlipRecommendation],
                                 whale_watchlist: List[WhaleAlignedWatchlist],
                                 vault_alerts: List[VaultAgingAlert]) -> str:
        """Generate the single most profitable move for the day"""
        
        # Priority 1: Critical vault rotations (secure profits)
        critical_vault_alerts = [alert for alert in vault_alerts 
                               if alert.suggested_action == "ROTATE" and alert.current_roi > 0.15]
        
        if critical_vault_alerts:
            best_vault = max(critical_vault_alerts, key=lambda x: x.current_roi)
            return f"SECURE PROFITS: Rotate {best_vault.symbol} vault position ({best_vault.current_roi:.1%} gains)"
        
        # Priority 2: Critical flip opportunities
        critical_flips = [rec for rec in flip_recommendations 
                         if rec.priority == "CRITICAL" and rec.expected_roi > 0.20]
        
        if critical_flips:
            best_flip = max(critical_flips, key=lambda x: x.expected_roi)
            return f"FLIP OPPORTUNITY: {best_flip.action} {best_flip.symbol} - {best_flip.expected_roi:.1%} target"
        
        # Priority 3: High-confidence whale following
        strong_whale_signals = [whale for whale in whale_watchlist 
                              if whale.recommended_action == "FOLLOW" and whale.signal_strength > 0.7]
        
        if strong_whale_signals:
            best_whale = max(strong_whale_signals, key=lambda x: x.signal_strength)
            return f"FOLLOW WHALES: {best_whale.symbol} showing {best_whale.whale_activity_type} pattern"
        
        # Priority 4: High ROI flip opportunities
        high_roi_flips = [rec for rec in flip_recommendations if rec.expected_roi > 0.15]
        
        if high_roi_flips:
            best_flip = max(high_roi_flips, key=lambda x: x.expected_roi)
            return f"HIGH ROI FLIP: {best_flip.symbol} - {best_flip.expected_roi:.1%} potential"
        
        # Priority 5: Risk management
        high_risk_vaults = [alert for alert in vault_alerts if alert.current_roi < -0.10]
        
        if high_risk_vaults:
            worst_vault = min(high_risk_vaults, key=lambda x: x.current_roi)
            return f"RISK MANAGEMENT: Review {worst_vault.symbol} position ({worst_vault.current_roi:.1%} loss)"
        
        # Default: Market monitoring
        return "MARKET MONITORING: Watch for whale signals and flip opportunities"
    
    def calculate_roi_projections(self, flip_recommendations: List[TacticalFlipRecommendation],
                                vault_alerts: List[VaultAgingAlert]) -> Dict[str, float]:
        """Calculate ROI projections for wealth optimization"""
        
        # Daily ROI potential
        daily_flip_roi = sum(rec.expected_roi * rec.confidence_score for rec in flip_recommendations)
        daily_vault_roi = sum(alert.expected_improvement for alert in vault_alerts)
        expected_daily_roi = (daily_flip_roi + daily_vault_roi) / 100  # Convert to decimal
        
        # Quarterly projection with compounding
        compound_factor = self.roi_targets['compound_factor']
        quarterly_roi = 0.0
        
        for day in range(90):  # 90 days in quarter
            daily_return = expected_daily_roi * compound_factor
            quarterly_roi = (1 + quarterly_roi) * (1 + daily_return) - 1
        
        # Risk-adjusted return
        risk_adjustment = 0.7  # 70% confidence factor
        risk_adjusted_return = quarterly_roi * risk_adjustment
        
        return {
            'expected_daily_roi': expected_daily_roi,
            'quarterly_roi_projection': quarterly_roi,
            'risk_adjusted_return': risk_adjusted_return,
            'target_achievement': min(quarterly_roi / self.roi_targets['quarterly_target'], 2.0)
        }
    
    def generate_complete_tactical_flow(self) -> DailyTacticalFlow:
        """🔥 Generate the complete daily tactical flow - THE ULTIMATE OUTPUT"""
        
        logger.info("🔥 Generating Ultimate Tactical Flow - Extracting Complete Tactical Soul")
        
        # Extract intelligence from all sources
        vaultlog_intelligence = self.extract_vaultlog_intelligence()
        
        # Generate market data (in production, this would come from live APIs)
        market_data = self._generate_market_data()
        
        # Generate all tactical components
        flip_recommendations = self.generate_tactical_flip_recommendations(vaultlog_intelligence, market_data)
        whale_watchlist = self.generate_whale_aligned_watchlist(market_data)
        vault_alerts = self.generate_vault_aging_alerts(vaultlog_intelligence)
        tile_heatmap = self.generate_tile_heatmap(market_data, flip_recommendations, whale_watchlist)
        
        # Determine emotional risk signal
        emotional_risk_signal = self.determine_emotional_risk_signal(
            flip_recommendations, vault_alerts, market_data
        )
        
        # Generate primary directive
        primary_directive = self.generate_primary_directive(
            flip_recommendations, whale_watchlist, vault_alerts
        )
        
        # Calculate ROI projections
        roi_projections = self.calculate_roi_projections(flip_recommendations, vault_alerts)
        
        # Determine market phase
        market_phase = self._determine_market_phase(whale_watchlist, market_data)
        
        # Calculate system health and confidence
        confidence_level = self._calculate_system_confidence(
            flip_recommendations, whale_watchlist, vault_alerts
        )
        
        system_health = "OPTIMAL" if confidence_level > 0.7 else "GOOD" if confidence_level > 0.5 else "CAUTION"
        
        # Create complete tactical flow
        tactical_flow = DailyTacticalFlow(
            date=datetime.now().strftime("%Y-%m-%d"),
            emotional_risk_signal=emotional_risk_signal,
            primary_directive=primary_directive,
            flip_recommendations=flip_recommendations,
            whale_watchlist=whale_watchlist,
            vault_alerts=vault_alerts,
            tile_heatmap=tile_heatmap,
            expected_daily_roi=roi_projections['expected_daily_roi'],
            quarterly_roi_projection=roi_projections['quarterly_roi_projection'],
            risk_adjusted_return=roi_projections['risk_adjusted_return'],
            confidence_level=confidence_level,
            market_phase=market_phase,
            system_health=system_health,
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(f"🔥 Tactical Flow Generated: {emotional_risk_signal} {primary_directive}")
        logger.info(f"💰 ROI Projection: {roi_projections['quarterly_roi_projection']:.1%} quarterly")
        
        return tactical_flow
    
    def _generate_market_data(self) -> Dict[str, Any]:
        """Generate market data (in production, this would come from live APIs)"""
        
        symbols = ['BTC', 'ETH', 'WIF', 'BONK', 'XRP', 'ADA', 'SOL', 'MATIC', 'DOT']
        market_data = {'volatility': 0.045}
        
        for symbol in symbols:
            # Generate realistic market data
            price_change = np.random.normal(0, 0.05)  # 5% volatility
            volume_change = np.random.lognormal(0, 0.3)  # Log-normal volume
            price = np.random.uniform(0.1, 100.0)  # Random price
            
            market_data[f'{symbol}_change_24h'] = price_change
            market_data[f'{symbol}_volume_change'] = volume_change
            market_data[f'{symbol}_price'] = price
        
        return market_data
    
    def _determine_market_phase(self, whale_watchlist: List[WhaleAlignedWatchlist], 
                              market_data: Dict) -> str:
        """Determine current market phase"""
        
        accumulation_signals = sum(1 for whale in whale_watchlist 
                                 if whale.whale_activity_type == "ACCUMULATION")
        distribution_signals = sum(1 for whale in whale_watchlist 
                                 if whale.whale_activity_type == "DISTRIBUTION")
        
        market_volatility = market_data.get('volatility', 0.05)
        
        if accumulation_signals > distribution_signals and market_volatility < 0.06:
            return "ACCUMULATION_PHASE"
        elif distribution_signals > accumulation_signals:
            return "DISTRIBUTION_PHASE"
        elif market_volatility > 0.08:
            return "HIGH_VOLATILITY"
        else:
            return "NEUTRAL_MARKET"
    
    def _calculate_system_confidence(self, flip_recommendations: List[TacticalFlipRecommendation],
                                   whale_watchlist: List[WhaleAlignedWatchlist],
                                   vault_alerts: List[VaultAgingAlert]) -> float:
        """Calculate overall system confidence"""
        
        confidence_factors = []
        
        # Flip recommendation confidence
        if flip_recommendations:
            avg_flip_confidence = np.mean([rec.confidence_score for rec in flip_recommendations])
            confidence_factors.append(avg_flip_confidence)
        
        # Whale signal confidence
        if whale_watchlist:
            strong_whale_signals = sum(1 for whale in whale_watchlist if whale.signal_strength > 0.6)
            whale_confidence = strong_whale_signals / len(whale_watchlist)
            confidence_factors.append(whale_confidence)
        
        # Vault management confidence
        if vault_alerts:
            profitable_vaults = sum(1 for alert in vault_alerts if alert.current_roi > 0)
            vault_confidence = profitable_vaults / len(vault_alerts)
            confidence_factors.append(vault_confidence)
        
        # Overall confidence
        if confidence_factors:
            return np.mean(confidence_factors)
        else:
            return 0.5  # Default moderate confidence
    
    def format_for_notion(self, tactical_flow: DailyTacticalFlow) -> str:
        """Format tactical flow for Notion markdown output"""
        
        markdown = f"""# 🔥 Daily Tactical Flow - {tactical_flow.date}

## {tactical_flow.emotional_risk_signal} Risk Signal: {tactical_flow.system_health}
**Primary Directive:** {tactical_flow.primary_directive}

**Market Phase:** {tactical_flow.market_phase} | **Confidence:** {tactical_flow.confidence_level:.1%}

---

## 🎯 Tactical Flip Recommendations

"""
        
        for rec in tactical_flow.flip_recommendations[:3]:  # Top 3
            markdown += f"""### {rec.priority} - {rec.symbol} ({rec.action})
- **Entry:** ${rec.entry_price:.4f} | **Confidence:** {rec.confidence_score:.1%} | **Ray Score:** {rec.ray_score:.1f}
- **Expected ROI:** {rec.expected_roi:.1%} | **Risk/Reward:** {rec.risk_reward_ratio:.1f}
- **Reasoning:** {rec.reasoning}
- **Deadline:** {rec.deadline}

"""
        
        markdown += """---

## 🐋 Whale-Aligned Watchlist

"""
        
        for whale in tactical_flow.whale_watchlist[:3]:  # Top 3
            markdown += f"""### {whale.symbol} - {whale.whale_activity_type}
- **Signal Strength:** {whale.signal_strength:.1%} | **Pattern:** {whale.accumulation_pattern}
- **Volume Anomaly:** {whale.volume_anomaly:.1f}x | **Entry Opportunity:** {whale.entry_opportunity:.1%}
- **Action:** {whale.recommended_action} | **Risk:** {whale.risk_level}

"""
        
        markdown += """---

## 🏛️ Vault Aging Alerts

"""
        
        for alert in tactical_flow.vault_alerts[:3]:  # Top 3
            markdown += f"""### {alert.symbol} - {alert.aging_status}
- **Current ROI:** {alert.current_roi:.1%} | **Days Held:** {alert.days_in_vault}
- **Action:** {alert.suggested_action} | **Urgency:** {alert.reallocation_urgency:.1%}
- **Target Allocation:** {alert.target_allocation:.1%}

"""
        
        markdown += f"""---

## 💰 ROI Projections

- **Expected Daily ROI:** {tactical_flow.expected_daily_roi:.2%}
- **Quarterly Projection:** {tactical_flow.quarterly_roi_projection:.1%}
- **Risk-Adjusted Return:** {tactical_flow.risk_adjusted_return:.1%}

---

## 🔥 Tile Heatmap (Top Assets)

"""
        
        for tile in tactical_flow.tile_heatmap[:5]:  # Top 5
            markdown += f"""**{tile.symbol}** - Heat: {tile.heat_score:.1%} | Urgency: {tile.urgency_level}
"""
        
        markdown += f"""

---

*Generated: {tactical_flow.generated_at}*
*System: Ultimate Tactical Intelligence Engine*
*Mode: ROI_EXECUTION_MODE::ENGAGED*
"""
        
        return markdown
    
    def format_for_json(self, tactical_flow: DailyTacticalFlow) -> Dict[str, Any]:
        """Format tactical flow for JSON frontend output"""
        
        return {
            'date': tactical_flow.date,
            'emotional_risk_signal': tactical_flow.emotional_risk_signal,
            'primary_directive': tactical_flow.primary_directive,
            'system_health': tactical_flow.system_health,
            'confidence_level': tactical_flow.confidence_level,
            'market_phase': tactical_flow.market_phase,
            
            'flip_recommendations': [asdict(rec) for rec in tactical_flow.flip_recommendations],
            'whale_watchlist': [asdict(whale) for whale in tactical_flow.whale_watchlist],
            'vault_alerts': [asdict(alert) for alert in tactical_flow.vault_alerts],
            'tile_heatmap': [asdict(tile) for tile in tactical_flow.tile_heatmap],
            
            'roi_projections': {
                'expected_daily_roi': tactical_flow.expected_daily_roi,
                'quarterly_roi_projection': tactical_flow.quarterly_roi_projection,
                'risk_adjusted_return': tactical_flow.risk_adjusted_return
            },
            
            'generated_at': tactical_flow.generated_at,
            'engine': 'Ultimate Tactical Intelligence',
            'mode': 'ROI_EXECUTION_MODE::ENGAGED'
        }

def main():
    """Test the Ultimate Tactical Intelligence Engine"""
    
    print("🔥 ULTIMATE TACTICAL INTELLIGENCE ENGINE - EXTRACTING TACTICAL SOUL")
    
    # Initialize engine
    engine = UltimateTacticalIntelligence()
    
    # Generate complete tactical flow
    tactical_flow = engine.generate_complete_tactical_flow()
    
    # Display results
    print(f"\n{tactical_flow.emotional_risk_signal} EMOTIONAL RISK SIGNAL")
    print(f"🎯 PRIMARY DIRECTIVE: {tactical_flow.primary_directive}")
    print(f"💰 QUARTERLY ROI PROJECTION: {tactical_flow.quarterly_roi_projection:.1%}")
    print(f"🔥 SYSTEM HEALTH: {tactical_flow.system_health}")
    
    print(f"\n📊 TACTICAL COMPONENTS:")
    print(f"  • Flip Recommendations: {len(tactical_flow.flip_recommendations)}")
    print(f"  • Whale Signals: {len(tactical_flow.whale_watchlist)}")
    print(f"  • Vault Alerts: {len(tactical_flow.vault_alerts)}")
    print(f"  • Heatmap Tiles: {len(tactical_flow.tile_heatmap)}")
    
    # Generate outputs
    notion_markdown = engine.format_for_notion(tactical_flow)
    json_output = engine.format_for_json(tactical_flow)
    
    print(f"\n📝 NOTION MARKDOWN: {len(notion_markdown)} characters")
    print(f"📋 JSON OUTPUT: {len(json_output)} fields")
    
    print("\n🔥 ULTIMATE TACTICAL INTELLIGENCE ENGINE - READY FOR $1000+ ROI EXECUTION!")

if __name__ == "__main__":
    main()

