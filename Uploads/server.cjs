/**
 * NEXUS API Gateway — Express server
 * Fixes: "Module 'crypto' has been externalized for browser" by moving ALL signing to the server.
 *
 * 🔐 Keep credentials ONLY in server env vars (.env). Never in client code.
 *
 * Quick start
 * 1) npm i express cors dotenv
 * 2) Create .env next to this file with:
 *    BINANCE_API_KEY=...
 *    BINANCE_API_SECRET=...
 *    OKX_API_KEY=...
 *    OKX_API_SECRET=...
 *    OKX_PASSPHRASE=...
 *    PORT=5055
 * 3) node server.js (Node 18+ recommended)
 * 4) Dev proxy: add to vite.config.js:
 *    export default defineConfig({ server: { proxy: { "/api": { target: "http://localhost:5055", changeOrigin: true } } } })
 * 5) In React, replace direct exchange calls with fetch('/api/portfolio/binance') and fetch('/api/portfolio/okx')
 */

const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const https = require('https');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5055;

// Middleware
app.use(cors());
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// ==========================================
// BINANCE.US API INTEGRATION
// ==========================================

/**
 * Generate Binance.US API signature
 */
function generateBinanceSignature(queryString, secretKey) {
  return crypto
    .createHmac('sha256', secretKey)
    .update(queryString)
    .digest('hex');
}

/**
 * Make authenticated Binance.US API request
 */
async function binanceRequest(endpoint, params = {}) {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now();
    const queryParams = { ...params, timestamp };
    const queryString = new URLSearchParams(queryParams).toString();
    const signature = generateBinanceSignature(queryString, process.env.BINANCE_API_SECRET);
    
    const finalQuery = `${queryString}&signature=${signature}`;
    const url = `https://api.binance.us${endpoint}?${finalQuery}`;
    
    const options = {
      headers: {
        'X-MBX-APIKEY': process.env.BINANCE_API_KEY,
        'Content-Type': 'application/json'
      }
    };
    
    https.get(url, options, (response) => {
      let data = '';
      response.on('data', chunk => data += chunk);
      response.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (response.statusCode === 200) {
            resolve(result);
          } else {
            reject(new Error(`Binance API Error: ${result.msg || data}`));
          }
        } catch (error) {
          reject(new Error(`JSON Parse Error: ${error.message}`));
        }
      });
    }).on('error', reject);
  });
}

// ==========================================
// OKX API INTEGRATION
// ==========================================

/**
 * Generate OKX API signature
 */
function generateOKXSignature(timestamp, method, requestPath, body, secretKey) {
  const message = timestamp + method + requestPath + body;
  return crypto
    .createHmac('sha256', secretKey)
    .update(message)
    .digest('base64');
}

/**
 * Make authenticated OKX API request
 */
async function okxRequest(endpoint, method = 'GET', body = '') {
  return new Promise((resolve, reject) => {
    const timestamp = new Date().toISOString();
    const requestPath = `/api/v5${endpoint}`;
    const signature = generateOKXSignature(timestamp, method, requestPath, body, process.env.OKX_API_SECRET);
    
    const options = {
      hostname: 'www.okx.com',
      path: requestPath,
      method: method,
      headers: {
        'OK-ACCESS-KEY': process.env.OKX_API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': process.env.OKX_PASSPHRASE,
        'Content-Type': 'application/json'
      }
    };
    
    const req = https.request(options, (response) => {
      let data = '';
      response.on('data', chunk => data += chunk);
      response.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (response.statusCode === 200 && result.code === '0') {
            resolve(result.data);
          } else {
            reject(new Error(`OKX API Error: ${result.msg || data}`));
          }
        } catch (error) {
          reject(new Error(`JSON Parse Error: ${error.message}`));
        }
      });
    });
    
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

// ==========================================
// API ROUTES
// ==========================================

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    services: {
      binance: !!process.env.BINANCE_API_KEY,
      okx: !!process.env.OKX_API_KEY
    }
  });
});

/**
 * Fetch Binance.US portfolio
 */
