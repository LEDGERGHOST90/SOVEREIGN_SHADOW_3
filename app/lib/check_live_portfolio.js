
const crypto = require('crypto');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Read .env file manually - SECURE VERSION
const envPath = process.env.NODE_ENV === 'production' 
  ? '/home/ubuntu/sovereign_legacy_loop/app/.env'
  : path.join(__dirname, '../.env');

let envVars = {};
try {
  if (fs.existsSync(envPath)) {
    const envFile = fs.readFileSync(envPath, 'utf8');
    envFile.split('\n').forEach(line => {
      const [key, ...valueParts] = line.split('=');
      if (key && valueParts.length) {
        envVars[key.trim()] = valueParts.join('=').trim();
      }
    });
  }
} catch (error) {
  console.error('❌ Error reading .env file:', error.message);
  process.exit(1);
}

const API_KEY = envVars.BINANCE_US_API_KEY;
const SECRET_KEY = envVars.BINANCE_US_SECRET_KEY;

// Security check
if (!API_KEY || !SECRET_KEY || API_KEY.includes('<your_') || SECRET_KEY.includes('<your_')) {
  console.error('❌ SECURITY ERROR: API keys not properly configured!');
  console.error('   Please copy env.template to .env and fill in your actual API keys.');
  process.exit(1);
}
const BASE_URL = 'api.binance.us';

function createSignature(queryString) {
  return crypto
    .createHmac('sha256', SECRET_KEY)
    .update(queryString)
    .digest('hex');
}

function makeRequest(endpoint, params = {}) {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now();
    const queryString = Object.keys(params)
      .map(key => `${key}=${params[key]}`)
      .concat([`timestamp=${timestamp}`])
      .join('&');
    
    const signature = createSignature(queryString);
    const fullPath = `${endpoint}?${queryString}&signature=${signature}`;

    const options = {
      hostname: BASE_URL,
      path: fullPath,
      method: 'GET',
      headers: {
        'X-MBX-APIKEY': API_KEY
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(data);
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

async function getAccountInfo() {
  console.log('\n🔍 Fetching Binance US Account Information...\n');
  
  try {
    const accountData = await makeRequest('/api/v3/account', { recvWindow: 60000 });
    
    if (accountData.code) {
      console.error('❌ Error:', accountData.msg);
      return;
    }

    console.log('✅ Account Status:', accountData.accountType);
    console.log('✅ Can Trade:', accountData.canTrade);
    console.log('✅ Can Withdraw:', accountData.canWithdraw);
    console.log('✅ Can Deposit:', accountData.canDeposit);
    
    console.log('\n💰 LIVE PORTFOLIO BALANCES:\n');
    console.log('═'.repeat(80));
    
    const balances = accountData.balances
      .filter(b => parseFloat(b.free) > 0 || parseFloat(b.locked) > 0)
      .map(b => ({
        asset: b.asset,
        free: parseFloat(b.free),
        locked: parseFloat(b.locked),
        total: parseFloat(b.free) + parseFloat(b.locked)
      }))
      .sort((a, b) => b.total - a.total);

    if (balances.length === 0) {
      console.log('No balances found in account.');
      return;
    }

    balances.forEach((balance, index) => {
      console.log(`${index + 1}. ${balance.asset}`);
      console.log(`   Available: ${balance.free.toFixed(8)}`);
      console.log(`   Locked:    ${balance.locked.toFixed(8)}`);
      console.log(`   Total:     ${balance.total.toFixed(8)}`);
      console.log('─'.repeat(80));
    });

    console.log('\n📊 SUMMARY:');
    console.log(`   Total Assets: ${balances.length}`);
    console.log(`   Update Time: ${new Date(accountData.updateTime).toLocaleString()}`);
    
    // Get 24h ticker prices for valuation
    console.log('\n💵 Fetching current market prices...\n');
    const prices = await makeRequest('/api/v3/ticker/24hr', {});
    
    if (Array.isArray(prices)) {
      const priceMap = {};
      prices.forEach(p => {
        priceMap[p.symbol] = parseFloat(p.lastPrice);
      });

      let totalUSDValue = 0;
      console.log('📈 ESTIMATED USD VALUES:\n');
      console.log('═'.repeat(80));
      
      balances.forEach((balance, index) => {
        let usdValue = 0;
        
        if (balance.asset === 'USD' || balance.asset === 'USDT' || balance.asset === 'USDC') {
          usdValue = balance.total;
        } else {
          // Try different pairs
          const pairs = [`${balance.asset}USDT`, `${balance.asset}USD`, `${balance.asset}USDC`];
          for (const pair of pairs) {
            if (priceMap[pair]) {
              usdValue = balance.total * priceMap[pair];
              break;
            }
          }
        }
        
        if (usdValue > 0) {
          totalUSDValue += usdValue;
          console.log(`${index + 1}. ${balance.asset}: $${usdValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
        } else {
          console.log(`${index + 1}. ${balance.asset}: Price not available`);
        }
      });
      
      console.log('═'.repeat(80));
      console.log(`\n💎 TOTAL ESTIMATED VALUE: $${totalUSDValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
    }

  } catch (error) {
    console.error('❌ Request failed:', error.message);
  }
}

async function getTradeHistory() {
  console.log('\n\n📜 Recent Trade History:\n');
  console.log('═'.repeat(80));
  
  try {
    // Get all trading symbols
    const exchangeInfo = await makeRequest('/api/v3/exchangeInfo', {});
    const symbols = exchangeInfo.symbols?.slice(0, 5).map(s => s.symbol) || [];
    
    if (symbols.length === 0) {
      console.log('No trading pairs available.');
      return;
    }

    // Try to get recent trades for major pairs
    const majorPairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'];
    
    for (const symbol of majorPairs) {
      try {
        const trades = await makeRequest('/api/v3/myTrades', { 
          symbol, 
          limit: 5,
          recvWindow: 60000 
        });
        
        if (Array.isArray(trades) && trades.length > 0) {
          console.log(`\n${symbol} - Last ${trades.length} trades:`);
          trades.forEach((trade, i) => {
            const date = new Date(trade.time).toLocaleString();
            console.log(`  ${i+1}. ${trade.isBuyer ? 'BUY' : 'SELL'} ${trade.qty} @ ${trade.price} on ${date}`);
          });
        }
      } catch (e) {
        // Symbol might not have trades, skip silently
      }
    }
  } catch (error) {
    console.log('Unable to fetch trade history:', error.message);
  }
}

// Run the portfolio check
(async () => {
  console.log('╔═══════════════════════════════════════════════════════════════╗');
  console.log('║         SOVEREIGN LEGACY LOOP - LIVE PORTFOLIO CHECK          ║');
  console.log('╚═══════════════════════════════════════════════════════════════╝');
  console.log(`\n⏰ ${new Date().toLocaleString()}\n`);
  
  await getAccountInfo();
  await getTradeHistory();
  
  console.log('\n\n📝 NOTE: Ledger Live does not have a public API.');
  console.log('   For Ledger balances, you can:');
  console.log('   1. Export CSV from Ledger Live app (File > Export accounts)');
  console.log('   2. Use Ledger Live Desktop app to view balances');
  console.log('   3. Check blockchain explorers with your public addresses\n');
})();
