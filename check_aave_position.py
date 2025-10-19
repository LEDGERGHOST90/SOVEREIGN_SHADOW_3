#!/usr/bin/env python3
"""
🚨 URGENT: AAVE Position Health Check
Monitor your active stETH collateral position

USAGE:
    python3 check_aave_position.py
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def get_eth_price():
    """Get current ETH price from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data["ethereum"]["usd"]
    except Exception as e:
        print(f"Error fetching ETH price: {e}")
        return None

def calculate_liquidation_risk(steth_amount, steth_price_usd, borrowed_usdc):
    """
    Calculate liquidation risk for AAVE stETH position
    
    AAVE Parameters for stETH:
    - Liquidation Threshold: 82.5%
    - Liquidation Bonus: 5%
    - LTV: 75% (max safe borrow)
    """
    LIQUIDATION_THRESHOLD = 0.825
    SAFE_LTV = 0.75
    
    # Calculate current values
    collateral_value = steth_amount * steth_price_usd
    current_ltv = borrowed_usdc / collateral_value if collateral_value > 0 else 0
    
    # Health Factor calculation
    # Health Factor = (Collateral * Liquidation Threshold) / Borrowed
    health_factor = (collateral_value * LIQUIDATION_THRESHOLD) / borrowed_usdc if borrowed_usdc > 0 else 999
    
    # Liquidation price calculation
    # Liquidation when: collateral_value * 0.825 = borrowed_usdc
    # collateral_value = borrowed_usdc / 0.825
    # steth_amount * liquidation_price = borrowed_usdc / 0.825
    liquidation_price = (borrowed_usdc / LIQUIDATION_THRESHOLD) / steth_amount if steth_amount > 0 else 0
    
    # Safe LTV calculation
    safe_borrow_amount = collateral_value * SAFE_LTV
    borrow_headroom = safe_borrow_amount - borrowed_usdc
    
    # Risk assessment
    if health_factor < 1.0:
        risk_level = "🚨 CRITICAL - LIQUIDATION IMMINENT"
        risk_color = "RED"
    elif health_factor < 1.2:
        risk_level = "🔴 EXTREME DANGER - REPAY NOW"
        risk_color = "RED"
    elif health_factor < 1.5:
        risk_level = "🟠 HIGH RISK - Monitor closely"
        risk_color = "ORANGE"
    elif health_factor < 2.0:
        risk_level = "🟡 MODERATE RISK - Caution"
        risk_color = "YELLOW"
    else:
        risk_level = "🟢 SAFE - Good cushion"
        risk_color = "GREEN"
    
    return {
        "collateral_value_usd": collateral_value,
        "borrowed_usdc": borrowed_usdc,
        "current_ltv": current_ltv,
        "health_factor": health_factor,
        "liquidation_price_eth": liquidation_price,
        "safe_borrow_amount": safe_borrow_amount,
        "borrow_headroom": borrow_headroom,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "current_eth_price": steth_price_usd
    }

