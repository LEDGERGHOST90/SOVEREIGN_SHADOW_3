"""
📡 BINANCE INTEGRATION WITH UNIFIED AGI
Enhanced Binance streaming with direct integration to unified AGI system
"""

import asyncio
import json
import websockets
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceAGIStreamer:
    """
    📡 Enhanced Binance streamer with direct AGI integration
    Streams live market data and feeds directly to unified AGI system
    """
    
    def __init__(self, unified_agi_system=None):
        self.unified_agi = unified_agi_system
        self.base_stream_url = "wss://stream.binance.com:9443/ws"
        
        # Ray's asset configuration
        self.sniper_symbols = ["suiusdt", "arbusdt", "renderusdt", "turbousdt", "hypeusdt", "bonkusdt", "virtualusdt", "wifusdt"]
        self.vault_symbols = ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "usdtusdt"]
        self.foresight_symbols = ["xrpusdt", "qntusdt", "hbarusdt", "fetusdt", "agixusdt", "ewtusdt", "powrusdt", "iotausdt"]
        
        # Combine all symbols for streaming
        self.all_symbols = list(set(self.sniper_symbols + self.vault_symbols + self.foresight_symbols))
        
        # Stream management
        self.is_streaming = False
        self.connection = None
        self.signal_count = 0
        self.last_prices = {}
        
        print("📡 BINANCE AGI STREAMER INITIALIZED")
        print(f"   Tracking {len(self.all_symbols)} symbols")
        print(f"   Sniper Assets: {len(self.sniper_symbols)}")
        print(f"   Vault Assets: {len(self.vault_symbols)}")
        print(f"   Foresight Assets: {len(self.foresight_symbols)}")
    
    def set_unified_agi(self, unified_agi_system):
        """🔗 Connect to unified AGI system"""
        self.unified_agi = unified_agi_system
        print("🔗 Connected to Unified AGI System")
    
    async def start_streaming(self):
        """🚀 Start live Binance streaming"""
        
        if not self.unified_agi:
            print("⚠️ No unified AGI system connected - streaming in monitor mode")
        
        # Create stream query for all symbols
        stream_query = "/".join([f"{symbol}@ticker" for symbol in self.all_symbols])
        full_stream_url = f"{self.base_stream_url}/{stream_query}"
        
        print(f"📡 STARTING BINANCE LIVE STREAM...")
        print(f"   URL: {full_stream_url}")
        print(f"   Symbols: {', '.join([s.upper() for s in self.all_symbols])}")
        
        self.is_streaming = True
        
        try:
            async with websockets.connect(full_stream_url) as websocket:
                self.connection = websocket
                print("✅ BINANCE STREAM CONNECTED")
                
                while self.is_streaming:
                    try:
                        # Receive message
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        # Process ticker data
                        await self._process_ticker_data(data)
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("⚠️ Binance connection closed, attempting reconnect...")
                        break
                    except Exception as e:
                        logger.error(f"Stream processing error: {e}")
                        await asyncio.sleep(1)
                        
        except Exception as e:
            logger.error(f"Binance streaming error: {e}")
        finally:
            self.is_streaming = False
            print("📡 Binance streaming stopped")
    
    async def _process_ticker_data(self, data: Dict):
        """📊 Process incoming ticker data"""
        
        try:
            symbol = data.get("s", "").lower()
            if symbol not in self.all_symbols:
                return
            
            # Extract key data
            current_price = float(data.get("c", 0))
            volume_24h = float(data.get("v", 0))
            price_change_24h = float(data.get("P", 0)) / 100  # Convert percentage
            high_24h = float(data.get("h", 0))
            low_24h = float(data.get("l", 0))
            
            # Calculate additional metrics
            price_volatility = (high_24h - low_24h) / current_price if current_price > 0 else 0
            
            # Determine signal type based on price change
            if price_change_24h > 0.05:  # +5%
                signal_type = "bullish"
            elif price_change_24h < -0.05:  # -5%
                signal_type = "bearish"
            else:
                signal_type = "neutral"
            
            # Create unified signal
            unified_signal = {
                'symbol': symbol.replace('usdt', '').upper(),
                'price': current_price,
                'volume': volume_24h,
                'price_change_24h': price_change_24h,
                'volatility': price_volatility,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'source': 'binance_live',
                'signal_type': signal_type,
                'timestamp': datetime.now(),
                'metadata': {
                    'raw_ticker': data,
                    'asset_classification': self._classify_asset(symbol),
                    'stream_count': self.signal_count
                }
            }
            
            # Track price changes
            if symbol in self.last_prices:
                price_delta = current_price - self.last_prices[symbol]
                unified_signal['price_delta'] = price_delta
                unified_signal['price_delta_pct'] = (price_delta / self.last_prices[symbol]) * 100 if self.last_prices[symbol] > 0 else 0
            
            self.last_prices[symbol] = current_price
            
            # Send to unified AGI if connected
            if self.unified_agi:
                await self.unified_agi.receive_binance_signal(unified_signal)
            
            # Log significant signals
            if abs(price_change_24h) > 0.03 or volume_24h > 100000:  # 3% change or high volume
                print(f"📊 SIGNAL: {unified_signal['symbol']} @ ${current_price:.4f} ({price_change_24h:+.1%}) Vol: {volume_24h:,.0f}")
            
            self.signal_count += 1
            
        except Exception as e:
            logger.error(f"Ticker processing error: {e}")
    
    def _classify_asset(self, symbol: str) -> str:
        """🏷️ Classify asset type"""
        
        if symbol in self.sniper_symbols:
            return "SNIPER_ASSET"
        elif symbol in self.vault_symbols:
            return "VAULT_ASSET"
        elif symbol in self.foresight_symbols:
            return "FORESIGHT_ASSET"
        else:
            return "UNKNOWN"
    
    async def stop_streaming(self):
        """🛑 Stop Binance streaming"""
        
        self.is_streaming = False
        if self.connection:
            await self.connection.close()
        
        print("🛑 Binance streaming stopped")
    
    def get_streaming_status(self) -> Dict:
        """📊 Get streaming status"""
        
        return {
            'is_streaming': self.is_streaming,
            'signal_count': self.signal_count,
            'symbols_tracked': len(self.all_symbols),
            'last_prices': dict(list(self.last_prices.items())[:5]),  # Show first 5
            'connected_to_agi': self.unified_agi is not None
        }

