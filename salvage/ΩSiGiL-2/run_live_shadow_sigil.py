#!/usr/bin/env python3
"""
🔥 LIVE ΩSHADOWSIGIL RUNNER
Real-time Binance integration with Trinity consciousness
"""

import asyncio
import sys
import os
from datetime import datetime
import signal as system_signal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.live_integration_core import LiveIntegratedShadowSIGIL
from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import threading
import json

class LiveShadowSIGILRunner:
    """
    🔥 LIVE ΩSHADOWSIGIL RUNNER
    Manages live integration with web dashboard
    """
    
    def __init__(self):
        self.live_system = None
        self.streaming_task = None
        self.flask_app = None
        self.socketio = None
        self.running = False
        
        print("🔥 LIVE ΩSHADOWSIGIL RUNNER INITIALIZED")
    
    async def initialize_live_system(self):
        """🔥 Initialize the live integrated system"""
        print("🔥 INITIALIZING LIVE SYSTEM...")
        self.live_system = LiveIntegratedShadowSIGIL()
        await self.live_system.initialize_live_systems()
        print("✅ LIVE SYSTEM READY")
    
    async def start_live_streaming(self):
        """📡 Start live streaming with monitoring"""
        if not self.live_system:
            await self.initialize_live_system()
        
        print("📡 STARTING LIVE STREAMING...")
        print("🚨 WARNING: PROCESSING REAL MARKET DATA")
        print("🚨 WARNING: RSI TRIGGERS ACTIVE FOR EWT")
        print("🚨 WARNING: TRINITY CONSENSUS OPERATIONAL")
        
        self.streaming_task = await self.live_system.start_live_streaming()
        self.running = True
        
        # Monitor and report status
        await self._monitor_live_system()
    
    async def _monitor_live_system(self):
        """📊 Monitor live system and report status"""
        last_report_time = datetime.now()
        
        while self.running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Get current status
                status = self.live_system.get_live_status()
                
                # Report every 60 seconds
                if (datetime.now() - last_report_time).seconds >= 60:
                    print(f"\n📊 LIVE STATUS REPORT:")
                    print(f"   🔴 Streaming: {'ACTIVE' if status['live_streaming'] else 'INACTIVE'}")
                    print(f"   📊 Signals Processed: {status['signals_processed']}")
                    print(f"   🚨 Triggers Activated: {status['triggers_activated']}")
                    print(f"   🔱 Trinity Decisions: {status['trinity_decisions']}")
                    print(f"   💼 Active Positions: {status['active_positions']}")
                    print(f"   📈 Recent Signals (5min): {status['recent_signals']}")
                    
                    if status['last_signal_time']:
                        time_since_signal = (datetime.now() - status['last_signal_time']).seconds
                        print(f"   ⏰ Last Signal: {time_since_signal}s ago")
                    
                    last_report_time = datetime.now()
                
                # Emit to web dashboard if available
                if self.socketio:
                    self.socketio.emit('live_status', status)
                    
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def stop_live_streaming(self):
        """🛑 Stop live streaming"""
        self.running = False
        if self.live_system:
            await self.live_system.stop_live_streaming()
        print("🛑 Live streaming stopped")
    
    def create_web_dashboard(self):
        """🌐 Create web dashboard for live monitoring"""
        self.flask_app = Flask(__name__)
        self.flask_app.config['SECRET_KEY'] = 'shadow_sigil_live'
        self.socketio = SocketIO(self.flask_app, cors_allowed_origins="*")
        
        @self.flask_app.route('/')
        def dashboard():
            return render_template_string(LIVE_DASHBOARD_HTML)
        
        @self.flask_app.route('/api/status')
        def api_status():
            if self.live_system:
                return jsonify(self.live_system.get_live_status())
            return jsonify({'error': 'System not initialized'})
        
        @self.socketio.on('connect')
        def handle_connect():
            print("🌐 Web client connected to live dashboard")
            if self.live_system:
                emit('live_status', self.live_system.get_live_status())
        
        @self.socketio.on('stop_streaming')
        def handle_stop():
            print("🛑 Stop command received from web dashboard")
            asyncio.create_task(self.stop_live_streaming())
        
        print("🌐 Web dashboard created at http://localhost:5000")
        return self.flask_app, self.socketio
    
    def run_web_server(self):
        """🌐 Run web server in background thread"""
        if not self.flask_app:
            self.create_web_dashboard()
        
        def run_server():
            self.socketio.run(self.flask_app, host='0.0.0.0', port=5000, debug=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print("🌐 Web server started in background")

# HTML template for live dashboard
LIVE_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔥 Live ΩShadowSIGIL Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { 
            background: #0a0a0a; 
            color: #8A2BE2; 
            font-family: 'Courier New', monospace; 
            margin: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status-card { 
            background: #1a1a1a; 
            border: 2px solid #8A2BE2; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 0 20px rgba(138, 43, 226, 0.3);
        }
        .metric { margin: 10px 0; }
        .metric-label { color: #666; }
        .metric-value { color: #8A2BE2; font-weight: bold; font-size: 1.2em; }
        .status-active { color: #00ff00; }
        .status-inactive { color: #ff4444; }
        .warning { color: #ff6600; font-weight: bold; }
        .button { 
            background: #8A2BE2; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px;
        }
        .button:hover { background: #9932CC; }
        #log { 
            background: #000; 
            border: 1px solid #8A2BE2; 
            height: 200px; 
            overflow-y: scroll; 
            padding: 10px; 
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 LIVE ΩSHADOWSIGIL DASHBOARD</h1>
            <p class="warning">⚠️ REAL-TIME MARKET DATA PROCESSING ACTIVE</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>📡 Streaming Status</h3>
                <div class="metric">
                    <span class="metric-label">Live Streaming:</span>
                    <span id="streaming-status" class="metric-value">UNKNOWN</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Signals Processed:</span>
                    <span id="signals-processed" class="metric-value">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Recent Signals (5min):</span>
                    <span id="recent-signals" class="metric-value">0</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🚨 RSI Triggers</h3>
                <div class="metric">
                    <span class="metric-label">Triggers Activated:</span>
                    <span id="triggers-activated" class="metric-value">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">EWT RSI Monitor:</span>
                    <span class="metric-value status-active">ACTIVE</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Trigger Threshold:</span>
                    <span class="metric-value">RSI < 28</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🔱 Trinity Consensus</h3>
                <div class="metric">
                    <span class="metric-label">Trinity Decisions:</span>
                    <span id="trinity-decisions" class="metric-value">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Consensus Active:</span>
                    <span class="metric-value status-active">OPERATIONAL</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Required Votes:</span>
                    <span class="metric-value">2 of 3</span>
                </div>
            </div>
            
            <div class="status-card">
                <h3>💼 Active Positions</h3>
                <div class="metric">
                    <span class="metric-label">Open Positions:</span>
                    <span id="active-positions" class="metric-value">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Position Mode:</span>
                    <span class="metric-value warning">SIMULATION</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Max Position Size:</span>
                    <span class="metric-value">1.25% vault</span>
                </div>
            </div>
        </div>
        
        <div class="status-card" style="margin-top: 20px;">
            <h3>📊 System Controls</h3>
            <button class="button" onclick="refreshStatus()">🔄 Refresh Status</button>
            <button class="button" onclick="stopStreaming()" style="background: #ff4444;">🛑 Stop Streaming</button>
            <div class="metric">
                <span class="metric-label">Last Update:</span>
                <span id="last-update" class="metric-value">Never</span>
            </div>
        </div>
        
        <div class="status-card" style="margin-top: 20px;">
            <h3>📝 Live Log</h3>
            <div id="log"></div>
        </div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', function() {
            addLog('🌐 Connected to live dashboard');
        });
        
        socket.on('live_status', function(status) {
            updateStatus(status);
        });
        
        function updateStatus(status) {
            document.getElementById('streaming-status').textContent = status.live_streaming ? 'ACTIVE' : 'INACTIVE';
            document.getElementById('streaming-status').className = status.live_streaming ? 'metric-value status-active' : 'metric-value status-inactive';
            
            document.getElementById('signals-processed').textContent = status.signals_processed || 0;
            document.getElementById('recent-signals').textContent = status.recent_signals || 0;
            document.getElementById('triggers-activated').textContent = status.triggers_activated || 0;
            document.getElementById('trinity-decisions').textContent = status.trinity_decisions || 0;
            document.getElementById('active-positions').textContent = status.active_positions || 0;
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            
            if (status.triggers_activated > 0) {
                addLog(`🚨 RSI Trigger activated! Total: ${status.triggers_activated}`);
            }
        }
        
        function addLog(message) {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            log.innerHTML += `[${timestamp}] ${message}<br>`;
            log.scrollTop = log.scrollHeight;
        }
        
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(status => updateStatus(status))
                .catch(error => addLog(`❌ Error: ${error}`));
        }
        
        function stopStreaming() {
            socket.emit('stop_streaming');
            addLog('🛑 Stop command sent');
        }
        
        // Auto-refresh every 10 seconds
        setInterval(refreshStatus, 10000);
    </script>
</body>
</html>
'''

async def main():
    """🔥 Main function for live ΩShadowSIGIL"""
    print("🔥 LIVE ΩSHADOWSIGIL STARTING...")
    
    runner = LiveShadowSIGILRunner()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutdown signal received...")
        asyncio.create_task(runner.stop_live_streaming())
    
    system_signal.signal(system_signal.SIGINT, signal_handler)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'server':
            print("🌐 Starting with web dashboard...")
            runner.run_web_server()
            await runner.start_live_streaming()
            
        elif mode == 'stream':
            print("📡 Starting streaming only...")
            await runner.start_live_streaming()
            
        elif mode == 'test':
            print("🧪 Running integration test...")
            await runner.initialize_live_system()
            status = runner.live_system.get_live_status()
            print(f"✅ Integration test complete: {status}")
            
        else:
            print("❌ Unknown mode. Use: server, stream, or test")
    else:
        print("🌐 Starting with web dashboard (default)...")
        runner.run_web_server()
        await runner.start_live_streaming()

if __name__ == "__main__":
    asyncio.run(main())

