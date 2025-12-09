#!/usr/bin/env python3
"""
LLF-ß Kraken Auto-Trading Engine
Advanced buy/exit automation with ΩSIGIL intelligence integration
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/kraken_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELED = "canceled"
    EXPIRED = "expired"

@dataclass
class TradingSignal:
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    ray_score: float
    frhi_score: float
    target_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime

@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    timestamp: datetime

class KrakenAutoTrader:
    """
    Advanced Kraken auto-trading engine with ΩSIGIL intelligence integration
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, sandbox: bool = True):
        self.api_key = api_key or os.getenv('KRAKEN_API_KEY', 'demo_key')
        self.api_secret = api_secret or os.getenv('KRAKEN_API_SECRET', 'demo_secret')
        self.sandbox = sandbox
        
        # Kraken API endpoints
        self.base_url = "https://api.kraken.com" if not sandbox else "https://api.kraken.com"
        self.api_version = "0"
        
        # Trading configuration
        self.max_position_size = 0.1  # 10% of portfolio per position
        self.risk_per_trade = 0.02    # 2% risk per trade
        self.min_ray_score = 0.7      # Minimum Ray Score for trades
        self.max_frhi_score = 0.6     # Maximum FRHI for entries
        
        # State tracking
        self.positions: Dict[str, Position] = {}
        self.open_orders: Dict[str, dict] = {}
        self.trading_enabled = True
        
        logger.info("🎯 Kraken Auto-Trading Engine initialized")
        logger.info(f"🔧 Sandbox mode: {sandbox}")
        logger.info(f"🛡️ Risk per trade: {self.risk_per_trade * 100}%")

    def _generate_signature(self, url_path: str, data: dict, nonce: str) -> str:
        """Generate Kraken API signature"""
        if self.sandbox:
            return "demo_signature"
            
        postdata = f"nonce={nonce}"
        for key, value in data.items():
            postdata += f"&{key}={value}"
        
        encoded = (nonce + postdata).encode()
        message = url_path.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message,
            hashlib.sha512
        )
        
        return base64.b64encode(signature.digest()).decode()

    def _make_request(self, endpoint: str, data: dict = None, private: bool = False) -> dict:
        """Make authenticated request to Kraken API"""
        if self.sandbox:
            # Return mock data for sandbox mode
            return self._get_mock_response(endpoint, data)
        
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        
        if private:
            nonce = str(int(time.time() * 1000))
            data = data or {}
            data['nonce'] = nonce
            
            headers = {
                'API-Key': self.api_key,
                'API-Sign': self._generate_signature(f"/{self.api_version}/{endpoint}", data, nonce)
            }
            
            response = requests.post(url, data=data, headers=headers)
        else:
            response = requests.get(url, params=data)
        
        return response.json()

    def _get_mock_response(self, endpoint: str, data: dict = None) -> dict:
        """Generate mock responses for sandbox mode"""
        mock_responses = {
            'public/Ticker': {
                'error': [],
                'result': {
                    'XXBTZUSD': {
                        'c': ['65432.10', '0.12345678'],
                        'v': ['1234.56789012', '5678.90123456'],
                        'p': ['65400.00', '65350.00'],
                        't': [1234, 5678],
                        'l': ['65200.00', '65100.00'],
                        'h': ['65600.00', '65700.00'],
                        'o': '65300.00'
                    }
                }
            },
            'private/Balance': {
                'error': [],
                'result': {
                    'ZUSD': '10000.0000',
                    'XXBT': '0.15000000',
                    'XETH': '5.00000000'
                }
            },
            'private/AddOrder': {
                'error': [],
                'result': {
                    'descr': {'order': 'buy 0.01000000 XBTUSD @ market'},
                    'txid': ['OQCLML-BW3P3-BUCMWZ']
                }
            },
            'private/OpenOrders': {
                'error': [],
                'result': {
                    'open': {}
                }
            }
        }
        
        return mock_responses.get(endpoint, {'error': [], 'result': {}})

    def get_account_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            response = self._make_request('private/Balance', private=True)
            
            if response.get('error'):
                logger.error(f"❌ Balance error: {response['error']}")
                return {}
            
            balances = {}
            for asset, balance in response['result'].items():
                if float(balance) > 0:
                    balances[asset] = float(balance)
            
            logger.info(f"💰 Account balances: {balances}")
            return balances
            
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return {}

    def get_ticker_price(self, symbol: str) -> float:
        """Get current ticker price"""
        try:
            response = self._make_request('public/Ticker', {'pair': symbol})
            
            if response.get('error'):
                logger.error(f"❌ Ticker error: {response['error']}")
                return 0.0
            
            # Get the first result (Kraken returns dict with pair as key)
            ticker_data = list(response['result'].values())[0]
            price = float(ticker_data['c'][0])  # Last trade price
            
            return price
            
        except Exception as e:
            logger.error(f"❌ Error getting ticker: {e}")
            return 0.0

    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        try:
            balance = self.get_account_balance()
            usd_balance = balance.get('ZUSD', 0)
            
            if usd_balance == 0:
                return 0.0
            
            # Calculate risk amount
            risk_amount = usd_balance * self.risk_per_trade
            
            # Calculate price difference for stop loss
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                return 0.0
            
            # Calculate position size
            position_size = risk_amount / price_diff
            
            # Apply maximum position size limit
            max_size = usd_balance * self.max_position_size / entry_price
            position_size = min(position_size, max_size)
            
            logger.info(f"📊 Position size calculated: {position_size:.8f} for {symbol}")
            return position_size
            
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            return 0.0

    def place_order(self, symbol: str, order_type: OrderType, quantity: float, 
                   price: float = None, order_flags: List[str] = None) -> Optional[str]:
        """Place order on Kraken"""
        try:
            order_data = {
                'pair': symbol,
                'type': order_type.value,
                'ordertype': 'market' if price is None else 'limit',
                'volume': str(quantity)
            }
            
            if price:
                order_data['price'] = str(price)
            
            if order_flags:
                order_data['oflags'] = ','.join(order_flags)
            
            response = self._make_request('private/AddOrder', order_data, private=True)
            
            if response.get('error'):
                logger.error(f"❌ Order error: {response['error']}")
                return None
            
            order_id = response['result']['txid'][0]
            logger.info(f"✅ Order placed: {order_id} - {order_type.value} {quantity} {symbol}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel open order"""
        try:
            response = self._make_request('private/CancelOrder', {'txid': order_id}, private=True)
            
            if response.get('error'):
                logger.error(f"❌ Cancel error: {response['error']}")
                return False
            
            logger.info(f"✅ Order canceled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error canceling order: {e}")
            return False

    def get_open_orders(self) -> Dict[str, dict]:
        """Get open orders"""
        try:
            response = self._make_request('private/OpenOrders', private=True)
            
            if response.get('error'):
                logger.error(f"❌ Open orders error: {response['error']}")
                return {}
            
            return response['result']['open']
            
        except Exception as e:
            logger.error(f"❌ Error getting open orders: {e}")
            return {}

    def process_omega_sigil_signal(self, signal: TradingSignal) -> bool:
        """Process ΩSIGIL trading signal"""
        try:
            logger.info(f"🧠 Processing ΩSIGIL signal for {signal.symbol}")
            logger.info(f"📊 Ray Score: {signal.ray_score}, FRHI: {signal.frhi_score}")
            logger.info(f"🎯 Action: {signal.action}, Confidence: {signal.confidence}")
            
            if not self.trading_enabled:
                logger.warning("⚠️ Trading disabled - signal ignored")
                return False
            
            # Check signal quality
            if signal.ray_score < self.min_ray_score:
                logger.warning(f"⚠️ Ray Score too low: {signal.ray_score} < {self.min_ray_score}")
                return False
            
            if signal.action == "BUY":
                return self._execute_buy_signal(signal)
            elif signal.action == "SELL":
                return self._execute_sell_signal(signal)
            else:
                logger.info(f"📊 HOLD signal for {signal.symbol} - no action taken")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error processing signal: {e}")
            return False

    def _execute_buy_signal(self, signal: TradingSignal) -> bool:
        """Execute buy signal"""
        try:
            # Check FRHI (Flip Risk Heat Index)
            if signal.frhi_score > self.max_frhi_score:
                logger.warning(f"⚠️ FRHI too high for entry: {signal.frhi_score} > {self.max_frhi_score}")
                return False
            
            # Check if we already have a position
            if signal.symbol in self.positions:
                logger.info(f"📊 Already have position in {signal.symbol}")
                return False
            
            # Get current price
            current_price = self.get_ticker_price(signal.symbol)
            if current_price == 0:
                logger.error(f"❌ Could not get price for {signal.symbol}")
                return False
            
            # Calculate position size
            position_size = self.calculate_position_size(
                signal.symbol, 
                current_price, 
                signal.stop_loss
            )
            
            if position_size == 0:
                logger.error(f"❌ Position size is 0 for {signal.symbol}")
                return False
            
            # Place buy order
            order_id = self.place_order(
                signal.symbol, 
                OrderType.BUY, 
                position_size
            )
            
            if order_id:
                # Track position
                self.positions[signal.symbol] = Position(
                    symbol=signal.symbol,
                    quantity=position_size,
                    entry_price=current_price,
                    current_price=current_price,
                    pnl=0.0,
                    pnl_percent=0.0,
                    timestamp=datetime.now()
                )
                
                logger.info(f"🎯 BUY executed: {signal.symbol} @ {current_price}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error executing buy signal: {e}")
            return False

    def _execute_sell_signal(self, signal: TradingSignal) -> bool:
        """Execute sell signal"""
        try:
            # Check if we have a position to sell
            if signal.symbol not in self.positions:
                logger.info(f"📊 No position to sell in {signal.symbol}")
                return False
            
            position = self.positions[signal.symbol]
            
            # Place sell order
            order_id = self.place_order(
                signal.symbol, 
                OrderType.SELL, 
                position.quantity
            )
            
            if order_id:
                # Calculate final P&L
                current_price = self.get_ticker_price(signal.symbol)
                final_pnl = (current_price - position.entry_price) * position.quantity
                final_pnl_percent = (current_price / position.entry_price - 1) * 100
                
                logger.info(f"🎯 SELL executed: {signal.symbol} @ {current_price}")
                logger.info(f"💰 P&L: ${final_pnl:.2f} ({final_pnl_percent:.2f}%)")
                
                # Remove position
                del self.positions[signal.symbol]
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error executing sell signal: {e}")
            return False

    def update_positions(self):
        """Update position P&L"""
        try:
            for symbol, position in self.positions.items():
                current_price = self.get_ticker_price(symbol)
                if current_price > 0:
                    position.current_price = current_price
                    position.pnl = (current_price - position.entry_price) * position.quantity
                    position.pnl_percent = (current_price / position.entry_price - 1) * 100
                    
        except Exception as e:
            logger.error(f"❌ Error updating positions: {e}")

    def get_portfolio_summary(self) -> dict:
        """Get portfolio summary"""
        try:
            self.update_positions()
            
            total_pnl = sum(pos.pnl for pos in self.positions.values())
            total_positions = len(self.positions)
            
            winning_positions = len([pos for pos in self.positions.values() if pos.pnl > 0])
            win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0
            
            summary = {
                'total_positions': total_positions,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'positions': [
                    {
                        'symbol': pos.symbol,
                        'quantity': pos.quantity,
                        'entry_price': pos.entry_price,
                        'current_price': pos.current_price,
                        'pnl': pos.pnl,
                        'pnl_percent': pos.pnl_percent
                    }
                    for pos in self.positions.values()
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting portfolio summary: {e}")
            return {}

    def emergency_exit_all(self) -> bool:
        """Emergency exit all positions"""
        try:
            logger.warning("🚨 EMERGENCY EXIT ALL POSITIONS")
            
            success_count = 0
            for symbol in list(self.positions.keys()):
                signal = TradingSignal(
                    symbol=symbol,
                    action="SELL",
                    confidence=1.0,
                    ray_score=1.0,
                    frhi_score=0.0,
                    target_price=0.0,
                    stop_loss=0.0,
                    take_profit=0.0,
                    timestamp=datetime.now()
                )
                
                if self._execute_sell_signal(signal):
                    success_count += 1
            
            logger.info(f"🚨 Emergency exit completed: {success_count} positions closed")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error in emergency exit: {e}")
            return False

def main():
    """Main trading engine demonstration"""
    print("🎯 KRAKEN AUTO-TRADING ENGINE - PHASE 3")
    print("=" * 60)
    
    # Initialize trader
    trader = KrakenAutoTrader(sandbox=True)
    
    # Get account balance
    balance = trader.get_account_balance()
    print(f"💰 Account Balance: {balance}")
    
    # Demo ΩSIGIL signal
    demo_signal = TradingSignal(
        symbol="XBTUSD",
        action="BUY",
        confidence=0.85,
        ray_score=0.907,
        frhi_score=0.35,
        target_price=66000.0,
        stop_loss=64000.0,
        take_profit=68000.0,
        timestamp=datetime.now()
    )
    
    print(f"\n🧠 Processing demo ΩSIGIL signal...")
    success = trader.process_omega_sigil_signal(demo_signal)
    print(f"✅ Signal processed: {success}")
    
    # Get portfolio summary
    summary = trader.get_portfolio_summary()
    print(f"\n📊 Portfolio Summary:")
    print(f"Total Positions: {summary.get('total_positions', 0)}")
    print(f"Total P&L: ${summary.get('total_pnl', 0):.2f}")
    print(f"Win Rate: {summary.get('win_rate', 0):.1f}%")
    
    print("\n🎯 KRAKEN AUTO-TRADING ENGINE STATUS: OPERATIONAL")
    print("Ready for Notion Bridge Integration...")

if __name__ == "__main__":
    main()

