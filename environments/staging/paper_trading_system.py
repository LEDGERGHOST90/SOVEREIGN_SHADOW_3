#!/usr/bin/env python3
"""
🧪 PAPER TRADING SYSTEM - SOVEREIGNSHADOW.AI
Complete paper trading system with real market data and validation
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add staging modules to path
sys.path.append(str(Path(__file__).parent))

from staging_data_feeds import LiveDataFeed
from paper_execution import PaperExecutionEngine
from validation_metrics import ValidationFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('environments/staging/logs/paper_trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("paper_trading_system")

class PaperTradingSystem:
    """Complete paper trading system with validation"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        
        # Initialize components
        self.data_feed = LiveDataFeed(self.config)
        self.execution_engine = PaperExecutionEngine(self.data_feed, self.config)
        self.validator = ValidationFramework(config_file)
        
        # Trading parameters
        self.scan_interval = self.config['trading_config']['scan_interval']
        self.min_spread_threshold = self.config['trading_config']['min_spread_threshold']
        
        logger.info("🧪 Paper Trading System initialized")
    
    def _load_config(self) -> Dict:
        """Load staging configuration"""
        try:
            import yaml
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)
    
    def start_system(self):
        """Start the paper trading system"""
        logger.info("🚀 Starting Paper Trading System")
        logger.info("=" * 60)
        logger.info(f"Mode: PAPER TRADING (Real data, simulated execution)")
        logger.info(f"Starting Balance: ${self.config['trading_config']['starting_balance']:,.2f}")
        logger.info(f"Max Position Size: {self.config['trading_config']['max_position_size']*100:.1f}%")
        logger.info(f"Max Daily Trades: {self.config['trading_config']['max_daily_trades']}")
        logger.info(f"Scan Interval: {self.scan_interval} seconds")
        logger.info("=" * 60)
        
        self.running = True
        
        try:
            # Start data feeds
            self.data_feed.start_feeds()
            
            # Subscribe to price updates
            self.data_feed.subscribe(self._on_price_update)
            
            # Main trading loop
            self._run_trading_loop()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Paper trading stopped by user")
        except Exception as e:
            logger.error(f"❌ System error: {e}")
        finally:
            self.stop_system()
    
    def _run_trading_loop(self):
        """Main trading loop"""
        logger.info("🔄 Starting trading loop...")
        
        while self.running:
            try:
                # Detect arbitrage opportunities
                opportunities = self.data_feed.detect_arbitrage_opportunities()
                
                # Execute trades for good opportunities
                for opportunity in opportunities[:2]:  # Max 2 trades per cycle
                    if self._should_execute_trade(opportunity):
                        self._execute_arbitrage_trade(opportunity)
                
                # Display status every 10 cycles
                if int(time.time()) % (self.scan_interval * 10) == 0:
                    self._display_status()
                
                # Wait before next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                time.sleep(30)  # Wait before retrying
    
    def _on_price_update(self, price_data: Dict):
        """Handle real-time price updates"""
        # Log significant price movements
        if price_data.get('symbol') in ['BTCUSDT', 'ETHUSDT']:
            logger.debug(f"📊 {price_data['exchange']} {price_data['symbol']}: ${price_data['price']:.2f}")
    
    def _should_execute_trade(self, opportunity: Dict) -> bool:
        """Determine if we should execute a trade"""
        # Check spread threshold
        if opportunity['spread'] < self.min_spread_threshold:
            return False
        
        # Check daily trade limit
        status = self.execution_engine.get_status()
        if status['remaining_daily_trades'] <= 0:
            logger.warning("⚠️ Daily trade limit reached")
            return False
        
        # Check position size limits
        current_price = opportunity['buy_price']
        max_position_value = self.config['trading_config']['starting_balance'] * self.config['trading_config']['max_position_size']
        
        # Calculate position size (1% of starting balance)
        position_size = (max_position_value * 0.5) / current_price  # Use 0.5% for safety
        
        if position_size < 0.001:  # Minimum trade size
            return False
        
        return True
    
    def _execute_arbitrage_trade(self, opportunity: Dict):
        """Execute arbitrage trade"""
        try:
            symbol = opportunity['symbol']
            buy_exchange = opportunity['buy_exchange']
            sell_exchange = opportunity['sell_exchange']
            
            # Calculate position size
            max_position_value = self.config['trading_config']['starting_balance'] * self.config['trading_config']['max_position_size']
            position_size = (max_position_value * 0.5) / opportunity['buy_price']
            
            # Map symbol names for different exchanges
            symbol_mapping = {
                'binance': {
                    'BTC': 'BTCUSDT',
                    'ETH': 'ETHUSDT',
                    'ADA': 'ADAUSDT',
                    'SOL': 'SOLUSDT'
                },
                'coinbase': {
                    'BTC': 'BTC-USD',
                    'ETH': 'ETH-USD',
                    'ADA': 'ADA-USD',
                    'SOL': 'SOL-USD'
                }
            }
            
            buy_symbol = symbol_mapping.get(buy_exchange, {}).get(symbol, f"{symbol}USDT")
            sell_symbol = symbol_mapping.get(sell_exchange, {}).get(symbol, f"{symbol}USDT")
            
            # Place buy order
            buy_order_id = self.execution_engine.place_order(
                buy_symbol, 'BUY', position_size, 'MARKET', buy_exchange
            )
            
            if buy_order_id:
                # Place sell order (simulate immediate arbitrage)
                time.sleep(0.1)  # Small delay between orders
                
                sell_order_id = self.execution_engine.place_order(
                    sell_symbol, 'SELL', position_size, 'MARKET', sell_exchange
                )
                
                if sell_order_id:
                    logger.info(f"✅ Arbitrage trade executed: {symbol} - Spread: {opportunity['spread']:.3%}")
                else:
                    logger.warning(f"⚠️ Sell order failed for {symbol}")
            else:
                logger.warning(f"⚠️ Buy order failed for {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Arbitrage execution error: {e}")
    
    def _display_status(self):
        """Display system status"""
        try:
            # Get execution engine status
            exec_status = self.execution_engine.get_status()
            metrics = self.execution_engine.get_performance_metrics()
            
            # Get data feed status
            feed_status = self.data_feed.get_feed_status()
            
            logger.info("📊 PAPER TRADING STATUS")
            logger.info("-" * 40)
            logger.info(f"Portfolio Value: ${exec_status['portfolio_value']:,.2f}")
            logger.info(f"Balance: ${exec_status['balance']:,.2f}")
            logger.info(f"Daily Trades: {exec_status['daily_trades']}/{exec_status['daily_trade_limit']}")
            logger.info(f"Open Orders: {exec_status['open_orders']}")
            logger.info(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
            logger.info(f"Data Feeds: {sum(feed_status.values())}/{len(feed_status)} active")
            logger.info("-" * 40)
            
        except Exception as e:
            logger.error(f"Status display error: {e}")
    
    def generate_validation_report(self):
        """Generate validation report"""
        try:
            logger.info("📋 Generating validation report...")
            
            # Load trades and calculate metrics
            if self.validator.load_paper_trades():
                report = self.validator.generate_validation_report()
                
                # Save report
                self.validator.save_validation_report(report)
                
                # Display key metrics
                metrics = self.validator.calculate_performance_metrics()
                if "error" not in metrics:
                    logger.info("📊 VALIDATION METRICS")
                    logger.info(f"Status: {metrics['validation_status']}")
                    logger.info(f"Win Rate: {metrics['win_rate']:.1%}")
                    logger.info(f"Monthly Return: {metrics['monthly_return_pct']:.2f}%")
                    logger.info(f"Total Trades: {metrics['total_trades']}")
                    
                    if metrics['validation_status'] == "VALIDATION_PASSED":
                        logger.info("🚀 SYSTEM READY FOR LIVE TRADING!")
                    else:
                        logger.info("⏳ Continue validation period")
            else:
                logger.warning("⚠️ No trades found for validation report")
                
        except Exception as e:
            logger.error(f"Validation report error: {e}")
    
    def stop_system(self):
        """Stop the paper trading system"""
        logger.info("🛑 Stopping Paper Trading System...")
        self.running = False
        
        # Stop data feeds
        self.data_feed.stop_feeds()
        
        # Generate final validation report
        self.generate_validation_report()
        
        logger.info("✅ Paper Trading System stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Paper Trading System')
    parser.add_argument('--config', required=True, help='Configuration file path')
    parser.add_argument('--report-only', action='store_true', help='Generate validation report only')
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create logs directory
    Path("environments/staging/logs").mkdir(parents=True, exist_ok=True)
    
    # Create system
    system = PaperTradingSystem(args.config)
    
    if args.report_only:
        # Generate report only
        system.generate_validation_report()
    else:
        # Run full system
        system.start_system()

if __name__ == "__main__":
    main()
