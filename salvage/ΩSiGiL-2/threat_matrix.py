"""
✳️ PHASE I - ΩSIGIL THREAT DETECTION MATRIX
Real-time SHADOW defense protocols for sovereign protection
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class ThreatLevel(Enum):
    SAFE = 0
    CAUTION = 1
    WARNING = 2
    DANGER = 3
    CRITICAL = 4

class ThreatType(Enum):
    WHALE_MANIPULATION = "WHALE_MANIPULATION"
    SPOOFING_ATTACK = "SPOOFING_ATTACK"
    FLASH_CRASH = "FLASH_CRASH"
    RUG_PULL = "RUG_PULL"
    FUD_CAMPAIGN = "FUD_CAMPAIGN"
    NEWS_INJECTION = "NEWS_INJECTION"
    ORDER_BOOK_COLLAPSE = "ORDER_BOOK_COLLAPSE"
    BLACKLIST_EVENT = "BLACKLIST_EVENT"

@dataclass
class ThreatSignature:
    threat_type: ThreatType
    confidence: float
    severity: ThreatLevel
    description: str
    timestamp: datetime
    asset: str
    metadata: Dict

@dataclass
class WhalePattern:
    wallet_address: str
    behavior_type: str
    volume_threshold: float
    time_pattern: str
    risk_score: float

class ThreatDetectionMatrix:
    """
    🛑 SHADOW's autonomous threat detection and override system
    Protects ΩSIGIL from market manipulation and systemic risks
    """
    
    def __init__(self):
        self.active_threats: List[ThreatSignature] = []
        self.whale_patterns: Dict[str, WhalePattern] = {}
        self.fud_keywords = self._initialize_fud_keywords()
        self.blacklist_events = []
        self.threat_history = []
        
        # Threat thresholds (configurable)
        self.whale_sell_wall_multiplier = 3.0
        self.fud_weight_threshold = 0.66
        self.order_book_collapse_threshold = 0.15
        self.time_window_minutes = 3
        
        print("🛑 THREAT DETECTION MATRIX ACTIVATED")
        print("👁 SHADOW autonomous defense protocols online")
    
    def _initialize_fud_keywords(self) -> Dict[str, float]:
        """Initialize FUD keyword detection patterns with weights"""
        return {
            # High severity FUD terms
            'crash': 0.9, 'dump': 0.8, 'scam': 0.95, 'rug': 0.9, 'exit': 0.7,
            'hack': 0.85, 'exploit': 0.8, 'ponzi': 0.9, 'fraud': 0.95,
            'collapse': 0.8, 'bubble': 0.6, 'manipulation': 0.7,
            
            # Medium severity terms
            'bearish': 0.5, 'sell': 0.4, 'drop': 0.5, 'fall': 0.4,
            'decline': 0.4, 'correction': 0.3, 'pullback': 0.2,
            
            # Whale activity terms
            'whale': 0.6, 'dump': 0.8, 'liquidation': 0.7, 'margin': 0.5,
            'leverage': 0.4, 'short': 0.5, 'futures': 0.3,
            
            # Regulatory FUD
            'ban': 0.8, 'regulation': 0.6, 'illegal': 0.9, 'sec': 0.7,
            'lawsuit': 0.8, 'investigation': 0.7, 'compliance': 0.4
        }
    
    async def scan_for_threats(self, market_data: Dict, news_data: List[str], 
                              order_book: Dict) -> List[ThreatSignature]:
        """
        🔍 Comprehensive threat scanning across all vectors
        Returns list of detected threats for SHADOW evaluation
        """
        threats = []
        
        # Scan for whale manipulation
        whale_threats = await self._detect_whale_manipulation(market_data, order_book)
        threats.extend(whale_threats)
        
        # Scan for spoofing attacks
        spoofing_threats = await self._detect_spoofing_attacks(order_book)
        threats.extend(spoofing_threats)
        
        # Scan for flash crash patterns
        flash_crash_threats = await self._detect_flash_crash_patterns(market_data)
        threats.extend(flash_crash_threats)
        
        # Scan for FUD campaigns
        fud_threats = await self._detect_fud_campaigns(news_data)
        threats.extend(fud_threats)
        
        # Scan for news injection attacks
        news_threats = await self._detect_news_injection(news_data)
        threats.extend(news_threats)
        
        # Scan for order book collapse
        orderbook_threats = await self._detect_orderbook_collapse(order_book)
        threats.extend(orderbook_threats)
        
        # Update active threats
        self.active_threats = threats
        self.threat_history.extend(threats)
        
        return threats
    
    async def _detect_whale_manipulation(self, market_data: Dict, 
                                       order_book: Dict) -> List[ThreatSignature]:
        """🐋 Detect whale sell walls and manipulation patterns"""
        threats = []
        
        # Get current sell wall data
        sell_walls = order_book.get('asks', [])
        if not sell_walls:
            return threats
        
        # Calculate rolling average sell wall size
        rolling_avg = self._calculate_rolling_average_sell_wall(market_data)
        
        # Check for abnormally large sell walls
        for price, volume in sell_walls[:10]:  # Check top 10 sell orders
            if volume > rolling_avg * self.whale_sell_wall_multiplier:
                threat = ThreatSignature(
                    threat_type=ThreatType.WHALE_MANIPULATION,
                    confidence=min(volume / (rolling_avg * self.whale_sell_wall_multiplier), 1.0),
                    severity=ThreatLevel.WARNING if volume < rolling_avg * 5 else ThreatLevel.DANGER,
                    description=f"Whale sell wall detected: {volume:.2f} (avg: {rolling_avg:.2f})",
                    timestamp=datetime.now(),
                    asset=market_data.get('symbol', 'UNKNOWN'),
                    metadata={'price': price, 'volume': volume, 'avg': rolling_avg}
                )
                threats.append(threat)
                
                print(f"🐋 WHALE THREAT DETECTED: {volume:.2f} at {price:.4f}")
        
        return threats
    
    async def _detect_spoofing_attacks(self, order_book: Dict) -> List[ThreatSignature]:
        """🎭 Detect order book spoofing and fake walls"""
        threats = []
        
        # Analyze order book for spoofing patterns
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        # Check for rapid order placement/cancellation patterns
        # (This would require historical order book data in real implementation)
        
        # Check for unrealistic order sizes
        for side, orders in [('bid', bids), ('ask', asks)]:
            for price, volume in orders[:5]:
                # Detect suspiciously large orders that might be spoofs
                if volume > 1000000:  # Configurable threshold
                    threat = ThreatSignature(
                        threat_type=ThreatType.SPOOFING_ATTACK,
                        confidence=0.6,
                        severity=ThreatLevel.CAUTION,
                        description=f"Potential spoof order: {volume:.2f} on {side} side",
                        timestamp=datetime.now(),
                        asset=order_book.get('symbol', 'UNKNOWN'),
                        metadata={'side': side, 'price': price, 'volume': volume}
                    )
                    threats.append(threat)
        
        return threats
    
    async def _detect_flash_crash_patterns(self, market_data: Dict) -> List[ThreatSignature]:
        """⚡ Detect flash crash precursor patterns"""
        threats = []
        
        # Analyze price volatility and volume spikes
        current_price = market_data.get('price', 0)
        volume_24h = market_data.get('volume_24h', 0)
        price_change_1h = market_data.get('price_change_1h', 0)
        
        # Flash crash indicators
        if abs(price_change_1h) > 0.1 and volume_24h > market_data.get('avg_volume', 0) * 3:
            threat = ThreatSignature(
                threat_type=ThreatType.FLASH_CRASH,
                confidence=min(abs(price_change_1h) * 5, 1.0),
                severity=ThreatLevel.WARNING if abs(price_change_1h) < 0.15 else ThreatLevel.DANGER,
                description=f"Flash crash pattern: {price_change_1h:.2%} in 1h with high volume",
                timestamp=datetime.now(),
                asset=market_data.get('symbol', 'UNKNOWN'),
                metadata={'price_change': price_change_1h, 'volume_ratio': volume_24h / market_data.get('avg_volume', 1)}
            )
            threats.append(threat)
            
            print(f"⚡ FLASH CRASH PATTERN: {price_change_1h:.2%} change detected")
        
        return threats
    
    async def _detect_fud_campaigns(self, news_data: List[str]) -> List[ThreatSignature]:
        """💀 Detect coordinated FUD campaigns"""
        threats = []
        
        if not news_data:
            return threats
        
        # Analyze news sentiment for FUD patterns
        total_fud_weight = 0.0
        fud_articles = []
        
        for article in news_data:
            article_lower = article.lower()
            article_fud_weight = 0.0
            detected_terms = []
            
            # Check for FUD keywords
            for keyword, weight in self.fud_keywords.items():
                if keyword in article_lower:
                    article_fud_weight += weight
                    detected_terms.append(keyword)
            
            if article_fud_weight > 0.5:  # Article contains significant FUD
                fud_articles.append({
                    'content': article[:200] + '...',
                    'weight': article_fud_weight,
                    'terms': detected_terms
                })
                total_fud_weight += article_fud_weight
        
        # Check if combined FUD weight exceeds threshold
        avg_fud_weight = total_fud_weight / len(news_data) if news_data else 0
        
        if avg_fud_weight > self.fud_weight_threshold:
            threat = ThreatSignature(
                threat_type=ThreatType.FUD_CAMPAIGN,
                confidence=min(avg_fud_weight, 1.0),
                severity=ThreatLevel.WARNING if avg_fud_weight < 0.8 else ThreatLevel.DANGER,
                description=f"FUD campaign detected: {avg_fud_weight:.2f} average weight across {len(fud_articles)} articles",
                timestamp=datetime.now(),
                asset="MARKET_WIDE",
                metadata={'fud_articles': fud_articles, 'total_weight': total_fud_weight}
            )
            threats.append(threat)
            
            print(f"💀 FUD CAMPAIGN DETECTED: {avg_fud_weight:.2f} weight across {len(news_data)} articles")
        
        return threats
    
    async def _detect_news_injection(self, news_data: List[str]) -> List[ThreatSignature]:
        """📰 Detect bot-amplified sentiment and news injection attacks"""
        threats = []
        
        # Look for patterns indicating bot amplification
        # - Identical or near-identical content
        # - Unusual posting frequency
        # - Coordinated timing
        
        if len(news_data) > 10:  # Unusual volume of news
            # Check for duplicate content patterns
            content_similarity = self._analyze_content_similarity(news_data)
            
            if content_similarity > 0.7:  # High similarity indicates bot amplification
                threat = ThreatSignature(
                    threat_type=ThreatType.NEWS_INJECTION,
                    confidence=content_similarity,
                    severity=ThreatLevel.WARNING,
                    description=f"News injection detected: {content_similarity:.2%} content similarity",
                    timestamp=datetime.now(),
                    asset="MARKET_WIDE",
                    metadata={'article_count': len(news_data), 'similarity': content_similarity}
                )
                threats.append(threat)
                
                print(f"📰 NEWS INJECTION: {content_similarity:.2%} similarity across {len(news_data)} articles")
        
        return threats
    
    async def _detect_orderbook_collapse(self, order_book: Dict) -> List[ThreatSignature]:
        """📉 Detect order book spread collapse"""
        threats = []
        
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids or not asks:
            return threats
        
        # Calculate spread
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        
        if best_bid > 0 and best_ask > 0:
            spread = (best_ask - best_bid) / best_bid
            
            # Check for abnormal spread expansion
            if spread > self.order_book_collapse_threshold:
                threat = ThreatSignature(
                    threat_type=ThreatType.ORDER_BOOK_COLLAPSE,
                    confidence=min(spread / self.order_book_collapse_threshold, 1.0),
                    severity=ThreatLevel.WARNING if spread < 0.25 else ThreatLevel.DANGER,
                    description=f"Order book collapse: {spread:.2%} spread",
                    timestamp=datetime.now(),
                    asset=order_book.get('symbol', 'UNKNOWN'),
                    metadata={'spread': spread, 'best_bid': best_bid, 'best_ask': best_ask}
                )
                threats.append(threat)
                
                print(f"📉 ORDER BOOK COLLAPSE: {spread:.2%} spread detected")
        
        return threats
    
    def should_auto_pause_flips(self, threats: List[ThreatSignature]) -> Tuple[bool, str]:
        """
        🚨 SHADOW autonomous override decision
        Returns (should_pause, reason) based on threat analysis
        """
        
        # Check for critical threats
        critical_threats = [t for t in threats if t.severity == ThreatLevel.CRITICAL]
        if critical_threats:
            return True, f"Critical threats detected: {len(critical_threats)}"
        
        # Check for multiple danger-level threats
        danger_threats = [t for t in threats if t.severity == ThreatLevel.DANGER]
        if len(danger_threats) >= 2:
            return True, f"Multiple danger threats: {len(danger_threats)}"
        
        # Check for specific threat combinations
        threat_types = {t.threat_type for t in threats}
        
        # Whale + FUD combination is particularly dangerous
        if ThreatType.WHALE_MANIPULATION in threat_types and ThreatType.FUD_CAMPAIGN in threat_types:
            return True, "Whale manipulation + FUD campaign detected"
        
        # Flash crash + order book collapse
        if ThreatType.FLASH_CRASH in threat_types and ThreatType.ORDER_BOOK_COLLAPSE in threat_types:
            return True, "Flash crash + order book collapse detected"
        
        return False, "No auto-pause conditions met"
    
    def get_threat_summary(self) -> Dict:
        """📊 Get current threat landscape summary"""
        active_by_type = {}
        for threat in self.active_threats:
            threat_type = threat.threat_type.value
            if threat_type not in active_by_type:
                active_by_type[threat_type] = []
            active_by_type[threat_type].append(threat)
        
        max_severity = ThreatLevel.SAFE
        if self.active_threats:
            max_severity = max(t.severity for t in self.active_threats)
        
        return {
            'total_threats': len(self.active_threats),
            'max_severity': max_severity.name,
            'threats_by_type': {k: len(v) for k, v in active_by_type.items()},
            'auto_pause_recommended': self.should_auto_pause_flips(self.active_threats)[0],
            'last_scan': datetime.now().isoformat()
        }
    
    # Helper methods
    def _calculate_rolling_average_sell_wall(self, market_data: Dict) -> float:
        """Calculate rolling average sell wall size"""
        # In real implementation, this would use historical data
        return market_data.get('avg_sell_wall', 1000.0)
    
    def _analyze_content_similarity(self, articles: List[str]) -> float:
        """Analyze similarity between news articles to detect bot amplification"""
        if len(articles) < 2:
            return 0.0
        
        # Simple similarity check based on common words
        # In real implementation, would use more sophisticated NLP
        word_sets = []
        for article in articles:
            words = set(article.lower().split())
            word_sets.append(words)
        
        # Calculate average pairwise similarity
        total_similarity = 0.0
        comparisons = 0
        
        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                intersection = len(word_sets[i] & word_sets[j])
                union = len(word_sets[i] | word_sets[j])
                similarity = intersection / union if union > 0 else 0
                total_similarity += similarity
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0

# Initialize the threat detection matrix
threat_matrix = ThreatDetectionMatrix()

async def scan_market_threats(market_data: Dict, news_data: List[str], 
                            order_book: Dict) -> Tuple[List[ThreatSignature], bool]:
    """
    🛑 Main threat scanning function for SHADOW
    Returns (threats, should_pause_flips)
    """
    threats = await threat_matrix.scan_for_threats(market_data, news_data, order_book)
    should_pause, reason = threat_matrix.should_auto_pause_flips(threats)
    
    if should_pause:
        print(f"🚨 SHADOW OVERRIDE TRIGGERED: {reason}")
    
    return threats, should_pause

if __name__ == "__main__":
    print("🛑 THREAT DETECTION MATRIX - STANDALONE TEST")
    
    # Demo threat detection
    demo_market_data = {
        'symbol': 'BTC/USDT',
        'price': 45000,
        'volume_24h': 1000000,
        'avg_volume': 500000,
        'price_change_1h': -0.12,
        'avg_sell_wall': 50.0
    }
    
    demo_news = [
        "Bitcoin crash imminent as whales dump massive positions",
        "Crypto market manipulation exposed in new investigation",
        "SEC lawsuit threatens entire cryptocurrency ecosystem"
    ]
    
    demo_order_book = {
        'symbol': 'BTC/USDT',
        'bids': [[44900, 10.5], [44850, 25.2], [44800, 15.8]],
        'asks': [[45100, 200.0], [45150, 8.3], [45200, 12.1]]  # Large sell wall
    }
    
    async def demo():
        threats, should_pause = await scan_market_threats(
            demo_market_data, demo_news, demo_order_book
        )
        
        print(f"\n📊 THREAT SCAN RESULTS:")
        print(f"   Threats Detected: {len(threats)}")
        print(f"   Auto-Pause Recommended: {should_pause}")
        
        for threat in threats:
            print(f"   🚨 {threat.threat_type.value}: {threat.description}")
    
    asyncio.run(demo())

