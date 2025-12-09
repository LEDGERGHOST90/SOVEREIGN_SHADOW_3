#!/usr/bin/env python3
"""
LLF-ß Advanced ΩSIGIL MetaStack Intelligence Engine
Enhanced pattern recognition with memory echo and cognitive alignment
"""

import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import logging
from collections import deque
import hashlib
import pickle
import sqlite3
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SigilConfidence(Enum):
    """ΩSIGIL confidence levels"""
    TRANSCENDENT = "TRANSCENDENT"  # 95%+
    LEGENDARY = "LEGENDARY"        # 90-95%
    SOVEREIGN = "SOVEREIGN"        # 85-90%
    ELITE = "ELITE"               # 80-85%
    STANDARD = "STANDARD"         # 70-80%
    CAUTION = "CAUTION"           # 60-70%
    HALT = "HALT"                 # <60%

class PatternType(Enum):
    """Pattern recognition types"""
    BREAKOUT = "BREAKOUT"
    RETEST = "RETEST"
    VOLATILITY = "VOLATILITY"
    LIQUIDITY_MIRROR = "LIQUIDITY_MIRROR"
    MEMORY_ECHO = "MEMORY_ECHO"
    COGNITIVE_ALIGNMENT = "COGNITIVE_ALIGNMENT"
    RETROSNIPER = "RETROSNIPER"

@dataclass
class MemoryEcho:
    """Memory echo pattern storage"""
    pattern_id: str
    pattern_type: PatternType
    timestamp: datetime
    market_conditions: Dict
    decision_context: Dict
    outcome: Dict
    ray_score: float
    confidence: float
    cognitive_markers: List[str]
    replay_protection_hash: str

@dataclass
class MetaStackLayer:
    """MetaStack intelligence layer"""
    layer_id: str
    layer_type: str
    weight: float
    confidence: float
    pattern_data: Dict
    memory_references: List[str]
    cognitive_alignment: float
    last_updated: datetime

@dataclass
class RetroSniperProfile:
    """RetroSniper trading profile"""
    profile_id: str
    aggression_mode: str  # STEALTH, STANDARD, ALPHA, SCALP
    ladder_depth: int
    spread_ratio: float
    entry_filter: PatternType
    max_snipes_per_flip: int
    cooldown_period: int
    success_rate: float
    total_snipes: int
    cognitive_score: float

