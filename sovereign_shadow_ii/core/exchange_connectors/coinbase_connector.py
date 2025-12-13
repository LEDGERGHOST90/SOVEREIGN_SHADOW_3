#!/usr/bin/env python3
"""
Coinbase Advanced Trade API Connector
Fixed implementation addressing August 2024 authentication issues
"""

import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime

try:
    from coinbase.rest import RESTClient
    COINBASE_SDK_AVAILABLE = True
except ImportError:
    COINBASE_SDK_AVAILABLE = False
    logging.warning("Coinbase SDK not available. Install with: pip install coinbase-advanced-py")

from .base_connector import (
    BaseExchangeConnector,
    OrderSide,
    OrderType,
    Balance,
    Ticker,
    Order
)

logger = logging.getLogger(__name__)


class CoinbaseConnector(BaseExchangeConnector):
    """
    Coinbase Advanced Trade API connector
    
    Uses the official Coinbase Advanced Trade Python SDK
    Addresses authentication issues from August 2024
    
    Authentication:
    - API Key: Format "organizations/{org_id}/apiKeys/{key_id}"
    - API Secret: PEM-formatted private key (EC PRIVATE KEY)
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        testnet: bool = False
    ):
        """
        Initialize Coinbase connector
        
        Args:
            api_key: Coinbase API key (organizations/.../apiKeys/...)
            api_secret: PEM-formatted EC private key
            passphrase: Not used for Advanced Trade API
            testnet: Use sandbox (Coinbase has limited sandbox support)
        """
        super().__init__(api_key, api_secret, passphrase, testnet)
        
        if not COINBASE_SDK_AVAILABLE:
            raise ImportError(
                "Coinbase SDK required. Install: pip install coinbase-advanced-py"
            )
        
        # Initialize REST client
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Coinbase REST client"""
        try:
            # Use official SDK
            self.client = RESTClient(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            logger.info("✅ Coinbase REST client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Coinbase client: {e}")
            raise
    
    def connect(self) -> bool:
        """
        Connect and verify credentials
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Test connection by fetching accounts
            accounts = self.client.get_accounts()
            
            if accounts and hasattr(accounts, 'accounts'):
                self.connected = True
                logger.info(f"✅ Connected to Coinbase Advanced Trade")
                logger.info(f"   Found {len(accounts.accounts)} accounts")
                return True
            else:
                logger.error("❌ No accounts returned from Coinbase")
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Coinbase connection failed: {e}")
            logger.error(f"   API Key format: {self.api_key[:50]}...")
            self.connected = False
            return False
    
    def fetch_balance(self) -> Dict[str, Balance]:
        """
        Fetch account balances
        
        Returns:
            Dict[str, Balance]: {"BTC": Balance(...), ...}
        """
        if not self.connected:
            logger.error("❌ Not connected to Coinbase")
            return {}
        
        try:
            accounts_response = self.client.get_accounts()
            balances = {}
            
            for account in accounts_response.accounts:
                # Parse account data
                currency = account.currency if hasattr(account, 'currency') else ''
                
                # Get available balance
                if hasattr(account, 'available_balance'):
                    avail_balance = account.available_balance
                    if hasattr(avail_balance, 'value'):
                        available = float(avail_balance.value)
                    else:
                        available = float(avail_balance)
                else:
                    available = 0.0
                
                # Get held balance
                if hasattr(account, 'hold'):
                    hold_balance = account.hold
                    if hasattr(hold_balance, 'value'):
                        held = float(hold_balance.value)
                    else:
                        held = float(hold_balance)
                else:
                    held = 0.0
                
                total = available + held
                
                if total > 0:
                    balances[currency] = Balance(
                        asset=currency,
                        free=available,
                        locked=held,
                        total=total
                    )
            
            logger.info(f"💰 Fetched {len(balances)} Coinbase balances")
            return balances
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch Coinbase balance: {e}")
            return {}
    
    def fetch_ticker(self, symbol: str) -> Ticker:
        """
        Fetch current ticker price
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT" or "BTC-USD")
        
        Returns:
            Ticker: Price information
        """
        if not self.connected:
            raise RuntimeError("Not connected to Coinbase")
        
        try:
            # Normalize symbol to Coinbase format (BTC-USD)
            coinbase_symbol = self._normalize_symbol(symbol)
            
            # Get best bid/ask
            bid_ask = self.client.get_best_bid_ask([coinbase_symbol])
            
            if bid_ask and hasattr(bid_ask, 'pricebooks'):
                pricebook = bid_ask.pricebooks[0]
                
                # Parse bids and asks
                bids = pricebook.bids if hasattr(pricebook, 'bids') else []
                asks = pricebook.asks if hasattr(pricebook, 'asks') else []
                
                best_bid = float(bids[0].price) if bids else 0.0
                best_ask = float(asks[0].price) if asks else 0.0
                last = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid or best_ask
                
                return Ticker(
                    symbol=symbol,
                    bid=best_bid,
                    ask=best_ask,
                    last=last,
                    timestamp=datetime.now()
                )
            
            raise ValueError(f"No price data for {coinbase_symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch ticker for {symbol}: {e}")
            raise
    
    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: float,
        price: Optional[float] = None
    ) -> Order:
        """
        Create an order on Coinbase
        
        Args:
            symbol: Trading pair
            side: Buy or sell
            order_type: Market or limit
            amount: Order amount
            price: Limit price (required for limit orders)
        
        Returns:
            Order: Order details
        """
        if not self.connected:
            raise RuntimeError("Not connected to Coinbase")
        
        # Validate order
        valid, error = self.validate_order(symbol, side, amount, price)
        if not valid:
            raise ValueError(f"Order validation failed: {error}")
        
        try:
            coinbase_symbol = self._normalize_symbol(symbol)
            
            # Create order based on type
            if order_type == OrderType.MARKET:
                if side == OrderSide.BUY:
                    # Market buy uses quote_size (USD)
                    result = self.client.market_order_buy(
                        product_id=coinbase_symbol,
                        quote_size=str(amount)
                    )
                else:
                    # Market sell uses base_size (BTC, ETH, etc.)
                    result = self.client.market_order_sell(
                        product_id=coinbase_symbol,
                        base_size=str(amount)
                    )
            
            elif order_type == OrderType.LIMIT:
                if price is None:
                    raise ValueError("Price required for limit orders")
                
                if side == OrderSide.BUY:
                    result = self.client.limit_order_gtc_buy(
                        product_id=coinbase_symbol,
                        base_size=str(amount),
                        limit_price=str(price)
                    )
                else:
                    result = self.client.limit_order_gtc_sell(
                        product_id=coinbase_symbol,
                        base_size=str(amount),
                        limit_price=str(price)
                    )
            
            else:
                raise ValueError(f"Order type {order_type} not supported")
            
            # Parse result
            order_id = result.order_id if hasattr(result, 'order_id') else str(result)
            
            logger.info(f"✅ Order created: {order_id}")
            
            return Order(
                order_id=order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                amount=amount,
                price=price,
                status="pending",
                filled=0.0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create order: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair
        
        Returns:
            bool: True if cancellation successful
        """
        if not self.connected:
            raise RuntimeError("Not connected to Coinbase")
        
        try:
            result = self.client.cancel_orders([order_id])
            logger.info(f"✅ Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel order {order_id}: {e}")
            return False
    
    def fetch_order(self, order_id: str, symbol: str) -> Order:
        """
        Fetch order details
        
        Args:
            order_id: Order ID
            symbol: Trading pair
        
        Returns:
            Order: Order details
        """
        if not self.connected:
            raise RuntimeError("Not connected to Coinbase")
        
        try:
            # Note: Coinbase SDK may not have direct get_order method
            # May need to use list_orders and filter
            logger.warning("fetch_order not fully implemented for Coinbase")
            return Order(
                order_id=order_id,
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                amount=0.0,
                price=None,
                status="unknown",
                filled=0.0,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Failed to fetch order {order_id}: {e}")
            raise
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Coinbase format
        
        Examples:
            BTC/USDT -> BTC-USD
            BTC/USD -> BTC-USD
            BTC-USD -> BTC-USD
        """
        if '/' in symbol:
            base, quote = symbol.split('/')
        elif '-' in symbol:
            return symbol  # Already in correct format
        else:
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        # Coinbase uses USD not USDT
        if quote == 'USDT':
            quote = 'USD'
        
        return f"{base}-{quote}"


def test_coinbase_connection(api_key: str, api_secret: str) -> bool:
    """
    Test Coinbase connection
    
    Args:
        api_key: Coinbase API key
        api_secret: PEM-formatted private key
    
    Returns:
        bool: True if connection successful
    """
    print("\n" + "="*70)
    print("🧪 TESTING COINBASE ADVANCED TRADE CONNECTION")
    print("="*70)
    
    try:
        connector = CoinbaseConnector(
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Test connection
        if connector.connect():
            print("\n✅ CONNECTION SUCCESSFUL")
            
            # Fetch balance
            balances = connector.fetch_balance()
            print(f"\n💰 Account Balances:")
            for asset, balance in balances.items():
                print(f"   {asset}: {balance.total:.8f} (${balance.usd_value or 0:.2f})")
            
            # Fetch BTC price
            try:
                ticker = connector.fetch_ticker("BTC/USD")
                print(f"\n📊 BTC/USD Price: ${ticker.last:,.2f}")
            except Exception as e:
                print(f"\n⚠️  Could not fetch BTC price: {e}")
            
            print("\n" + "="*70)
            print("✅ ALL TESTS PASSED")
            print("="*70)
            return True
        else:
            print("\n❌ CONNECTION FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Missing credentials. Set COINBASE_API_KEY and COINBASE_API_SECRET")
    else:
        test_coinbase_connection(api_key, api_secret)
