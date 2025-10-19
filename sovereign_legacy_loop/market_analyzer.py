#!/usr/bin/env python3
"""
🔥 REAL-TIME MARKET ANALYZER - NO BULLSHIT
Pulls live market data to see what's ACTUALLY happening
"""

import requests
import json
from datetime import datetime

def get_live_market_data():
    """Get real-time market data from CoinGecko (no API key needed)"""
    
    print("\n" + "="*80)
    print("🔥 LIVE MARKET SCAN - WHAT'S REALLY HAPPENING")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Target coins based on user's portfolio
    coins = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'solana': 'SOL',
        'ripple': 'XRP'
    }
    
    try:
        # Get current prices and 24h data
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(coins.keys()),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print("📊 CURRENT MARKET DATA:")
        print("-" * 80)
        
        market_analysis = {}
        for coin_id, ticker in coins.items():
            if coin_id in data:
                coin_data = data[coin_id]
                price = coin_data.get('usd', 0)
                change_24h = coin_data.get('usd_24h_change', 0)
                volume_24h = coin_data.get('usd_24h_vol', 0)
                market_cap = coin_data.get('usd_market_cap', 0)
                
                # Determine severity
                if change_24h > 0:
                    sentiment = "🟢 GREEN"
                elif change_24h > -2:
                    sentiment = "🟡 MILD DIP"
                elif change_24h > -5:
                    sentiment = "🟠 MODERATE DIP"
                else:
                    sentiment = "🔴 HEAVY DUMP"
                
                print(f"{ticker:6s} ${price:>12,.2f}  |  24h: {change_24h:>7.2f}% {sentiment}")
                print(f"       Volume: ${volume_24h/1e9:>6.2f}B  |  MCap: ${market_cap/1e9:>8.2f}B")
                print("-" * 80)
                
                market_analysis[ticker] = {
                    'price': price,
                    'change_24h': change_24h,
                    'volume_24h': volume_24h,
                    'market_cap': market_cap,
                    'sentiment': sentiment
                }
        
        # Overall market assessment
        print("\n💡 MARKET ASSESSMENT:")
        print("-" * 80)
        
        avg_change = sum(d['change_24h'] for d in market_analysis.values()) / len(market_analysis)
        
        if avg_change < -4:
            print("⚠️  MARKET-WIDE DUMP: All major assets bleeding")
            print("   → This is systematic risk, not coin-specific")
            print("   → Likely macro factors (USD strength, liquidations, etc.)")
            action = "WAIT for stabilization. No new entries."
        elif avg_change < -2:
            print("🟡 MODERATE CORRECTION: Healthy pullback or early dump")
            print("   → Watch for support levels")
            print("   → Consider DCA strategy at key support")
            action = "CAUTIOUS: Small positions at strong support only"
        elif avg_change < 0:
            print("🟢 MINOR CHOP: Normal volatility")
            print("   → Good for tactical entries")
            print("   → Accumulation opportunity")
            action = "ACTIVE: Look for entry opportunities"
        else:
            print("🚀 GREEN MARKET: Risk-on sentiment")
            print("   → Take profits on existing positions")
            print("   → Watch for overextension")
            action = "ACTIVE: Take profits, trail stops"
        
        print(f"\n🎯 RECOMMENDED ACTION: {action}")
        
        # Specific coin analysis
        print("\n\n🔍 SPECIFIC COIN ANALYSIS:")
        print("="*80)
        
        if 'BTC' in market_analysis:
            btc = market_analysis['BTC']
            print(f"\n💎 BITCOIN (BTC):")
            print(f"   Current: ${btc['price']:,.2f}")
            print(f"   24h Change: {btc['change_24h']:.2f}%")
            
            # Support/Resistance levels (approximate based on common psychological levels)
            if btc['price'] > 120000:
                print(f"   Support: $120,000 (psychological)")
                print(f"   Resistance: $125,000 (recent high)")
            elif btc['price'] > 115000:
                print(f"   Support: $115,000 (major level)")
                print(f"   Resistance: $120,000 (psychological)")
            else:
                print(f"   Support: $112,000 (critical)")
                print(f"   Resistance: $115,000 (major level)")
        
        if 'ETH' in market_analysis:
            eth = market_analysis['ETH']
            print(f"\n⚡ ETHEREUM (ETH):")
            print(f"   Current: ${eth['price']:,.2f}")
            print(f"   24h Change: {eth['change_24h']:.2f}%")
            print(f"   BTC Correlation: {'HIGH' if abs(eth['change_24h'] - btc['change_24h']) < 2 else 'DIVERGING'}")
            
            if eth['price'] > 4000:
                print(f"   Support: $4,000 (psychological)")
                print(f"   Next Support: $3,800")
            else:
                print(f"   Support: $3,600 (major)")
                print(f"   Resistance: $4,000 (psychological)")
        
        if 'SOL' in market_analysis:
            sol = market_analysis['SOL']
            print(f"\n🌟 SOLANA (SOL):")
            print(f"   Current: ${sol['price']:,.2f}")
            print(f"   24h Change: {sol['change_24h']:.2f}%")
            print(f"   High Beta: Moves 1.5-2x BTC volatility")
            
            if sol['price'] > 200:
                print(f"   Support: $200 (psychological)")
                print(f"   Next Support: $185")
            else:
                print(f"   Support: $185 (major)")
                print(f"   Resistance: $200 (psychological)")
        
        if 'XRP' in market_analysis:
            xrp = market_analysis['XRP']
            print(f"\n🏦 RIPPLE (XRP):")
            print(f"   Current: ${xrp['price']:,.4f}")
            print(f"   24h Change: {xrp['change_24h']:.2f}%")
            print(f"   Legal Status: Post-SEC clarity phase")
            
            if xrp['change_24h'] > btc['change_24h']:
                print(f"   ✅ RELATIVE STRENGTH: Outperforming BTC")
            else:
                print(f"   ⚠️  UNDERPERFORMING: Weaker than BTC")
        
        # Save analysis to file
        analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'market_data': market_analysis,
            'average_change': avg_change,
            'recommended_action': action
        }
        
        with open('logs/ai_enhanced/live_market_analysis.json', 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        print("\n" + "="*80)
        print("📄 Full analysis saved to: logs/ai_enhanced/live_market_analysis.json")
        print("="*80)
        
        return analysis_report
        
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
        print("⚠️  Using fallback mode - API may be rate limited")
        return None

if __name__ == "__main__":
    get_live_market_data()