class OmegaSigilMetaStack:
    """
    Advanced ΩSIGIL Intelligence Engine with MetaStack and RetroSniper capabilities
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/app/config/omega_sigil_config.json"
        self.config = self._load_config()
        
        # Initialize components
        self.memory_echoes: deque = deque(maxlen=10000)
        self.metastack_layers: Dict[str, MetaStackLayer] = {}
        self.retrosniper_profiles: Dict[str, RetroSniperProfile] = {}
        
        # Machine learning models
        self.pattern_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.confidence_regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Cognitive alignment system
        self.ray_rules_engine = RayRulesEngine()
        self.cognitive_memory = CognitiveMemorySystem()
        
        # Database for persistent storage
        self.db_path = "/app/data/omega_sigil_metastack.db"
        self._initialize_database()
        
        # Load existing data
        self._load_memory_echoes()
        self._load_metastack_layers()
        self._load_retrosniper_profiles()
        
        # Training data
        self.training_data = []
        self.is_trained = False
        
    def _load_config(self) -> Dict:
        """Load ΩSIGIL configuration"""
        default_config = {
            "ray_score_threshold": 60,
            "confidence_threshold": 0.8,
            "memory_echo_retention": 10000,
            "metastack_layers": 7,
            "retrosniper_cooldown": 120,
            "cognitive_alignment_weight": 0.3,
            "pattern_learning_rate": 0.01,
            "menace_accuracy_target": 0.87,
            "transcendent_threshold": 0.95,
            "quantum_resistance": True
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            
        return default_config
    
    def _initialize_database(self):
        """Initialize SQLite database for persistent storage"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Memory echoes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_echoes (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    timestamp TEXT,
                    market_conditions TEXT,
                    decision_context TEXT,
                    outcome TEXT,
                    ray_score REAL,
                    confidence REAL,
                    cognitive_markers TEXT,
                    replay_protection_hash TEXT
                )
            ''')
            
            # MetaStack layers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metastack_layers (
                    layer_id TEXT PRIMARY KEY,
                    layer_type TEXT,
                    weight REAL,
                    confidence REAL,
                    pattern_data TEXT,
                    memory_references TEXT,
                    cognitive_alignment REAL,
                    last_updated TEXT
                )
            ''')
            
            # RetroSniper profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS retrosniper_profiles (
                    profile_id TEXT PRIMARY KEY,
                    aggression_mode TEXT,
                    ladder_depth INTEGER,
                    spread_ratio REAL,
                    entry_filter TEXT,
                    max_snipes_per_flip INTEGER,
                    cooldown_period INTEGER,
                    success_rate REAL,
                    total_snipes INTEGER,
                    cognitive_score REAL
                )
            ''')
            
            conn.commit()
    
    def _load_memory_echoes(self):
        """Load memory echoes from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM memory_echoes ORDER BY timestamp DESC LIMIT 1000')
                
                for row in cursor.fetchall():
                    echo = MemoryEcho(
                        pattern_id=row[0],
                        pattern_type=PatternType(row[1]),
                        timestamp=datetime.fromisoformat(row[2]),
                        market_conditions=json.loads(row[3]),
                        decision_context=json.loads(row[4]),
                        outcome=json.loads(row[5]),
                        ray_score=row[6],
                        confidence=row[7],
                        cognitive_markers=json.loads(row[8]),
                        replay_protection_hash=row[9]
                    )
                    self.memory_echoes.append(echo)
                    
        except Exception as e:
            logger.error(f"Failed to load memory echoes: {e}")
    
    def _load_metastack_layers(self):
        """Load MetaStack layers from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM metastack_layers')
                
                for row in cursor.fetchall():
                    layer = MetaStackLayer(
                        layer_id=row[0],
                        layer_type=row[1],
                        weight=row[2],
                        confidence=row[3],
                        pattern_data=json.loads(row[4]),
                        memory_references=json.loads(row[5]),
                        cognitive_alignment=row[6],
                        last_updated=datetime.fromisoformat(row[7])
                    )
                    self.metastack_layers[layer.layer_id] = layer
                    
        except Exception as e:
            logger.error(f"Failed to load MetaStack layers: {e}")
    
    def _load_retrosniper_profiles(self):
        """Load RetroSniper profiles from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM retrosniper_profiles')
                
                for row in cursor.fetchall():
                    profile = RetroSniperProfile(
                        profile_id=row[0],
                        aggression_mode=row[1],
                        ladder_depth=row[2],
                        spread_ratio=row[3],
                        entry_filter=PatternType(row[4]),
                        max_snipes_per_flip=row[5],
                        cooldown_period=row[6],
                        success_rate=row[7],
                        total_snipes=row[8],
                        cognitive_score=row[9]
                    )
                    self.retrosniper_profiles[profile.profile_id] = profile
                    
        except Exception as e:
            logger.error(f"Failed to load RetroSniper profiles: {e}")
    
    async def create_memory_echo(self, pattern_data: Dict, decision_context: Dict, outcome: Dict) -> MemoryEcho:
        """Create a new memory echo from trading pattern"""
        try:
            # Generate pattern ID
            pattern_id = self._generate_pattern_id(pattern_data, decision_context)
            
            # Calculate Ray Score using cognitive alignment
            ray_score = await self.ray_rules_engine.calculate_ray_score(decision_context)
            
            # Determine pattern type
            pattern_type = self._classify_pattern_type(pattern_data)
            
            # Calculate confidence
            confidence = self._calculate_pattern_confidence(pattern_data, outcome)
            
            # Extract cognitive markers
            cognitive_markers = self._extract_cognitive_markers(decision_context)
            
            # Generate replay protection hash
            replay_hash = self._generate_replay_protection_hash(pattern_data, decision_context)
            
            # Create memory echo
            echo = MemoryEcho(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                timestamp=datetime.now(),
                market_conditions=pattern_data.get('market_conditions', {}),
                decision_context=decision_context,
                outcome=outcome,
                ray_score=ray_score,
                confidence=confidence,
                cognitive_markers=cognitive_markers,
                replay_protection_hash=replay_hash
            )
            
            # Store in memory and database
            self.memory_echoes.append(echo)
            await self._save_memory_echo(echo)
            
            # Update MetaStack layers
            await self._update_metastack_layers(echo)
            
            logger.info(f"Created memory echo: {pattern_id} (Ray Score: {ray_score:.2f})")
            return echo
            
        except Exception as e:
            logger.error(f"Failed to create memory echo: {e}")
            raise
    
    def _generate_pattern_id(self, pattern_data: Dict, decision_context: Dict) -> str:
        """Generate unique pattern ID"""
        data_str = json.dumps({**pattern_data, **decision_context}, sort_keys=True)
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{data_str}_{timestamp}".encode()).hexdigest()[:16]
    
    def _classify_pattern_type(self, pattern_data: Dict) -> PatternType:
        """Classify pattern type based on market data"""
        # Simplified classification logic
        volatility = pattern_data.get('volatility', 0)
        volume_spike = pattern_data.get('volume_spike', False)
        price_action = pattern_data.get('price_action', {})
        
        if volume_spike and volatility > 0.05:
            return PatternType.BREAKOUT
        elif price_action.get('retest_level'):
            return PatternType.RETEST
        elif volatility > 0.03:
            return PatternType.VOLATILITY
        else:
            return PatternType.LIQUIDITY_MIRROR
    
    def _calculate_pattern_confidence(self, pattern_data: Dict, outcome: Dict) -> float:
        """Calculate pattern confidence based on outcome"""
        success = outcome.get('success', False)
        profit_ratio = outcome.get('profit_ratio', 0)
        
        base_confidence = 0.5
        
        if success:
            base_confidence += 0.3
        
        if profit_ratio > 0.1:
            base_confidence += 0.2
        elif profit_ratio > 0.05:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _extract_cognitive_markers(self, decision_context: Dict) -> List[str]:
        """Extract cognitive alignment markers"""
        markers = []
        
        # Check for Ray Rules application
        if decision_context.get('ray_rules_applied'):
            markers.append('RAY_RULES_APPLIED')
        
        # Check for emotional state
        emotional_state = decision_context.get('emotional_state', 'neutral')
        if emotional_state in ['calm', 'confident']:
            markers.append('POSITIVE_EMOTIONAL_STATE')
        elif emotional_state in ['fear', 'greed', 'fomo']:
            markers.append('NEGATIVE_EMOTIONAL_STATE')
        
        # Check for time horizon alignment
        time_horizon = decision_context.get('time_horizon', 'short')
        if time_horizon == 'long':
            markers.append('LONG_TERM_THINKING')
        
        # Check for value alignment
        if decision_context.get('value_aligned', False):
            markers.append('VALUE_ALIGNED')
        
        return markers
    
    def _generate_replay_protection_hash(self, pattern_data: Dict, decision_context: Dict) -> str:
        """Generate replay protection hash"""
        combined_data = {
            **pattern_data,
            **decision_context,
            'timestamp': datetime.now().isoformat(),
            'nonce': os.urandom(16).hex()
        }
        
        data_str = json.dumps(combined_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _save_memory_echo(self, echo: MemoryEcho):
        """Save memory echo to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO memory_echoes 
                    (pattern_id, pattern_type, timestamp, market_conditions, decision_context, 
                     outcome, ray_score, confidence, cognitive_markers, replay_protection_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    echo.pattern_id,
                    echo.pattern_type.value,
                    echo.timestamp.isoformat(),
                    json.dumps(echo.market_conditions),
                    json.dumps(echo.decision_context),
                    json.dumps(echo.outcome),
                    echo.ray_score,
                    echo.confidence,
                    json.dumps(echo.cognitive_markers),
                    echo.replay_protection_hash
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save memory echo: {e}")
    
    async def _update_metastack_layers(self, echo: MemoryEcho):
        """Update MetaStack layers based on new memory echo"""
        try:
            # Update pattern recognition layer
            await self._update_pattern_layer(echo)
            
            # Update cognitive alignment layer
            await self._update_cognitive_layer(echo)
            
            # Update confidence layer
            await self._update_confidence_layer(echo)
            
            # Update memory correlation layer
            await self._update_memory_correlation_layer(echo)
            
        except Exception as e:
            logger.error(f"Failed to update MetaStack layers: {e}")
    
    async def _update_pattern_layer(self, echo: MemoryEcho):
        """Update pattern recognition layer"""
        layer_id = "pattern_recognition"
        
        existing_layer = self.metastack_layers.get(layer_id)
        
        if existing_layer:
            # Update existing layer
            existing_layer.confidence = (existing_layer.confidence + echo.confidence) / 2
            existing_layer.pattern_data['recent_patterns'] = existing_layer.pattern_data.get('recent_patterns', [])
            existing_layer.pattern_data['recent_patterns'].append({
                'pattern_id': echo.pattern_id,
                'pattern_type': echo.pattern_type.value,
                'confidence': echo.confidence
            })
            
            # Keep only last 100 patterns
            if len(existing_layer.pattern_data['recent_patterns']) > 100:
                existing_layer.pattern_data['recent_patterns'] = existing_layer.pattern_data['recent_patterns'][-100:]
            
            existing_layer.last_updated = datetime.now()
        else:
            # Create new layer
            layer = MetaStackLayer(
                layer_id=layer_id,
                layer_type="PATTERN_RECOGNITION",
                weight=0.25,
                confidence=echo.confidence,
                pattern_data={
                    'recent_patterns': [{
                        'pattern_id': echo.pattern_id,
                        'pattern_type': echo.pattern_type.value,
                        'confidence': echo.confidence
                    }]
                },
                memory_references=[echo.pattern_id],
                cognitive_alignment=echo.ray_score / 100.0,
                last_updated=datetime.now()
            )
            self.metastack_layers[layer_id] = layer
        
        await self._save_metastack_layer(self.metastack_layers[layer_id])
    
    async def _update_cognitive_layer(self, echo: MemoryEcho):
        """Update cognitive alignment layer"""
        layer_id = "cognitive_alignment"
        
        existing_layer = self.metastack_layers.get(layer_id)
        
        cognitive_score = echo.ray_score / 100.0
        
        if existing_layer:
            # Update cognitive alignment score
            existing_layer.cognitive_alignment = (existing_layer.cognitive_alignment + cognitive_score) / 2
            existing_layer.pattern_data['cognitive_markers'] = existing_layer.pattern_data.get('cognitive_markers', {})
            
            # Update cognitive markers frequency
            for marker in echo.cognitive_markers:
                existing_layer.pattern_data['cognitive_markers'][marker] = existing_layer.pattern_data['cognitive_markers'].get(marker, 0) + 1
            
            existing_layer.last_updated = datetime.now()
        else:
            # Create new cognitive layer
            layer = MetaStackLayer(
                layer_id=layer_id,
                layer_type="COGNITIVE_ALIGNMENT",
                weight=0.3,
                confidence=cognitive_score,
                pattern_data={
                    'cognitive_markers': {marker: 1 for marker in echo.cognitive_markers},
                    'ray_score_history': [echo.ray_score]
                },
                memory_references=[echo.pattern_id],
                cognitive_alignment=cognitive_score,
                last_updated=datetime.now()
            )
            self.metastack_layers[layer_id] = layer
        
        await self._save_metastack_layer(self.metastack_layers[layer_id])
    
    async def _update_confidence_layer(self, echo: MemoryEcho):
        """Update confidence calculation layer"""
        layer_id = "confidence_calculation"
        
        existing_layer = self.metastack_layers.get(layer_id)
        
        if existing_layer:
            # Update confidence metrics
            existing_layer.confidence = (existing_layer.confidence + echo.confidence) / 2
            existing_layer.pattern_data['confidence_history'] = existing_layer.pattern_data.get('confidence_history', [])
            existing_layer.pattern_data['confidence_history'].append(echo.confidence)
            
            # Keep only last 1000 confidence scores
            if len(existing_layer.pattern_data['confidence_history']) > 1000:
                existing_layer.pattern_data['confidence_history'] = existing_layer.pattern_data['confidence_history'][-1000:]
            
            existing_layer.last_updated = datetime.now()
        else:
            # Create new confidence layer
            layer = MetaStackLayer(
                layer_id=layer_id,
                layer_type="CONFIDENCE_CALCULATION",
                weight=0.2,
                confidence=echo.confidence,
                pattern_data={
                    'confidence_history': [echo.confidence],
                    'accuracy_metrics': {}
                },
                memory_references=[echo.pattern_id],
                cognitive_alignment=echo.ray_score / 100.0,
                last_updated=datetime.now()
            )
            self.metastack_layers[layer_id] = layer
        
        await self._save_metastack_layer(self.metastack_layers[layer_id])
    
    async def _update_memory_correlation_layer(self, echo: MemoryEcho):
        """Update memory correlation layer"""
        layer_id = "memory_correlation"
        
        # Find similar patterns in memory
        similar_patterns = await self._find_similar_patterns(echo)
        
        existing_layer = self.metastack_layers.get(layer_id)
        
        if existing_layer:
            # Update correlation data
            existing_layer.pattern_data['correlations'] = existing_layer.pattern_data.get('correlations', {})
            existing_layer.pattern_data['correlations'][echo.pattern_id] = [p.pattern_id for p in similar_patterns]
            existing_layer.memory_references.append(echo.pattern_id)
            
            # Keep only last 1000 memory references
            if len(existing_layer.memory_references) > 1000:
                existing_layer.memory_references = existing_layer.memory_references[-1000:]
            
            existing_layer.last_updated = datetime.now()
        else:
            # Create new correlation layer
            layer = MetaStackLayer(
                layer_id=layer_id,
                layer_type="MEMORY_CORRELATION",
                weight=0.15,
                confidence=echo.confidence,
                pattern_data={
                    'correlations': {echo.pattern_id: [p.pattern_id for p in similar_patterns]}
                },
                memory_references=[echo.pattern_id],
                cognitive_alignment=echo.ray_score / 100.0,
                last_updated=datetime.now()
            )
            self.metastack_layers[layer_id] = layer
        
        await self._save_metastack_layer(self.metastack_layers[layer_id])
    
    async def _find_similar_patterns(self, echo: MemoryEcho, similarity_threshold: float = 0.7) -> List[MemoryEcho]:
        """Find similar patterns in memory echoes"""
        similar_patterns = []
        
        for existing_echo in self.memory_echoes:
            if existing_echo.pattern_id == echo.pattern_id:
                continue
            
            # Calculate similarity based on multiple factors
            similarity = self._calculate_pattern_similarity(echo, existing_echo)
            
            if similarity >= similarity_threshold:
                similar_patterns.append(existing_echo)
        
        # Sort by similarity (highest first)
        similar_patterns.sort(key=lambda x: self._calculate_pattern_similarity(echo, x), reverse=True)
        
        return similar_patterns[:10]  # Return top 10 similar patterns
    
    def _calculate_pattern_similarity(self, echo1: MemoryEcho, echo2: MemoryEcho) -> float:
        """Calculate similarity between two memory echoes"""
        similarity_score = 0.0
        
        # Pattern type similarity
        if echo1.pattern_type == echo2.pattern_type:
            similarity_score += 0.3
        
        # Ray score similarity
        ray_score_diff = abs(echo1.ray_score - echo2.ray_score)
        ray_similarity = max(0, 1 - (ray_score_diff / 100))
        similarity_score += ray_similarity * 0.2
        
        # Cognitive markers similarity
        common_markers = set(echo1.cognitive_markers) & set(echo2.cognitive_markers)
        total_markers = set(echo1.cognitive_markers) | set(echo2.cognitive_markers)
        
        if total_markers:
            marker_similarity = len(common_markers) / len(total_markers)
            similarity_score += marker_similarity * 0.3
        
        # Confidence similarity
        confidence_diff = abs(echo1.confidence - echo2.confidence)
        confidence_similarity = max(0, 1 - confidence_diff)
        similarity_score += confidence_similarity * 0.2
        
        return similarity_score
    
    async def _save_metastack_layer(self, layer: MetaStackLayer):
        """Save MetaStack layer to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO metastack_layers 
                    (layer_id, layer_type, weight, confidence, pattern_data, 
                     memory_references, cognitive_alignment, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    layer.layer_id,
                    layer.layer_type,
                    layer.weight,
                    layer.confidence,
                    json.dumps(layer.pattern_data),
                    json.dumps(layer.memory_references),
                    layer.cognitive_alignment,
                    layer.last_updated.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save MetaStack layer: {e}")
    
    async def calculate_omega_sigil_intelligence(self, market_data: Dict, decision_context: Dict = None) -> Dict:
        """Calculate comprehensive ΩSIGIL intelligence"""
        try:
            # Initialize intelligence components
            intelligence = {
                'ray_score': 0.0,
                'confidence_level': SigilConfidence.HALT,
                'pattern_recognition': {},
                'memory_echo_analysis': {},
                'cognitive_alignment': {},
                'metastack_synthesis': {},
                'retrosniper_recommendation': {},
                'menace_accuracy': 0.0,
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate Ray Score
            if decision_context:
                intelligence['ray_score'] = await self.ray_rules_engine.calculate_ray_score(decision_context)
            
            # Pattern recognition analysis
            intelligence['pattern_recognition'] = await self._analyze_patterns(market_data)
            
            # Memory echo analysis
            intelligence['memory_echo_analysis'] = await self._analyze_memory_echoes(market_data)
            
            # Cognitive alignment assessment
            intelligence['cognitive_alignment'] = await self._assess_cognitive_alignment(decision_context)
            
            # MetaStack synthesis
            intelligence['metastack_synthesis'] = await self._synthesize_metastack(market_data, decision_context)
            
            # RetroSniper recommendation
            intelligence['retrosniper_recommendation'] = await self._generate_retrosniper_recommendation(market_data, intelligence)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(intelligence)
            intelligence['confidence_level'] = self._determine_confidence_level(overall_confidence)
            
            # Calculate MENACE accuracy
            intelligence['menace_accuracy'] = await self._calculate_menace_accuracy()
            
            logger.info(f"ΩSIGIL Intelligence calculated: Ray Score {intelligence['ray_score']:.2f}, Confidence {intelligence['confidence_level'].value}")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Failed to calculate ΩSIGIL intelligence: {e}")
            return {
                'ray_score': 0.0,
                'confidence_level': SigilConfidence.HALT,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_patterns(self, market_data: Dict) -> Dict:
        """Analyze current market patterns"""
        try:
            patterns = {
                'detected_patterns': [],
                'pattern_strength': 0.0,
                'historical_success_rate': 0.0,
                'pattern_confidence': 0.0
            }
            
            # Detect current patterns
            current_patterns = self._detect_current_patterns(market_data)
            patterns['detected_patterns'] = current_patterns
            
            # Calculate pattern strength
            patterns['pattern_strength'] = self._calculate_pattern_strength(current_patterns, market_data)
            
            # Calculate historical success rate
            patterns['historical_success_rate'] = await self._calculate_historical_success_rate(current_patterns)
            
            # Calculate pattern confidence
            patterns['pattern_confidence'] = (patterns['pattern_strength'] + patterns['historical_success_rate']) / 2
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_current_patterns(self, market_data: Dict) -> List[Dict]:
        """Detect current market patterns"""
        patterns = []
        
        # Price action patterns
        price_data = market_data.get('price_data', {})
        if price_data:
            # Breakout pattern
            if self._is_breakout_pattern(price_data):
                patterns.append({
                    'type': PatternType.BREAKOUT.value,
                    'strength': self._calculate_breakout_strength(price_data),
                    'timeframe': market_data.get('timeframe', '1h')
                })
            
            # Retest pattern
            if self._is_retest_pattern(price_data):
                patterns.append({
                    'type': PatternType.RETEST.value,
                    'strength': self._calculate_retest_strength(price_data),
                    'timeframe': market_data.get('timeframe', '1h')
                })
        
        # Volume patterns
        volume_data = market_data.get('volume_data', {})
        if volume_data:
            if self._is_volume_spike(volume_data):
                patterns.append({
                    'type': 'VOLUME_SPIKE',
                    'strength': self._calculate_volume_strength(volume_data),
                    'timeframe': market_data.get('timeframe', '1h')
                })
        
        return patterns
    
    def _is_breakout_pattern(self, price_data: Dict) -> bool:
        """Check if current price action indicates breakout"""
        # Simplified breakout detection
        current_price = price_data.get('current_price', 0)
        resistance_level = price_data.get('resistance_level', 0)
        volume_increase = price_data.get('volume_increase', False)
        
        return current_price > resistance_level and volume_increase
    
    def _is_retest_pattern(self, price_data: Dict) -> bool:
        """Check if current price action indicates retest"""
        current_price = price_data.get('current_price', 0)
        support_level = price_data.get('support_level', 0)
        previous_bounce = price_data.get('previous_bounce', False)
        
        return abs(current_price - support_level) / support_level < 0.02 and previous_bounce
    
    def _is_volume_spike(self, volume_data: Dict) -> bool:
        """Check for volume spike"""
        current_volume = volume_data.get('current_volume', 0)
        average_volume = volume_data.get('average_volume', 0)
        
        return current_volume > average_volume * 2
    
    def _calculate_breakout_strength(self, price_data: Dict) -> float:
        """Calculate breakout pattern strength"""
        price_momentum = price_data.get('price_momentum', 0)
        volume_ratio = price_data.get('volume_ratio', 1)
        
        return min(1.0, (price_momentum * 0.6 + volume_ratio * 0.4))
    
    def _calculate_retest_strength(self, price_data: Dict) -> float:
        """Calculate retest pattern strength"""
        support_strength = price_data.get('support_strength', 0.5)
        bounce_count = price_data.get('bounce_count', 1)
        
        return min(1.0, support_strength * (1 + bounce_count * 0.1))
    
    def _calculate_volume_strength(self, volume_data: Dict) -> float:
        """Calculate volume pattern strength"""
        volume_ratio = volume_data.get('volume_ratio', 1)
        return min(1.0, volume_ratio / 5)  # Normalize to 0-1 scale
    
    def _calculate_pattern_strength(self, patterns: List[Dict], market_data: Dict) -> float:
        """Calculate overall pattern strength"""
        if not patterns:
            return 0.0
        
        total_strength = sum(pattern.get('strength', 0) for pattern in patterns)
        return total_strength / len(patterns)
    
    async def _calculate_historical_success_rate(self, patterns: List[Dict]) -> float:
        """Calculate historical success rate for detected patterns"""
        if not patterns:
            return 0.0
        
        success_rates = []
        
        for pattern in patterns:
            pattern_type = pattern.get('type')
            
            # Find historical patterns of same type
            historical_patterns = [
                echo for echo in self.memory_echoes
                if echo.pattern_type.value == pattern_type
            ]
            
            if historical_patterns:
                successful_patterns = [
                    echo for echo in historical_patterns
                    if echo.outcome.get('success', False)
                ]
                
                success_rate = len(successful_patterns) / len(historical_patterns)
                success_rates.append(success_rate)
        
        return sum(success_rates) / len(success_rates) if success_rates else 0.0
    
    async def _analyze_memory_echoes(self, market_data: Dict) -> Dict:
        """Analyze relevant memory echoes"""
        try:
            analysis = {
                'relevant_echoes': [],
                'pattern_correlations': {},
                'success_probability': 0.0,
                'risk_assessment': {}
            }
            
            # Find relevant memory echoes
            relevant_echoes = await self._find_relevant_echoes(market_data)
            analysis['relevant_echoes'] = [
                {
                    'pattern_id': echo.pattern_id,
                    'pattern_type': echo.pattern_type.value,
                    'ray_score': echo.ray_score,
                    'confidence': echo.confidence,
                    'outcome': echo.outcome
                }
                for echo in relevant_echoes[:10]  # Top 10 relevant echoes
            ]
            
            # Calculate success probability based on relevant echoes
            if relevant_echoes:
                successful_echoes = [echo for echo in relevant_echoes if echo.outcome.get('success', False)]
                analysis['success_probability'] = len(successful_echoes) / len(relevant_echoes)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Memory echo analysis failed: {e}")
            return {'error': str(e)}
    
    async def _find_relevant_echoes(self, market_data: Dict, limit: int = 50) -> List[MemoryEcho]:
        """Find memory echoes relevant to current market conditions"""
        relevant_echoes = []
        
        current_volatility = market_data.get('volatility', 0)
        current_trend = market_data.get('trend', 'neutral')
        
        for echo in self.memory_echoes:
            # Calculate relevance score
            relevance_score = 0.0
            
            # Volatility similarity
            echo_volatility = echo.market_conditions.get('volatility', 0)
            volatility_diff = abs(current_volatility - echo_volatility)
            volatility_similarity = max(0, 1 - volatility_diff)
            relevance_score += volatility_similarity * 0.3
            
            # Trend similarity
            echo_trend = echo.market_conditions.get('trend', 'neutral')
            if current_trend == echo_trend:
                relevance_score += 0.3
            
            # Time relevance (more recent echoes are more relevant)
            time_diff = datetime.now() - echo.timestamp
            time_relevance = max(0, 1 - (time_diff.days / 30))  # Decay over 30 days
            relevance_score += time_relevance * 0.2
            
            # Ray score relevance (higher Ray scores are more relevant)
            ray_relevance = echo.ray_score / 100.0
            relevance_score += ray_relevance * 0.2
            
            if relevance_score > 0.5:  # Threshold for relevance
                relevant_echoes.append((echo, relevance_score))
        
        # Sort by relevance score
        relevant_echoes.sort(key=lambda x: x[1], reverse=True)
        
        return [echo for echo, score in relevant_echoes[:limit]]
    
    async def _assess_cognitive_alignment(self, decision_context: Dict) -> Dict:
        """Assess cognitive alignment with Ray's principles"""
        if not decision_context:
            return {'alignment_score': 0.0, 'assessment': 'No decision context provided'}
        
        try:
            assessment = {
                'alignment_score': 0.0,
                'ray_rules_compliance': {},
                'cognitive_markers': [],
                'recommendations': []
            }
            
            # Calculate Ray Rules compliance
            ray_compliance = await self.ray_rules_engine.assess_compliance(decision_context)
            assessment['ray_rules_compliance'] = ray_compliance
            
            # Calculate overall alignment score
            assessment['alignment_score'] = ray_compliance.get('overall_score', 0.0)
            
            # Extract cognitive markers
            assessment['cognitive_markers'] = self._extract_cognitive_markers(decision_context)
            
            # Generate recommendations
            assessment['recommendations'] = await self._generate_cognitive_recommendations(ray_compliance)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Cognitive alignment assessment failed: {e}")
            return {'error': str(e)}
    
    async def _generate_cognitive_recommendations(self, ray_compliance: Dict) -> List[str]:
        """Generate cognitive alignment recommendations"""
        recommendations = []
        
        overall_score = ray_compliance.get('overall_score', 0.0)
        
        if overall_score < 60:
            recommendations.append("Consider pausing to reassess decision clarity")
            recommendations.append("Apply Ray Rules framework before proceeding")
        
        if overall_score < 80:
            recommendations.append("Review long-term value alignment")
            recommendations.append("Consider emotional state impact on decision")
        
        # Specific rule recommendations
        for rule, score in ray_compliance.get('rule_scores', {}).items():
            if score < 70:
                recommendations.append(f"Focus on improving {rule} alignment")
        
        return recommendations
    
    async def _synthesize_metastack(self, market_data: Dict, decision_context: Dict) -> Dict:
        """Synthesize MetaStack layer intelligence"""
        try:
            synthesis = {
                'layer_contributions': {},
                'weighted_confidence': 0.0,
                'consensus_signal': 'NEUTRAL',
                'layer_conflicts': []
            }
            
            total_weight = 0.0
            weighted_confidence_sum = 0.0
            
            # Analyze each MetaStack layer
            for layer_id, layer in self.metastack_layers.items():
                layer_contribution = await self._analyze_layer_contribution(layer, market_data, decision_context)
                synthesis['layer_contributions'][layer_id] = layer_contribution
                
                # Calculate weighted confidence
                weighted_confidence_sum += layer.confidence * layer.weight
                total_weight += layer.weight
            
            # Calculate overall weighted confidence
            if total_weight > 0:
                synthesis['weighted_confidence'] = weighted_confidence_sum / total_weight
            
            # Determine consensus signal
            synthesis['consensus_signal'] = self._determine_consensus_signal(synthesis['layer_contributions'])
            
            # Identify layer conflicts
            synthesis['layer_conflicts'] = self._identify_layer_conflicts(synthesis['layer_contributions'])
            
            return synthesis
            
        except Exception as e:
            logger.error(f"MetaStack synthesis failed: {e}")
            return {'error': str(e)}
    
    async def _analyze_layer_contribution(self, layer: MetaStackLayer, market_data: Dict, decision_context: Dict) -> Dict:
        """Analyze individual layer contribution"""
        contribution = {
            'layer_type': layer.layer_type,
            'confidence': layer.confidence,
            'weight': layer.weight,
            'signal': 'NEUTRAL',
            'reasoning': []
        }
        
        if layer.layer_type == "PATTERN_RECOGNITION":
            # Analyze pattern layer
            recent_patterns = layer.pattern_data.get('recent_patterns', [])
            if recent_patterns:
                avg_confidence = sum(p.get('confidence', 0) for p in recent_patterns) / len(recent_patterns)
                if avg_confidence > 0.7:
                    contribution['signal'] = 'BULLISH'
                    contribution['reasoning'].append(f"Strong pattern confidence: {avg_confidence:.2f}")
                elif avg_confidence < 0.3:
                    contribution['signal'] = 'BEARISH'
                    contribution['reasoning'].append(f"Weak pattern confidence: {avg_confidence:.2f}")
        
        elif layer.layer_type == "COGNITIVE_ALIGNMENT":
            # Analyze cognitive layer
            if layer.cognitive_alignment > 0.8:
                contribution['signal'] = 'BULLISH'
                contribution['reasoning'].append(f"High cognitive alignment: {layer.cognitive_alignment:.2f}")
            elif layer.cognitive_alignment < 0.6:
                contribution['signal'] = 'BEARISH'
                contribution['reasoning'].append(f"Low cognitive alignment: {layer.cognitive_alignment:.2f}")
        
        return contribution
    
    def _determine_consensus_signal(self, layer_contributions: Dict) -> str:
        """Determine consensus signal from layer contributions"""
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for contribution in layer_contributions.values():
            signal = contribution.get('signal', 'NEUTRAL')
            if signal == 'BULLISH':
                bullish_count += 1
            elif signal == 'BEARISH':
                bearish_count += 1
            else:
                neutral_count += 1
        
        if bullish_count > bearish_count and bullish_count > neutral_count:
            return 'BULLISH'
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _identify_layer_conflicts(self, layer_contributions: Dict) -> List[str]:
        """Identify conflicts between layer signals"""
        conflicts = []
        
        signals = [contrib.get('signal', 'NEUTRAL') for contrib in layer_contributions.values()]
        
        if 'BULLISH' in signals and 'BEARISH' in signals:
            conflicts.append("Conflicting bullish and bearish signals detected")
        
        # Check for high confidence conflicts
        high_conf_bullish = [
            layer_id for layer_id, contrib in layer_contributions.items()
            if contrib.get('signal') == 'BULLISH' and contrib.get('confidence', 0) > 0.8
        ]
        
        high_conf_bearish = [
            layer_id for layer_id, contrib in layer_contributions.items()
            if contrib.get('signal') == 'BEARISH' and contrib.get('confidence', 0) > 0.8
        ]
        
        if high_conf_bullish and high_conf_bearish:
            conflicts.append(f"High confidence conflict: {high_conf_bullish} vs {high_conf_bearish}")
        
        return conflicts
    
    async def _generate_retrosniper_recommendation(self, market_data: Dict, intelligence: Dict) -> Dict:
        """Generate RetroSniper trading recommendation"""
        try:
            recommendation = {
                'action': 'HOLD',
                'confidence': 0.0,
                'profile_recommendation': 'STEALTH',
                'entry_points': [],
                'risk_assessment': {},
                'sniper_parameters': {}
            }
            
            # Determine action based on intelligence
            ray_score = intelligence.get('ray_score', 0)
            pattern_confidence = intelligence.get('pattern_recognition', {}).get('pattern_confidence', 0)
            memory_success_prob = intelligence.get('memory_echo_analysis', {}).get('success_probability', 0)
            
            # Calculate overall confidence
            overall_confidence = (ray_score/100 + pattern_confidence + memory_success_prob) / 3
            recommendation['confidence'] = overall_confidence
            
            # Determine action
            if overall_confidence > 0.8 and ray_score > 80:
                recommendation['action'] = 'BUY'
                recommendation['profile_recommendation'] = 'ALPHA'
            elif overall_confidence > 0.6 and ray_score > 60:
                recommendation['action'] = 'BUY'
                recommendation['profile_recommendation'] = 'STANDARD'
            elif overall_confidence < 0.4 or ray_score < 60:
                recommendation['action'] = 'HALT'
                recommendation['profile_recommendation'] = 'STEALTH'
            
            # Generate sniper parameters
            recommendation['sniper_parameters'] = await self._generate_sniper_parameters(
                recommendation['profile_recommendation'], 
                market_data, 
                overall_confidence
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"RetroSniper recommendation failed: {e}")
            return {'error': str(e)}
    
    async def _generate_sniper_parameters(self, profile: str, market_data: Dict, confidence: float) -> Dict:
        """Generate sniper parameters based on profile and market conditions"""
        base_params = {
            'STEALTH': {
                'ladder_depth': 3,
                'spread_ratio': 0.3,
                'aggression_mode': 'STEALTH',
                'max_snipes_per_flip': 1,
                'cooldown_period': 300
            },
            'STANDARD': {
                'ladder_depth': 5,
                'spread_ratio': 0.5,
                'aggression_mode': 'STANDARD',
                'max_snipes_per_flip': 2,
                'cooldown_period': 180
            },
            'ALPHA': {
                'ladder_depth': 7,
                'spread_ratio': 0.8,
                'aggression_mode': 'ALPHA',
                'max_snipes_per_flip': 3,
                'cooldown_period': 120
            }
        }
        
        params = base_params.get(profile, base_params['STEALTH']).copy()
        
        # Adjust based on market volatility
        volatility = market_data.get('volatility', 0.02)
        if volatility > 0.05:
            params['spread_ratio'] *= 1.5  # Wider spreads in high volatility
            params['cooldown_period'] *= 1.2  # Longer cooldown
        
        # Adjust based on confidence
        if confidence > 0.9:
            params['max_snipes_per_flip'] += 1
            params['cooldown_period'] *= 0.8
        elif confidence < 0.6:
            params['max_snipes_per_flip'] = max(1, params['max_snipes_per_flip'] - 1)
            params['cooldown_period'] *= 1.5
        
        return params
    
    def _calculate_overall_confidence(self, intelligence: Dict) -> float:
        """Calculate overall confidence from intelligence components"""
        components = [
            intelligence.get('ray_score', 0) / 100.0,  # Normalize to 0-1
            intelligence.get('pattern_recognition', {}).get('pattern_confidence', 0),
            intelligence.get('memory_echo_analysis', {}).get('success_probability', 0),
            intelligence.get('cognitive_alignment', {}).get('alignment_score', 0) / 100.0,
            intelligence.get('metastack_synthesis', {}).get('weighted_confidence', 0)
        ]
        
        # Filter out zero values
        valid_components = [c for c in components if c > 0]
        
        if valid_components:
            return sum(valid_components) / len(valid_components)
        else:
            return 0.0
    
    def _determine_confidence_level(self, confidence: float) -> SigilConfidence:
        """Determine confidence level from numeric confidence"""
        if confidence >= 0.95:
            return SigilConfidence.TRANSCENDENT
        elif confidence >= 0.90:
            return SigilConfidence.LEGENDARY
        elif confidence >= 0.85:
            return SigilConfidence.SOVEREIGN
        elif confidence >= 0.80:
            return SigilConfidence.ELITE
        elif confidence >= 0.70:
            return SigilConfidence.STANDARD
        elif confidence >= 0.60:
            return SigilConfidence.CAUTION
        else:
            return SigilConfidence.HALT
    
    async def _calculate_menace_accuracy(self) -> float:
        """Calculate MENACE system accuracy"""
        try:
            # Get recent predictions and outcomes
            recent_echoes = list(self.memory_echoes)[-100:]  # Last 100 echoes
            
            if not recent_echoes:
                return 0.0
            
            # Calculate accuracy based on prediction vs outcome
            correct_predictions = 0
            total_predictions = 0
            
            for echo in recent_echoes:
                if echo.outcome.get('prediction_made', False):
                    total_predictions += 1
                    predicted_success = echo.confidence > 0.7
                    actual_success = echo.outcome.get('success', False)
                    
                    if predicted_success == actual_success:
                        correct_predictions += 1
            
            if total_predictions > 0:
                accuracy = correct_predictions / total_predictions
                return accuracy
            else:
                return self.config.get('menace_accuracy_target', 0.87)  # Default target
                
        except Exception as e:
            logger.error(f"MENACE accuracy calculation failed: {e}")
            return 0.0


class RayRulesEngine:
    """
    Ray Rules cognitive alignment engine
    """
    
    def __init__(self):
        self.rules = {
            'rule_1': {'weight': 0.2, 'description': 'Long-term value creation'},
            'rule_2': {'weight': 0.2, 'description': 'Emotional state awareness'},
            'rule_3': {'weight': 0.2, 'description': 'Risk-reward alignment'},
            'rule_4': {'weight': 0.2, 'description': 'Cognitive clarity'},
            'rule_5': {'weight': 0.2, 'description': 'Legacy consideration'}
        }
    
    async def calculate_ray_score(self, decision_context: Dict) -> float:
        """Calculate Ray Score based on decision context"""
        try:
            total_score = 0.0
            
            for rule_id, rule_config in self.rules.items():
                rule_score = await self._evaluate_rule(rule_id, decision_context)
                weighted_score = rule_score * rule_config['weight']
                total_score += weighted_score
            
            return min(100.0, total_score * 100)  # Scale to 0-100
            
        except Exception as e:
            logger.error(f"Ray Score calculation failed: {e}")
            return 0.0
    
    async def _evaluate_rule(self, rule_id: str, decision_context: Dict) -> float:
        """Evaluate individual Ray Rule"""
        # Simplified rule evaluation - in real implementation would be more sophisticated
        
        if rule_id == 'rule_1':  # Long-term value creation
            time_horizon = decision_context.get('time_horizon', 'short')
            if time_horizon == 'long':
                return 1.0
            elif time_horizon == 'medium':
                return 0.7
            else:
                return 0.3
        
        elif rule_id == 'rule_2':  # Emotional state awareness
            emotional_state = decision_context.get('emotional_state', 'neutral')
            if emotional_state in ['calm', 'confident']:
                return 1.0
            elif emotional_state == 'neutral':
                return 0.7
            else:
                return 0.3
        
        elif rule_id == 'rule_3':  # Risk-reward alignment
            risk_level = decision_context.get('risk_level', 'medium')
            expected_reward = decision_context.get('expected_reward', 'medium')
            
            if risk_level == 'low' and expected_reward in ['medium', 'high']:
                return 1.0
            elif risk_level == 'medium' and expected_reward == 'high':
                return 0.8
            else:
                return 0.5
        
        elif rule_id == 'rule_4':  # Cognitive clarity
            clarity_score = decision_context.get('clarity_score', 50)
            return min(1.0, clarity_score / 100.0)
        
        elif rule_id == 'rule_5':  # Legacy consideration
            legacy_aligned = decision_context.get('legacy_aligned', False)
            return 1.0 if legacy_aligned else 0.5
        
        return 0.5  # Default score
    
    async def assess_compliance(self, decision_context: Dict) -> Dict:
        """Assess overall Ray Rules compliance"""
        compliance = {
            'overall_score': 0.0,
            'rule_scores': {},
            'recommendations': []
        }
        
        total_score = 0.0
        
        for rule_id, rule_config in self.rules.items():
            rule_score = await self._evaluate_rule(rule_id, decision_context)
            compliance['rule_scores'][rule_id] = rule_score * 100
            total_score += rule_score * rule_config['weight']
        
        compliance['overall_score'] = total_score * 100
        
        # Generate recommendations
        for rule_id, score in compliance['rule_scores'].items():
            if score < 70:
                rule_desc = self.rules[rule_id]['description']
                compliance['recommendations'].append(f"Improve {rule_desc} (current: {score:.1f}%)")
        
        return compliance


class CognitiveMemorySystem:
    """
    Cognitive memory system for pattern learning and recall
    """
    
    def __init__(self):
        self.cognitive_patterns = {}
        self.learning_rate = 0.01
    
    async def store_cognitive_pattern(self, pattern_id: str, pattern_data: Dict):
        """Store cognitive pattern for future reference"""
        self.cognitive_patterns[pattern_id] = {
            'data': pattern_data,
            'timestamp': datetime.now(),
            'access_count': 0,
            'success_rate': 0.0
        }
    
    async def recall_similar_patterns(self, query_pattern: Dict, similarity_threshold: float = 0.7) -> List[Dict]:
        """Recall similar cognitive patterns"""
        similar_patterns = []
        
        for pattern_id, pattern_info in self.cognitive_patterns.items():
            similarity = self._calculate_cognitive_similarity(query_pattern, pattern_info['data'])
            
            if similarity >= similarity_threshold:
                similar_patterns.append({
                    'pattern_id': pattern_id,
                    'similarity': similarity,
                    'data': pattern_info['data'],
                    'success_rate': pattern_info['success_rate']
                })
        
        # Sort by similarity
        similar_patterns.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_patterns
    
    def _calculate_cognitive_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between cognitive patterns"""
        # Simplified similarity calculation
        common_keys = set(pattern1.keys()) & set(pattern2.keys())
        
        if not common_keys:
            return 0.0
        
        similarity_sum = 0.0
        
        for key in common_keys:
            if pattern1[key] == pattern2[key]:
                similarity_sum += 1.0
            elif isinstance(pattern1[key], (int, float)) and isinstance(pattern2[key], (int, float)):
                # Numeric similarity
                diff = abs(pattern1[key] - pattern2[key])
                max_val = max(abs(pattern1[key]), abs(pattern2[key]), 1)
                similarity_sum += max(0, 1 - (diff / max_val))
        
        return similarity_sum / len(common_keys)


# Example usage and testing
async def main():
    """Test the Advanced ΩSIGIL MetaStack system"""
    
    # Initialize MetaStack
    metastack = OmegaSigilMetaStack()
    
    # Sample market data
    market_data = {
        'price_data': {
            'current_price': 100.0,
            'resistance_level': 98.0,
            'support_level': 95.0,
            'volume_increase': True,
            'price_momentum': 0.05
        },
        'volume_data': {
            'current_volume': 1000000,
            'average_volume': 500000,
            'volume_ratio': 2.0
        },
        'volatility': 0.03,
        'trend': 'bullish',
        'timeframe': '1h'
    }
    
    # Sample decision context
    decision_context = {
        'time_horizon': 'long',
        'emotional_state': 'calm',
        'risk_level': 'medium',
        'expected_reward': 'high',
        'clarity_score': 85,
        'legacy_aligned': True,
        'ray_rules_applied': True,
        'value_aligned': True
    }
    
    # Calculate ΩSIGIL intelligence
    intelligence = await metastack.calculate_omega_sigil_intelligence(market_data, decision_context)
    
    print("🧠 ΩSIGIL MetaStack Intelligence Report")
    print("=" * 50)
    print(f"Ray Score: {intelligence['ray_score']:.2f}")
    print(f"Confidence Level: {intelligence['confidence_level'].value}")
    print(f"MENACE Accuracy: {intelligence['menace_accuracy']:.2%}")
    
    # Create memory echo
    outcome = {
        'success': True,
        'profit_ratio': 0.15,
        'prediction_made': True
    }
    
    echo = await metastack.create_memory_echo(market_data, decision_context, outcome)
    print(f"\nMemory Echo Created: {echo.pattern_id}")
    print(f"Pattern Type: {echo.pattern_type.value}")
    print(f"Ray Score: {echo.ray_score:.2f}")
    
    print("\n🎯 RetroSniper Recommendation:")
    retrosniper = intelligence.get('retrosniper_recommendation', {})
    print(f"Action: {retrosniper.get('action', 'UNKNOWN')}")
    print(f"Profile: {retrosniper.get('profile_recommendation', 'UNKNOWN')}")
    print(f"Confidence: {retrosniper.get('confidence', 0):.2%}")


if __name__ == "__main__":
    asyncio.run(main())

