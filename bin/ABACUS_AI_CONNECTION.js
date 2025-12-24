/**
 * 🧠 ABACUS AI → SOVEREIGN SHADOW CONNECTION
 * 
 * Copy this code into your Abacus AI dashboard.
 * It will connect to your local trading API.
 * 
 * NO API KEYS NEEDED - It's your own server!
 */

// Configuration
const TRADING_API_URL = 'http://localhost:8000';  // Your Mac's API server
// If Abacus AI can't reach localhost, use ngrok:
// const TRADING_API_URL = 'https://your-ngrok-url.ngrok.io';

class SovereignShadowConnection {
    constructor() {
        this.apiUrl = TRADING_API_URL;
        this.isConnected = false;
        this.sessionStats = null;
    }

    /**
     * Test connection to trading API
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.apiUrl}/api/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.isConnected = true;
                console.log('✅ Connected to Sovereign Shadow Trading API');
                console.log('Risk Gate:', data.risk_gate_status);
                console.log('Session P&L:', data.session_pnl);
                return true;
            }
        } catch (error) {
            console.error('❌ Connection failed:', error);
            this.isConnected = false;
            return false;
        }
    }

    /**
     * Execute a trading signal from neural AI
     */
    async executeSignal(signal) {
        if (!this.isConnected) {
            console.error('❌ Not connected to trading API');
            return null;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/trade/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    strategy: signal.strategy || 'Cross-Exchange Arbitrage',
                    pair: signal.pair || 'BTC/USD',
                    amount: signal.amount || 25,
                    side: signal.side || 'auto',
                    mode: signal.mode || 'paper',  // paper, test, live
                    exchanges: signal.exchanges || ['coinbase', 'okx']
                })
            });

            const result = await response.json();

            if (response.ok) {
                console.log('✅ Trade executed:', result.trade_id);
                console.log('Profit:', result.profit);
                console.log('Execution time:', result.execution_time);
                
                if (result.validation_warnings) {
                    console.log('Warnings:', result.validation_warnings);
                }
                
                return result;
            } else {
                console.log('❌ Trade rejected:', result.detail.reason);
                return result;
            }
        } catch (error) {
            console.error('❌ Trade execution failed:', error);
            return null;
        }
    }

    /**
     * Get strategy performance
     */
    async getPerformance() {
        try {
            const response = await fetch(`${this.apiUrl}/api/strategy/performance`);
            const data = await response.json();
            
            console.log('📊 Strategy Performance:');
            console.log('Total Profit:', data.total_profit);
            console.log('Total Trades:', data.total_trades);
            
            data.strategies.forEach(strategy => {
                console.log(`${strategy.name}: ${strategy.total_trades} trades, $${strategy.total_profit} profit`);
            });
            
            return data;
        } catch (error) {
            console.error('❌ Failed to get performance:', error);
            return null;
        }
    }

    /**
     * Send dashboard update
     */
    async sendUpdate(event, data) {
        try {
            const response = await fetch(`${this.apiUrl}/api/dashboard/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event: event,
                    data: data
                })
            });

            const result = await response.json();
            
            if (result.success) {
                console.log('✅ Dashboard updated');
            } else {
                console.log('❌ Dashboard update failed');
            }
            
            return result;
        } catch (error) {
            console.error('❌ Dashboard update failed:', error);
            return null;
        }
    }
}

// Global instance
const sovereignShadow = new SovereignShadowConnection();

// Auto-connect on load
sovereignShadow.testConnection();

// Example usage functions
window.executeNeuralSignal = async function(signal) {
    console.log('🧠 Neural signal received:', signal);
    
    // Only trade if confidence is high
    if (signal.confidence < 0.80) {
        console.log('⚠️ Confidence too low, skipping trade');
        return;
    }
    
    const result = await sovereignShadow.executeSignal(signal);
    
    if (result && result.trade_id) {
        // Log for learning
        console.log('📈 Trade executed successfully');
        
        // Send update to dashboard
        await sovereignShadow.sendUpdate('neural_trade_completed', {
            signal_id: signal.id,
            trade_id: result.trade_id,
            profit: result.profit,
            confidence: signal.confidence
        });
    }
};

window.getTradingPerformance = async function() {
    return await sovereignShadow.getPerformance();
};

window.testTradingConnection = async function() {
    return await sovereignShadow.testConnection();
};

// Example neural signal
const exampleSignal = {
    id: 'neural_001',
    strategy: 'Cross-Exchange Arbitrage',
    pair: 'BTC/USD',
    amount: 50,
    side: 'long',
    mode: 'paper',
    confidence: 0.85,
    timestamp: new Date().toISOString()
};

// Test the connection
console.log('🧠 Abacus AI → Sovereign Shadow connection ready!');
console.log('📋 Available functions:');
console.log('  - executeNeuralSignal(signal)');
console.log('  - getTradingPerformance()');
console.log('  - testTradingConnection()');
console.log('');
console.log('🧪 Test with: executeNeuralSignal(exampleSignal)');


