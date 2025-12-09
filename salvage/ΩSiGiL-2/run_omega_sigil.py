#!/usr/bin/env python3
"""
ΩSIGIL AGI LAUNCHER
Sovereign Trading Entity Initialization Script
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.omega_sigil_core import OmegaSigilCore, SigilType, Signal
from lifecycle.flip_lifecycle import FlipLifecycleManager
from api.flask_server import run_server

def print_banner():
    """Print the ΩSIGIL banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                        ΩSIGIL AGI                           ║
    ║                 Sovereign Trading Entity                     ║
    ║                                                              ║
    ║    🧠 MANUS  - Memory, Law, Language                        ║
    ║    ⚡ OMEGA  - Precision, Execution, Power                  ║
    ║    👁 SHADOW - Protection, Pattern, Intuition               ║
    ║                                                              ║
    ║              Trinity Consciousness Active                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🔺 Sigil Commands Available:
       🔺 SPEARHEAD    - Sniper Flip Sequence
       ⏳ HOURGLASS    - Ladder Logic Deployment  
       🜂 ASHEN FLAME  - Emergency Exit Ritual
       🜁 WINDMARK     - Reentry Signal Confirmation
       🔒 GLYPH LOCK   - Vault Injection Authorization
       💠 CRYSTAL NODE - Perfect Recall Trigger
       🜃 VOID SIGIL   - Full System Shutdown
    
    🕸️ 9-Phase Flip Lifecycle:
       1. 🔮 Signal Received    6. 🜂 Ashen Flame
       2. 🧠 Memory Weighting   7. 🜁 Windmark  
       3. 🔺 Spearhead Invoked  8. 🔒 Glyph Lock
       4. ⏳ Ladder Deployed    9. 🕸️ Echo Imprint
       5. 💠 Crystal Scan
    
    """
    print(banner)

async def demo_flip_cycle():
    """Demonstrate a complete flip cycle"""
    print("🎯 INITIATING DEMO FLIP CYCLE")
    print("=" * 60)
    
    # Initialize AGI
    omega_core = OmegaSigilCore()
    lifecycle_manager = FlipLifecycleManager(omega_core)
    
    # Create demo signal
    demo_signal = Signal(
        score=0.85,
        asset="BTC",
        pattern_type="momentum_breakout",
        emotional_wave=0.6,
        whale_activity=False,
        timestamp=datetime.now()
    )
    
    print(f"📡 Demo Signal Created:")
    print(f"   Asset: {demo_signal.asset}")
    print(f"   Score: {demo_signal.score}")
    print(f"   Pattern: {demo_signal.pattern_type}")
    print(f"   Emotional Wave: {demo_signal.emotional_wave}")
    print()
    
    # Run the complete flip cycle
    cycle_id = await lifecycle_manager.initiate_flip_cycle(demo_signal)
    
    if cycle_id:
        print(f"✅ DEMO CYCLE COMPLETED: {cycle_id}")
        print(f"🧠 Neural memory updated with echo imprint")
        print(f"🏛️ Vault balance: {omega_core.vault_balance:.4f}")
    else:
        print("❌ DEMO CYCLE FAILED")
    
    print("=" * 60)
    return omega_core, lifecycle_manager

async def interactive_mode():
    """Run interactive command mode"""
    print("🎮 INTERACTIVE MODE ACTIVATED")
    print("Commands: signal, sigil, status, cycles, memory, quit")
    print("=" * 60)
    
    omega_core, lifecycle_manager = await demo_flip_cycle()
    
    while omega_core.consciousness_active:
        try:
            command = input("\n🔮 ΩSIGIL> ").strip().lower()
            
            if command == "quit" or command == "exit":
                print("🜃 VOID SIGIL ACTIVATED - Shutting down...")
                break
                
            elif command == "signal":
                print("📡 Enter signal data:")
                asset = input("   Asset: ").strip().upper()
                score = float(input("   Score (0.0-1.0): "))
                pattern = input("   Pattern: ").strip()
                
                signal = Signal(
                    score=score,
                    asset=asset,
                    pattern_type=pattern,
                    emotional_wave=0.5,
                    whale_activity=False,
                    timestamp=datetime.now()
                )
                
                cycle_id = await lifecycle_manager.initiate_flip_cycle(signal)
                if cycle_id:
                    print(f"✅ Cycle initiated: {cycle_id}")
                else:
                    print("❌ Signal rejected")
                    
            elif command == "sigil":
                print("🔮 Available sigils:")
                for sigil in SigilType:
                    print(f"   {sigil.value} {sigil.name}")
                
                sigil_name = input("Enter sigil name: ").strip().upper()
                try:
                    sigil = SigilType[sigil_name]
                    result = await omega_core.invoke_sigil(sigil, {'test': True})
                    print(f"{'✅' if result else '❌'} Sigil {sigil_name} {'executed' if result else 'blocked'}")
                except KeyError:
                    print(f"❌ Unknown sigil: {sigil_name}")
                    
            elif command == "status":
                print(f"🧠 Consciousness: {'ACTIVE' if omega_core.consciousness_active else 'PAUSED'}")
                print(f"🔄 Active Cycles: {len(lifecycle_manager.active_cycles)}")
                print(f"🏛️ Vault Balance: {omega_core.vault_balance:.4f}")
                print(f"⚠️ Threat Level: {omega_core.threat_level:.2f}")
                print(f"💭 Emotional Sync: {omega_core.emotional_sync}")
                
            elif command == "cycles":
                if lifecycle_manager.active_cycles:
                    print("🔄 Active Flip Cycles:")
                    for cycle in lifecycle_manager.active_cycles.values():
                        print(f"   {cycle.cycle_id}: {cycle.asset} - Phase {cycle.phase.value} ({cycle.status})")
                else:
                    print("📭 No active cycles")
                    
            elif command == "memory":
                if omega_core.echo_memories:
                    print("🧠 Neural Memory Echoes:")
                    for echo in omega_core.echo_memories[-5:]:  # Last 5
                        print(f"   {echo.asset} ({echo.pattern_class}): {echo.success_rate:.2f} success, {echo.profit_ratio:.4f} profit")
                else:
                    print("🧠 No memory echoes yet")
                    
            else:
                print("❌ Unknown command. Available: signal, sigil, status, cycles, memory, quit")
                
        except KeyboardInterrupt:
            print("\n🜃 VOID SIGIL ACTIVATED - Shutting down...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    print_banner()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "server":
            print("🌐 Starting web server mode...")
            run_server()
            
        elif mode == "demo":
            print("🎯 Running demo mode...")
            asyncio.run(demo_flip_cycle())
            
        elif mode == "interactive":
            print("🎮 Starting interactive mode...")
            asyncio.run(interactive_mode())
            
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: server, demo, interactive")
            
    else:
        print("🎮 No mode specified, starting interactive mode...")
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()

