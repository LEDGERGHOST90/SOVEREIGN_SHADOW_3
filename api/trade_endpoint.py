"""
Trade API Endpoint for Replit
Add this to your Shadow.AI Flask app

Enables Claude Mobile to execute trades via POST request
"""

# Add these imports to your main.py
# from coinbase.rest import RESTClient
# import uuid

# Add this route to your Flask app:

TRADE_ENDPOINT_CODE = '''
# ═══════════════════════════════════════════════════════
# TRADE ENDPOINT - Add to your Replit Flask app
# ═══════════════════════════════════════════════════════

from flask import request, jsonify
from coinbase.rest import RESTClient
import uuid
import os

# Coinbase credentials (add to Replit Secrets)
# COINBASE_API_KEY = "organizations/9338aba7-1875-4d27-84b9-a4a10af0d7fb/apiKeys/e24bc8b0-4fe7-48a4-9d21-53c4cdd4b381"
# COINBASE_API_SECRET = """-----BEGIN EC PRIVATE KEY-----
# MHcCAQEEIMeivy/ACnkWKglT24HGS3/504DtTaDQhTey0qD5lClqoAoGCCqGSM49
# AwEHoUQDQgAE2xa+wKLKQWcOavRbxfPoVwR3Dc9p8gjn5FaflxbNAspQS7u0VJkT
# INMc0JU4uIujZ8Aw/GWjW7NSte6o5QacpA==
# -----END EC PRIVATE KEY-----"""

ALLOWED_IPS = ['68.165.100.178', '127.0.0.1']  # Your VPN IP

def get_coinbase_client():
    """Get authenticated Coinbase client"""
    api_key = os.environ.get('COINBASE_API_KEY')
    api_secret = os.environ.get('COINBASE_API_SECRET')
    return RESTClient(api_key=api_key, api_secret=api_secret)

@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """
    Execute a trade on Coinbase

    POST /api/trade
    {
        "action": "BUY" or "SELL",
        "symbol": "BTC", "XRP", "SOL", "ETH",
        "amount": 25  (USD amount)
    }
    """
    # IP check
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    if client_ip not in ALLOWED_IPS:
        return jsonify({'error': 'Unauthorized IP', 'ip': client_ip}), 403

    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data'}), 400

    action = data.get('action', 'BUY').upper()
    symbol = data.get('symbol', 'BTC').upper()
    amount = data.get('amount', 25)

    # Validate
    if action not in ['BUY', 'SELL']:
        return jsonify({'error': 'Invalid action. Use BUY or SELL'}), 400

    if symbol not in ['BTC', 'ETH', 'XRP', 'SOL']:
        return jsonify({'error': 'Invalid symbol. Use BTC, ETH, XRP, or SOL'}), 400

    if amount < 1 or amount > 100:
        return jsonify({'error': 'Amount must be between 1 and 100 USD'}), 400

    # Execute trade
    try:
        client = get_coinbase_client()
        product_id = f'{symbol}-USDC'
        order_id = str(uuid.uuid4())

        if action == 'BUY':
            order = client.market_order_buy(
                client_order_id=order_id,
                product_id=product_id,
                quote_size=str(amount)
            )
        else:
            # For SELL, need to specify base_size (amount of crypto)
            # Get current price to calculate
            price = float(client.get_product(f'{symbol}-USD')['price'])
            base_size = str(round(amount / price, 8))
            order = client.market_order_sell(
                client_order_id=order_id,
                product_id=product_id,
                base_size=base_size
            )

        success = order.get('success', False) if isinstance(order, dict) else order['success']

        if success:
            return jsonify({
                'success': True,
                'action': action,
                'symbol': symbol,
                'amount_usd': amount,
                'order_id': order.get('success_response', {}).get('order_id', order_id),
                'message': f'{action} {symbol} ${amount} executed!'
            })
        else:
            error = order.get('error_response', {}).get('message', 'Unknown error')
            return jsonify({'success': False, 'error': error}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get current Coinbase balances"""
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    if client_ip not in ALLOWED_IPS:
        return jsonify({'error': 'Unauthorized IP'}), 403

    try:
        client = get_coinbase_client()
        accounts = client.get_accounts()

        balances = {}
        for acc in accounts['accounts']:
            bal = float(acc['available_balance']['value'])
            if bal > 0.0001:
                balances[acc['currency']] = bal

        return jsonify({'success': True, 'balances': balances})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''

print(TRADE_ENDPOINT_CODE)
