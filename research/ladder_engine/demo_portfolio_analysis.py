#!/usr/bin/env python3
"""
Demo Portfolio Analysis
Shows exactly what the secure portfolio analyzer would return
Uses simulated data for demonstration purposes
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List

def generate_demo_portfolio() -> Dict[str, Any]:
    """Generate realistic demo portfolio data"""
    
    # Simulated current prices (realistic as of 2025)
    current_prices = {
        'BTC': 45000.00,
        'ETH': 3000.00,
        'ADA': 0.45,
        'INJ': 25.50,
        'ATOM': 12.80,
        'RNDR': 8.75,
        'BONK': 0.000032,
        'WIF': 2.65,
        'STMX': 0.028,
        'KAVA': 0.95,
        'ALGO': 0.18,
        'XTZ': 1.25,
        'NEAR': 4.20,
        'USDT': 1.00
    }
    
    # Simulated portfolio holdings
    holdings = [
        {'asset': 'BTC', 'total': 0.125, 'avg_entry': 42000.00},
        {'asset': 'ETH', 'total': 1.85, 'avg_entry': 2800.00},
        {'asset': 'ADA', 'total': 2200.0, 'avg_entry': 0.42},
        {'asset': 'INJ', 'total': 45.0, 'avg_entry': 22.00},
        {'asset': 'ATOM', 'total': 85.0, 'avg_entry': 11.50},
        {'asset': 'RNDR', 'total': 65.0, 'avg_entry': 7.80},
        {'asset': 'BONK', 'total': 15000000.0, 'avg_entry': 0.000028},
        {'asset': 'WIF', 'total': 180.0, 'avg_entry': 2.40},
        {'asset': 'STMX', 'total': 8500.0, 'avg_entry': 0.025},
        {'asset': 'USDT', 'total': 1250.0, 'avg_entry': 1.00}
    ]
    
    # Calculate portfolio metrics
    balances = []
    total_usd_value = 0.0
    
    for holding in holdings:
        asset = holding['asset']
        total = holding['total']
        avg_entry = holding['avg_entry']
        current_price = current_prices.get(asset, 0)
        
        usd_value = total * current_price
        total_usd_value += usd_value
        
        # Calculate unrealized PnL
        entry_value = total * avg_entry
        unrealized_pnl = usd_value - entry_value
        pnl_percentage = (unrealized_pnl / entry_value * 100) if entry_value > 0 else 0
        
        balances.append({
            'asset': asset,
            'free': total * 0.9,  # 90% free
            'locked': total * 0.1,  # 10% in orders
            'total': total,
            'avg_entry': avg_entry,
            'current_price': current_price,
            'usd_value': usd_value,
            'unrealized_pnl': unrealized_pnl,
            'pnl_percentage': pnl_percentage
        })
    
    # Sort by USD value
    balances.sort(key=lambda x: x['usd_value'], reverse=True)
    
    # Calculate percentages
    for balance in balances:
        balance['percentage'] = (balance['usd_value'] / total_usd_value * 100) if total_usd_value > 0 else 0
    
    # Simulated open orders
    open_orders = [
        {
            'symbol': 'RNDRUSDT',
            'side': 'BUY',
            'type': 'LIMIT',
            'quantity': 25.0,
            'price': 8.20,
            'status': 'NEW',
            'time': '2025-01-07T10:30:00Z'
        },
        {
            'symbol': 'BONKUSDT',
            'side': 'SELL',
            'type': 'LIMIT',
            'quantity': 5000000.0,
            'price': 0.000035,
            'status': 'NEW',
            'time': '2025-01-07T09:15:00Z'
        },
        {
            'symbol': 'WIFUSDT',
            'side': 'SELL',
            'type': 'STOP_LOSS_LIMIT',
            'quantity': 90.0,
            'price': 2.25,
            'status': 'NEW',
            'time': '2025-01-07T08:45:00Z'
        }
    ]
    
    # Simulated recent trades
    recent_trades = [
        {
            'symbol': 'INJUSDT',
            'side': 'BUY',
            'quantity': 15.0,
            'price': 25.50,
            'commission': 0.383,
            'commission_asset': 'USDT',
            'time': '2025-01-07T14:22:00Z'
        },
        {
            'symbol': 'STMXUSDT',
            'side': 'SELL',
            'quantity': 2000.0,
            'price': 0.029,
            'commission': 0.058,
            'commission_asset': 'USDT',
            'time': '2025-01-07T13:45:00Z'
        },
        {
            'symbol': 'ADAUSDT',
            'side': 'BUY',
            'quantity': 500.0,
            'price': 0.44,
            'commission': 0.22,
            'commission_asset': 'USDT',
            'time': '2025-01-07T12:30:00Z'
        }
    ]
    
    # SLEEP/FLIP allocation analysis
    sleep_assets = ['ADA', 'KAVA', 'INJ', 'COTI', 'ALGO', 'XTZ', 'ATOM', 'FLOW', 'NEAR']
    flip_assets = ['BTC', 'ETH', 'BONK', 'WIF', 'RNDR', 'STMX']
    
    sleep_value = sum(b['usd_value'] for b in balances if b['asset'] in sleep_assets)
    flip_value = sum(b['usd_value'] for b in balances if b['asset'] in flip_assets)
    other_value = total_usd_value - sleep_value - flip_value
    
    sleep_percentage = (sleep_value / total_usd_value * 100) if total_usd_value > 0 else 0
    flip_percentage = (flip_value / total_usd_value * 100) if total_usd_value > 0 else 0
    
    # Generate alerts
    alerts = []
    target_sleep = 60.0
    target_flip = 40.0
    
    if abs(sleep_percentage - target_sleep) > 5.0:
        alerts.append(f"🚨 SLEEP allocation {sleep_percentage:.1f}% deviates >5% from target {target_sleep}%")
    
    if abs(flip_percentage - target_flip) > 5.0:
        alerts.append(f"🚨 FLIP allocation {flip_percentage:.1f}% deviates >5% from target {target_flip}%")
    
    # Check for large positions
    for balance in balances:
        if balance['percentage'] > 25.0:
            alerts.append(f"⚠️  Large position: {balance['asset']} represents {balance['percentage']:.1f}% of portfolio")
    
    current_time = datetime.now(timezone.utc)
    world_time_sync = f"World Time Sync – {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    
    return {
        'timestamp': world_time_sync,
        'account_summary': {
            'total_usd_value': round(total_usd_value, 2),
            'total_unrealized_pnl': round(sum(b['unrealized_pnl'] for b in balances), 2),
            'asset_count': len(balances),
            'open_orders_count': len(open_orders),
            'recent_trades_count': len(recent_trades)
        },
        'balances': balances,
        'open_orders': open_orders,
        'recent_trades': recent_trades,
        'allocation_analysis': {
            'sleep_tier': {
                'value': round(sleep_value, 2),
                'percentage': round(sleep_percentage, 1),
                'assets': [b for b in balances if b['asset'] in sleep_assets]
            },
            'flip_tier': {
                'value': round(flip_value, 2),
                'percentage': round(flip_percentage, 1),
                'assets': [b for b in balances if b['asset'] in flip_assets]
            },
            'other': {
                'value': round(other_value, 2),
                'percentage': round(100 - sleep_percentage - flip_percentage, 1)
            }
        },
        'alerts': alerts
    }

def print_demo_portfolio_report(analysis: Dict[str, Any]):
    """Print formatted demo portfolio report"""
    print("🎯 DEMO PORTFOLIO SNAPSHOT")
    print(f"⏰ {analysis['timestamp']}")
    print("=" * 70)
    
    # Account Summary
    summary = analysis['account_summary']
    total_pnl = summary['total_unrealized_pnl']
    pnl_icon = "📈" if total_pnl > 0 else "📉" if total_pnl < 0 else "📊"
    
    print(f"💰 Total Portfolio Value: ${summary['total_usd_value']:,.2f}")
    print(f"{pnl_icon} Total Unrealized PnL: ${total_pnl:,.2f}")
    print(f"📈 Active Assets: {summary['asset_count']}")
    print(f"📋 Open Orders: {summary['open_orders_count']}")
    print(f"⏱️  Recent Trades (24h): {summary['recent_trades_count']}")
    
    # Holdings with PnL
    print(f"\n📈 POSITIONS (Symbol | Qty | Avg Entry | Current | PnL % | USD Value | Weight)")
    print("-" * 70)
    for balance in analysis['balances']:
        pnl_pct = balance['pnl_percentage']
        pnl_icon = "🟢" if pnl_pct > 0 else "🔴" if pnl_pct < 0 else "⚪"
        
        print(f"{pnl_icon} {balance['asset']:<6} | "
              f"{balance['total']:>10,.2f} | "
              f"${balance['avg_entry']:>8.4f} | "
              f"${balance['current_price']:>8.4f} | "
              f"{pnl_pct:>6.1f}% | "
              f"${balance['usd_value']:>8,.0f} | "
              f"{balance['percentage']:>5.1f}%")
    
    # Allocation Analysis
    alloc = analysis['allocation_analysis']
    print(f"\n🎯 ALLOCATION ANALYSIS")
    print("-" * 70)
    print(f"💤 SLEEP Tier (Passive): ${alloc['sleep_tier']['value']:>8,.0f} ({alloc['sleep_tier']['percentage']:>5.1f}%)")
    
    # Show SLEEP assets
    for asset in alloc['sleep_tier']['assets']:
        print(f"   └─ {asset['asset']}: ${asset['usd_value']:>6,.0f} ({asset['pnl_percentage']:>+5.1f}%)")
    
    print(f"⚡ FLIP Tier (Active):   ${alloc['flip_tier']['value']:>8,.0f} ({alloc['flip_tier']['percentage']:>5.1f}%)")
    
    # Show FLIP assets
    for asset in alloc['flip_tier']['assets']:
        print(f"   └─ {asset['asset']}: ${asset['usd_value']:>6,.0f} ({asset['pnl_percentage']:>+5.1f}%)")
    
    print(f"🔄 Other/Cash:           ${alloc['other']['value']:>8,.0f} ({alloc['other']['percentage']:>5.1f}%)")
    
    # Open Orders
    if analysis['open_orders']:
        print(f"\n📋 OPEN ORDERS")
        print("-" * 70)
        for order in analysis['open_orders']:
            side_icon = "🟢" if order['side'] == 'BUY' else "🔴"
            print(f"{side_icon} {order['symbol']} | {order['side']} {order['type']} | "
                  f"{order['quantity']:,.0f} @ ${order['price']:.6f} | {order['status']}")
    
    # Recent Trades
    if analysis['recent_trades']:
        print(f"\n⏱️  RECENT TRADES")
        print("-" * 70)
        for trade in analysis['recent_trades']:
            side_icon = "🟢" if trade['side'] == 'BUY' else "🔴"
            print(f"{side_icon} {trade['symbol']} | {trade['side']} | "
                  f"{trade['quantity']:,.0f} @ ${trade['price']:.6f} | "
                  f"Fee: {trade['commission']:.3f} {trade['commission_asset']}")
    
    # Alerts
    if analysis['alerts']:
        print(f"\n🚨 PORTFOLIO ALERTS")
        print("-" * 70)
        for alert in analysis['alerts']:
            print(alert)
    else:
        print(f"\n✅ NO ALERTS - Portfolio allocation within target ranges")
    
    print("\n" + "=" * 70)
    print("📊 This is a DEMONSTRATION using simulated data")
    print("🔒 Use the secure_portfolio_analyzer.py script with your real credentials")

def main():
    """Run demo portfolio analysis"""
    print("🎯 DEMO PORTFOLIO ANALYSIS")
    print("=" * 70)
    print("📊 This demonstrates the exact format you'd receive")
    print("🛡️  Using simulated data for security")
    print()
    
    # Generate demo data
    analysis = generate_demo_portfolio()
    
    # Print formatted report
    print_demo_portfolio_report(analysis)
    
    # Save demo data
    with open('demo_portfolio_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n📄 Demo analysis saved to: demo_portfolio_analysis.json")

if __name__ == "__main__":
    main()