def display_position_analysis(position_data):
    """Display comprehensive position analysis"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚨 AAVE POSITION HEALTH CHECK                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print("📊 CURRENT POSITION:")
    print("=" * 80)
    print(f"Collateral (stETH): {position_data['steth_amount']:.4f} ETH")
    print(f"Collateral Value: ${position_data['collateral_value_usd']:,.2f}")
    print(f"Borrowed (USDC): ${position_data['borrowed_usdc']:,.2f}")
    print(f"Current ETH Price: ${position_data['current_eth_price']:,.2f}")
    print()
    
    print("📈 RISK METRICS:")
    print("=" * 80)
    print(f"Loan-to-Value (LTV): {position_data['current_ltv']*100:.2f}%")
    print(f"Health Factor: {position_data['health_factor']:.3f}")
    print(f"Risk Level: {position_data['risk_level']}")
    print()
    
    print("🎯 LIQUIDATION ANALYSIS:")
    print("=" * 80)
    print(f"Liquidation Price: ${position_data['liquidation_price_eth']:,.2f} per ETH")
    print(f"Current ETH Price: ${position_data['current_eth_price']:,.2f}")
    price_cushion = ((position_data['current_eth_price'] - position_data['liquidation_price_eth']) / position_data['current_eth_price']) * 100
    print(f"Price Cushion: {price_cushion:.1f}% ({position_data['current_eth_price'] - position_data['liquidation_price_eth']:,.0f} USD)")
    print()
    
    print("💰 BORROW CAPACITY:")
    print("=" * 80)
    print(f"Safe Borrow Amount (75% LTV): ${position_data['safe_borrow_amount']:,.2f}")
    print(f"Currently Borrowed: ${position_data['borrowed_usdc']:,.2f}")
    print(f"Additional Borrow Headroom: ${position_data['borrow_headroom']:,.2f}")
    print()
    
    # Action recommendations
    print("🎯 RECOMMENDED ACTIONS:")
    print("=" * 80)
    
    if position_data['health_factor'] < 1.2:
        print("🚨 URGENT ACTION REQUIRED:")
        print("   1. Repay immediately to bring Health Factor above 1.5")
        print(f"   2. Repay at least ${(position_data['borrowed_usdc'] * 0.4):,.2f} to be safe")
        print("   3. Or add more stETH collateral")
        print("   4. Do NOT wait - liquidation risk is HIGH")
    elif position_data['health_factor'] < 1.5:
        print("⚠️  CAUTION:")
        print("   1. Consider partial repayment to increase Health Factor")
        print(f"   2. Repay ${(position_data['borrowed_usdc'] * 0.2):,.2f} to get to safer zone")
        print("   3. Set price alerts for ETH at ${:,.0f}".format(position_data['liquidation_price_eth'] * 1.15))
        print("   4. Have repayment USDC ready")
    elif position_data['health_factor'] < 2.0:
        print("🟡 MONITOR CLOSELY:")
        print("   1. Your position is relatively safe but monitor during crashes")
        print("   2. If ETH drops 10-15%, reassess risk")
        print("   3. Keep $200-300 USDC ready for emergency repayment")
        print(f"   4. Set alert if ETH drops below ${position_data['current_eth_price'] * 0.90:,.0f}")
    else:
        print("✅ POSITION IS SAFE:")
        print("   1. Good cushion for volatility")
        print("   2. Can weather 20-30% ETH drop before risk")
        print("   3. Continue monitoring weekly")
        print("   4. Consider this a healthy leveraged position")
    
    print()
    print("=" * 80)
    
    # Save report
    os.makedirs('logs/ai_enhanced', exist_ok=True)
    report_file = Path('logs/ai_enhanced/aave_position_report.json')
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "position": position_data,
        "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"📄 Report saved to: {report_file}")
    print("=" * 80)

def main():
    """Main execution"""
    print("🚨 AAVE POSITION HEALTH CHECK")
    print("=" * 80)
    print()
    
    # Get current ETH price
    print("📡 Fetching current ETH price...")
    eth_price = get_eth_price()
    
    if not eth_price:
        print("❌ Could not fetch ETH price. Using manual input.")
        eth_price = float(input("Enter current ETH price: $"))
    else:
        print(f"✅ Current ETH Price: ${eth_price:,.2f}")
    
    print()
    
    # Get user's position data
    print("📊 Enter your AAVE position details:")
    print("(Check at: https://app.aave.com/)")
    print()
    
    try:
        steth_amount = float(input("Amount of stETH deposited as collateral (in ETH): "))
        borrowed_usdc = float(input("Amount of USDC borrowed: $"))
        
        # Calculate risk
        position_data = calculate_liquidation_risk(steth_amount, eth_price, borrowed_usdc)
        position_data['steth_amount'] = steth_amount
        
        # Display analysis
        display_position_analysis(position_data)
        
        # Save for monitoring
        position_config = {
            "steth_amount": steth_amount,
            "borrowed_usdc": borrowed_usdc,
            "last_checked": datetime.now().isoformat(),
            "liquidation_price": position_data['liquidation_price_eth'],
            "health_factor": position_data['health_factor']
        }
        
        config_file = Path('logs/ai_enhanced/aave_position_config.json')
        with open(config_file, 'w') as f:
            json.dump(position_config, f, indent=2)
        
        print(f"\n💾 Position config saved for automated monitoring")
        print(f"   Run this script anytime to check your position health")
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        print("Please enter numeric values only.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

