#!/usr/bin/env python3
"""
🚀 CLAUDE-GENERATED ARBITRAGE TRADING SYSTEM
Advanced multi-exchange arbitrage detection and execution
"""

import os
import sys
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import ccxt
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_enhanced/claude_arbitrage_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("claude_arbitrage_trader")

@dataclass
class ArbitrageOpportunity:
    """Data class for arbitrage opportunities"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    profit_percent: float
    profit_amount: float
    volume: float
    timestamp: datetime
    risk_score: float

@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    exchange_class: type
    api_key: str
    secret: str
    password: Optional[str] = None
    sandbox: bool = True
    rate_limit: int = 1000

class ClaudeArbitrageTrader:
    """Claude-generated advanced arbitrage trading system"""
    
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.is_running = False
        self.min_profit_percent = 1.0  # 1.0% minimum profit (breakeven after fees, wait for volatility)
        self.max_risk_score = 0.7  # Maximum risk score
        # Focus on USDT pairs for OKX disbursement
        self.symbols_to_monitor = [
            'BTC/USDT',   # Bitcoin
            'ETH/USDT',   # Ethereum
            'SOL/USDT',   # Solana
            'AVAX/USDT',  # Avalanche
            'MATIC/USDT', # Polygon
            'LINK/USDT',  # Chainlink
        ]
        self.sandbox = os.getenv('SANDBOX', '0') == '1'
        
        # Portfolio configuration - SET TO $500 EXACTLY
        self.coinbase_balance_usd = 500  # $500 on Coinbase
        self.active_capital = self.coinbase_balance_usd  # $500 TOTAL
        
        # Position sizing based on real portfolio
        self.max_position_size = self.active_capital * 0.02  # $23.20 (2%)
        self.conservative_size = self.active_capital * 0.01  # $11.60 (1%)
        self.standard_size = self.active_capital * 0.015     # $17.40 (1.5%)
        
        # Daily limits - CONSERVATIVE TO AVOID OVERTRADING
        self.max_trades_per_day = 3  # Max 3 trades/day (avoid fee bleed)
        self.max_daily_exposure = self.active_capital * 0.10  # $50 (10%)
        self.stop_loss_per_trade = self.active_capital * 0.01  # $11.60 (1%)
        
        logger.info(f"💰 Portfolio Config: Coinbase=${self.coinbase_balance_usd}, Total=${self.active_capital}")
        logger.info(f"📊 Position Sizes: Conservative=${self.conservative_size:.2f}, Standard=${self.standard_size:.2f}, Max=${self.max_position_size:.2f}")
        
        # Initialize exchange configurations - COINBASE + OKX + KRAKEN
        # Load credentials from environment
        coin_key = os.getenv('COINBASE_KEY', '')
        coin_secret = os.getenv('COINBASE_SECRET', '')
        
        okx_key = os.getenv('OKX_API_KEY', os.getenv('OKX_KEY', ''))
        okx_secret = os.getenv('OKX_API_SECRET', os.getenv('OKX_SECRET', ''))
        okx_pass = os.getenv('OKX_API_PASS', os.getenv('OKX_PASSPHRASE', ''))
        
        kraken_key = os.getenv('KRAKEN_API_KEY', '')
        kraken_secret = os.getenv('KRAKEN_API_SECRET', '')
        
        # 3-EXCHANGE ARBITRAGE: Coinbase + OKX + Kraken
        self.exchange_configs = [
            ExchangeConfig(
                name='Coinbase',
                exchange_class=ccxt.coinbase,
                api_key=coin_key,
                secret=coin_secret,
                sandbox=False,
                rate_limit=1000
            ),
            ExchangeConfig(
                name='OKX',
                exchange_class=ccxt.okx,
                api_key=okx_key,
                secret=okx_secret,
                password=okx_pass,
                sandbox=False,
                rate_limit=100
            ),
            ExchangeConfig(
                name='Kraken',
                exchange_class=ccxt.kraken,
                api_key=kraken_key if kraken_key else '',
                secret=kraken_secret if kraken_secret else '',
                sandbox=False,
                rate_limit=1000
            )
        ]
        
        logger.info("🚀 Claude Arbitrage Trader initialized")
    
    async def initialize_exchanges(self) -> bool:
        """Initialize all exchange connections"""
        logger.info("🔧 Initializing exchange connections...")
        logger.info(f"🧪 SANDBOX MODE: {'ON' if self.sandbox else 'OFF'} (via ccxt.set_sandbox_mode)")
        
        for config in self.exchange_configs:
            try:
                exchange_config = {
                    'apiKey': config.api_key,
                    'secret': config.secret,
                    'enableRateLimit': True,
                    'rateLimit': config.rate_limit,
                    'timeout': 30000,
                    'options': {
                        'defaultType': 'spot',
                        'adjustForTimeDifference': True
                    }
                }
                
                if config.password:
                    exchange_config['password'] = config.password
                
                if config.sandbox:
                    exchange_config['sandbox'] = True
                
                exchange = config.exchange_class(exchange_config)
                
                # Set sandbox mode via ccxt API
                try:
                    exchange.set_sandbox_mode(self.sandbox)
                except Exception:
                    pass
                
                exchange.load_markets()
                
                # Test connection
                ticker = exchange.fetch_ticker('BTC/USD' if config.name != 'Kraken' else 'BTC/USD')
                
                self.exchanges[config.name] = exchange
                logger.info(f"✅ {config.name} connected - {len(exchange.markets)} markets, BTC: ${ticker['last']}")
                
            except Exception as e:
                logger.error(f"❌ {config.name} connection failed: {e}")
                # Continue trying other exchanges instead of failing completely
                continue
        
        # Return True if we have at least 1 exchange connected
        if len(self.exchanges) >= 1:
            logger.info(f"✅ Successfully connected to {len(self.exchanges)} exchange(s)")
            return True
        else:
            logger.error("❌ No exchanges connected")
            return False
    
    async def fetch_prices(self, symbol: str) -> Dict[str, float]:
        """Fetch prices for a symbol across all exchanges"""
        prices = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                # Handle different symbol formats
                if exchange_name == 'Kraken' and symbol.endswith('/USDT'):
                    kraken_symbol = symbol.replace('/USDT', '/USD')
                else:
                    kraken_symbol = symbol
                
                ticker = exchange.fetch_ticker(kraken_symbol)
                prices[exchange_name] = ticker['last']
                
            except Exception as e:
                logger.warning(f"⚠️ {exchange_name} price fetch failed for {symbol}: {e}")
                continue
        
        return prices
    
    def calculate_arbitrage_opportunity(self, symbol: str, prices: Dict[str, float]) -> Optional[ArbitrageOpportunity]:
        """Calculate arbitrage opportunity from prices"""
        if len(prices) < 2:
            return None
        
        # Find best buy and sell prices
        buy_exchange = min(prices.keys(), key=lambda x: prices[x])
        sell_exchange = max(prices.keys(), key=lambda x: prices[x])
        
        buy_price = prices[buy_exchange]
        sell_price = prices[sell_exchange]
        
        # Calculate profit
        profit_percent = ((sell_price - buy_price) / buy_price) * 100
        profit_amount = sell_price - buy_price
        
        # Skip if profit is too small
        if profit_percent < self.min_profit_percent:
            return None
        
        # Calculate risk score (simplified)
        price_spread = (sell_price - buy_price) / buy_price
        risk_score = min(price_spread * 10, 1.0)  # Higher spread = higher risk
        
        if risk_score > self.max_risk_score:
            return None
        
        return ArbitrageOpportunity(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=buy_price,
            sell_price=sell_price,
            profit_percent=profit_percent,
            profit_amount=profit_amount,
            volume=1000,  # Placeholder volume
            timestamp=datetime.now(),
            risk_score=risk_score
        )
    
    async def scan_arbitrage_opportunities(self) -> List[ArbitrageOpportunity]:
        """Scan for arbitrage opportunities across all symbols"""
        opportunities = []
        
        for symbol in self.symbols_to_monitor:
            try:
                prices = await self.fetch_prices(symbol)
                opportunity = self.calculate_arbitrage_opportunity(symbol, prices)
                
                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(f"🎯 Arbitrage found: {symbol} - Buy {opportunity.buy_exchange} @ ${opportunity.buy_price:.2f}, Sell {opportunity.sell_exchange} @ ${opportunity.sell_price:.2f} - Profit: {opportunity.profit_percent:.3f}%")
                
            except Exception as e:
                logger.error(f"❌ Error scanning {symbol}: {e}")
                continue
        
        return opportunities
    
    def save_opportunities(self, opportunities: List[ArbitrageOpportunity]):
        """Save opportunities to file"""
        os.makedirs('logs/ai_enhanced', exist_ok=True)
        
        data = []
        for opp in opportunities:
            data.append({
                'symbol': opp.symbol,
                'buy_exchange': opp.buy_exchange,
                'sell_exchange': opp.sell_exchange,
                'buy_price': opp.buy_price,
                'sell_price': opp.sell_price,
                'profit_percent': opp.profit_percent,
                'profit_amount': opp.profit_amount,
                'volume': opp.volume,
                'timestamp': opp.timestamp.isoformat(),
                'risk_score': opp.risk_score
            })
        
        with open('logs/ai_enhanced/arbitrage_opportunities.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    async def run_arbitrage_scanner(self, duration_minutes: int = 60):
        """Run the arbitrage scanner for specified duration"""
        logger.info(f"🚀 Starting arbitrage scanner for {duration_minutes} minutes...")
        self.is_running = True
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while self.is_running and datetime.now() < end_time:
            try:
                opportunities = await self.scan_arbitrage_opportunities()
                
                if opportunities:
                    self.opportunities.extend(opportunities)
                    self.save_opportunities(opportunities)
                    
                    # Log summary
                    total_profit = sum(opp.profit_percent for opp in opportunities)
                    logger.info(f"📊 Found {len(opportunities)} opportunities, Total profit potential: {total_profit:.3f}%")
                
                # Wait before next scan
                await asyncio.sleep(30)  # Scan every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Scanner error: {e}")
                await asyncio.sleep(10)
        
        self.is_running = False
        logger.info("🏁 Arbitrage scanner completed")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive arbitrage report"""
        if not self.opportunities:
            return {"message": "No opportunities found"}
        
        # Calculate statistics
        total_opportunities = len(self.opportunities)
        avg_profit = sum(opp.profit_percent for opp in self.opportunities) / total_opportunities
        max_profit = max(opp.profit_percent for opp in self.opportunities)
        min_profit = min(opp.profit_percent for opp in self.opportunities)
        
        # Group by symbol
        by_symbol = {}
        for opp in self.opportunities:
            if opp.symbol not in by_symbol:
                by_symbol[opp.symbol] = []
            by_symbol[opp.symbol].append(opp)
        
        # Group by exchange pair
        by_exchange_pair = {}
        for opp in self.opportunities:
            pair = f"{opp.buy_exchange}→{opp.sell_exchange}"
            if pair not in by_exchange_pair:
                by_exchange_pair[pair] = []
            by_exchange_pair[pair].append(opp)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_opportunities': total_opportunities,
                'average_profit_percent': round(avg_profit, 4),
                'max_profit_percent': round(max_profit, 4),
                'min_profit_percent': round(min_profit, 4),
                'total_potential_profit': round(sum(opp.profit_percent for opp in self.opportunities), 4)
            },
            'by_symbol': {symbol: len(opps) for symbol, opps in by_symbol.items()},
            'by_exchange_pair': {pair: len(opps) for pair, opps in by_exchange_pair.items()},
            'top_opportunities': [
                {
                    'symbol': opp.symbol,
                    'buy_exchange': opp.buy_exchange,
                    'sell_exchange': opp.sell_exchange,
                    'profit_percent': round(opp.profit_percent, 4),
                    'timestamp': opp.timestamp.isoformat()
                }
                for opp in sorted(self.opportunities, key=lambda x: x.profit_percent, reverse=True)[:10]
            ]
        }
        
        return report

