from datetime import datetime
import json
from src.models.user import db

class ExchangeConfig(db.Model):
    """Exchange configuration for API connections"""
    __tablename__ = 'exchange_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exchange_name = db.Column(db.String(50), nullable=False)  # binance_us, kucoin, bybit
    
    # API credentials (encrypted)
    api_key = db.Column(db.String(255), nullable=False)
    api_secret = db.Column(db.String(255), nullable=False)
    passphrase = db.Column(db.String(255))  # For KuCoin
    
    # Configuration
    is_testnet = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_paper_trading = db.Column(db.Boolean, default=True)
    
    # VPN and routing
    use_vpn = db.Column(db.Boolean, default=False)
    vpn_endpoint = db.Column(db.String(255))
    
    # Trading settings
    default_order_type = db.Column(db.String(20), default='limit')  # market, limit
    max_slippage = db.Column(db.Float, default=0.5)  # percentage
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('exchange_configs', lazy=True))
    
    def __repr__(self):
        return f'<ExchangeConfig {self.exchange_name} for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exchange_name': self.exchange_name,
            'is_testnet': self.is_testnet,
            'is_active': self.is_active,
            'is_paper_trading': self.is_paper_trading,
            'use_vpn': self.use_vpn,
            'default_order_type': self.default_order_type,
            'max_slippage': self.max_slippage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RiskSettings(db.Model):
    """Risk management settings"""
    __tablename__ = 'risk_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Daily limits
    max_daily_loss = db.Column(db.Float, default=1000.0)
    max_daily_trades = db.Column(db.Integer, default=10)
    max_concurrent_positions = db.Column(db.Integer, default=5)
    
    # Position sizing
    max_position_size = db.Column(db.Float, default=500.0)
    position_size_percentage = db.Column(db.Float, default=2.0)  # % of account
    
    # Ray Score filtering
    min_ray_score = db.Column(db.Float, default=60.0)  # Mental stop loss
    ray_exit_threshold = db.Column(db.Float, default=40.0)  # Force exit below this
    
    # Risk/Reward requirements
    min_risk_reward_ratio = db.Column(db.Float, default=1.5)
    max_risk_percentage = db.Column(db.Float, default=2.0)  # % of account per trade
    
    # Vault siphon settings
    vault_siphon_enabled = db.Column(db.Boolean, default=True)
    vault_siphon_percentage = db.Column(db.Float, default=30.0)
    vault_siphon_threshold = db.Column(db.Float, default=100.0)  # Min profit to trigger
    
    # Emergency settings
    emergency_stop = db.Column(db.Boolean, default=False)
    max_drawdown_percentage = db.Column(db.Float, default=10.0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('risk_settings', lazy=True))
    
    def __repr__(self):
        return f'<RiskSettings for User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'max_daily_loss': self.max_daily_loss,
            'max_daily_trades': self.max_daily_trades,
            'max_concurrent_positions': self.max_concurrent_positions,
            'max_position_size': self.max_position_size,
            'position_size_percentage': self.position_size_percentage,
            'min_ray_score': self.min_ray_score,
            'ray_exit_threshold': self.ray_exit_threshold,
            'min_risk_reward_ratio': self.min_risk_reward_ratio,
            'max_risk_percentage': self.max_risk_percentage,
            'vault_siphon_enabled': self.vault_siphon_enabled,
            'vault_siphon_percentage': self.vault_siphon_percentage,
            'vault_siphon_threshold': self.vault_siphon_threshold,
            'emergency_stop': self.emergency_stop,
            'max_drawdown_percentage': self.max_drawdown_percentage,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Position(db.Model):
    """Active trading positions"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # long, short
    quantity = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float)
    
    # Order IDs for tracking
    entry_order_id = db.Column(db.String(100))
    tp1_order_id = db.Column(db.String(100))
    tp2_order_id = db.Column(db.String(100))
    sl_order_id = db.Column(db.String(100))
    
    # Status tracking
    status = db.Column(db.String(20), default='open')  # open, partial, closed
    filled_quantity = db.Column(db.Float, default=0.0)
    remaining_quantity = db.Column(db.Float)
    
    # PnL tracking
    unrealized_pnl = db.Column(db.Float, default=0.0)
    realized_pnl = db.Column(db.Float, default=0.0)
    fees_paid = db.Column(db.Float, default=0.0)
    
    # Timing
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    signal = db.relationship('TradingSignal', backref=db.backref('positions', lazy=True))
    user = db.relationship('User', backref=db.backref('positions', lazy=True))
    
    def __repr__(self):
        return f'<Position {self.symbol} {self.side} {self.quantity}>'
    
    def calculate_pnl(self, current_price=None):
        """Calculate current PnL"""
        if not current_price:
            current_price = self.current_price
        
        if not current_price or not self.entry_price:
            return 0.0
        
        if self.side == 'long':
            pnl = (current_price - self.entry_price) * self.filled_quantity
        else:
            pnl = (self.entry_price - current_price) * self.filled_quantity
        
        self.unrealized_pnl = pnl - self.fees_paid
        return self.unrealized_pnl
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'entry_order_id': self.entry_order_id,
            'tp1_order_id': self.tp1_order_id,
            'tp2_order_id': self.tp2_order_id,
            'sl_order_id': self.sl_order_id,
            'status': self.status,
            'filled_quantity': self.filled_quantity,
            'remaining_quantity': self.remaining_quantity,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'fees_paid': self.fees_paid,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }

