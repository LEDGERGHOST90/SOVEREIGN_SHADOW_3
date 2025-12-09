#!/usr/bin/env python3
"""
LLF-ß Ledger Biometric API Integration
Real-time biometric authentication and device status monitoring
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import websockets
import threading
from enhanced_ledger_manager import EnhancedLedgerManager, LedgerStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerBiometricAPI:
    """
    Real-time API for Ledger biometric authentication and device monitoring
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize Enhanced Ledger Manager
        self.ledger_manager = EnhancedLedgerManager()
        
        # WebSocket connections for real-time updates
        self.websocket_clients = set()
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        self.background_tasks_active = True
        
    def _setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'LLF-ß Ledger Biometric API',
                'version': '1.0.0'
            })
        
        @self.app.route('/api/ledger/register', methods=['POST'])
        async def register_device():
            """Register a new Ledger device"""
            try:
                device_info = request.get_json()
                
                if not device_info:
                    return jsonify({'error': 'Device information required'}), 400
                
                success = await self.ledger_manager.register_device(device_info)
                
                if success:
                    # Broadcast device registration to WebSocket clients
                    await self._broadcast_device_update(device_info['device_id'], 'REGISTERED')
                    
                    return jsonify({
                        'success': True,
                        'message': 'Device registered successfully',
                        'device_id': device_info['device_id']
                    })
                else:
                    return jsonify({'error': 'Device registration failed'}), 500
                    
            except Exception as e:
                logger.error(f"Device registration error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/biometric/setup', methods=['POST'])
        async def setup_biometric():
            """Setup biometric authentication profile"""
            try:
                data = request.get_json()
                
                user_id = data.get('user_id')
                biometric_data = data.get('biometric_data')
                
                if not user_id or not biometric_data:
                    return jsonify({'error': 'User ID and biometric data required'}), 400
                
                success = await self.ledger_manager.setup_biometric_profile(user_id, biometric_data)
                
                return jsonify({
                    'success': success,
                    'message': 'Biometric profile setup completed' if success else 'Biometric setup failed'
                })
                
            except Exception as e:
                logger.error(f"Biometric setup error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/biometric/authenticate', methods=['POST'])
        async def authenticate_biometric():
            """Authenticate user using biometric data"""
            try:
                data = request.get_json()
                
                user_id = data.get('user_id')
                biometric_data = data.get('biometric_data')
                
                if not user_id or not biometric_data:
                    return jsonify({'error': 'User ID and biometric data required'}), 400
                
                success = await self.ledger_manager.authenticate_biometric(user_id, biometric_data)
                
                # Log authentication attempt
                auth_event = {
                    'user_id': user_id,
                    'success': success,
                    'timestamp': datetime.now().isoformat(),
                    'ip_address': request.remote_addr
                }
                
                # Broadcast authentication result
                await self._broadcast_auth_update(auth_event)
                
                return jsonify({
                    'success': success,
                    'message': 'Authentication successful' if success else 'Authentication failed',
                    'timestamp': auth_event['timestamp']
                })
                
            except Exception as e:
                logger.error(f"Biometric authentication error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/device/ping/<device_id>', methods=['GET'])
        async def ping_device(device_id):
            """Ping specific device for status"""
            try:
                result = await self.ledger_manager.ping_device(device_id)
                
                # Broadcast device status update
                await self._broadcast_device_update(device_id, result.get('status', 'UNKNOWN'))
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Device ping error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/device/status', methods=['GET'])
        @self.app.route('/api/ledger/device/status/<device_id>', methods=['GET'])
        async def get_device_status(device_id=None):
            """Get device status information"""
            try:
                status = await self.ledger_manager.get_device_status(device_id)
                return jsonify(status)
                
            except Exception as e:
                logger.error(f"Device status error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/transaction/sign', methods=['POST'])
        async def sign_transaction():
            """Sign transaction with Ledger device"""
            try:
                data = request.get_json()
                
                device_id = data.get('device_id')
                transaction_data = data.get('transaction')
                user_id = data.get('user_id')
                
                if not device_id or not transaction_data:
                    return jsonify({'error': 'Device ID and transaction data required'}), 400
                
                result = await self.ledger_manager.sign_transaction(device_id, transaction_data, user_id)
                
                # Broadcast transaction signing event
                if result.get('success'):
                    await self._broadcast_transaction_update(device_id, 'TRANSACTION_SIGNED')
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Transaction signing error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/security/events', methods=['GET'])
        def get_security_events():
            """Get recent security events"""
            try:
                limit = request.args.get('limit', 100, type=int)
                events = self.ledger_manager.get_security_events(limit)
                
                return jsonify({
                    'events': events,
                    'count': len(events),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Security events error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/ledger/realtime/status', methods=['GET'])
        async def get_realtime_status():
            """Get real-time system status"""
            try:
                # Get all device statuses
                device_status = await self.ledger_manager.get_device_status()
                
                # Get recent security events
                security_events = self.ledger_manager.get_security_events(10)
                
                # Calculate system health
                total_devices = len(device_status) if isinstance(device_status, dict) else 0
                connected_devices = sum(
                    1 for status in device_status.values() 
                    if status.get('status') == 'CONNECTED'
                ) if isinstance(device_status, dict) else 0
                
                system_health = (connected_devices / total_devices * 100) if total_devices > 0 else 0
                
                return jsonify({
                    'system_health': system_health,
                    'total_devices': total_devices,
                    'connected_devices': connected_devices,
                    'device_status': device_status,
                    'recent_events': security_events[-5:],  # Last 5 events
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Real-time status error: {e}")
                return jsonify({'error': str(e)}), 500
    
    async def _broadcast_device_update(self, device_id: str, status: str):
        """Broadcast device status update to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'DEVICE_UPDATE',
            'device_id': device_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connected WebSocket clients
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients
    
    async def _broadcast_auth_update(self, auth_event: Dict):
        """Broadcast authentication update to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'AUTH_UPDATE',
            'data': auth_event
        }
        
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        self.websocket_clients -= disconnected_clients
    
    async def _broadcast_transaction_update(self, device_id: str, event_type: str):
        """Broadcast transaction update to WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = {
            'type': 'TRANSACTION_UPDATE',
            'device_id': device_id,
            'event': event_type,
            'timestamp': datetime.now().isoformat()
        }
        
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        self.websocket_clients -= disconnected_clients
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections for real-time updates"""
        logger.info(f"New WebSocket connection: {websocket.remote_address}")
        
        # Add client to set
        self.websocket_clients.add(websocket)
        
        try:
            # Send initial status
            initial_status = await self.ledger_manager.get_device_status()
            await websocket.send(json.dumps({
                'type': 'INITIAL_STATUS',
                'data': initial_status,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Keep connection alive
            async for message in websocket:
                # Handle incoming messages if needed
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {message}")
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {websocket.remote_address}")
        finally:
            # Remove client from set
            self.websocket_clients.discard(websocket)
    
    async def _handle_websocket_message(self, websocket, data: Dict):
        """Handle incoming WebSocket messages"""
        message_type = data.get('type')
        
        if message_type == 'PING':
            # Respond to ping
            await websocket.send(json.dumps({
                'type': 'PONG',
                'timestamp': datetime.now().isoformat()
            }))
        
        elif message_type == 'SUBSCRIBE_DEVICE':
            # Subscribe to specific device updates
            device_id = data.get('device_id')
            if device_id:
                # Send current device status
                status = await self.ledger_manager.get_device_status(device_id)
                await websocket.send(json.dumps({
                    'type': 'DEVICE_STATUS',
                    'device_id': device_id,
                    'data': status,
                    'timestamp': datetime.now().isoformat()
                }))
    
    async def start_background_monitoring(self):
        """Start background monitoring tasks"""
        logger.info("Starting background monitoring tasks...")
        
        # Start ledger manager monitoring
        monitoring_task = asyncio.create_task(self.ledger_manager.start_monitoring())
        
        # Start periodic status broadcasts
        broadcast_task = asyncio.create_task(self._periodic_status_broadcast())
        
        # Wait for tasks to complete
        await asyncio.gather(monitoring_task, broadcast_task)
    
    async def _periodic_status_broadcast(self):
        """Periodically broadcast status updates to WebSocket clients"""
        while self.background_tasks_active:
            try:
                if self.websocket_clients:
                    # Get current system status
                    device_status = await self.ledger_manager.get_device_status()
                    
                    # Broadcast to all clients
                    message = {
                        'type': 'PERIODIC_UPDATE',
                        'data': device_status,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    disconnected_clients = set()
                    for client in self.websocket_clients:
                        try:
                            await client.send(json.dumps(message))
                        except websockets.exceptions.ConnectionClosed:
                            disconnected_clients.add(client)
                    
                    # Remove disconnected clients
                    self.websocket_clients -= disconnected_clients
                
                # Wait 30 seconds before next broadcast
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Periodic broadcast error: {e}")
                await asyncio.sleep(5)
    
    def start_websocket_server(self, ws_port: int = 8081):
        """Start WebSocket server for real-time updates"""
        def run_websocket_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_server = websockets.serve(
                self.websocket_handler,
                "0.0.0.0",
                ws_port
            )
            
            logger.info(f"WebSocket server starting on port {ws_port}")
            loop.run_until_complete(start_server)
            loop.run_forever()
        
        # Start WebSocket server in separate thread
        ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
        ws_thread.start()
        
        return ws_thread
    
    def run(self, host: str = "0.0.0.0", debug: bool = False):
        """Run the Flask API server"""
        logger.info(f"Starting LLF-ß Ledger Biometric API on {host}:{self.port}")
        
        # Start WebSocket server
        self.start_websocket_server()
        
        # Start background monitoring
        monitoring_thread = threading.Thread(
            target=lambda: asyncio.run(self.start_background_monitoring()),
            daemon=True
        )
        monitoring_thread.start()
        
        # Run Flask app
        self.app.run(host=host, port=self.port, debug=debug)
    
    def stop(self):
        """Stop the API server and background tasks"""
        self.background_tasks_active = False
        self.ledger_manager.stop_monitoring()
        logger.info("LLF-ß Ledger Biometric API stopped")


# Example usage and testing
if __name__ == "__main__":
    # Create and run the API
    api = LedgerBiometricAPI(port=8080)
    
    try:
        api.run(debug=True)
    except KeyboardInterrupt:
        api.stop()
        logger.info("API server stopped by user")

