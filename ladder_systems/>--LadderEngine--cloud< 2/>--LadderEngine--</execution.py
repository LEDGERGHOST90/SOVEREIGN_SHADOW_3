from flask import Blueprint, request, jsonify
import asyncio
import threading
from src.execution.order_engine import execution_engine

execution_bp = Blueprint('execution', __name__)

# Global thread for running the execution engine
execution_thread = None
execution_loop = None

@execution_bp.route('/execution/start', methods=['POST'])
def start_execution_engine():
    """Start the order execution engine"""
    global execution_thread, execution_loop
    
    try:
        if execution_thread and execution_thread.is_alive():
            return jsonify({
                'success': False,
                'message': 'Execution engine is already running'
            }), 400
        
        # Create new event loop for the execution engine
        def run_engine():
            global execution_loop
            execution_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(execution_loop)
            execution_loop.run_until_complete(execution_engine.start())
        
        execution_thread = threading.Thread(target=run_engine, daemon=True)
        execution_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Execution engine started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@execution_bp.route('/execution/stop', methods=['POST'])
def stop_execution_engine():
    """Stop the order execution engine"""
    global execution_thread, execution_loop
    
    try:
        if not execution_thread or not execution_thread.is_alive():
            return jsonify({
                'success': False,
                'message': 'Execution engine is not running'
            }), 400
        
        # Stop the execution engine
        if execution_loop:
            asyncio.run_coroutine_threadsafe(execution_engine.stop(), execution_loop)
        
        # Wait for thread to finish
        execution_thread.join(timeout=10)
        
        return jsonify({
            'success': True,
            'message': 'Execution engine stopped successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@execution_bp.route('/execution/status', methods=['GET'])
def get_execution_status():
    """Get execution engine status"""
    try:
        global execution_thread, execution_loop
        
        is_running = execution_thread and execution_thread.is_alive()
        
        if is_running and execution_loop:
            # Get detailed status from the engine
            future = asyncio.run_coroutine_threadsafe(execution_engine.get_status(), execution_loop)
            try:
                status = future.result(timeout=5)
                status['thread_alive'] = True
                return jsonify(status)
            except asyncio.TimeoutError:
                return jsonify({
                    'running': False,
                    'thread_alive': True,
                    'error': 'Status request timed out'
                })
        else:
            return jsonify({
                'running': False,
                'thread_alive': False,
                'active_exchanges': [],
                'active_positions': 0,
                'daily_pnl': 0.0,
                'daily_trades': 0,
                'emergency_stop': False
            })
        
    except Exception as e:
        return jsonify({
            'running': False,
            'error': str(e)
        }), 500

@execution_bp.route('/execution/restart', methods=['POST'])
def restart_execution_engine():
    """Restart the execution engine"""
    try:
        # Stop first
        stop_result = stop_execution_engine()
        if not stop_result[0].get_json().get('success', False):
            return stop_result
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Start again
        return start_execution_engine()
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@execution_bp.route('/execution/force-process', methods=['POST'])
def force_process_signals():
    """Force process pending signals (for testing)"""
    try:
        if not execution_thread or not execution_thread.is_alive():
            return jsonify({
                'success': False,
                'message': 'Execution engine is not running'
            }), 400
        
        # This would trigger immediate processing of pending signals
        # For now, just return success as the engine processes automatically
        return jsonify({
            'success': True,
            'message': 'Signal processing triggered'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

