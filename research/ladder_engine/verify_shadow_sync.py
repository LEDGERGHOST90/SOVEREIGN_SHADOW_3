
import sys
import os

# Add project root to path so imports work
sys.path.append(os.path.abspath("/Volumes/LegacySafe/SS_III"))

from research.ladder_engine.paper_trading_engine import MarketSimulator

def verify_engine_sync():
    sim = MarketSimulator()
    
    tokens_to_check = {
        'MASK': 0.07,
        'TRUMP': 0.15,
        'ARB': 0.05,
        'QNT': 0.04
    }
    
    print("🧬 Verifying Shadow Stack Integration...")
    all_passed = True
    
    for token, expected_vol in tokens_to_check.items():
        # Check volatility
        # The simulator uses partial matching: "if key in symbol"
        # So we test with the keys we added
        actual_vol = sim.get_volatility(token)
        
        # Check base price existence
        symbol_key = f"{token}USDT"
        price_exists = symbol_key in sim.current_prices
        
        status = "✅" if (actual_vol == expected_vol and price_exists) else "❌"
        if status == "❌": 
            all_passed = False
            
        print(f"{status} {token}: Volatility {actual_vol} (Expected {expected_vol}) | Base Price: {'Found' if price_exists else 'MISSING'}")

    if all_passed:
        print("\n✨ SUCCESS: Engine is fully synced with Shadow Stack strategy.")
    else:
        print("\n⚠️ FAILURE: Some tokens are not correctly configured.")

if __name__ == "__main__":
    verify_engine_sync()
