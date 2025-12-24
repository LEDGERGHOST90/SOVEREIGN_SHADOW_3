from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import json
from src.models.user import db
from src.models.signal import TradingSignal, ExecutionLog
from src.models.exchange_config import RiskSettings

signals_bp = Blueprint('signals', __name__)

@signals_bp.route('/webhook', methods=['POST'])
def receive_signal():
    """
    Webhook endpoint for receiving trading signals
    Supports multiple signal formats from different sources
    """
    start_time = time.time()
    
    try:
        # Get signal data
        signal_data = request.get_json()
        if not signal_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Log signal reception
        print(f"[SIGNAL] Received: {json.dumps(signal_data, indent=2)}")
        
        # Parse signal based on source format
        parsed_signal = parse_signal(signal_data)
        if not parsed_signal:
            return jsonify({'error': 'Invalid signal format'}), 400
        
        # Create signal record
        signal = TradingSignal(**parsed_signal)
        signal.set_raw_data(signal_data)
        
        db.session.add(signal)
        db.session.commit()
        
        # Log reception
        log_execution(signal.id, 'signal_received', 
                     f"Signal received from {signal.source}", 
                     int((time.time() - start_time) * 1000))
        
        # Validate signal against risk settings
        validation_result = validate_signal(signal)
        if not validation_result['valid']:
            signal.status = 'rejected'
            signal.error_message = validation_result['reason']
            db.session.commit()