class BinanceRESTClient:
    """
    📈 Binance REST API client for additional data
    Provides historical data and detailed market information
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    async def get_24h_ticker(self, symbol: str) -> Optional[Dict]:
        """📊 Get 24h ticker statistics"""
        
        try:
            url = f"{self.base_url}/ticker/24hr"
            params = {'symbol': symbol.upper() + 'USDT'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"24h ticker error for {symbol}: {e}")
            return None
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[List]:
        """📈 Get historical kline data"""
        
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol.upper() + 'USDT',
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Klines error for {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Optional[Dict]:
        """📋 Get order book depth"""
        
        try:
            url = f"{self.base_url}/depth"
            params = {
                'symbol': symbol.upper() + 'USDT',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Order book error for {symbol}: {e}")
            return None

# Global instances
binance_streamer = None
binance_rest = None

def initialize_binance_integration(unified_agi_system=None):
    """📡 Initialize Binance integration"""
    global binance_streamer, binance_rest
    
    binance_streamer = BinanceAGIStreamer(unified_agi_system)
    binance_rest = BinanceRESTClient()
    
    print("📡 BINANCE INTEGRATION INITIALIZED")
    return binance_streamer, binance_rest

async def start_live_streaming(unified_agi_system=None):
    """🚀 Start live Binance streaming"""
    global binance_streamer
    
    if not binance_streamer:
        binance_streamer, _ = initialize_binance_integration(unified_agi_system)
    
    if unified_agi_system:
        binance_streamer.set_unified_agi(unified_agi_system)
    
    await binance_streamer.start_streaming()

if __name__ == "__main__":
    print("📡 BINANCE INTEGRATION - STANDALONE TEST")
    
    async def test_binance_integration():
        # Initialize
        streamer, rest_client = initialize_binance_integration()
        
        # Test REST API
        print("📈 Testing REST API...")
        btc_ticker = await rest_client.get_24h_ticker('BTC')
        if btc_ticker:
            print(f"   BTC 24h: ${float(btc_ticker['lastPrice']):,.2f} ({float(btc_ticker['priceChangePercent']):+.2f}%)")
        
        # Test streaming (run for 30 seconds)
        print("📡 Testing live streaming...")
        streaming_task = asyncio.create_task(streamer.start_streaming())
        
        # Let it run for 30 seconds
        await asyncio.sleep(30)
        
        # Stop streaming
        await streamer.stop_streaming()
        
        # Show status
        status = streamer.get_streaming_status()
        print(f"\n📊 STREAMING STATUS:")
        print(f"   Signals Processed: {status['signal_count']}")
        print(f"   Symbols Tracked: {status['symbols_tracked']}")
        
        print("\n✅ BINANCE INTEGRATION TEST COMPLETE")
    
    asyncio.run(test_binance_integration())

