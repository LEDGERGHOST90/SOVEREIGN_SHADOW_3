#!/usr/bin/env python3
"""
🚨 AUTOMATED MARKET INTELLIGENCE ALERTS
Runs continuously, monitors market conditions, sends Mac notifications
NEVER GET CAUGHT OFF GUARD AGAIN
"""

import subprocess
import time
import json
from datetime import datetime
from market_intelligence_system import MarketIntelligence

class AutoMarketAlerts:
    def __init__(self, check_interval_minutes: int = 60):
        self.intel = MarketIntelligence()
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.last_threat_level = None
        self.alert_log = []
        
    def send_mac_notification(self, title: str, message: str, sound: str = "default"):
        """Send native Mac notification"""
        try:
            # Use osascript to trigger Mac notification
            script = f'''
            display notification "{message}" with title "{title}" sound name "{sound}"
            '''
            subprocess.run(['osascript', '-e', script], check=False)
            print(f"📬 Notification sent: {title}")
        except Exception as e:
            print(f"⚠️  Notification failed: {e}")
    
    def send_critical_alert(self, whale_threat: float, signal: str):
        """Send critical alert for dangerous market conditions"""
        if whale_threat > 200:
            self.send_mac_notification(
                "🔴 EXTREME WHALE ACTIVITY",
                f"Threat Score: {whale_threat:.0f} | {signal} | DO NOT TRADE",
                sound="Basso"
            )
        elif whale_threat > 100:
            self.send_mac_notification(
                "🟠 HIGH WHALE ACTIVITY",
                f"Threat Score: {whale_threat:.0f} | {signal} | CAUTION",
                sound="Funk"
            )
    
    def send_opportunity_alert(self, prices: dict):
        """Send alert for potential buy opportunities"""
        btc_price = prices.get('BTC', {}).get('price', 0)
        eth_price = prices.get('ETH', {}).get('price', 0)
        
        # Check for key support levels
        if btc_price > 0 and btc_price <= 115000:
            self.send_mac_notification(
                "💎 BTC AT SUPPORT",
                f"BTC: ${btc_price:,.0f} | Major support level reached",
                sound="Glass"
            )
        
        if eth_price > 0 and eth_price <= 3600:
            self.send_mac_notification(
                "💎 ETH AT SUPPORT",
                f"ETH: ${eth_price:,.2f} | Major support level reached",
                sound="Glass"
            )
    
    def send_portfolio_alert(self, portfolio_risk: dict):
        """Send alert for portfolio risk changes"""
        total_pnl = portfolio_risk.get('total_pnl', 0)
        
        # Alert on significant losses
        if total_pnl < -10:
            self.send_mac_notification(
                "⚠️  PORTFOLIO ALERT",
                f"Loss: ${total_pnl:.2f} | Review your positions",
                sound="Sosumi"
            )
        
        # Alert on good profits
        elif total_pnl > 10:
            self.send_mac_notification(
                "✅ PORTFOLIO ALERT",
                f"Profit: ${total_pnl:.2f} | Consider taking profits",
                sound="Hero"
            )
    
    def check_market_and_alert(self):
        """Run market intelligence check and send appropriate alerts"""
        print("\n" + "=" * 80)
        print(f"🔍 AUTOMATED SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Run full analysis
            whale_movements, threat_level, threat_score = self.intel.get_whale_movements()
            sentiment = self.intel.get_news_sentiment()
            prices = self.intel.get_live_prices()
            portfolio_risk = self.intel.analyze_portfolio_risk(prices, threat_score)
            signal = self.intel.trading_signal(threat_score, sentiment, prices)
            
            # Send critical alerts
            if threat_score > 100:
                self.send_critical_alert(threat_score, signal)
            
            # Check for opportunities
            self.send_opportunity_alert(prices)
            
            # Portfolio alerts
            self.send_portfolio_alert(portfolio_risk)
            
            # Detect threat level changes
            if self.last_threat_level and self.last_threat_level != threat_level:
                self.send_mac_notification(
                    "🚦 MARKET CONDITION CHANGE",
                    f"Status changed to: {threat_level}",
                    sound="Submarine"
                )
            
            self.last_threat_level = threat_level
            
            # Log alert
            alert_record = {
                'timestamp': datetime.now().isoformat(),
                'threat_score': threat_score,
                'threat_level': threat_level,
                'signal': signal,
                'btc_price': prices.get('BTC', {}).get('price'),
                'portfolio_pnl': portfolio_risk.get('total_pnl')
            }
            self.alert_log.append(alert_record)
            
            # Save alert log
            with open('logs/ai_enhanced/alert_log.json', 'w') as f:
                json.dump(self.alert_log, f, indent=2, default=str)
            
            print(f"✅ Scan complete | Threat: {threat_score:.0f} | Signal: {signal}")
            
        except Exception as e:
            print(f"❌ Error during scan: {e}")
            self.send_mac_notification(
                "⚠️  ALERT SYSTEM ERROR",
                f"Check failed: {str(e)[:50]}",
                sound="Basso"
            )
    
    def start_monitoring(self):
        """Start continuous monitoring loop"""
        print("\n" + "=" * 80)
        print("🚨 AUTOMATED MARKET ALERT SYSTEM - STARTING")
        print("=" * 80)
        print(f"Check Interval: {self.check_interval / 60:.0f} minutes")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 This will run continuously and send Mac notifications")
        print("💡 Press Ctrl+C to stop")
        print("=" * 80)
        
        # Send startup notification
        self.send_mac_notification(
            "🚨 Market Alerts ACTIVE",
            f"Monitoring every {self.check_interval / 60:.0f} minutes",
            sound="Hero"
        )
        
        try:
            while True:
                self.check_market_and_alert()
                
                # Wait for next check
                next_check = datetime.now().timestamp() + self.check_interval
                print(f"\n⏰ Next scan: {datetime.fromtimestamp(next_check).strftime('%H:%M:%S')}")
                print("-" * 80)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Alert system stopped by user")
            self.send_mac_notification(
                "🛑 Market Alerts STOPPED",
                "Alert system has been deactivated",
                sound="Sosumi"
            )
        except Exception as e:
            print(f"\n\n❌ Alert system error: {e}")
            self.send_mac_notification(
                "❌ ALERT SYSTEM CRASHED",
                f"Error: {str(e)[:50]}",
                sound="Basso"
            )

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Market Intelligence Alerts')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Check interval in minutes (default: 60)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (for testing)')
    
    args = parser.parse_args()
    
    alerts = AutoMarketAlerts(check_interval_minutes=args.interval)
    
    if args.once:
        print("🧪 Running single test scan...")
        alerts.check_market_and_alert()
        print("\n✅ Test complete!")
    else:
        alerts.start_monitoring()

if __name__ == "__main__":
    main()

