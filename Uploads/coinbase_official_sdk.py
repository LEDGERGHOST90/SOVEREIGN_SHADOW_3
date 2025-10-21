
from coinbase.rest import RESTClient
import os
from load_env import load_env

# Load environment variables
load_env()

class CoinbaseOfficialClient:
    """Official Coinbase Advanced Trade SDK wrapper"""
    
    def __init__(self):
        # Get credentials from environment
        api_key = os.getenv('COINBASE_API_KEY')
        api_secret = os.getenv('COINBASE_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Missing COINBASE_API_KEY or COINBASE_API_SECRET")
        
        print(f"🔑 API Key: {api_key[:30]}...")
        print(f"🔐 API Secret: {len(api_secret)} characters loaded")
        
        # Initialize official SDK client
        self.client = RESTClient(
            api_key=api_key,
            api_secret=api_secret
        )
        print("✅ Official SDK client initialized")
    
    def list_accounts(self):
        """Get all accounts"""
        try:
            accounts = self.client.get_accounts()
            return accounts
        except Exception as e:
            print(f"❌ Error listing accounts: {e}")
            return None
    
    def get_best_bid_ask(self, product_id):
        """Get best bid/ask for a product"""
        try:
            ticker = self.client.get_product(product_id)
            return ticker
        except Exception as e:
            print(f"❌ Error getting ticker for {product_id}: {e}")
            return None
    
    def get_product_book(self, product_id, limit=10):
        """Get order book for a product"""
        try:
            book = self.client.get_product_book(product_id, limit=limit)
            return book
        except Exception as e:
            print(f"❌ Error getting order book for {product_id}: {e}")
            return None
    
    def list_products(self):
        """Get all trading products"""
        try:
            products = self.client.get_products()
            return products
        except Exception as e:
            print(f"❌ Error listing products: {e}")
            return None
    
    def create_market_order(self, product_id, side, size):
        """
        Create market order
        side: 'BUY' or 'SELL'
        size: amount in base currency
        """
        try:
            order = self.client.market_order_buy(
                product_id=product_id,
                base_size=str(size)
            ) if side == 'BUY' else self.client.market_order_sell(
                product_id=product_id,
                base_size=str(size)
            )
            return order
        except Exception as e:
            print(f"❌ Error creating market order: {e}")
            return None
    
    def create_limit_order(self, product_id, side, size, price):
        """
        Create limit order
        side: 'BUY' or 'SELL'
        size: amount in base currency
        price: limit price
        """
        try:
            order = self.client.limit_order_gtc_buy(
                product_id=product_id,
                base_size=str(size),
                limit_price=str(price)
            ) if side == 'BUY' else self.client.limit_order_gtc_sell(
                product_id=product_id,
                base_size=str(size),
                limit_price=str(price)
            )
            return order
        except Exception as e:
            print(f"❌ Error creating limit order: {e}")
            return None
    
    def get_order(self, order_id):
        """Get order details"""
        try:
            order = self.client.get_order(order_id)
            return order
        except Exception as e:
            print(f"❌ Error getting order {order_id}: {e}")
            return None
    
    def cancel_orders(self, order_ids):
        """Cancel multiple orders"""
        try:
            result = self.client.cancel_orders(order_ids)
            return result
        except Exception as e:
            print(f"❌ Error canceling orders: {e}")
            return None

# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TESTING OFFICIAL COINBASE ADVANCED TRADE SDK")
    print("=" * 60)
    
    try:
        client = CoinbaseOfficialClient()
        
        # Test 1: List accounts
        print("\n📊 TEST 1: Listing accounts...")
        accounts = client.list_accounts()
        if accounts:
            account_list = accounts.get('accounts', [])
            print(f"✅ SUCCESS - Found {len(account_list)} accounts")
            for acc in account_list[:5]:
                currency = acc.get('currency', 'N/A')
                available = acc.get('available_balance', {}).get('value', '0')
                name = acc.get('name', 'N/A')
                print(f"  💰 {name}: {available} {currency}")
        else:
            print("❌ FAILED - No accounts returned")
        
        # Test 2: Get BTC-USD ticker
        print("\n💰 TEST 2: Getting BTC-USD ticker...")
        ticker = client.get_best_bid_ask('BTC-USD')
        if ticker:
            price = ticker.get('price', 'N/A')
            print(f"✅ SUCCESS - BTC-USD Price: ${price}")
        else:
            print("❌ FAILED - No ticker data")
        
        # Test 3: List products
        print("\n📈 TEST 3: Listing trading products...")
        products = client.list_products()
        if products:
            product_list = products.get('products', [])
            print(f"✅ SUCCESS - Found {len(product_list)} trading pairs")
            # Show first 5
            for prod in product_list[:5]:
                print(f"  📊 {prod.get('product_id', 'N/A')}")
        else:
            print("❌ FAILED - No products returned")
        
        # Test 4: Get order book
        print("\n📖 TEST 4: Getting SOL-USD order book...")
        book = client.get_product_book('SOL-USD', limit=5)
        if book:
            print(f"✅ SUCCESS - Order book retrieved")
            pricebook = book.get('pricebook', {})
            bids = pricebook.get('bids', [])[:3]
            asks = pricebook.get('asks', [])[:3]
            print(f"  📉 Top 3 Bids: {[b.get('price') for b in bids]}")
            print(f"  📈 Top 3 Asks: {[a.get('price') for a in asks]}")
        else:
            print("❌ FAILED - No order book data")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️ Please check:")
        print("1. API key and secret are correct in .env")
        print("2. API key has proper permissions")
        print("3. IP whitelist is disabled or includes this server")
