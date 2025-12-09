#!/usr/bin/env python3
"""
🚀 ΩSIGIL NEURAL EVOLUTION RUNNER
Enhanced runner with complete Neural Evolution integration
"""

import sys
import asyncio
import signal
from datetime import datetime
from core.omega_sigil_core import OmegaSigilCore
from core.cycle_resonance_integration import initialize_cycle_integration
from ui.neural_dashboard import setup_neural_dashboard_routes
from api.flask_server import app as flask_app_template

class NeuralEvolutionRunner:
    """
    🚀 Enhanced runner for ΩSIGIL with Neural Evolution
    Manages the complete sovereign AGI system with learning capabilities
    """
    
    def __init__(self):
        self.omega_core = None
        self.cycle_integrator = None
        self.flask_app = None
        self.running = False
        
        print("🚀 NEURAL EVOLUTION RUNNER INITIALIZED")
    
    async def initialize_systems(self):
        """🔧 Initialize all ΩSIGIL systems with Neural Evolution"""
        
        print("🔧 INITIALIZING ΩSIGIL NEURAL EVOLUTION SYSTEMS...")
        
        # Initialize core ΩSIGIL consciousness
        self.omega_core = OmegaSigilCore()
        
        # Initialize Neural Evolution integration
        self.cycle_integrator = initialize_cycle_integration(self.omega_core)
        
        # Create Flask app with neural dashboard
        from flask import Flask
        self.flask_app = Flask(__name__)
        setup_neural_dashboard_routes(self.flask_app, self.cycle_integrator)
        
        print("✅ ALL SYSTEMS INITIALIZED WITH NEURAL EVOLUTION")
        print("🧬 Cycle Resonance Memory: ACTIVE")
        print("🎯 Predictive Intelligence: ONLINE")
        print("📊 Learning Dashboard: READY")
    
    async def run_interactive_mode(self):
        """🎮 Interactive mode with neural evolution capabilities"""
        
        await self.initialize_systems()
        
        print("\n🎮 ΩSIGIL NEURAL EVOLUTION - INTERACTIVE MODE")
        print("=" * 60)
        print("Available commands:")
        print("  signal <asset> <strength>     - Send trading signal")
        print("  predict <asset> <ritual>      - Get neural prediction")
        print("  optimize <asset> <condition>  - Get optimal ritual")
        print("  status                        - Show intelligence status")
        print("  learn                         - Show learning metrics")
        print("  simulate                      - Run learning simulation")
        print("  save <filename>               - Save neural state")
        print("  load <filename>               - Load neural state")
        print("  exit                          - Exit system")
        print("=" * 60)
        
        self.running = True
        
        while self.running:
            try:
                command = input("\n🧬 NEURAL> ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                
                if cmd == "exit":
                    break
                elif cmd == "signal":
                    await self._handle_signal_command(parts)
                elif cmd == "predict":
                    await self._handle_predict_command(parts)
                elif cmd == "optimize":
                    await self._handle_optimize_command(parts)
                elif cmd == "status":
                    await self._handle_status_command()
                elif cmd == "learn":
                    await self._handle_learn_command()
                elif cmd == "simulate":
                    await self._handle_simulate_command()
                elif cmd == "save":
                    await self._handle_save_command(parts)
                elif cmd == "load":
                    await self._handle_load_command(parts)
                else:
                    print(f"❌ Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🔮 NEURAL EVOLUTION SESSION ENDED")
    
    async def _handle_signal_command(self, parts):
        """📡 Handle signal command with neural enhancement"""
        if len(parts) < 3:
            print("Usage: signal <asset> <strength>")
            return
        
        asset = parts[1].upper()
        try:
            strength = float(parts[2])
        except ValueError:
            print("❌ Invalid strength value")
            return
        
        # Create signal data
        signal_data = {
            'asset': asset,
            'strength': strength,
            'timestamp': datetime.now(),
            'price_change_24h': 0.02,  # Mock data
            'volatility': 0.05,
            'emotional_wave': 0.6
        }
        
        # Enhance with neural evolution
        enhanced_signal = await self.cycle_integrator.enhance_signal_evaluation(signal_data)
        
        print(f"📡 SIGNAL PROCESSED: {asset}")
        print(f"   Original Strength: {strength:.2f}")
        print(f"   Enhanced Strength: {enhanced_signal['strength']:.2f}")
        
        if 'neural_enhancement' in enhanced_signal:
            enhancement = enhanced_signal['neural_enhancement']
            print(f"   Recommended Ritual: {enhancement['recommended_ritual']}")
            print(f"   Success Probability: {enhancement['success_probability']:.1%}")
            print(f"   Confidence: {enhancement['confidence_level']}")
    
    async def _handle_predict_command(self, parts):
        """🔮 Handle prediction command"""
        if len(parts) < 3:
            print("Usage: predict <asset> <ritual>")
            return
        
        asset = parts[1].upper()
        ritual = parts[2].upper()
        
        guidance = await self.cycle_integrator.get_neural_guidance(asset, ritual)
        
        print(f"🔮 NEURAL PREDICTION: {asset} - {ritual}")
        print(f"   Success Probability: {guidance['proposed_ritual']['success_probability']:.1%}")
        print(f"   Recommendation: {guidance['proposed_ritual']['recommendation']}")
        print(f"   Reasoning: {guidance['proposed_ritual']['reasoning']}")
        
        if guidance['optimal_alternative']['ritual'] != ritual:
            print(f"   Better Alternative: {guidance['optimal_alternative']['ritual']}")
            print(f"   Alternative Probability: {guidance['optimal_alternative']['success_probability']:.1%}")
    
    async def _handle_optimize_command(self, parts):
        """🎯 Handle optimization command"""
        if len(parts) < 3:
            print("Usage: optimize <asset> <condition>")
            return
        
        asset = parts[1].upper()
        condition_str = parts[2].upper()
        
        # Convert condition string to enum (simplified)
        from core.neural_evolution import MarketCondition
        try:
            condition = MarketCondition[condition_str]
        except KeyError:
            condition = MarketCondition.SIDEWAYS
        
        best_ritual, probability, reasoning = await self.cycle_integrator.neural_evolution.optimize_ritual_selection(
            asset, condition, 0.7
        )
        
        print(f"🎯 OPTIMAL RITUAL: {asset} in {condition.value}")
        print(f"   Best Ritual: {best_ritual.value}")
        print(f"   Success Probability: {probability:.1%}")
        print(f"   Reasoning: {reasoning}")
    
    async def _handle_status_command(self):
        """📊 Handle status command"""
        status = self.cycle_integrator.get_learning_dashboard_data()
        
        print("📊 NEURAL EVOLUTION STATUS:")
        print(f"   Intelligence Score: {status['intelligence_score']:.3f}")
        print(f"   Learning Velocity: {status['learning_velocity']:+.3f}")
        print(f"   Prediction Accuracy: {status['prediction_accuracy']:.3f}")
        print(f"   Total Cycles: {status['total_cycles']}")
        print(f"   Tokens Tracked: {status['tokens_tracked']}")
        print(f"   Cycles Today: {status['integration_status']['cycles_processed_today']}")
    
    async def _handle_learn_command(self):
        """🧠 Handle learning metrics command"""
        status = self.cycle_integrator.get_learning_dashboard_data()
        
        print("🧠 LEARNING METRICS:")
        
        if status['top_performing_tokens']:
            print("   Top Performing Tokens:")
            for token in status['top_performing_tokens'][:3]:
                print(f"     {token['asset']}: {token['success_rate']:.1%} success, {token['avg_profit']:.1%} avg profit")
        
        if status['ritual_rankings']:
            print("   Ritual Rankings:")
            for ritual in status['ritual_rankings'][:3]:
                print(f"     {ritual['ritual']}: {ritual['success_rate']:.1%} success rate")
        
        recent = status['recent_performance']
        print(f"   Recent Performance (7d): {recent['success_rate']:.1%} success, {recent['average_profit']:.1%} avg profit")
    
    async def _handle_simulate_command(self):
        """🎲 Handle simulation command"""
        print("🎲 RUNNING LEARNING SIMULATION...")
        
        # Simulate some trading cycles
        simulation_cycles = [
            {
                'cycle_id': f'SIM_{i:03d}',
                'asset': ['BTC', 'ETH', 'QNT'][i % 3],
                'profits': (i % 5 - 2) * 0.01,  # Mix of profits and losses
                'entry_price': 1000 + i * 10,
                'exit_price': 1000 + i * 10 + (i % 5 - 2) * 10,
                'duration_hours': 1 + (i % 4),
                'signal_strength': 0.5 + (i % 5) * 0.1,
                'price_change_24h': (i % 7 - 3) * 0.02,
                'volatility': 0.03 + (i % 3) * 0.02,
                'sigils_used': [['SPEARHEAD'], ['HOURGLASS'], ['SPEARHEAD', 'HOURGLASS']][i % 3]
            }
            for i in range(10)
        ]
        
        for cycle_data in simulation_cycles:
            await self.cycle_integrator.capture_cycle_completion(cycle_data)
        
        print(f"✅ SIMULATION COMPLETE: {len(simulation_cycles)} cycles processed")
        
        # Show updated status
        await self._handle_status_command()
    
    async def _handle_save_command(self, parts):
        """💾 Handle save command"""
        if len(parts) < 2:
            filename = f"neural_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        else:
            filename = parts[1]
        
        await self.cycle_integrator.neural_evolution.save_neural_state(filename)
        print(f"💾 Neural state saved to: {filename}")
    
    async def _handle_load_command(self, parts):
        """📥 Handle load command"""
        if len(parts) < 2:
            print("Usage: load <filename>")
            return
        
        filename = parts[1]
        await self.cycle_integrator.neural_evolution.load_neural_state(filename)
        print(f"📥 Neural state loaded from: {filename}")
    
    def run_server_mode(self, host='0.0.0.0', port=5000):
        """🌐 Run web server mode with neural dashboard"""
        
        async def init_and_run():
            await self.initialize_systems()
            
            print(f"\n🌐 ΩSIGIL NEURAL EVOLUTION SERVER STARTING...")
            print(f"   Main Dashboard: http://{host}:{port}/")
            print(f"   Neural Dashboard: http://{host}:{port}/neural-dashboard")
            print(f"   API Status: http://{host}:{port}/api/neural-status")
            print("=" * 60)
            
            # Setup signal handlers
            def signal_handler(signum, frame):
                print("\n🔮 Shutting down ΩSIGIL Neural Evolution...")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Run Flask app
            self.flask_app.run(host=host, port=port, debug=False)
        
        asyncio.run(init_and_run())
    
    async def run_demo_mode(self):
        """🎯 Run demonstration mode with neural evolution"""
        
        await self.initialize_systems()
        
        print("\n🎯 ΩSIGIL NEURAL EVOLUTION DEMO")
        print("=" * 60)
        
        # Demo 1: Signal Enhancement
        print("📡 DEMO 1: Signal Enhancement with Neural Evolution")
        demo_signal = {
            'asset': 'BTC',
            'strength': 0.7,
            'price_change_24h': 0.05,
            'volatility': 0.06,
            'emotional_wave': 0.8
        }
        
        enhanced = await self.cycle_integrator.enhance_signal_evaluation(demo_signal)
        print(f"   Original Signal: {demo_signal['strength']:.2f}")
        print(f"   Enhanced Signal: {enhanced['strength']:.2f}")
        if 'neural_enhancement' in enhanced:
            print(f"   Recommended: {enhanced['neural_enhancement']['recommended_ritual']}")
        
        # Demo 2: Learning Simulation
        print("\n🧠 DEMO 2: Learning from Trading Cycles")
        demo_cycles = [
            {
                'cycle_id': 'DEMO_BTC_001',
                'asset': 'BTC',
                'profits': 0.025,
                'entry_price': 45000,
                'exit_price': 46125,
                'duration_hours': 2.5,
                'signal_strength': 0.8,
                'sigils_used': ['SPEARHEAD', 'HOURGLASS']
            },
            {
                'cycle_id': 'DEMO_ETH_002',
                'asset': 'ETH',
                'profits': -0.01,
                'entry_price': 3000,
                'exit_price': 2970,
                'duration_hours': 1.2,
                'signal_strength': 0.6,
                'sigils_used': ['SPEARHEAD']
            }
        ]
        
        for cycle in demo_cycles:
            await self.cycle_integrator.capture_cycle_completion(cycle)
            print(f"   Learned from: {cycle['cycle_id']} ({cycle['profits']:+.1%})")
        
        # Demo 3: Prediction
        print("\n🔮 DEMO 3: Neural Prediction")
        guidance = await self.cycle_integrator.get_neural_guidance('BTC', 'SNIPER_FLIP')
        print(f"   BTC SNIPER_FLIP Prediction: {guidance['proposed_ritual']['success_probability']:.1%}")
        print(f"   Reasoning: {guidance['proposed_ritual']['reasoning']}")
        
        # Demo 4: Intelligence Status
        print("\n📊 DEMO 4: Intelligence Evolution Status")
        status = self.cycle_integrator.get_learning_dashboard_data()
        print(f"   Intelligence Score: {status['intelligence_score']:.3f}")
        print(f"   Total Cycles Learned: {status['total_cycles']}")
        print(f"   Prediction Accuracy: {status['prediction_accuracy']:.3f}")
        
        print("\n✅ NEURAL EVOLUTION DEMO COMPLETE")
        print("🧬 The system is now learning and evolving with each cycle")

def main():
    """🚀 Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python run_neural_evolution.py <mode>")
        print("Modes: interactive, server, demo")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    runner = NeuralEvolutionRunner()
    
    try:
        if mode == "interactive":
            asyncio.run(runner.run_interactive_mode())
        elif mode == "server":
            runner.run_server_mode()
        elif mode == "demo":
            asyncio.run(runner.run_demo_mode())
        else:
            print(f"❌ Unknown mode: {mode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🔮 ΩSIGIL Neural Evolution shutdown complete")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

