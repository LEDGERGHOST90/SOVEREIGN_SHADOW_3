from datetime import datetime
import json
from src.models.user import db

class TradingSignal(db.Model):
    """Trading signal model for storing incoming signals"""
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.String(100), unique=True, nullable=False)
    source = db.Column(db.String(50), nullable=False)  # webhook, manual, bot
    symbol = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # buy, sell
    entry_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    
    # Take profit levels
    tp1_price = db.Column(db.Float)
    tp1_quantity = db.Column(db.Float)
    tp2_price = db.Column(db.Float)
    tp2_quantity = db.Column(db.Float)
    
    # Stop loss
    sl_price = db.Column(db.Float)
    
    # Ray Score for decision filtering
    ray_score = db.Column(db.Float, default=0.0)
    
    # Signal metadata
    status = db.Column(db.String(20), default='pending')  # pending, processing, executed, rejected, failed
    priority = db.Column(db.Integer, default=5)  # 1-10, higher = more urgent
    exchange = db.Column(db.String(20))
    
    # Timing
    signal_time = db.Column(db.DateTime, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Raw data and error handling
    raw_data = db.Column(db.Text)
    error_message = db.Column(db.Text)
    
    # Vault siphon settings
    vault_siphon_enabled = db.Column(db.Boolean, default=False)
    vault_siphon_percentage = db.Column(db.Float, default=30.0)
    
    def __repr__(self):
        return f'<TradingSignal {self.signal_id}: {self.symbol} {self.action}>'
    
    def set_raw_data(self, data):
        """Store raw signal data as JSON"""
        self.raw_data = json.dumps(data)
    
    def get_raw_data(self):
        """Retrieve raw signal data"""
        if self.raw_data:
            return json.loads(self.raw_data)
        return None
    
    def calculate_ray_score(self):
        """Calculate Ray Score based on signal quality metrics"""
        # Placeholder implementation - should be enhanced with actual Ray Rules
        score = 50.0  # Base score
        
        # Add points for complete signal data
        if self.tp1_price and self.tp2_price:
            score += 15
        if self.sl_price:
            score += 10
        if self.priority >= 7:
            score += 10
        
        # Risk/reward ratio bonus
        if self.entry_price and self.tp1_price and self.sl_price:
            risk = abs(self.entry_price - self.sl_price)
            reward = abs(self.tp1_price - self.entry_price)
            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio >= 2.0:
                    score += 15
                elif rr_ratio >= 1.5:
                    score += 10
        
        self.ray_score = min(100.0, max(0.0, score))
        return self.ray_score
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'source': self.source,
            'symbol': self.symbol,
            'action': self.action,
            'entry_price': self.entry_price,
            'quantity': self.quantity,
            'tp1_price': self.tp1_price,
            'tp1_quantity': self.tp1_quantity,
            'tp2_price': self.tp2_price,
            'tp2_quantity': self.tp2_quantity,
            'sl_price': self.sl_price,
            'ray_score': self.ray_score,
            'status': self.status,
            'priority': self.priority,
            'exchange': self.exchange,
            'signal_time': self.signal_time.isoformat() if self.signal_time else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'vault_siphon_enabled': self.vault_siphon_enabled,
            'vault_siphon_percentage': self.vault_siphon_percentage,
            'error_message': self.error_message
        }


class ExecutionLog(db.Model):
    """Execution log for tracking order processing"""
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    execution_time_ms = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Order details
    order_id = db.Column(db.String(100))
    exchange = db.Column(db.String(20))
    order_type = db.Column(db.String(20))  # market, limit, stop
    filled_quantity = db.Column(db.Float)
    filled_price = db.Column(db.Float)
    fees = db.Column(db.Float)
    
    # PnL tracking
    pnl = db.Column(db.Float)
    pnl_percentage = db.Column(db.Float)
    
    signal = db.relationship('TradingSignal', backref=db.backref('execution_logs', lazy=True))
    
    def __repr__(self):
        return f'<ExecutionLog {self.action} for Signal {self.signal_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'action': self.action,
            'message': self.message,
            'execution_time_ms': self.execution_time_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'order_id': self.order_id,
            'exchange': self.exchange,
            'order_type': self.order_type,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'fees': self.fees,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage
        }

