from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.exchange_config import ExchangeConfig, RiskSettings

exchanges_bp = Blueprint('exchanges', __name__)

@exchanges_bp.route('/exchanges', methods=['GET'])
def get_exchanges():
    """Get list of configured exchanges"""
    try:
        exchanges = ExchangeConfig.query.all()
        return jsonify({
            'exchanges': [exchange.to_dict(include_credentials=True) for exchange in exchanges]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/exchanges', methods=['POST'])
def create_exchange():
    """Create or update exchange configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Exchange name is required'}), 400
        
        # Check if exchange already exists
        exchange = ExchangeConfig.query.filter_by(name=name).first()
        if not exchange:
            exchange = ExchangeConfig(name=name)
        
        # Update fields
        exchange.display_name = data.get('display_name', name.title())
        exchange.testnet = data.get('testnet', False)
        exchange.enabled = data.get('enabled', False)
        exchange.base_url = data.get('base_url')
        exchange.rate_limit = data.get('rate_limit', 1000)
        exchange.max_position_size = data.get('max_position_size')
        exchange.default_leverage = data.get('default_leverage', 1.0)
        exchange.vpn_friendly = data.get('vpn_friendly', False)
        
        # Set API credentials if provided
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        passphrase = data.get('passphrase')
        
        if api_key and api_secret:
            exchange.set_api_credentials(api_key, api_secret, passphrase)
        
        # Set supported assets if provided
        supported_assets = data.get('supported_assets')
        if supported_assets:
            exchange.set_supported_assets(supported_assets)
        
        db.session.add(exchange)
        db.session.commit()
        
        return jsonify({
            'message': 'Exchange configuration saved successfully',
            'exchange': exchange.to_dict(include_credentials=True)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/exchanges/<int:exchange_id>', methods=['PUT'])
def update_exchange(exchange_id):
    """Update specific exchange configuration"""
    try:
        exchange = ExchangeConfig.query.get_or_404(exchange_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update fields
        if 'display_name' in data:
            exchange.display_name = data['display_name']
        if 'testnet' in data:
            exchange.testnet = data['testnet']
        if 'enabled' in data:
            exchange.enabled = data['enabled']
        if 'base_url' in data:
            exchange.base_url = data['base_url']
        if 'rate_limit' in data:
            exchange.rate_limit = data['rate_limit']
        if 'max_position_size' in data:
            exchange.max_position_size = data['max_position_size']
        if 'default_leverage' in data:
            exchange.default_leverage = data['default_leverage']
        if 'vpn_friendly' in data:
            exchange.vpn_friendly = data['vpn_friendly']
        
        # Update API credentials if provided
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        passphrase = data.get('passphrase')
        
        if api_key and api_secret:
            exchange.set_api_credentials(api_key, api_secret, passphrase)
        
        # Update supported assets if provided
        supported_assets = data.get('supported_assets')
        if supported_assets is not None:
            exchange.set_supported_assets(supported_assets)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exchange configuration updated successfully',
            'exchange': exchange.to_dict(include_credentials=True)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/exchanges/<int:exchange_id>', methods=['DELETE'])
def delete_exchange(exchange_id):
    """Delete exchange configuration"""
    try:
        exchange = ExchangeConfig.query.get_or_404(exchange_id)
        db.session.delete(exchange)
        db.session.commit()
        
        return jsonify({'message': 'Exchange configuration deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/exchanges/presets', methods=['GET'])
def get_exchange_presets():
    """Get predefined exchange configurations"""
    presets = [
        {
            'name': 'binance_us',
            'display_name': 'Binance.US',
            'base_url': 'https://api.binance.us',
            'vpn_friendly': False,
            'rate_limit': 1200,
            'supported_assets': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT']
        },
        {
            'name': 'bybit',
            'display_name': 'Bybit',
            'base_url': 'https://api.bybit.com',
            'vpn_friendly': True,
            'rate_limit': 600,
            'supported_assets': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
        },
        {
            'name': 'kucoin',
            'display_name': 'KuCoin',
            'base_url': 'https://api.kucoin.com',
            'vpn_friendly': True,
            'rate_limit': 1800,
            'supported_assets': ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT', 'DOT-USDT']
        },
        {
            'name': 'mexc',
            'display_name': 'MEXC',
            'base_url': 'https://api.mexc.com',
            'vpn_friendly': True,
            'rate_limit': 1000,
            'supported_assets': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
        },
        {
            'name': 'okx',
            'display_name': 'OKX',
            'base_url': 'https://www.okx.com',
            'vpn_friendly': True,
            'rate_limit': 600,
            'supported_assets': ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT', 'DOT-USDT']
        }
    ]
    
    return jsonify({'presets': presets})

@exchanges_bp.route('/exchanges/<int:exchange_id>/test', methods=['POST'])
def test_exchange_connection(exchange_id):
    """Test exchange API connection"""
    try:
        exchange = ExchangeConfig.query.get_or_404(exchange_id)
        
        # Get API credentials
        api_key, api_secret, passphrase = exchange.get_api_credentials()
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'error': 'API credentials not configured'
            }), 400
        
        # TODO: Implement actual API connection test
        # For now, return mock response
        return jsonify({
            'success': True,
            'message': f'Connection test for {exchange.display_name} would be performed here',
            'exchange': exchange.name,
            'testnet': exchange.testnet
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@exchanges_bp.route('/risk-settings', methods=['GET'])
def get_risk_settings():
    """Get current risk management settings"""
    try:
        settings = RiskSettings.query.first()
        if not settings:
            # Create default settings
            settings = RiskSettings()
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({'risk_settings': settings.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/risk-settings', methods=['PUT'])
def update_risk_settings():
    """Update risk management settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        settings = RiskSettings.query.first()
        if not settings:
            settings = RiskSettings()
        
        # Update fields
        if 'max_daily_loss' in data:
            settings.max_daily_loss = float(data['max_daily_loss'])
        if 'max_position_size' in data:
            settings.max_position_size = float(data['max_position_size'])
        if 'max_portfolio_risk' in data:
            settings.max_portfolio_risk = float(data['max_portfolio_risk'])
        if 'min_ray_score' in data:
            settings.min_ray_score = int(data['min_ray_score'])
        if 'max_concurrent_trades' in data:
            settings.max_concurrent_trades = int(data['max_concurrent_trades'])
        if 'stop_loss_percentage' in data:
            settings.stop_loss_percentage = float(data['stop_loss_percentage'])
        if 'take_profit_ratio' in data:
            settings.take_profit_ratio = float(data['take_profit_ratio'])
        if 'emergency_stop' in data:
            settings.emergency_stop = bool(data['emergency_stop'])
        
        # Update symbol lists
        if 'whitelist_symbols' in data:
            settings.set_symbol_list(data['whitelist_symbols'], 'whitelist')
        if 'blacklist_symbols' in data:
            settings.set_symbol_list(data['blacklist_symbols'], 'blacklist')
        
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'message': 'Risk settings updated successfully',
            'risk_settings': settings.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/emergency-stop', methods=['POST'])
def emergency_stop():
    """Activate emergency stop to halt all trading"""
    try:
        settings = RiskSettings.query.first()
        if not settings:
            settings = RiskSettings()
        
        settings.emergency_stop = True
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'message': 'Emergency stop activated - all trading halted',
            'emergency_stop': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchanges_bp.route('/emergency-stop', methods=['DELETE'])
def deactivate_emergency_stop():
    """Deactivate emergency stop to resume trading"""
    try:
        settings = RiskSettings.query.first()
        if not settings:
            settings = RiskSettings()
        
        settings.emergency_stop = False
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'message': 'Emergency stop deactivated - trading resumed',
            'emergency_stop': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

