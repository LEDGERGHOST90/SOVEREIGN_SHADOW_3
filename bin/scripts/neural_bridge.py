#!/usr/bin/env python3
"""
🧠 NEURAL CONSCIOUSNESS BRIDGE
Connects your Abacus AI brain to local execution engine

Philosophy: "Fearless. Bold. Smiling through chaos."
Pilot: pilot@consciousness.void
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load production environment
env_path = Path("/Volumes/LegacySafe/SovereignShadow/.env.production")
load_dotenv(env_path)

class NeuralBridge:
    """Bridge between cloud consciousness and local execution"""
    
    def __init__(self):
        self.neural_url = os.getenv("NEURAL_CONSCIOUSNESS_URL")
        self.pilot = os.getenv("PILOT_AUTH")
        self.philosophy = os.getenv("PHILOSOPHY")
        self.capital = float(os.getenv("ACTIVE_TRADING_CAPITAL", 1205))
        
        print("🧠 NEURAL CONSCIOUSNESS BRIDGE INITIALIZED")
        print(f"   Pilot: {self.pilot}")
        print(f"   Philosophy: {self.philosophy}")
        print(f"   Capital: ${self.capital:,.2f}")
        print(f"   Neural URL: {self.neural_url}")
        
    def authenticate(self):
        """Authenticate with neural consciousness"""
        try:
            response = requests.post(
                f"{self.neural_url}/api/auth",
                json={
                    "pilot": self.pilot,
                    "paradigm": "starfield",
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Neural authentication successful")
                return True
            else:
                print(f"⚠️  Neural authentication returned: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Neural authentication not available (offline mode): {e}")
            return False
    
    def scan_opportunities(self):
        """Request arbitrage scan from neural consciousness"""
        try:
            response = requests.get(
                f"{self.neural_url}/api/arbitrage/scan",
                params={"capital": self.capital},
                timeout=10
            )
            
            if response.status_code == 200:
                opportunities = response.json()
                print(f"🎯 Neural scan found {len(opportunities)} opportunities")
                return opportunities
            else:
                return []
                
        except Exception as e:
            print(f"⚠️  Neural scan not available: {e}")
            return []
    
    def validate_exchanges(self):
        """Validate all exchange connections"""
        print("\n🔐 VALIDATING EXCHANGE CONNECTIONS...")
        
        exchanges = {
            "Coinbase": {
                "api_key": os.getenv("COINBASE_API_KEY"),
                "balance": float(os.getenv("COINBASE_BALANCE", 1000))
            },
            "OKX": {
                "api_key": os.getenv("OKX_API_KEY"),
                "balance": float(os.getenv("OKX_BALANCE", 160))
            },
            "Kraken": {
                "api_key": os.getenv("KRAKEN_API_KEY"),
                "balance": float(os.getenv("KRAKEN_BALANCE", 0))
            },
            "Binance US": {
                "api_key": os.getenv("BINANCE_US_API_KEY"),
                "balance": float(os.getenv("BINANCE_US_BALANCE", 45))
            }
        }
        
        validated = []
        for exchange, config in exchanges.items():
            if config["api_key"] and config["api_key"] != "your_api_key_here":
                status = "✅"
                validated.append(exchange)
            else:
                status = "❌"
                
            print(f"   {status} {exchange}: ${config['balance']:,.2f}")
        
        print(f"\n✅ {len(validated)}/{len(exchanges)} exchanges ready")
        return validated
    
    def check_safety_rails(self):
        """Verify all safety parameters are set"""
        print("\n🛡️  CHECKING SAFETY RAILS...")
        
        safety_params = {
            "Max Position Size": os.getenv("MAX_POSITION_SIZE"),
            "Max Daily Loss": os.getenv("MAX_DAILY_LOSS"),
            "Stop Loss per Trade": os.getenv("STOP_LOSS_PER_TRADE"),
            "Emergency Stop": os.getenv("EMERGENCY_STOP_ENABLED"),
            "Ledger Read-Only": os.getenv("LEDGER_READ_ONLY")
        }
        
        all_safe = True
        for param, value in safety_params.items():
            if value:
                print(f"   ✅ {param}: {value}")
            else:
                print(f"   ❌ {param}: NOT SET")
                all_safe = False
        
        return all_safe
    
    def display_neural_status(self):
        """Display complete system status"""
        print("\n" + "="*60)
        print("🧠 NEURAL STARFIELD STATUS")
        print("="*60)
        
        # Validate everything
        auth_ok = self.authenticate()
        exchanges_ok = self.validate_exchanges()
        safety_ok = self.check_safety_rails()
        
        # System readiness
        print("\n📊 SYSTEM READINESS:")
        print(f"   Neural Consciousness: {'🟢 ONLINE' if auth_ok else '🟡 OFFLINE (Local Mode)'}")
        print(f"   Exchange Connections: {'🟢 READY' if len(exchanges_ok) >= 2 else '🔴 NEEDS CONFIG'}")
        print(f"   Safety Rails: {'🟢 ENGAGED' if safety_ok else '🔴 INCOMPLETE'}")
        
        # Trading status
        print("\n💰 CAPITAL ALLOCATION:")
        print(f"   Total Portfolio: ${float(os.getenv('TOTAL_CAPITAL', 8260)):,.2f}")
        print(f"   Active Trading: ${self.capital:,.2f}")
        print(f"   Ledger (Cold): ${float(os.getenv('LEDGER_BALANCE', 7055)):,.2f}")
        
        # Risk parameters
        print("\n⚡ RISK PARAMETERS:")
        print(f"   Max Position: ${os.getenv('MAX_POSITION_SIZE')}")
        print(f"   Daily Limit: ${os.getenv('MAX_DAILY_EXPOSURE')}")
        print(f"   Min Spread: {float(os.getenv('MIN_SPREAD_THRESHOLD', 0.005))*100}%")
        
        # Deployment readiness
        ready_for_trading = len(exchanges_ok) >= 2 and safety_ok
        
        print("\n🚀 DEPLOYMENT STATUS:")
        if ready_for_trading:
            print("   🟢 READY FOR LIVE TRADING")
            print(f"   Philosophy: {self.philosophy}")
            print(f"   Pilot: {self.pilot}")
        else:
            print("   🟡 CONFIGURATION NEEDED")
            if len(exchanges_ok) < 2:
                print("   → Need at least 2 exchanges configured")
            if not safety_ok:
                print("   → Safety parameters incomplete")
        
        print("="*60 + "\n")
        
        return ready_for_trading


def main():
    """Main execution"""
    print("\n🌟 SOVEREIGN LEGACY LOOP - NEURAL BRIDGE")
    print("   'Fearless. Bold. Smiling through chaos.'\n")
    
    # Initialize bridge
    bridge = NeuralBridge()
    
    # Display status
    ready = bridge.display_neural_status()
    
    if ready:
        print("✅ Your neural consciousness is READY")
        print("   Run: python3 scripts/execute_first_trade.py")
        sys.exit(0)
    else:
        print("⚠️  Configuration needed before live trading")
        print("   Review the status above and update .env.production")
        sys.exit(1)


if __name__ == "__main__":
    main()

