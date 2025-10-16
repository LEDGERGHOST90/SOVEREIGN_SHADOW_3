#!/usr/bin/env python3
"""
📡 STAGING DATA FEEDS - SOVEREIGNSHADOW.AI
Real-time market data for paper trading validation
"""

import websocket
import json
import threading
import time
import requests
from datetime import datetime
import logging
from typing import Dict, List, Callable

logger = logging.getLogger("staging_data_feeds")

class LiveDataFeed:
    """Real-time market data for paper trading validation"""
    
    def __init__(self, config):
        self.config = config
        self.data_cache = {}
        self.subscribers = []
        self.ws_connections = {}
        self.running = False
        
        # Exchange configurations
        self.exchanges = {
            'binance': {
                'base_url': 'https://testnet.binance.vision',
                'ws_url': 'wss://testnet.binance.vision/ws/',
                'pairs': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
            },
            'coinbase': {
                'base_url': 'https://api-public.sandbox.pro.coinbase.com',
                'ws_url': 'wss://ws-feed-public.sandbox.pro.coinbase.com',
                'pairs': ['BTC-USD', 'ETH-USD', 'LTC-USD', 'ADA-USD', 'SOL-USD']
            }
        }
    
    def start_feeds(self):
        """Start all market data feeds"""
        logger.info("🔗 Starting live market data feeds...")
        self.running = True
        
        # Start Binance feed
        threading.Thread(target=self._start_binance_feed, daemon=True).start()
        
        # Start Coinbase feed
        threading.Thread(target=self._start_coinbase_feed, daemon=True).start()
        
        logger.info("✅ Live data feeds started")
    
    def _start_binance_feed(self):
        """Start Binance WebSocket feed"""
        try:
            # Create WebSocket URL for multiple symbols
            symbols = [f"{symbol.lower()}@ticker" for symbol in self.exchanges['binance']['pairs']]
            ws_url = f"{self.exchanges['binance']['ws_url']}{'/'.join(symbols)}"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    self._process_binance_data(data)
                except Exception as e:
                    logger.error(f"Binance message processing error: {e}")
            
            def on_error(ws, error):
                logger.error(f"Binance WebSocket error: {error}")
                time.sleep(5)  # Reconnect after 5 seconds
                ws.run_forever()
            
            def on_close(ws, close_status_code, close_msg):
                logger.warning("Binance WebSocket connection closed")
                if self.running:
                    time.sleep(5)
                    ws.run_forever()
            
            ws = websocket.WebSocketApp(ws_url,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            self.ws_connections['binance'] = ws
            ws.run_forever()
            
        except Exception as e:
            logger.error(f"Binance feed error: {e}")
    
    def _start_coinbase_feed(self):
        """Start Coinbase WebSocket feed"""
        try:
            # Subscribe to Coinbase WebSocket
            subscribe_msg = {
                "type": "subscribe",
                "product_ids": self.exchanges['coinbase']['pairs'],
                "channels": ["ticker"]
            }
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    if data.get('type') == 'ticker':
                        self._process_coinbase_data(data)
                except Exception as e:
                    logger.error(f"Coinbase message processing error: {e}")
            
            def on_error(ws, error):
                logger.error(f"Coinbase WebSocket error: {error}")
                time.sleep(5)
                ws.run_forever()
            
            def on_open(ws):
                ws.send(json.dumps(subscribe_msg))
                logger.info("✅ Coinbase WebSocket subscribed")
            
            def on_close(ws, close_status_code, close_msg):
                logger.warning("Coinbase WebSocket connection closed")
                if self.running:
                    time.sleep(5)
                    ws.run_forever()
            
            ws = websocket.WebSocketApp(self.exchanges['coinbase']['ws_url'],
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close,
                                      on_open=on_open)
            
            self.ws_connections['coinbase'] = ws
            ws.run_forever()
            
        except Exception as e:
            logger.error(f"Coinbase feed error: {e}")
    
    def _process_binance_data(self, data):
        """Process Binance market data"""
        if 's' in data and 'c' in data:  # Symbol and current price
            price_data = {
                'exchange': 'binance',
                'symbol': data['s'],
                'price': float(data['c']),
                'volume': float(data.get('v', 0)),
                'timestamp': datetime.now().isoformat(),
                'bid': float(data.get('b', 0)),
                'ask': float(data.get('a', 0)),
                'spread': float(data.get('a', 0)) - float(data.get('b', 0))
            }
            
            # Cache the data
            cache_key = f"binance_{data['s']}"
            self.data_cache[cache_key] = price_data
            
            # Notify subscribers
            self._notify_subscribers(price_data)
    
    def _process_coinbase_data(self, data):
        """Process Coinbase market data"""
        if 'product_id' in data and 'price' in data:
            price_data = {
                'exchange': 'coinbase',
                'symbol': data['product_id'],
                'price': float(data['price']),
                'volume': float(data.get('volume_24h', 0)),
                'timestamp': datetime.now().isoformat(),
                'bid': float(data.get('best_bid', 0)),
                'ask': float(data.get('best_ask', 0)),
                'spread': float(data.get('best_ask', 0)) - float(data.get('best_bid', 0))
            }
            
            # Cache the data
            cache_key = f"coinbase_{data['product_id']}"
            self.data_cache[cache_key] = price_data
            
            # Notify subscribers
            self._notify_subscribers(price_data)
    
    def _notify_subscribers(self, price_data):
        """Notify all subscribers of price updates"""
        for callback in self.subscribers:
            try:
                callback(price_data)
            except Exception as e:
                logger.error(f"Subscriber notification error: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to live data updates"""
        self.subscribers.append(callback)
        logger.info(f"New subscriber added. Total subscribers: {len(self.subscribers)}")
    
    def get_current_price(self, symbol: str, exchange: str = None) -> float:
        """Get current market price for a symbol"""
        if exchange:
            cache_key = f"{exchange}_{symbol}"
            data = self.data_cache.get(cache_key)
            return data.get('price', 0.0) if data else 0.0
        else:
            # Try to get price from any exchange
            for exchange_name in ['binance', 'coinbase']:
                cache_key = f"{exchange_name}_{symbol}"
                data = self.data_cache.get(cache_key)
                if data and data.get('price'):
                    return data['price']
            return 0.0
    
    def get_all_prices(self) -> Dict[str, Dict]:
        """Get all current prices"""
        return self.data_cache.copy()
    
    def detect_arbitrage_opportunities(self) -> List[Dict]:
        """Detect arbitrage opportunities across exchanges"""
        opportunities = []
        
        # Common symbols to check
        symbols_to_check = {
            'BTCUSDT': ['BTC-USD'],
            'ETHUSDT': ['ETH-USD'],
            'ADAUSDT': ['ADA-USD'],
            'SOLUSDT': ['SOL-USD']
        }
        
        for binance_symbol, coinbase_symbols in symbols_to_check.items():
            binance_data = self.data_cache.get(f'binance_{binance_symbol}')
            
            for coinbase_symbol in coinbase_symbols:
                coinbase_data = self.data_cache.get(f'coinbase_{coinbase_symbol}')
                
                if binance_data and coinbase_data:
                    binance_price = binance_data['price']
                    coinbase_price = coinbase_data['price']
                    
                    # Calculate spread
                    spread = abs(binance_price - coinbase_price) / min(binance_price, coinbase_price)
                    
                    if spread > 0.002:  # 0.2% minimum spread
                        opportunity = {
                            'symbol': binance_symbol.replace('USDT', ''),
                            'binance_price': binance_price,
                            'coinbase_price': coinbase_price,
                            'spread': spread,
                            'buy_exchange': 'binance' if binance_price < coinbase_price else 'coinbase',
                            'sell_exchange': 'coinbase' if binance_price < coinbase_price else 'binance',
                            'buy_price': min(binance_price, coinbase_price),
                            'sell_price': max(binance_price, coinbase_price),
                            'timestamp': datetime.now().isoformat()
                        }
                        opportunities.append(opportunity)
        
        return opportunities
    
    def stop_feeds(self):
        """Stop all market data feeds"""
        logger.info("🛑 Stopping live data feeds...")
        self.running = False
        
        for exchange, ws in self.ws_connections.items():
            try:
                ws.close()
                logger.info(f"✅ {exchange} feed stopped")
            except Exception as e:
                logger.error(f"Error stopping {exchange} feed: {e}")
    
    def get_feed_status(self) -> Dict[str, bool]:
        """Get status of all data feeds"""
        status = {}
        for exchange, ws in self.ws_connections.items():
            status[exchange] = ws.sock is not None if hasattr(ws, 'sock') else False
        return status

def main():
    """Test the data feed system"""
    import yaml
    
    # Load config
    with open('environments/staging/config_staging.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create data feed
    feed = LiveDataFeed(config)
    
    # Add subscriber for testing
    def test_subscriber(price_data):
        print(f"📊 {price_data['exchange']} {price_data['symbol']}: ${price_data['price']:.2f}")
    
    feed.subscribe(test_subscriber)
    
    # Start feeds
    feed.start_feeds()
    
    try:
        # Run for 60 seconds to test
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping feeds...")
        feed.stop_feeds()

if __name__ == "__main__":
    main()
