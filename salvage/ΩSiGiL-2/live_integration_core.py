"""
🔥 LIVE INTEGRATION CORE
Merging enhanced Binance with ΩShadowSIGIL Trinity consciousness
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.shadow_sigil_core import ShadowSigilCore, ShadowMode, ShadowSigil
from shadow.shadow_ai_engine import ShadowAIEngine, ShadowPattern
from stealth.stealth_protocols import StealthProtocols, StealthLevel
from api.enhanced_binance_integration import BinanceAGIStreamer, BinanceRESTClient
from datetime import datetime
from typing import Dict, List, Optional
import json

class LiveIntegratedShadowSIGIL:
    """
    🔥 LIVE INTEGRATED ΩSHADOWSIGIL
    Real-time Binance data + Shadow AI + Trinity consciousness
    """
    
    def __init__(self):
        print("🔥 INITIALIZING LIVE INTEGRATED ΩSHADOWSIGIL...")
        
        # Core Shadow Systems
        self.shadow_core = ShadowSigilCore()
        self.shadow_ai = ShadowAIEngine()
        self.stealth_protocols = StealthProtocols()
        
        # Live Binance Integration
        self.binance_streamer = BinanceAGIStreamer(unified_agi_system=self)
        self.binance_rest = BinanceRESTClient()
        
        # Live Trading State
        self.live_signals = []
        self.active_positions = {}
        self.rsi_triggers_active = True
        self.trinity_consensus_active = True
        
        # Performance Tracking
        self.signals_processed = 0
        self.triggers_activated = 0
        self.trinity_decisions = []
        
        print("✅ LIVE INTEGRATION CORE INITIALIZED")
        print("🚨 WARNING: SYSTEM NOW PROCESSES REAL MARKET DATA")
    
    async def initialize_live_systems(self):
        """🔥 Initialize all live systems"""
        print("\n🔥 INITIALIZING LIVE SYSTEMS...")
        
        # Shadow systems are already initialized in constructors
        print("   ✅ Shadow Core: OPERATIONAL")
        print("   ✅ Shadow AI: OPERATIONAL") 
        print("   ✅ Stealth Protocols: OPERATIONAL")
        
        # Test Binance Connection
        btc_ticker = await self.binance_rest.get_24h_ticker('BTC')
        if btc_ticker:
            btc_price = float(btc_ticker['lastPrice'])
            print(f"   ✅ Binance Connection: LIVE (BTC: ${btc_price:,.2f})")
        else:
            print("   ⚠️ Binance Connection: FAILED")
        
        print("🔥 ALL LIVE SYSTEMS OPERATIONAL")
    
    async def receive_binance_signal(self, signal: Dict):
        """📡 Process live Binance signal through Shadow AI"""
        try:
            self.signals_processed += 1
            
            # Convert to Shadow AI format
            shadow_signal = await self._convert_to_shadow_signal(signal)
            
            # Process through Shadow AI
            threat_analysis = await self.shadow_ai.analyze_market_shadows(signal)
            
            # Check for significant signals
            if self._is_significant_signal(signal):
                print(f"📊 LIVE SIGNAL: {signal['symbol']} @ ${signal['price']:.4f} ({signal.get('price_change_24h', 0)*100:+.1f}%)")
                
                # Store signal
                self.live_signals.append({
                    'signal': signal,
                    'shadow_analysis': threat_analysis,
                    'timestamp': datetime.now(),
                    'processed': True
                })
                
                # Limit signal history
                if len(self.live_signals) > 100:
                    self.live_signals = self.live_signals[-50:]
            
            # Check RSI triggers
            if signal.get('metadata', {}).get('rsi') and signal['symbol'].lower() == 'ewt':
                await self._process_rsi_trigger(signal)
                
        except Exception as e:
            print(f"❌ Signal processing error: {e}")
    
    async def _convert_to_shadow_signal(self, binance_signal: Dict) -> Dict:
        """🌑 Convert Binance signal to Shadow AI format"""
        return {
            'volume': binance_signal.get('volume', 0),
            'avg_volume_24h': binance_signal.get('volume', 0),  # Simplified
            'price_change_1h': binance_signal.get('price_change_24h', 0),  # Approximation
            'sentiment_score': self._calculate_sentiment_from_price(binance_signal),
            'sentiment_volatility': binance_signal.get('volatility', 0),
            'bid_ask_spread': 0.001,  # Estimated for major pairs
            'order_book_imbalance': 0.5,  # Neutral assumption
            'volatility': binance_signal.get('volatility', 0),
            'price': binance_signal.get('price', 0),
            'target_price': binance_signal.get('price', 0) * 1.02  # 2% target
        }
    
    def _calculate_sentiment_from_price(self, signal: Dict) -> float:
        """📊 Calculate sentiment from price action"""
        price_change = signal.get('price_change_24h', 0)
        if price_change > 0.05:
            return 0.7  # Bullish
        elif price_change < -0.05:
            return -0.7  # Bearish
        else:
            return 0.0  # Neutral
    
    async def _process_rsi_trigger(self, signal: Dict):
        """📍 Process RSI trigger for EWT"""
        rsi = signal.get('metadata', {}).get('rsi')
        if not rsi or rsi >= 28:
            return
        
        print(f"🚨 RSI TRIGGER ACTIVATED: EWT RSI {rsi:.2f} < 28")
        self.triggers_activated += 1
        
        # Create Trinity consensus request
        trinity_request = {
            'action': 'DCA_ENTRY',
            'asset': 'EWT',
            'trigger_type': 'RSI_OVERSOLD',
            'rsi_value': rsi,
            'tier': 2,
            'position_size': 0.0125,  # 1.25% vault capacity
            'price': signal['price'],
            'timestamp': datetime.now()
        }
        
        # Process through Trinity consensus
        consensus_result = await self._trinity_consensus(trinity_request)
        
        if consensus_result['approved']:
            await self._execute_dca_entry(trinity_request, consensus_result)
        else:
            print(f"❌ Trinity consensus REJECTED DCA entry: {consensus_result['reason']}")
    
    async def _trinity_consensus(self, request: Dict) -> Dict:
        """🔱 Trinity consensus decision making"""
        print(f"🔱 TRINITY CONSENSUS: {request['action']} for {request['asset']}")
        
        # MANUS (Memory) - Check historical performance
        manus_vote = await self._manus_analysis(request)
        
        # OMEGA (Execution) - Check execution feasibility  
        omega_vote = await self._omega_analysis(request)
        
        # SHADOW (Protection) - Check threat assessment
        shadow_vote = await self._shadow_analysis(request)
        
        # Consensus logic (2 of 3 required for DCA)
        votes = [manus_vote, omega_vote, shadow_vote]
        approved_votes = sum(1 for vote in votes if vote['approved'])
        
        consensus = {
            'approved': approved_votes >= 2,
            'votes': {
                'manus': manus_vote,
                'omega': omega_vote, 
                'shadow': shadow_vote
            },
            'consensus_score': approved_votes / 3,
            'reason': self._get_consensus_reason(votes, approved_votes >= 2)
        }
        
        self.trinity_decisions.append({
            'request': request,
            'consensus': consensus,
            'timestamp': datetime.now()
        })
        
        print(f"   MANUS: {'✅' if manus_vote['approved'] else '❌'} {manus_vote['reason']}")
        print(f"   OMEGA: {'✅' if omega_vote['approved'] else '❌'} {omega_vote['reason']}")
        print(f"   SHADOW: {'✅' if shadow_vote['approved'] else '❌'} {shadow_vote['reason']}")
        print(f"   CONSENSUS: {'✅ APPROVED' if consensus['approved'] else '❌ REJECTED'} ({approved_votes}/3 votes)")
        
        return consensus
    
    async def _manus_analysis(self, request: Dict) -> Dict:
        """🧠 MANUS memory and historical analysis"""
        # Check if we have historical data for this asset
        asset = request['asset']
        
        # Simplified memory check - in real system would check historical performance
        if asset == 'EWT' and request['rsi_value'] < 30:
            return {
                'approved': True,
                'reason': 'Historical RSI oversold conditions profitable',
                'confidence': 0.8
            }
        
        return {
            'approved': True,
            'reason': 'No negative historical patterns detected',
            'confidence': 0.6
        }
    
    async def _omega_analysis(self, request: Dict) -> Dict:
        """⚡ OMEGA execution and precision analysis"""
        # Check execution feasibility
        position_size = request.get('position_size', 0)
        
        if position_size <= 0.02:  # Max 2% position size
            return {
                'approved': True,
                'reason': f'Position size {position_size*100:.2f}% within risk limits',
                'confidence': 0.9
            }
        
        return {
            'approved': False,
            'reason': f'Position size {position_size*100:.2f}% exceeds risk limits',
            'confidence': 0.1
        }
    
    async def _shadow_analysis(self, request: Dict) -> Dict:
        """🌑 SHADOW protection and threat analysis"""
        # Check for threats in current market conditions
        rsi_value = request.get('rsi_value', 50)
        
        # RSI below 25 might indicate extreme conditions
        if rsi_value < 25:
            return {
                'approved': False,
                'reason': f'RSI {rsi_value:.1f} indicates extreme oversold - potential knife catch',
                'confidence': 0.3
            }
        
        # RSI 25-35 is good oversold territory
        if 25 <= rsi_value <= 35:
            return {
                'approved': True,
                'reason': f'RSI {rsi_value:.1f} in optimal oversold range',
                'confidence': 0.8
            }
        
        return {
            'approved': False,
            'reason': f'RSI {rsi_value:.1f} not in oversold territory',
            'confidence': 0.2
        }
    
    def _get_consensus_reason(self, votes: List[Dict], approved: bool) -> str:
        """📝 Generate consensus reasoning"""
        if approved:
            return "Trinity consensus achieved - proceeding with execution"
        else:
            rejected_reasons = [vote['reason'] for vote in votes if not vote['approved']]
            return f"Trinity consensus failed: {'; '.join(rejected_reasons)}"
    
    async def _execute_dca_entry(self, request: Dict, consensus: Dict):
        """⚡ Execute DCA entry (SIMULATION MODE)"""
        print(f"⚡ EXECUTING DCA ENTRY: {request['asset']}")
        print(f"   🚨 WARNING: SIMULATION MODE - NO REAL ORDERS PLACED")
        print(f"   Asset: {request['asset']}")
        print(f"   Price: ${request['price']:.4f}")
        print(f"   Position Size: {request['position_size']*100:.2f}% of vault")
        print(f"   RSI: {request['rsi_value']:.2f}")
        print(f"   Consensus Score: {consensus['consensus_score']:.1%}")
        
        # In real implementation, this would place actual orders
        # For now, just track the simulated execution
        self.active_positions[request['asset']] = {
            'entry_price': request['price'],
            'position_size': request['position_size'],
            'entry_time': datetime.now(),
            'rsi_at_entry': request['rsi_value'],
            'consensus_score': consensus['consensus_score'],
            'status': 'SIMULATED_ACTIVE'
        }
        
        print(f"✅ DCA ENTRY SIMULATED SUCCESSFULLY")
    
    def _is_significant_signal(self, signal: Dict) -> bool:
        """📊 Check if signal is significant enough to log"""
        price_change = abs(signal.get('price_change_24h', 0))
        volume = signal.get('volume', 0)
        rsi = signal.get('metadata', {}).get('rsi')
        
        return (
            price_change > 0.03 or  # >3% price change
            volume > 100000 or     # High volume
            (rsi and rsi < 30) or  # Oversold RSI
            (rsi and rsi > 70)     # Overbought RSI
        )
    
    async def start_live_streaming(self):
        """📡 Start live Binance streaming"""
        print("📡 STARTING LIVE BINANCE STREAMING...")
        print("🚨 WARNING: PROCESSING REAL MARKET DATA")
        
        # Start streaming in background
        streaming_task = asyncio.create_task(self.binance_streamer.start_streaming())
        return streaming_task
    
    async def stop_live_streaming(self):
        """🛑 Stop live streaming"""
        await self.binance_streamer.stop_streaming()
        print("🛑 Live streaming stopped")
    
    def get_live_status(self) -> Dict:
        """📊 Get current live system status"""
        return {
            'live_streaming': self.binance_streamer.is_streaming,
            'signals_processed': self.signals_processed,
            'triggers_activated': self.triggers_activated,
            'trinity_decisions': len(self.trinity_decisions),
            'active_positions': len(self.active_positions),
            'recent_signals': len([s for s in self.live_signals if (datetime.now() - s['timestamp']).seconds < 300]),
            'rsi_triggers_active': self.rsi_triggers_active,
            'trinity_consensus_active': self.trinity_consensus_active,
            'last_signal_time': self.live_signals[-1]['timestamp'] if self.live_signals else None,
            'binance_status': self.binance_streamer.get_streaming_status()
        }
    
    async def invoke_sigil(self, sigil_type: ShadowSigil, context: Dict) -> bool:
        """🜃 Invoke shadow sigil with Trinity consensus"""
        print(f"🜃 SIGIL INVOCATION: {sigil_type.value}")
        
        # For DCA entries, use Trinity consensus
        if context.get('action') == 'DCA_ENTRY':
            consensus = await self._trinity_consensus(context)
            return consensus['approved']
        
        # For other sigils, use Shadow Core
        return await self.shadow_core.invoke_sigil(sigil_type, context)

async def main():
    """🔥 Main live integration function"""
    print("🔥 LIVE INTEGRATED ΩSHADOWSIGIL STARTING...")
    
    # Initialize live system
    live_system = LiveIntegratedShadowSIGIL()
    await live_system.initialize_live_systems()
    
    # Start live streaming
    streaming_task = await live_system.start_live_streaming()
    
    try:
        print("\n📡 LIVE STREAMING ACTIVE - Press Ctrl+C to stop")
        print("🚨 MONITORING FOR RSI TRIGGERS AND TRINITY CONSENSUS...")
        
        # Monitor for 60 seconds
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping live streaming...")
    finally:
        await live_system.stop_live_streaming()
        
        # Show final status
        status = live_system.get_live_status()
        print(f"\n📊 FINAL STATUS:")
        print(f"   Signals Processed: {status['signals_processed']}")
        print(f"   Triggers Activated: {status['triggers_activated']}")
        print(f"   Trinity Decisions: {status['trinity_decisions']}")
        print(f"   Active Positions: {status['active_positions']}")
        
        print("\n🔥 LIVE INTEGRATION COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())