async def main():
    """Main execution function"""
    print("🚀 CLAUDE ARBITRAGE TRADING SYSTEM")
    print("=" * 60)
    
    trader = ClaudeArbitrageTrader()
    
    # Initialize exchanges
    if not await trader.initialize_exchanges():
        print("❌ Failed to initialize exchanges")
        return
    
    print(f"✅ Initialized {len(trader.exchanges)} exchanges")
    
    # Run scanner for 5 minutes (demo)
    await trader.run_arbitrage_scanner(duration_minutes=5)
    
    # Generate report
    report = trader.generate_report()
    
    print("\n📊 ARBITRAGE SCAN REPORT")
    print("=" * 60)
    
    if 'summary' in report:
        summary = report['summary']
        print(f"Total Opportunities: {summary['total_opportunities']}")
        print(f"Average Profit: {summary['average_profit_percent']}%")
        print(f"Max Profit: {summary['max_profit_percent']}%")
        print(f"Total Potential: {summary['total_potential_profit']}%")
        
        if report['top_opportunities']:
            print("\n🎯 TOP OPPORTUNITIES:")
            for i, opp in enumerate(report['top_opportunities'][:5], 1):
                print(f"{i}. {opp['symbol']}: {opp['buy_exchange']}→{opp['sell_exchange']} - {opp['profit_percent']}%")
    else:
        print("No arbitrage opportunities found during scan")
    
    # Save report
    os.makedirs('logs/ai_enhanced', exist_ok=True)
    with open('logs/ai_enhanced/claude_arbitrage_report.json', 'w') as f:
        json.dump(report, f, indent=4)
    
    print(f"\n📄 Report saved to: logs/ai_enhanced/claude_arbitrage_report.json")

if __name__ == "__main__":
    asyncio.run(main())
