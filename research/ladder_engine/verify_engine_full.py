
import sys
import os

# 🔧 CONFIGURATION: Add the project root to sys.path
# This fixes the "ModuleNotFoundError: No module named 'src'"
project_root = os.path.abspath("/Volumes/LegacySafe/SS_III")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from research.ladder_engine.paper_trading_engine import MarketSimulator
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print(f"Debug: sys.path is {sys.path}")
    sys.exit(1)

def verify_full_sync():
    sim = MarketSimulator()

    print("\n🔥 PAPER TRADING ENGINE - FULL ASSET SYNC")
    print("=" * 60)

    categories = {
        "📊 CORE HOLDINGS (Ledger + Coinbase)": ['BTC', 'ETH', 'SOL', 'XRP'],
        "🤖 AI BASKET (Coinbase Active)": ['FET', 'RNDR', 'SUI'],
        "🥷 SHADOW STACK": ['MASK', 'TRUMP', 'ARB', 'QNT', 'STMX', 'WIF', 'BONK']
    }

    total_verified = 0
    
    for category_name, tokens in categories.items():
        print(f"\n{category_name}")
        for token in tokens:
            # Check volatility
            vol = sim.get_volatility(token)
            
            # Check price (handle RNDR/RENDER mapping manually if needed, or rely on finding the key)
            # The user's code mapped RNDR -> RENDERUSDT for price check
            search_key = f"{token}USDT"
            if token == 'RNDR': 
                search_key = 'RENDERUSDT'
            
            price = sim.current_prices.get(search_key)
            
            if price is not None:
                print(f"  ✅ {token:<5} | Vol: {vol*100:4.0f}% | Price: ${price:,.2f}")
                total_verified += 1
            else:
                print(f"  ⚠️ {token:<5} | Vol: {vol*100:4.0f}% | Price: MISSING (Checked {search_key})")

    print("\n" + "=" * 60)
    print(f"✨ Total Asset Profiles Loaded: {len(sim.volatility_profiles)}")
    print(f"✨ Total Base Prices Loaded:   {len(sim.base_prices)}")

if __name__ == "__main__":
    verify_full_sync()
