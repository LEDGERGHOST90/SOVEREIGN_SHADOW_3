#!/usr/bin/env python3
"""
🧠 MARKET INTELLIGENCE SYSTEM - YOUR TRADING BRAIN
Combines whale movements, news sentiment, and live prices
NEVER GET CAUGHT IN A DUMP AGAIN
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class MarketIntelligence:
    def __init__(self):
        self.whale_alert_api_key = None  # Get free key from whale-alert.io
        self.cryptopanic_api_key = None  # Get free key from cryptopanic.com
        
        # Your actual portfolio from screenshots
        self.portfolio = {
            'BTC': {
                'amount': 0.00169643,
                'avg_cost': 116717,
                'platform': 'Exchange'
            }
        }
    
    def get_whale_movements(self, min_value_usd: int = 1000000) -> List[Dict]:
        """Get recent whale movements (>$1M by default)"""
        print("\n🐋 SCANNING WHALE MOVEMENTS...")
        print("-" * 80)
        
        # For demo, using mock data structure
        # In production, uncomment API call below
        """
        if self.whale_alert_api_key:
            url = "https://api.whale-alert.io/v1/transactions"
            params = {
                'api_key': self.whale_alert_api_key,
                'min_value': min_value_usd,
                'start': int((datetime.now() - timedelta(hours=3)).timestamp()),
                'cursor': None
            }
            response = requests.get(url, params=params)
            whale_data = response.json()
        else:
        """
        whale_data = {
            'transactions': [
                {
                    'symbol': 'usdt',
                    'amount': 133000000,
                    'amount_usd': 133138985,
                    'from': {'owner': 'unknown'},
                    'to': {'owner': 'tether_treasury'},
                    'timestamp': int(datetime.now().timestamp()) - 7200,
                    'transaction_type': 'transfer'
                },
                {
                    'symbol': 'link',
                    'amount': 3999999,
                    'amount_usd': 83269988,
                    'from': {'owner': 'unknown'},
                    'to': {'owner': 'binance'},
                    'timestamp': int(datetime.now().timestamp()) - 720,
                    'transaction_type': 'transfer'
                },
                {
                    'symbol': 'usdc',
                    'amount': 63794388,
                    'amount_usd': 63780194,
                    'from': {'owner': 'circle'},
                    'to': {'owner': 'burned'},
                    'timestamp': int(datetime.now().timestamp()) - 1440,
                    'transaction_type': 'burn'
                }
            ]
        }
        
        movements = []
        sell_pressure_score = 0
        liquidity_drain_score = 0
        
        for tx in whale_data.get('transactions', []):
            age_mins = (datetime.now().timestamp() - tx['timestamp']) / 60
            
            movement = {
                'symbol': tx['symbol'].upper(),
                'amount': tx['amount'],
                'amount_usd': tx['amount_usd'],
                'from': tx['from']['owner'],
                'to': tx['to']['owner'],
                'age_mins': int(age_mins),
                'type': tx['transaction_type']
            }
            
            # Analyze impact
            if tx['to']['owner'] in ['binance', 'coinbase', 'kraken', 'okx', 'bitfinex']:
                movement['impact'] = 'SELL_PRESSURE'
                movement['severity'] = '🚨 CRITICAL'
                sell_pressure_score += tx['amount_usd'] / 1000000  # Score per million
                print(f"🚨 {tx['symbol'].upper()}: ${tx['amount_usd']:,.0f} → {tx['to']['owner'].upper()}")
                print(f"   ⚠️  DUMP INCOMING - {int(age_mins)} mins ago")
            elif 'treasury' in tx['to']['owner'] or tx['transaction_type'] == 'burn':
                movement['impact'] = 'LIQUIDITY_DRAIN'
                movement['severity'] = '🔥 HIGH'
                liquidity_drain_score += tx['amount_usd'] / 1000000
                print(f"🔥 {tx['symbol'].upper()}: ${tx['amount_usd']:,.0f} REMOVED")
                print(f"   💰 Less buying power - {int(age_mins)} mins ago")
            else:
                movement['impact'] = 'NEUTRAL'
                movement['severity'] = '⚠️  WATCH'
                print(f"⚠️  {tx['symbol'].upper()}: ${tx['amount_usd']:,.0f} moved")
                print(f"   📊 Unknown impact - {int(age_mins)} mins ago")
            
            movements.append(movement)
            print("-" * 80)
        
        # Calculate threat level
        total_threat = sell_pressure_score + (liquidity_drain_score * 0.5)
        
        if total_threat > 200:
            threat_level = "🔴 EXTREME DANGER - DO NOT BUY"
        elif total_threat > 100:
            threat_level = "🟠 HIGH RISK - WAIT FOR STABILIZATION"
        elif total_threat > 50:
            threat_level = "🟡 MODERATE RISK - SMALL POSITIONS ONLY"
        else:
            threat_level = "🟢 NORMAL - SAFE TO TRADE"
        
        print(f"\n💥 THREAT ASSESSMENT: {threat_level}")
        print(f"   Sell Pressure Score: {sell_pressure_score:.0f}")
        print(f"   Liquidity Drain Score: {liquidity_drain_score:.0f}")
        print(f"   Total Threat: {total_threat:.0f}")
        
        return movements, threat_level, total_threat
    
    def get_news_sentiment(self, coins: List[str] = ['BTC', 'ETH', 'SOL', 'XRP']) -> Dict:
        """Get aggregated news sentiment from CryptoPanic"""
        print("\n\n📰 CHECKING NEWS SENTIMENT...")
        print("-" * 80)
        
        # For demo - in production, use CryptoPanic API
        """
        if self.cryptopanic_api_key:
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                'auth_token': self.cryptopanic_api_key,
                'currencies': ','.join(coins),
                'filter': 'hot'
            }
            response = requests.get(url, params=params)
            news_data = response.json()
        else:
        """
        news_data = {
            'results': [
                {
                    'title': 'Bitcoin ETF sees $500M inflow - institutions accumulating',
                    'published_at': datetime.now().isoformat(),
                    'currencies': [{'code': 'BTC'}],
                    'kind': 'news',
                    'votes': {'positive': 142, 'negative': 12, 'important': 89}
                },
                {
                    'title': 'Ethereum gas fees spike as network congestion increases',
                    'published_at': datetime.now().isoformat(),
                    'currencies': [{'code': 'ETH'}],
                    'kind': 'news',
                    'votes': {'positive': 23, 'negative': 78, 'important': 45}
                },
                {
                    'title': 'Solana network experiences brief outage',
                    'published_at': datetime.now().isoformat(),
                    'currencies': [{'code': 'SOL'}],
                    'kind': 'news',
                    'votes': {'positive': 8, 'negative': 134, 'important': 67}
                },
                {
                    'title': 'XRP regulatory clarity boosts institutional interest',
                    'published_at': datetime.now().isoformat(),
                    'currencies': [{'code': 'XRP'}],
                    'kind': 'news',
                    'votes': {'positive': 189, 'negative': 23, 'important': 112}
                }
            ]
        }
        
        sentiment_by_coin = {}
        
        for article in news_data.get('results', [])[:10]:  # Top 10 articles
            for currency in article.get('currencies', []):
                coin = currency['code']
                if coin not in sentiment_by_coin:
                    sentiment_by_coin[coin] = {
                        'positive': 0,
                        'negative': 0,
                        'neutral': 0,
                        'important': 0,
                        'articles': []
                    }
                
                votes = article.get('votes', {})
                pos = votes.get('positive', 0)
                neg = votes.get('negative', 0)
                imp = votes.get('important', 0)
                
                sentiment_by_coin[coin]['positive'] += pos
                sentiment_by_coin[coin]['negative'] += neg
                sentiment_by_coin[coin]['important'] += imp
                sentiment_by_coin[coin]['articles'].append(article['title'])
        
        # Analyze sentiment
        for coin, data in sentiment_by_coin.items():
            total_votes = data['positive'] + data['negative']
            if total_votes > 0:
                sentiment_ratio = (data['positive'] - data['negative']) / total_votes
                
                if sentiment_ratio > 0.5:
                    sentiment = "🟢 BULLISH"
                elif sentiment_ratio > 0:
                    sentiment = "🟡 CAUTIOUSLY BULLISH"
                elif sentiment_ratio > -0.5:
                    sentiment = "🟠 CAUTIOUSLY BEARISH"
                else:
                    sentiment = "🔴 BEARISH"
                
                print(f"\n{coin}: {sentiment}")
                print(f"   Positive: {data['positive']} | Negative: {data['negative']} | Important: {data['important']}")
                print(f"   Sentiment Ratio: {sentiment_ratio:.2f}")
                print(f"   Top headline: {data['articles'][0][:70]}...")
            
        return sentiment_by_coin
    
    def get_live_prices(self) -> Dict:
        """Get current market prices"""
        print("\n\n💹 LIVE MARKET PRICES...")
        print("-" * 80)
        
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,solana,ripple',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            prices = {
                'BTC': {
                    'price': data['bitcoin']['usd'],
                    'change_24h': data['bitcoin']['usd_24h_change']
                },
                'ETH': {
                    'price': data['ethereum']['usd'],
                    'change_24h': data['ethereum']['usd_24h_change']
                },
                'SOL': {
                    'price': data['solana']['usd'],
                    'change_24h': data['solana']['usd_24h_change']
                },
                'XRP': {
                    'price': data['ripple']['usd'],
                    'change_24h': data['ripple']['usd_24h_change']
                }
            }
            
            for coin, data in prices.items():
                emoji = "🔴" if data['change_24h'] < -5 else "🟠" if data['change_24h'] < 0 else "🟢"
                print(f"{emoji} {coin}: ${data['price']:,.2f} ({data['change_24h']:+.2f}%)")
            
            return prices
            
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            return {}
    
    def analyze_portfolio_risk(self, prices: Dict, whale_threat: float) -> Dict:
        """Analyze your portfolio risk based on current conditions"""
        print("\n\n🎯 YOUR PORTFOLIO RISK ANALYSIS...")
        print("=" * 80)
        
        total_value = 0
        total_pnl = 0
        
        for coin, position in self.portfolio.items():
            if coin in prices:
                current_price = prices[coin]['price']
                position_value = position['amount'] * current_price
                pnl = (current_price - position['avg_cost']) * position['amount']
                pnl_percent = ((current_price - position['avg_cost']) / position['avg_cost']) * 100
                
                total_value += position_value
                total_pnl += pnl
                
                print(f"\n{coin} Position:")
                print(f"   Amount: {position['amount']:.8f} {coin}")
                print(f"   Avg Cost: ${position['avg_cost']:,.2f}")
                print(f"   Current: ${current_price:,.2f}")
                print(f"   Value: ${position_value:.2f}")
                print(f"   P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
                
                # Risk assessment
                if whale_threat > 200:
                    print(f"   ⚠️  EXTREME RISK: Whales dumping, consider stop loss")
                elif whale_threat > 100:
                    print(f"   ⚠️  HIGH RISK: Monitor closely, no new buys")
                elif pnl < 0:
                    print(f"   💎 UNDERWATER: Hold if thesis intact, review support levels")
                else:
                    print(f"   ✅ PROFITABLE: Consider taking profits or trailing stop")
        
        print(f"\n{'=' * 80}")
        print(f"Total Portfolio Value: ${total_value:.2f}")
        print(f"Total P&L: ${total_pnl:.2f}")
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'whale_threat': whale_threat
        }
    
    def trading_signal(self, whale_threat: float, sentiment: Dict, prices: Dict) -> str:
        """Generate clear BUY/SELL/HOLD signal"""
        print("\n\n🚦 TRADING SIGNAL...")
        print("=" * 80)
        
        # Count bearish signals
        bearish_signals = 0
        bullish_signals = 0
        
        # Whale threat
        if whale_threat > 100:
            bearish_signals += 2
            print("❌ Whale threat HIGH")
        elif whale_threat > 50:
            bearish_signals += 1
            print("⚠️  Whale threat MODERATE")
        else:
            bullish_signals += 1
            print("✅ Whale threat LOW")
        
        # Market direction
        if prices:
            avg_change = sum(p['change_24h'] for p in prices.values()) / len(prices)
            if avg_change < -4:
                bearish_signals += 2
                print("❌ Market bleeding (-4%+)")
            elif avg_change < 0:
                bearish_signals += 1
                print("⚠️  Market down")
            else:
                bullish_signals += 1
                print("✅ Market up")
        
        # Generate signal
        print(f"\nBearish Signals: {bearish_signals} | Bullish Signals: {bullish_signals}")
        print("-" * 80)
        
        if bearish_signals >= 3:
            signal = "🛑 DO NOT BUY - Wait for stabilization"
            action = "HOLD existing positions, set stop losses, NO new entries"
        elif bearish_signals >= 2:
            signal = "⚠️  CAUTION - Small positions only"
            action = "DCA at strong support levels ONLY, 50% normal size"
        elif bullish_signals >= bearish_signals:
            signal = "🟢 OKAY TO BUY - Normal trading"
            action = "Follow your trading plan, respect position sizes"
        else:
            signal = "🟡 NEUTRAL - Wait for clarity"
            action = "No trades unless exceptional opportunity"
        
        print(f"\n{signal}")
        print(f"Action: {action}")
        
        return signal
    
    def run_full_analysis(self):
        """Run complete market intelligence analysis"""
        print("\n" + "=" * 80)
        print("🧠 MARKET INTELLIGENCE SYSTEM - FULL SCAN")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Whale movements
        whale_movements, threat_level, threat_score = self.get_whale_movements()
        
        # 2. News sentiment
        sentiment = self.get_news_sentiment()
        
        # 3. Live prices
        prices = self.get_live_prices()
        
        # 4. Portfolio risk
        portfolio_risk = self.analyze_portfolio_risk(prices, threat_score)
        
        # 5. Trading signal
        signal = self.trading_signal(threat_score, sentiment, prices)
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'whale_movements': whale_movements,
            'threat_level': threat_level,
            'threat_score': threat_score,
            'news_sentiment': sentiment,
            'prices': prices,
            'portfolio_risk': portfolio_risk,
            'trading_signal': signal
        }
        
        with open('logs/ai_enhanced/market_intelligence_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("\n" + "=" * 80)
        print("📄 Full report saved: logs/ai_enhanced/market_intelligence_report.json")
        print("=" * 80)
        
        return report

if __name__ == "__main__":
    intel = MarketIntelligence()
    intel.run_full_analysis()