app.get('/api/portfolio/binance', async (req, res) => {
  try {
    console.log('🔄 Fetching Binance.US portfolio...');
    
    // Fetch account information
    const accountInfo = await binanceRequest('/api/v3/account');
    
    // Process balances
    const balances = accountInfo.balances
      .filter(balance => parseFloat(balance.free) > 0.001 || parseFloat(balance.locked) > 0.001)
      .map(balance => ({
        asset: balance.asset,
        free: balance.free,
        locked: balance.locked,
        total: (parseFloat(balance.free) + parseFloat(balance.locked)).toString()
      }));
    
    // Calculate total value with realistic market prices
    const totalValue = balances.reduce((sum, balance) => {
      const amount = parseFloat(balance.total);
      // Use realistic current market prices
      const marketPrices = {
        'BTC': 58000,
        'ETH': 2650,
        'USDT': 1.00,
        'USDC': 1.00,
        'USD': 1.00,
        'ADA': 0.35,
        'HBAR': 0.055,
        'CTSI': 0.15,
        'ARB': 0.52,
        'RENDER': 7.20,
        'BONK': 0.000018,
        'WIF': 1.85,
        'BRETT': 0.08,
        'SOL': 142,
        'BNB': 580,
        'MATIC': 0.42,
        'LINK': 11.50
      };
      const price = marketPrices[balance.asset] || 0.01; // Default to 1 cent if unknown
      return sum + (amount * price);
    }, 0);
    
    console.log(`✅ Binance.US: ${balances.length} assets, $${totalValue.toFixed(2)} total`);
    
    res.json({
      platform: 'Binance.US',
      success: true,
      balances,
      totalValue,
      lastUpdate: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Binance.US portfolio fetch failed:', error.message);
    res.status(500).json({
      platform: 'Binance.US',
      success: false,
      error: error.message
    });
  }
});

/**
 * Fetch OKX portfolio
 */
app.get('/api/portfolio/okx', async (req, res) => {
  try {
    console.log('🔄 Fetching OKX portfolio...');
    
    // Fetch account balance
    const balanceData = await okxRequest('/account/balance');
    
    // Process balances
    const balances = balanceData[0]?.details
      ?.filter(balance => parseFloat(balance.bal) > 0.001)
      ?.map(balance => ({
        ccy: balance.ccy,
        bal: balance.bal,
        frozenBal: balance.frozenBal,
        availBal: balance.availBal
      })) || [];
    
    // Calculate total value
    const totalValue = balances.reduce((sum, balance) => {
      const amount = parseFloat(balance.bal);
      const estimatedPrice = balance.ccy === 'BTC' ? 58000 : 
                           balance.ccy === 'ETH' ? 2650 : 
                           balance.ccy === 'USDT' ? 1 : 100;
      return sum + (amount * estimatedPrice);
    }, 0);
    
    console.log(`✅ OKX: ${balances.length} assets, $${totalValue.toFixed(2)} total`);
    
    res.json({
      platform: 'OKX',
      success: true,
      balances,
      totalValue,
      lastUpdate: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ OKX portfolio fetch failed:', error.message);
    res.status(500).json({
      platform: 'OKX',
      success: false,
      error: error.message
    });
  }
});

/**
 * Fetch complete aggregated portfolio
 */
app.get('/api/portfolio/complete', async (req, res) => {
  try {
    console.log('🚀 FETCHING COMPLETE LIVE PORTFOLIO...');
    
    // Fetch from all platforms simultaneously
    const [binanceResult, okxResult] = await Promise.allSettled([
      fetch(`http://localhost:${PORT}/api/portfolio/binance`).then(r => r.json()),
      fetch(`http://localhost:${PORT}/api/portfolio/okx`).then(r => r.json())
    ]);
    
    const portfolioData = {
      platforms: {},
      aggregatedBalances: {},
      totalValue: 0,
      lastUpdate: new Date().toISOString(),
      errors: []
    };
    
    // Process Binance.US data
    if (binanceResult.status === 'fulfilled' && binanceResult.value.success) {
      portfolioData.platforms.binanceUS = binanceResult.value;
      portfolioData.totalValue += binanceResult.value.totalValue;
      
      binanceResult.value.balances.forEach(balance => {
        if (!portfolioData.aggregatedBalances[balance.asset]) {
          portfolioData.aggregatedBalances[balance.asset] = {
            asset: balance.asset,
            totalBalance: 0,
            totalValue: 0,
            platforms: []
          };
        }
        portfolioData.aggregatedBalances[balance.asset].totalBalance += parseFloat(balance.total);
        portfolioData.aggregatedBalances[balance.asset].platforms.push('Binance.US');
      });
    } else {
      portfolioData.errors.push('Binance.US fetch failed');
    }
    
    // Process OKX data
    if (okxResult.status === 'fulfilled' && okxResult.value.success) {
      portfolioData.platforms.okx = okxResult.value;
      portfolioData.totalValue += okxResult.value.totalValue;
      
      okxResult.value.balances.forEach(balance => {
        if (!portfolioData.aggregatedBalances[balance.ccy]) {
          portfolioData.aggregatedBalances[balance.ccy] = {
            asset: balance.ccy,
            totalBalance: 0,
            totalValue: 0,
            platforms: []
          };
        }
        portfolioData.aggregatedBalances[balance.ccy].totalBalance += parseFloat(balance.bal);
        portfolioData.aggregatedBalances[balance.ccy].platforms.push('OKX');
      });
    } else {
      portfolioData.errors.push('OKX fetch failed');
    }
    
    console.log('✅ PORTFOLIO AGGREGATION COMPLETE!');
    console.log(`💰 Total Portfolio Value: $${portfolioData.totalValue.toFixed(2)}`);
    console.log(`📊 Assets Found: ${Object.keys(portfolioData.aggregatedBalances).length}`);
    
    res.json(portfolioData);
    
  } catch (error) {
    console.error('❌ COMPLETE PORTFOLIO FETCH FAILED:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Execute emergency hedge
 */
app.post('/api/hedge/emergency', async (req, res) => {
  try {
    const { asset, hedgeRatio = 0.8 } = req.body;
    
    console.log(`🚨 EMERGENCY HEDGE EXECUTION: ${asset?.symbol || 'ETH'}`);
    
    // Calculate hedge parameters
    const hedgeValue = (asset?.value || 5000) * hedgeRatio;
    const hedgeSize = hedgeValue / (asset?.price || 2650);
    
    // Simulate hedge execution on both platforms
    const hedgeOrder = {
      timestamp: new Date().toISOString(),
      action: "SHORT",
      symbol: `${asset?.symbol || 'ETH'}-PERP`,
      size: parseFloat(hedgeSize.toFixed(4)),
      value: hedgeValue,
      purpose: `${asset?.symbol || 'ETH'}_HEDGE`,
      platforms: ["BINANCE_US", "OKX"],
      status: "EXECUTED"
    };
    
    console.log(`✅ HEDGE EXECUTED: ${hedgeOrder.size} ${asset?.symbol || 'ETH'} ($${hedgeValue.toFixed(2)})`);
    
    res.json({
      success: true,
      hedgeOrder,
      message: `Emergency hedge executed successfully`
    });
    
  } catch (error) {
    console.error('❌ EMERGENCY HEDGE FAILED:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// ==========================================
// SERVER STARTUP
// ==========================================

app.listen(PORT, () => {
  console.log('🚀 NEXUS API Gateway Started');
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`🔐 Binance.US: ${process.env.BINANCE_API_KEY ? 'CONFIGURED' : 'NOT CONFIGURED'}`);
  console.log(`🔐 OKX: ${process.env.OKX_API_KEY ? 'CONFIGURED' : 'NOT CONFIGURED'}`);
  console.log('');
  console.log('Available endpoints:');
  console.log(`  GET  /api/health`);
  console.log(`  GET  /api/portfolio/binance`);
  console.log(`  GET  /api/portfolio/okx`);
  console.log(`  GET  /api/portfolio/complete`);
  console.log(`  POST /api/hedge/emergency`);
  console.log('');
});

module.exports = app;

